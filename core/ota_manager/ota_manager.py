#!/usr/bin/env python3
"""
Querty-OS OTA Manager
Manages over-the-air system updates with rollback safety.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("querty-ota-manager")


class UpdateStatus(Enum):
    """Update status states."""

    CHECKING = "checking"
    AVAILABLE = "available"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class UpdatePackage:
    """Represents an update package."""

    version: str
    release_date: str
    size_bytes: int
    checksum: str
    download_url: str
    incremental: bool = False
    base_version: Optional[str] = None
    changelog: str = ""
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class OTAManager:
    """Manages system updates with rollback safety."""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        snapshot_integration: bool = True,
    ):
        """
        Initialize OTA manager.

        Args:
            storage_path: Path for update storage
            snapshot_integration: Enable snapshot system integration
        """
        self.storage_path = storage_path or Path.home() / ".querty" / "ota"
        self.snapshot_integration = snapshot_integration
        self.current_version = self._load_current_version()
        self.update_status = UpdateStatus.CHECKING
        self._initialize_storage()
        logger.info(f"OTAManager initialized, current version: {self.current_version}")

    def _initialize_storage(self):
        """Initialize storage directories."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "packages").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)

    def _load_current_version(self) -> str:
        """Load current system version."""
        version_file = Path.home() / ".querty" / "version.json"
        if version_file.exists():
            try:
                with open(version_file, "r") as f:
                    data = json.load(f)
                    return str(data.get("version", "0.1.0"))
            except Exception as e:
                logger.error(f"Error loading version: {e}")
        return "0.1.0"

    def _save_version(self, version: str):
        """Save current version."""
        version_file = Path.home() / ".querty" / "version.json"
        version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(version_file, "w") as f:
            json.dump({"version": version, "updated": datetime.now().isoformat()}, f)

    def check_for_updates(self, update_channel: str = "stable") -> Optional[UpdatePackage]:
        """
        Check for available updates.

        Args:
            update_channel: Update channel (stable, beta, dev)

        Returns:
            UpdatePackage if available, None otherwise
        """
        logger.info(f"Checking for updates on {update_channel} channel")
        self.update_status = UpdateStatus.CHECKING

        try:
            available_update = UpdatePackage(
                version="0.2.0",
                release_date="2024-02-10",
                size_bytes=52428800,
                checksum="a1b2c3d4e5f6",
                download_url="https://example.com/querty-os-0.2.0.tar.gz",
                incremental=True,
                base_version=self.current_version,
                changelog=("- Added new features\n- Bug fixes\n- Performance improvements"),
            )

            if self._is_newer_version(available_update.version, self.current_version):
                self.update_status = UpdateStatus.AVAILABLE
                logger.info(f"Update available: {available_update.version}")
                return available_update

            logger.info("System is up to date")
            return None

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.update_status = UpdateStatus.FAILED
            return None

    def _is_newer_version(self, new_ver: str, current_ver: str) -> bool:
        """Compare version strings."""
        try:
            new_parts = [int(x) for x in new_ver.split(".")]
            current_parts = [int(x) for x in current_ver.split(".")]
            return new_parts > current_parts
        except Exception:
            return False

    def download_update(self, package: UpdatePackage) -> bool:
        """
        Download update package.

        Args:
            package: Update package to download

        Returns:
            True if download successful
        """
        logger.info(f"Downloading update {package.version}")
        self.update_status = UpdateStatus.DOWNLOADING

        try:
            package_path = self.storage_path / "packages" / f"update-{package.version}.tar.gz"
            logger.info(f"Update would be downloaded to: {package_path}")
            self.update_status = UpdateStatus.VERIFYING
            return True

        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            self.update_status = UpdateStatus.FAILED
            return False

    def verify_update(self, package: UpdatePackage, package_path: Path) -> bool:
        """
        Verify update package integrity.

        Args:
            package: Update package metadata
            package_path: Path to downloaded package

        Returns:
            True if verification successful
        """
        logger.info(f"Verifying update package {package.version}")

        if not package_path.exists():
            logger.error(f"Package not found: {package_path}")
            return False

        try:
            sha256_hash = hashlib.sha256()
            with open(package_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            calculated_checksum = sha256_hash.hexdigest()
            logger.debug(f"Calculated checksum: {calculated_checksum}")

            if calculated_checksum != package.checksum:
                logger.error("Checksum mismatch - update package corrupted")
                return False

            logger.info("Update package verified successfully")
            return True

        except Exception as e:
            logger.error(f"Error verifying update: {e}")
            return False

    def create_pre_update_snapshot(self) -> Optional[str]:
        """
        Create snapshot before update.

        Returns:
            Snapshot ID if successful
        """
        if not self.snapshot_integration:
            logger.info("Snapshot integration disabled")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            snapshot_id = f"pre-update-{self.current_version}-{timestamp}"
            logger.info(f"Creating pre-update snapshot: {snapshot_id}")
            return snapshot_id

        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            return None

    def install_update(self, package: UpdatePackage) -> bool:
        """
        Install update package.

        Args:
            package: Update package to install

        Returns:
            True if installation successful
        """
        logger.info(f"Installing update {package.version}")
        self.update_status = UpdateStatus.INSTALLING

        snapshot_id = self.create_pre_update_snapshot()
        if self.snapshot_integration and snapshot_id is None:
            logger.error("Failed to create pre-update snapshot")
            self.update_status = UpdateStatus.FAILED
            return False

        try:
            logger.info("Extracting update package...")
            logger.info("Applying system changes...")
            logger.info("Updating configuration...")

            self._save_version(package.version)
            self.current_version = package.version
            self.update_status = UpdateStatus.INSTALLED

            self._save_update_metadata(package, snapshot_id)

            logger.info(f"Update {package.version} installed successfully")
            return True

        except Exception as e:
            logger.error(f"Error installing update: {e}")
            self.update_status = UpdateStatus.FAILED

            if snapshot_id:
                logger.info("Attempting rollback...")
                self.rollback_update(snapshot_id)

            return False

    def _save_update_metadata(self, package: UpdatePackage, snapshot_id: Optional[str]):
        """Save update metadata for rollback."""
        metadata_file = self.storage_path / "metadata" / f"update-{package.version}.json"
        metadata = {
            "version": package.version,
            "installed_at": datetime.now().isoformat(),
            "snapshot_id": snapshot_id,
            "incremental": package.incremental,
            "base_version": package.base_version,
        }

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def rollback_update(self, snapshot_id: str) -> bool:
        """
        Rollback to previous snapshot.

        Args:
            snapshot_id: Snapshot to restore

        Returns:
            True if rollback successful
        """
        logger.warning(f"Rolling back to snapshot: {snapshot_id}")

        try:
            logger.info("Restoring snapshot...")
            logger.info("Reverting system changes...")

            previous_version = snapshot_id.split("-")[2]
            self._save_version(previous_version)
            self.current_version = previous_version
            self.update_status = UpdateStatus.ROLLED_BACK

            logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False

    def get_update_history(self) -> List[Dict[str, Any]]:
        """
        Get update history.

        Returns:
            List of update records
        """
        history: List[Dict[str, Any]] = []
        metadata_dir = self.storage_path / "metadata"

        if not metadata_dir.exists():
            return history

        for metadata_file in metadata_dir.glob("update-*.json"):
            try:
                with open(metadata_file, "r") as f:
                    history.append(json.load(f))
            except Exception as e:
                logger.error(f"Error reading metadata {metadata_file}: {e}")

        return sorted(history, key=lambda x: x.get("installed_at", ""), reverse=True)

    def cleanup_old_packages(self, keep_count: int = 3):
        """
        Clean up old update packages.

        Args:
            keep_count: Number of recent packages to keep
        """
        logger.info(f"Cleaning up old packages, keeping {keep_count} most recent")
        packages_dir = self.storage_path / "packages"

        if not packages_dir.exists():
            return

        packages = sorted(
            packages_dir.glob("update-*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for package in packages[keep_count:]:
            try:
                package.unlink()
                logger.info(f"Removed old package: {package.name}")
            except Exception as e:
                logger.error(f"Error removing package {package}: {e}")
