"""
Linux chroot management for Querty-OS.
Handles mount/unmount, command execution, and package management in chroot environments.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from core.exceptions import LinuxControlError

logger = logging.getLogger(__name__)


class ChrootState(Enum):
    """Chroot environment state."""

    UNMOUNTED = "unmounted"
    MOUNTED = "mounted"
    ACTIVE = "active"
    ERROR = "error"


class PackageManager(Enum):
    """Supported package managers."""

    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PACMAN = "pacman"
    ZYPPER = "zypper"
    APK = "apk"


@dataclass
class ChrootInfo:
    """Information about a chroot environment."""

    name: str
    path: Path
    state: ChrootState
    distro: Optional[str] = None
    architecture: Optional[str] = None
    package_manager: Optional[PackageManager] = None
    mount_points: Optional[List[str]] = None


class LinuxChroot:
    """Manages Linux chroot environments."""

    def __init__(self, chroot_base: str = "/data/linux", use_sudo: bool = True):
        """
        Initialize Linux chroot manager.

        Args:
            chroot_base: Base directory for chroot environments
            use_sudo: Whether to use sudo for privileged operations
        """
        self.chroot_base = Path(chroot_base)
        self.use_sudo = use_sudo
        self.chroots: Dict[str, ChrootInfo] = {}
        logger.info(f"Initialized LinuxChroot with base: {chroot_base}")

    def _run_command(
        self, cmd: List[str], check: bool = True, capture_output: bool = True, timeout: int = 60
    ) -> subprocess.CompletedProcess:
        """
        Run a command with optional sudo.

        Args:
            cmd: Command and arguments
            check: Whether to raise on non-zero exit
            capture_output: Whether to capture stdout/stderr
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess instance

        Raises:
            LinuxControlError: If command fails
        """
        if self.use_sudo and cmd[0] not in ["sudo"]:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd, check=check, capture_output=capture_output, text=True, timeout=timeout
            )
            return result
        except subprocess.CalledProcessError as e:
            raise LinuxControlError(
                f"Command failed: {' '.join(cmd)}",
                error_code="COMMAND_FAILED",
                details={"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode},
            )
        except subprocess.TimeoutExpired:
            raise LinuxControlError(
                f"Command timed out: {' '.join(cmd)}",
                error_code="COMMAND_TIMEOUT",
                details={"timeout": timeout},
            )
        except FileNotFoundError as e:
            raise LinuxControlError(
                f"Command not found: {cmd[0]}", error_code="COMMAND_NOT_FOUND", details={"cmd": cmd}
            )

    def _detect_package_manager(self, chroot_path: Path) -> Optional[PackageManager]:
        """
        Detect the package manager in a chroot.

        Args:
            chroot_path: Path to chroot

        Returns:
            PackageManager enum or None if not detected
        """
        managers = {
            "usr/bin/apt": PackageManager.APT,
            "usr/bin/yum": PackageManager.YUM,
            "usr/bin/dnf": PackageManager.DNF,
            "usr/bin/pacman": PackageManager.PACMAN,
            "usr/bin/zypper": PackageManager.ZYPPER,
            "sbin/apk": PackageManager.APK,
        }

        for path, manager in managers.items():
            if (chroot_path / path).exists():
                logger.debug(f"Detected package manager: {manager.value}")
                return manager

        logger.warning(f"Could not detect package manager in {chroot_path}")
        return None

    def create_chroot(
        self, name: str, distro: str = "debian", architecture: str = "arm64"
    ) -> ChrootInfo:
        """
        Create a new chroot environment.

        Args:
            name: Chroot name
            distro: Distribution name
            architecture: Target architecture

        Returns:
            ChrootInfo object

        Raises:
            LinuxControlError: If creation fails
        """
        chroot_path = self.chroot_base / name

        if chroot_path.exists():
            raise LinuxControlError(
                f"Chroot already exists: {name}",
                error_code="CHROOT_EXISTS",
                details={"path": str(chroot_path)},
            )

        try:
            # Create chroot directory
            self._run_command(["mkdir", "-p", str(chroot_path)])

            # Create basic directory structure
            for subdir in ["dev", "proc", "sys", "tmp", "home", "root"]:
                self._run_command(["mkdir", "-p", str(chroot_path / subdir)])

            info = ChrootInfo(
                name=name,
                path=chroot_path,
                state=ChrootState.UNMOUNTED,
                distro=distro,
                architecture=architecture,
                mount_points=[],
            )

            self.chroots[name] = info
            logger.info(f"Created chroot: {name} at {chroot_path}")
            return info

        except LinuxControlError as e:
            logger.error(f"Failed to create chroot: {e}")
            raise

    def mount_chroot(self, name: str) -> bool:
        """
        Mount necessary filesystems in chroot.

        Args:
            name: Chroot name

        Returns:
            True if successful, False otherwise

        Raises:
            LinuxControlError: If chroot not found or mount fails
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        if info.state == ChrootState.MOUNTED:
            logger.info(f"Chroot {name} already mounted")
            return True

        mount_points = [
            ("proc", "proc", "proc"),
            ("sys", "sysfs", "sys"),
            ("dev", "devtmpfs", "dev"),
            ("dev/pts", "devpts", "dev/pts"),
        ]

        mounted = []
        try:
            for target, fstype, source in mount_points:
                target_path = info.path / target
                self._run_command(["mkdir", "-p", str(target_path)])
                self._run_command(["mount", "-t", fstype, source, str(target_path)])
                mounted.append(str(target_path))
                logger.debug(f"Mounted {fstype} at {target_path}")

            info.state = ChrootState.MOUNTED
            info.mount_points = mounted
            logger.info(f"Successfully mounted chroot: {name}")
            return True

        except LinuxControlError as e:
            logger.error(f"Failed to mount chroot: {e}")
            # Try to unmount what we mounted
            for mount_point in reversed(mounted):
                try:
                    self._run_command(["umount", mount_point], check=False)
                except:
                    pass
            info.state = ChrootState.ERROR
            raise

    def unmount_chroot(self, name: str, force: bool = False) -> bool:
        """
        Unmount filesystems in chroot.

        Args:
            name: Chroot name
            force: Force unmount with lazy option

        Returns:
            True if successful, False otherwise

        Raises:
            LinuxControlError: If chroot not found
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        if info.state == ChrootState.UNMOUNTED:
            logger.info(f"Chroot {name} already unmounted")
            return True

        mount_points = info.mount_points or []
        # Reverse order for unmounting
        mount_points = sorted(mount_points, reverse=True)

        failed_unmounts = []
        for mount_point in mount_points:
            try:
                cmd = ["umount"]
                if force:
                    cmd.append("-l")  # Lazy unmount
                cmd.append(mount_point)
                self._run_command(cmd, check=False)
                logger.debug(f"Unmounted {mount_point}")
            except LinuxControlError:
                failed_unmounts.append(mount_point)
                logger.warning(f"Failed to unmount {mount_point}")

        if failed_unmounts:
            logger.error(f"Failed to unmount some filesystems: {failed_unmounts}")
            info.state = ChrootState.ERROR
            return False

        info.state = ChrootState.UNMOUNTED
        info.mount_points = []
        logger.info(f"Successfully unmounted chroot: {name}")
        return True

    def execute_in_chroot(
        self, name: str, command: str, timeout: int = 60, env: Optional[Dict[str, str]] = None
    ) -> subprocess.CompletedProcess:
        """
        Execute a command inside the chroot.

        Args:
            name: Chroot name
            command: Command to execute
            timeout: Command timeout in seconds
            env: Environment variables

        Returns:
            CompletedProcess instance

        Raises:
            LinuxControlError: If chroot not found or command fails
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        if info.state != ChrootState.MOUNTED:
            raise LinuxControlError(
                f"Chroot not mounted: {name}",
                error_code="CHROOT_NOT_MOUNTED",
                details={"state": info.state.value},
            )

        # Build chroot command
        cmd = ["chroot", str(info.path), "/bin/sh", "-c", command]

        # Set environment variables if provided
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False, env=full_env
            )
            if result.returncode != 0:
                logger.warning(
                    f"Command in chroot returned {result.returncode}: {result.stderr.strip()}"
                )
            return result
        except subprocess.TimeoutExpired:
            raise LinuxControlError(
                f"Command timed out in chroot: {command}",
                error_code="CHROOT_COMMAND_TIMEOUT",
                details={"timeout": timeout},
            )

    def install_package(self, name: str, packages: List[str], update_repos: bool = True) -> bool:
        """
        Install packages in chroot using detected package manager.

        Args:
            name: Chroot name
            packages: List of package names
            update_repos: Whether to update package repositories first

        Returns:
            True if successful, False otherwise

        Raises:
            LinuxControlError: If chroot not found or no package manager detected
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        if not info.package_manager:
            info.package_manager = self._detect_package_manager(info.path)

        if not info.package_manager:
            raise LinuxControlError(
                f"No package manager detected in chroot: {name}",
                error_code="NO_PACKAGE_MANAGER",
                details={"path": str(info.path)},
            )

        pm = info.package_manager
        package_str = " ".join(packages)

        try:
            # Update repositories
            if update_repos:
                if pm == PackageManager.APT:
                    self.execute_in_chroot(name, "apt-get update -y", timeout=300)
                elif pm in [PackageManager.YUM, PackageManager.DNF]:
                    self.execute_in_chroot(name, f"{pm.value} makecache", timeout=300)
                elif pm == PackageManager.PACMAN:
                    self.execute_in_chroot(name, "pacman -Sy", timeout=300)
                elif pm == PackageManager.APK:
                    self.execute_in_chroot(name, "apk update", timeout=300)

            # Install packages
            if pm == PackageManager.APT:
                cmd = f"DEBIAN_FRONTEND=noninteractive apt-get install -y {package_str}"
            elif pm == PackageManager.YUM:
                cmd = f"yum install -y {package_str}"
            elif pm == PackageManager.DNF:
                cmd = f"dnf install -y {package_str}"
            elif pm == PackageManager.PACMAN:
                cmd = f"pacman -S --noconfirm {package_str}"
            elif pm == PackageManager.ZYPPER:
                cmd = f"zypper install -y {package_str}"
            elif pm == PackageManager.APK:
                cmd = f"apk add {package_str}"
            else:
                raise LinuxControlError(
                    f"Unsupported package manager: {pm}",
                    error_code="UNSUPPORTED_PACKAGE_MANAGER",
                )

            result = self.execute_in_chroot(name, cmd, timeout=600)

            if result.returncode == 0:
                logger.info(f"Successfully installed packages in {name}: {packages}")
                return True
            else:
                logger.error(f"Failed to install packages: {result.stderr}")
                return False

        except LinuxControlError as e:
            logger.error(f"Package installation failed: {e}")
            return False

    def remove_package(self, name: str, packages: List[str]) -> bool:
        """
        Remove packages from chroot.

        Args:
            name: Chroot name
            packages: List of package names

        Returns:
            True if successful, False otherwise
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        if not info.package_manager:
            info.package_manager = self._detect_package_manager(info.path)

        if not info.package_manager:
            raise LinuxControlError(
                f"No package manager detected in chroot: {name}",
                error_code="NO_PACKAGE_MANAGER",
            )

        pm = info.package_manager
        package_str = " ".join(packages)

        try:
            if pm == PackageManager.APT:
                cmd = f"apt-get remove -y {package_str}"
            elif pm == PackageManager.YUM:
                cmd = f"yum remove -y {package_str}"
            elif pm == PackageManager.DNF:
                cmd = f"dnf remove -y {package_str}"
            elif pm == PackageManager.PACMAN:
                cmd = f"pacman -R --noconfirm {package_str}"
            elif pm == PackageManager.ZYPPER:
                cmd = f"zypper remove -y {package_str}"
            elif pm == PackageManager.APK:
                cmd = f"apk del {package_str}"
            else:
                raise LinuxControlError(
                    f"Unsupported package manager: {pm}",
                    error_code="UNSUPPORTED_PACKAGE_MANAGER",
                )

            result = self.execute_in_chroot(name, cmd, timeout=300)

            if result.returncode == 0:
                logger.info(f"Successfully removed packages from {name}: {packages}")
                return True
            else:
                logger.error(f"Failed to remove packages: {result.stderr}")
                return False

        except LinuxControlError as e:
            logger.error(f"Package removal failed: {e}")
            return False

    def list_chroots(self) -> List[ChrootInfo]:
        """
        List all managed chroots.

        Returns:
            List of ChrootInfo objects
        """
        return list(self.chroots.values())

    def get_chroot_info(self, name: str) -> Optional[ChrootInfo]:
        """
        Get information about a chroot.

        Args:
            name: Chroot name

        Returns:
            ChrootInfo object or None if not found
        """
        return self.chroots.get(name)

    def destroy_chroot(self, name: str, force: bool = False) -> bool:
        """
        Destroy a chroot environment.

        Args:
            name: Chroot name
            force: Force destruction even if unmount fails

        Returns:
            True if successful, False otherwise
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]

        # Try to unmount first
        if info.state == ChrootState.MOUNTED:
            try:
                self.unmount_chroot(name, force=force)
            except LinuxControlError as e:
                if not force:
                    logger.error(f"Cannot destroy chroot, unmount failed: {e}")
                    return False
                logger.warning(f"Forcing destruction despite unmount failure: {e}")

        try:
            # Remove chroot directory
            self._run_command(["rm", "-rf", str(info.path)])
            del self.chroots[name]
            logger.info(f"Destroyed chroot: {name}")
            return True
        except LinuxControlError as e:
            logger.error(f"Failed to destroy chroot: {e}")
            return False

    def copy_to_chroot(self, name: str, source: str, destination: str) -> bool:
        """
        Copy files into chroot.

        Args:
            name: Chroot name
            source: Source path on host
            destination: Destination path in chroot (relative)

        Returns:
            True if successful, False otherwise
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        dest_path = info.path / destination.lstrip("/")

        try:
            self._run_command(["cp", "-r", source, str(dest_path)])
            logger.info(f"Copied {source} to chroot {name}:{destination}")
            return True
        except LinuxControlError as e:
            logger.error(f"Failed to copy to chroot: {e}")
            return False

    def copy_from_chroot(self, name: str, source: str, destination: str) -> bool:
        """
        Copy files from chroot to host.

        Args:
            name: Chroot name
            source: Source path in chroot (relative)
            destination: Destination path on host

        Returns:
            True if successful, False otherwise
        """
        if name not in self.chroots:
            raise LinuxControlError(
                f"Chroot not found: {name}", error_code="CHROOT_NOT_FOUND", details={"name": name}
            )

        info = self.chroots[name]
        source_path = info.path / source.lstrip("/")

        try:
            self._run_command(["cp", "-r", str(source_path), destination])
            logger.info(f"Copied from chroot {name}:{source} to {destination}")
            return True
        except LinuxControlError as e:
            logger.error(f"Failed to copy from chroot: {e}")
            return False
