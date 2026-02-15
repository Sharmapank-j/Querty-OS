"""
Incremental backup engine tracking changed files.
Efficiently backs up only modified files since last backup.
"""

import hashlib
import json
import logging
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from core.exceptions import SnapshotError

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Metadata for a tracked file."""

    path: str
    size: int
    mtime: float
    checksum: str
    backed_up: bool = False
    backup_path: Optional[str] = None


@dataclass
class BackupManifest:
    """Manifest for an incremental backup."""

    backup_id: str
    name: str
    source_path: str
    backup_dir: str
    created_at: datetime
    parent_backup_id: Optional[str] = None
    files: Dict[str, FileMetadata] = None
    new_files: int = 0
    modified_files: int = 0
    deleted_files: int = 0
    total_size: int = 0

    def __post_init__(self):
        if self.files is None:
            self.files = {}


class IncrementalBackup:
    """Incremental backup engine with change tracking."""

    def __init__(self, backup_dir: str = "/data/backups"):
        """
        Initialize incremental backup engine.

        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.manifests: Dict[str, BackupManifest] = {}
        self.file_index: Dict[str, Dict[str, FileMetadata]] = {}  # source_path -> file_index

        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized IncrementalBackup with dir: {backup_dir}")
        except Exception as e:
            raise SnapshotError(
                f"Failed to create backup directory: {e}",
                error_code="BACKUP_DIR_FAILED",
                details={"path": backup_dir},
            )

    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().isoformat()
        data = f"{timestamp}:{len(self.manifests)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """
        Calculate MD5 checksum of file (fast for change detection).

        Args:
            file_path: Path to file

        Returns:
            Hex digest of checksum
        """
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192 * 16)  # 128KB chunks
                if not chunk:
                    break
                md5.update(chunk)
        return md5.hexdigest()

    def _scan_directory(self, source_path: Path) -> Dict[str, FileMetadata]:
        """
        Scan directory and build file index.

        Args:
            source_path: Directory to scan

        Returns:
            Dictionary mapping relative path to FileMetadata
        """
        file_index = {}

        try:
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(source_path))
                    stat = file_path.stat()

                    # Calculate checksum
                    checksum = self._calculate_file_checksum(file_path)

                    file_index[relative_path] = FileMetadata(
                        path=relative_path,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        checksum=checksum,
                    )

            logger.debug(f"Scanned {len(file_index)} files from {source_path}")
            return file_index

        except Exception as e:
            logger.error(f"Failed to scan directory: {e}")
            raise SnapshotError(
                f"Directory scan failed: {e}",
                error_code="SCAN_FAILED",
                details={"path": str(source_path)},
            )

    def _detect_changes(
        self, current_index: Dict[str, FileMetadata], previous_index: Dict[str, FileMetadata]
    ) -> tuple[Set[str], Set[str], Set[str]]:
        """
        Detect file changes between two indices.

        Args:
            current_index: Current file index
            previous_index: Previous file index

        Returns:
            Tuple of (new_files, modified_files, deleted_files)
        """
        current_files = set(current_index.keys())
        previous_files = set(previous_index.keys())

        new_files = current_files - previous_files
        deleted_files = previous_files - current_files
        potentially_modified = current_files & previous_files

        # Check which files actually changed
        modified_files = set()
        for file_path in potentially_modified:
            current = current_index[file_path]
            previous = previous_index[file_path]

            # Compare checksum for definitive change detection
            if current.checksum != previous.checksum:
                modified_files.add(file_path)

        logger.debug(
            f"Changes detected: {len(new_files)} new, {len(modified_files)} modified, "
            f"{len(deleted_files)} deleted"
        )
        return (new_files, modified_files, deleted_files)

    def create_backup(
        self,
        source_path: str,
        name: str,
        parent_backup_id: Optional[str] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> BackupManifest:
        """
        Create an incremental backup.

        Args:
            source_path: Path to backup
            name: Backup name
            parent_backup_id: Parent backup for incremental (None for full)
            exclude_patterns: Patterns to exclude

        Returns:
            BackupManifest object

        Raises:
            SnapshotError: If backup creation fails
        """
        source = Path(source_path)
        if not source.exists():
            raise SnapshotError(
                f"Source path not found: {source_path}",
                error_code="SOURCE_NOT_FOUND",
                details={"path": source_path},
            )

        backup_id = self._generate_backup_id()
        backup_subdir = self.backup_dir / f"{name}_{backup_id}"
        backup_subdir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Creating backup: {name} (id={backup_id})")

            # Scan current state
            current_index = self._scan_directory(source)

            # Apply exclusions
            if exclude_patterns:
                for pattern in exclude_patterns:
                    current_index = {k: v for k, v in current_index.items() if pattern not in k}

            # Determine changes
            new_files = set()
            modified_files = set()
            deleted_files = set()

            if parent_backup_id and parent_backup_id in self.manifests:
                parent_manifest = self.manifests[parent_backup_id]
                previous_index = parent_manifest.files
                new_files, modified_files, deleted_files = self._detect_changes(
                    current_index, previous_index
                )
            else:
                # Full backup - all files are new
                new_files = set(current_index.keys())
                logger.info("Creating full backup (no parent)")

            # Copy changed files
            files_to_backup = new_files | modified_files
            total_size = 0

            for file_path in files_to_backup:
                source_file = source / file_path
                dest_file = backup_subdir / file_path

                # Create parent directories
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(source_file, dest_file)

                # Update metadata
                current_index[file_path].backed_up = True
                current_index[file_path].backup_path = str(dest_file)
                total_size += current_index[file_path].size

            # Create manifest
            manifest = BackupManifest(
                backup_id=backup_id,
                name=name,
                source_path=source_path,
                backup_dir=str(backup_subdir),
                created_at=datetime.now(),
                parent_backup_id=parent_backup_id,
                files=current_index,
                new_files=len(new_files),
                modified_files=len(modified_files),
                deleted_files=len(deleted_files),
                total_size=total_size,
            )

            # Save manifest
            self._save_manifest(manifest)

            self.manifests[backup_id] = manifest
            self.file_index[source_path] = current_index

            logger.info(
                f"Created backup: {name} ({len(files_to_backup)} files, {total_size} bytes)"
            )
            return manifest

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            # Clean up partial backup
            if backup_subdir.exists():
                shutil.rmtree(backup_subdir, ignore_errors=True)
            raise SnapshotError(
                f"Backup creation failed: {e}",
                error_code="BACKUP_FAILED",
                details={"source": source_path, "error": str(e)},
            )

    def _save_manifest(self, manifest: BackupManifest) -> None:
        """
        Save backup manifest to disk.

        Args:
            manifest: BackupManifest to save
        """
        manifest_file = Path(manifest.backup_dir) / "manifest.json"

        try:
            # Convert to dict for JSON serialization
            manifest_dict = asdict(manifest)
            manifest_dict["created_at"] = manifest.created_at.isoformat()

            with open(manifest_file, "w") as f:
                json.dump(manifest_dict, f, indent=2)

            logger.debug(f"Saved manifest: {manifest_file}")

        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")

    def _load_manifest(self, manifest_file: Path) -> BackupManifest:
        """
        Load backup manifest from disk.

        Args:
            manifest_file: Path to manifest file

        Returns:
            BackupManifest object
        """
        try:
            with open(manifest_file, "r") as f:
                data = json.load(f)

            # Reconstruct FileMetadata objects
            files = {}
            if "files" in data and data["files"]:
                for path, file_data in data["files"].items():
                    files[path] = FileMetadata(**file_data)

            data["files"] = files
            data["created_at"] = datetime.fromisoformat(data["created_at"])

            return BackupManifest(**data)

        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            raise SnapshotError(
                f"Manifest load failed: {e}",
                error_code="MANIFEST_LOAD_FAILED",
                details={"path": str(manifest_file)},
            )

    def restore_backup(
        self, backup_id: str, dest_path: str, incremental_chain: bool = True
    ) -> bool:
        """
        Restore a backup.

        Args:
            backup_id: Backup ID to restore
            dest_path: Destination path
            incremental_chain: Restore full chain (parent backups)

        Returns:
            True if successful, False otherwise

        Raises:
            SnapshotError: If restore fails
        """
        if backup_id not in self.manifests:
            raise SnapshotError(
                f"Backup not found: {backup_id}",
                error_code="BACKUP_NOT_FOUND",
                details={"backup_id": backup_id},
            )

        dest = Path(dest_path)
        dest.mkdir(parents=True, exist_ok=True)

        try:
            # Build restore chain
            restore_chain = [backup_id]

            if incremental_chain:
                current_id = backup_id
                while self.manifests[current_id].parent_backup_id:
                    parent_id = self.manifests[current_id].parent_backup_id
                    if parent_id in self.manifests:
                        restore_chain.insert(0, parent_id)
                        current_id = parent_id
                    else:
                        logger.warning(f"Parent backup not found: {parent_id}")
                        break

            logger.info(f"Restoring backup chain: {restore_chain}")

            # Restore in order (oldest to newest)
            for backup_id_to_restore in restore_chain:
                manifest = self.manifests[backup_id_to_restore]
                backup_dir = Path(manifest.backup_dir)

                # Copy all backed up files
                for file_metadata in manifest.files.values():
                    if file_metadata.backed_up and file_metadata.backup_path:
                        source_file = Path(file_metadata.backup_path)
                        dest_file = dest / file_metadata.path

                        if source_file.exists():
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_file, dest_file)
                        else:
                            logger.warning(f"Backup file not found: {source_file}")

            logger.info(f"Successfully restored backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise SnapshotError(
                f"Restore failed: {e}",
                error_code="RESTORE_FAILED",
                details={"backup_id": backup_id, "error": str(e)},
            )

    def delete_backup(self, backup_id: str, delete_children: bool = False) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: Backup ID to delete
            delete_children: Also delete child backups

        Returns:
            True if deleted, False if not found
        """
        if backup_id not in self.manifests:
            logger.warning(f"Backup not found: {backup_id}")
            return False

        manifest = self.manifests[backup_id]

        # Check for child backups
        children = [mid for mid, m in self.manifests.items() if m.parent_backup_id == backup_id]

        if children and not delete_children:
            logger.warning(
                f"Cannot delete backup with children: {backup_id} (children: {children})"
            )
            return False

        try:
            # Delete children first
            if delete_children:
                for child_id in children:
                    self.delete_backup(child_id, delete_children=True)

            # Delete backup directory
            backup_dir = Path(manifest.backup_dir)
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            del self.manifests[backup_id]
            logger.info(f"Deleted backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False

    def list_backups(self, source_path: Optional[str] = None) -> List[BackupManifest]:
        """
        List backups.

        Args:
            source_path: Filter by source path

        Returns:
            List of BackupManifest objects
        """
        backups = list(self.manifests.values())
        if source_path:
            backups = [b for b in backups if b.source_path == source_path]
        return sorted(backups, key=lambda b: b.created_at, reverse=True)

    def get_backup(self, backup_id: str) -> Optional[BackupManifest]:
        """
        Get backup manifest.

        Args:
            backup_id: Backup ID

        Returns:
            BackupManifest or None if not found
        """
        return self.manifests.get(backup_id)

    def get_backup_chain(self, backup_id: str) -> List[str]:
        """
        Get full backup chain for a backup.

        Args:
            backup_id: Backup ID

        Returns:
            List of backup IDs in chain (oldest to newest)
        """
        if backup_id not in self.manifests:
            return []

        chain = [backup_id]
        current_id = backup_id

        while self.manifests[current_id].parent_backup_id:
            parent_id = self.manifests[current_id].parent_backup_id
            if parent_id in self.manifests:
                chain.insert(0, parent_id)
                current_id = parent_id
            else:
                break

        return chain

    def get_total_size(self) -> int:
        """
        Get total size of all backups.

        Returns:
            Total size in bytes
        """
        return sum(b.total_size for b in self.manifests.values())

    def verify_backup(self, backup_id: str) -> bool:
        """
        Verify backup integrity.

        Args:
            backup_id: Backup ID to verify

        Returns:
            True if valid, False otherwise
        """
        if backup_id not in self.manifests:
            logger.warning(f"Backup not found: {backup_id}")
            return False

        manifest = self.manifests[backup_id]
        backup_dir = Path(manifest.backup_dir)

        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_dir}")
            return False

        # Verify all backed up files exist
        for file_metadata in manifest.files.values():
            if file_metadata.backed_up and file_metadata.backup_path:
                if not Path(file_metadata.backup_path).exists():
                    logger.error(f"Backup file missing: {file_metadata.backup_path}")
                    return False

        logger.info(f"Backup verified: {backup_id}")
        return True
