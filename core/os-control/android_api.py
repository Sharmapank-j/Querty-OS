"""
Android API wrapper for app management, intent handling, and system commands.
Provides high-level interface to Android functionality via ADB/shell commands.
"""

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.exceptions import AndroidControlError

logger = logging.getLogger(__name__)


class IntentAction(Enum):
    """Common Android intent actions."""

    VIEW = "android.intent.action.VIEW"
    MAIN = "android.intent.action.MAIN"
    SEND = "android.intent.action.SEND"
    DIAL = "android.intent.action.DIAL"
    CALL = "android.intent.action.CALL"
    EDIT = "android.intent.action.EDIT"
    PICK = "android.intent.action.PICK"
    SENDTO = "android.intent.action.SENDTO"


class PackageState(Enum):
    """Package installation state."""

    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class PackageInfo:
    """Information about an Android package."""

    package_name: str
    version_code: Optional[str] = None
    version_name: Optional[str] = None
    state: PackageState = PackageState.INSTALLED
    install_location: Optional[str] = None
    first_install_time: Optional[str] = None
    last_update_time: Optional[str] = None


@dataclass
class IntentResult:
    """Result of an intent broadcast."""

    success: bool
    result_code: Optional[int] = None
    data: Optional[str] = None
    error: Optional[str] = None


class AndroidAPI:
    """Android API wrapper using ADB and shell commands."""

    def __init__(self, adb_path: str = "adb", use_root: bool = False):
        """
        Initialize Android API wrapper.

        Args:
            adb_path: Path to ADB executable
            use_root: Whether to use root privileges for commands
        """
        self.adb_path = adb_path
        self.use_root = use_root
        self._device_id: Optional[str] = None
        logger.info(f"Initialized AndroidAPI with adb_path={adb_path}, use_root={use_root}")

    def _run_adb_command(
        self, args: List[str], check: bool = True, capture_output: bool = True, timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """
        Run an ADB command.

        Args:
            args: Command arguments (without 'adb' prefix)
            check: Whether to raise on non-zero exit
            capture_output: Whether to capture stdout/stderr
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess instance

        Raises:
            AndroidControlError: If command fails
        """
        cmd = [self.adb_path]
        if self._device_id:
            cmd.extend(["-s", self._device_id])
        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd, check=check, capture_output=capture_output, text=True, timeout=timeout
            )
            return result
        except subprocess.CalledProcessError as e:
            raise AndroidControlError(
                f"ADB command failed: {' '.join(cmd)}",
                error_code="ADB_COMMAND_FAILED",
                details={"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode},
            )
        except subprocess.TimeoutExpired as e:
            raise AndroidControlError(
                f"ADB command timed out: {' '.join(cmd)}",
                error_code="ADB_TIMEOUT",
                details={"timeout": timeout},
            )
        except FileNotFoundError:
            raise AndroidControlError(
                f"ADB not found at: {self.adb_path}",
                error_code="ADB_NOT_FOUND",
                details={"adb_path": self.adb_path},
            )

    def _run_shell_command(
        self, command: str, check: bool = True, timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """
        Run a shell command on the Android device.

        Args:
            command: Shell command to execute
            check: Whether to raise on non-zero exit
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess instance
        """
        if self.use_root:
            command = f"su -c '{command}'"

        return self._run_adb_command(["shell", command], check=check, timeout=timeout)

    def set_device(self, device_id: str) -> None:
        """
        Set target device for ADB commands.

        Args:
            device_id: Device serial number
        """
        self._device_id = device_id
        logger.info(f"Set target device to: {device_id}")

    def list_devices(self) -> List[str]:
        """
        List connected Android devices.

        Returns:
            List of device serial numbers
        """
        try:
            result = self._run_adb_command(["devices"])
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            devices = [
                line.split()[0] for line in lines if line.strip() and "device" in line.lower()
            ]
            logger.debug(f"Found {len(devices)} devices: {devices}")
            return devices
        except AndroidControlError as e:
            logger.error(f"Failed to list devices: {e}")
            return []

    def install_package(self, apk_path: str, allow_downgrade: bool = False) -> bool:
        """
        Install an APK package.

        Args:
            apk_path: Path to APK file
            allow_downgrade: Allow version downgrade

        Returns:
            True if successful, False otherwise
        """
        if not Path(apk_path).exists():
            raise AndroidControlError(
                f"APK not found: {apk_path}", error_code="APK_NOT_FOUND", details={"path": apk_path}
            )

        args = ["install"]
        if allow_downgrade:
            args.append("-d")
        args.append(apk_path)

        try:
            result = self._run_adb_command(args)
            success = "Success" in result.stdout
            if success:
                logger.info(f"Successfully installed package: {apk_path}")
            else:
                logger.error(f"Failed to install package: {result.stdout}")
            return success
        except AndroidControlError as e:
            logger.error(f"Package installation failed: {e}")
            return False

    def uninstall_package(self, package_name: str, keep_data: bool = False) -> bool:
        """
        Uninstall a package.

        Args:
            package_name: Package name to uninstall
            keep_data: Whether to keep app data

        Returns:
            True if successful, False otherwise
        """
        args = ["uninstall"]
        if keep_data:
            args.append("-k")
        args.append(package_name)

        try:
            result = self._run_adb_command(args)
            success = "Success" in result.stdout
            if success:
                logger.info(f"Successfully uninstalled package: {package_name}")
            else:
                logger.error(f"Failed to uninstall package: {result.stdout}")
            return success
        except AndroidControlError as e:
            logger.error(f"Package uninstallation failed: {e}")
            return False

    def list_packages(self, filter_enabled: bool = False) -> List[str]:
        """
        List installed packages.

        Args:
            filter_enabled: Only list enabled packages

        Returns:
            List of package names
        """
        cmd = "pm list packages"
        if filter_enabled:
            cmd += " -e"

        try:
            result = self._run_shell_command(cmd)
            packages = [
                line.replace("package:", "").strip()
                for line in result.stdout.strip().split("\n")
                if line.startswith("package:")
            ]
            logger.debug(f"Found {len(packages)} packages")
            return packages
        except AndroidControlError as e:
            logger.error(f"Failed to list packages: {e}")
            return []

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """
        Get detailed package information.

        Args:
            package_name: Package name

        Returns:
            PackageInfo object or None if not found
        """
        try:
            result = self._run_shell_command(f"dumpsys package {package_name}", check=False)
            if result.returncode != 0:
                return None

            output = result.stdout
            info = PackageInfo(package_name=package_name)

            for line in output.split("\n"):
                line = line.strip()
                if "versionCode=" in line:
                    info.version_code = line.split("versionCode=")[1].split()[0]
                elif "versionName=" in line:
                    info.version_name = line.split("versionName=")[1].strip()
                elif "firstInstallTime=" in line:
                    info.first_install_time = line.split("firstInstallTime=")[1].strip()
                elif "lastUpdateTime=" in line:
                    info.last_update_time = line.split("lastUpdateTime=")[1].strip()

            logger.debug(f"Retrieved package info for: {package_name}")
            return info
        except AndroidControlError as e:
            logger.error(f"Failed to get package info: {e}")
            return None

    def send_intent(
        self,
        action: str,
        data: Optional[str] = None,
        component: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        flags: Optional[List[str]] = None,
    ) -> IntentResult:
        """
        Send an Android intent.

        Args:
            action: Intent action (e.g., "android.intent.action.VIEW")
            data: Intent data URI
            component: Component name (package/activity)
            extras: Extra key-value pairs
            flags: Intent flags

        Returns:
            IntentResult object
        """
        cmd_parts = ["am", "start" if component else "broadcast"]

        if action:
            cmd_parts.extend(["-a", action])

        if data:
            cmd_parts.extend(["-d", data])

        if component:
            cmd_parts.extend(["-n", component])

        if extras:
            for key, value in extras.items():
                if isinstance(value, bool):
                    cmd_parts.extend(["--ez", key, str(value).lower()])
                elif isinstance(value, int):
                    cmd_parts.extend(["--ei", key, str(value)])
                elif isinstance(value, str):
                    cmd_parts.extend(["--es", key, value])

        if flags:
            for flag in flags:
                cmd_parts.extend(["-f", flag])

        try:
            result = self._run_shell_command(" ".join(cmd_parts), check=False)
            success = result.returncode == 0
            return IntentResult(
                success=success,
                result_code=result.returncode,
                data=result.stdout.strip() if success else None,
                error=result.stderr.strip() if not success else None,
            )
        except AndroidControlError as e:
            logger.error(f"Failed to send intent: {e}")
            return IntentResult(success=False, error=str(e))

    def start_activity(self, package_name: str, activity_name: str) -> bool:
        """
        Start an Android activity.

        Args:
            package_name: Package name
            activity_name: Activity name (can be relative with dot prefix)

        Returns:
            True if successful, False otherwise
        """
        if activity_name.startswith("."):
            component = f"{package_name}/{package_name}{activity_name}"
        else:
            component = f"{package_name}/{activity_name}"

        result = self.send_intent(action=IntentAction.MAIN.value, component=component)
        return result.success

    def stop_app(self, package_name: str, force: bool = False) -> bool:
        """
        Stop an application.

        Args:
            package_name: Package name
            force: Force stop even if app is foreground

        Returns:
            True if successful, False otherwise
        """
        try:
            if force:
                self._run_shell_command(f"am force-stop {package_name}")
            else:
                self._run_shell_command(f"am kill {package_name}")
            logger.info(f"Stopped app: {package_name}")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to stop app: {e}")
            return False

    def get_property(self, prop_name: str) -> Optional[str]:
        """
        Get Android system property.

        Args:
            prop_name: Property name

        Returns:
            Property value or None if not found
        """
        try:
            result = self._run_shell_command(f"getprop {prop_name}", check=False)
            if result.returncode == 0 and result.stdout.strip():
                value = result.stdout.strip()
                logger.debug(f"Property {prop_name} = {value}")
                return value
            return None
        except AndroidControlError as e:
            logger.error(f"Failed to get property: {e}")
            return None

    def set_property(self, prop_name: str, value: str) -> bool:
        """
        Set Android system property (requires root).

        Args:
            prop_name: Property name
            value: Property value

        Returns:
            True if successful, False otherwise
        """
        if not self.use_root:
            logger.warning("Setting properties requires root access")
            return False

        try:
            self._run_shell_command(f"setprop {prop_name} {value}")
            logger.info(f"Set property {prop_name} = {value}")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to set property: {e}")
            return False

    def take_screenshot(self, output_path: str) -> bool:
        """
        Take a screenshot and save to device.

        Args:
            output_path: Output path on device (e.g., /sdcard/screenshot.png)

        Returns:
            True if successful, False otherwise
        """
        try:
            self._run_shell_command(f"screencap -p {output_path}")
            logger.info(f"Screenshot saved to: {output_path}")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def input_text(self, text: str) -> bool:
        """
        Input text into focused field.

        Args:
            text: Text to input

        Returns:
            True if successful, False otherwise
        """
        try:
            escaped_text = text.replace(" ", "%s")
            self._run_shell_command(f"input text '{escaped_text}'")
            logger.debug(f"Input text: {text}")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to input text: {e}")
            return False

    def input_tap(self, x: int, y: int) -> bool:
        """
        Simulate a tap at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful, False otherwise
        """
        try:
            self._run_shell_command(f"input tap {x} {y}")
            logger.debug(f"Tapped at ({x}, {y})")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to tap: {e}")
            return False

    def input_keyevent(self, keycode: int) -> bool:
        """
        Send a key event.

        Args:
            keycode: Android keycode

        Returns:
            True if successful, False otherwise
        """
        try:
            self._run_shell_command(f"input keyevent {keycode}")
            logger.debug(f"Sent keyevent: {keycode}")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to send keyevent: {e}")
            return False

    def reboot(self, mode: Optional[str] = None) -> bool:
        """
        Reboot device.

        Args:
            mode: Reboot mode (None, "recovery", "bootloader")

        Returns:
            True if command sent successfully
        """
        try:
            if mode:
                self._run_adb_command(["reboot", mode])
            else:
                self._run_adb_command(["reboot"])
            logger.info(f"Reboot command sent (mode={mode})")
            return True
        except AndroidControlError as e:
            logger.error(f"Failed to reboot: {e}")
            return False
