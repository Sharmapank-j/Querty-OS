"""
Filesystem-level snapshot using tar/rsync.
Provides point-in-time backups of filesystems.
"""

import hashlib
import logging
import os
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from core.exceptions import SnapshotError

logger = logging.getLogger(__name__)


class SnapshotFormat(Enum):
    """Snapshot storage format."""

    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    RSYNC = "rsync"


class CompressionLevel(Enum):
    """Compression level for tar archives."""

    NONE = 0
    FAST = 1
    BALANCED = 6
    BEST = 9


@dataclass
class SnapshotMetadata:
    """Metadata for a filesystem snapshot."""

    snapshot_id: str
    name: str
    source_path: str
    snapshot_path: str
    format: SnapshotFormat
    created_at: datetime
    size_bytes: int
    checksum: Optional[str] = None
    compressed: bool = False
    compression_ratio: float = 1.0
    file_count: int = 0
    error: Optional[str] = None


class FilesystemSnapshot:
    """Filesystem-level snapshot manager."""

    def __init__(self, snapshot_dir: str = "/data/snapshots"):
        """
        Initialize filesystem snapshot manager.

        Args:
            snapshot_dir: Directory to store snapshots
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshots: Dict[str, SnapshotMetadata] = {}

        try:
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized FilesystemSnapshot with dir: {snapshot_dir}")
        except Exception as e:
            raise SnapshotError(
                f"Failed to create snapshot directory: {e}",
                error_code="SNAPSHOT_DIR_FAILED",
                details={"path": snapshot_dir},
            )

    def _generate_snapshot_id(self, source_path: str) -> str:
        """
        Generate unique snapshot ID.

        Args:
            source_path: Source path

        Returns:
            Snapshot ID
        """
        timestamp = datetime.now().isoformat()
        data = f"{source_path}:{timestamp}:{len(self.snapshots)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of checksum
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192 * 128)  # 1MB chunks
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def create_tar_snapshot(
        self,
        source_path: str,
        name: str,
        format: SnapshotFormat = SnapshotFormat.TAR_GZ,
        exclude_patterns: Optional[List[str]] = None,
    ) -> SnapshotMetadata:
        """
        Create a tar-based snapshot.

        Args:
            source_path: Path to snapshot
            name: Snapshot name
            format: Tar format (TAR, TAR_GZ, TAR_BZ2, TAR_XZ)
            exclude_patterns: Patterns to exclude

        Returns:
            SnapshotMetadata object

        Raises:
            SnapshotError: If snapshot creation fails
        """
        source = Path(source_path)
        if not source.exists():
            raise SnapshotError(
                f"Source path not found: {source_path}",
                error_code="SOURCE_NOT_FOUND",
                details={"path": source_path},
            )

        snapshot_id = self._generate_snapshot_id(source_path)

        # Determine file extension
        ext_map = {
            SnapshotFormat.TAR: ".tar",
            SnapshotFormat.TAR_GZ: ".tar.gz",
            SnapshotFormat.TAR_BZ2: ".tar.bz2",
            SnapshotFormat.TAR_XZ: ".tar.xz",
        }
        ext = ext_map.get(format, ".tar")

        snapshot_file = self.snapshot_dir / f"{name}_{snapshot_id}{ext}"

        # Determine tar mode
        mode_map = {
            SnapshotFormat.TAR: "w",
            SnapshotFormat.TAR_GZ: "w:gz",
            SnapshotFormat.TAR_BZ2: "w:bz2",
            SnapshotFormat.TAR_XZ: "w:xz",
        }
        tar_mode = mode_map.get(format, "w")

        try:
            logger.info(f"Creating tar snapshot: {name} from {source_path}")

            # Count files
            file_count = sum(1 for _ in source.rglob("*") if _.is_file())

            # Create tar archive
            with tarfile.open(snapshot_file, tar_mode) as tar:
                # Add filter function for excludes
                def tar_filter(tarinfo):
                    if exclude_patterns:
                        for pattern in exclude_patterns:
                            if pattern in tarinfo.name:
                                logger.debug(f"Excluding: {tarinfo.name}")
                                return None
                    return tarinfo

                tar.add(source, arcname=source.name, filter=tar_filter)

            # Get snapshot size
            size_bytes = snapshot_file.stat().st_size

            # Calculate original size if compressed
            if format != SnapshotFormat.TAR:
                original_size = sum(f.stat().st_size for f in source.rglob("*") if f.is_file())
                compression_ratio = size_bytes / original_size if original_size > 0 else 1.0
            else:
                compression_ratio = 1.0

            # Calculate checksum
            checksum = self._calculate_checksum(snapshot_file)

            # Create metadata
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                name=name,
                source_path=source_path,
                snapshot_path=str(snapshot_file),
                format=format,
                created_at=datetime.now(),
                size_bytes=size_bytes,
                checksum=checksum,
                compressed=(format != SnapshotFormat.TAR),
                compression_ratio=compression_ratio,
                file_count=file_count,
            )

            self.snapshots[snapshot_id] = metadata
            logger.info(
                f"Created tar snapshot: {name} ({size_bytes} bytes, "
                f"compression={compression_ratio:.2f})"
            )
            return metadata

        except Exception as e:
            logger.error(f"Failed to create tar snapshot: {e}")
            # Clean up partial snapshot
            if snapshot_file.exists():
                snapshot_file.unlink()
            raise SnapshotError(
                f"Snapshot creation failed: {e}",
                error_code="SNAPSHOT_FAILED",
                details={"source": source_path, "error": str(e)},
            )

    def create_rsync_snapshot(
        self,
        source_path: str,
        name: str,
        link_dest: Optional[str] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> SnapshotMetadata:
        """
        Create an rsync-based snapshot.

        Args:
            source_path: Path to snapshot
            name: Snapshot name
            link_dest: Previous snapshot for hard-linking (incremental)
            exclude_patterns: Patterns to exclude

        Returns:
            SnapshotMetadata object

        Raises:
            SnapshotError: If snapshot creation fails
        """
        source = Path(source_path)
        if not source.exists():
            raise SnapshotError(
                f"Source path not found: {source_path}",
                error_code="SOURCE_NOT_FOUND",
                details={"path": source_path},
            )

        snapshot_id = self._generate_snapshot_id(source_path)
        snapshot_path = self.snapshot_dir / f"{name}_{snapshot_id}"

        try:
            snapshot_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Creating rsync snapshot: {name} from {source_path}")

            # Build rsync command
            cmd = ["rsync", "-a", "--delete"]

            if link_dest:
                cmd.extend(["--link-dest", link_dest])

            if exclude_patterns:
                for pattern in exclude_patterns:
                    cmd.extend(["--exclude", pattern])

            # Ensure trailing slash on source
            source_str = str(source)
            if not source_str.endswith("/"):
                source_str += "/"

            cmd.extend([source_str, str(snapshot_path) + "/"])

            # Execute rsync
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=3600)

            # Calculate size and file count
            size_bytes = sum(f.stat().st_size for f in snapshot_path.rglob("*") if f.is_file())
            file_count = sum(1 for _ in snapshot_path.rglob("*") if _.is_file())

            # Create metadata
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                name=name,
                source_path=source_path,
                snapshot_path=str(snapshot_path),
                format=SnapshotFormat.RSYNC,
                created_at=datetime.now(),
                size_bytes=size_bytes,
                compressed=False,
                compression_ratio=1.0,
                file_count=file_count,
            )

            self.snapshots[snapshot_id] = metadata
            logger.info(f"Created rsync snapshot: {name} ({size_bytes} bytes)")
            return metadata

        except subprocess.CalledProcessError as e:
            logger.error(f"rsync failed: {e.stderr}")
            raise SnapshotError(
                f"rsync snapshot failed: {e.stderr}",
                error_code="RSYNC_FAILED",
                details={"stderr": e.stderr},
            )
        except subprocess.TimeoutExpired:
            raise SnapshotError("rsync snapshot timed out", error_code="RSYNC_TIMEOUT")
        except FileNotFoundError:
            raise SnapshotError("rsync not found", error_code="RSYNC_NOT_FOUND")
        except Exception as e:
            logger.error(f"Failed to create rsync snapshot: {e}")
            raise SnapshotError(
                f"Snapshot creation failed: {e}",
                error_code="SNAPSHOT_FAILED",
                details={"source": source_path, "error": str(e)},
            )

    def restore_snapshot(self, snapshot_id: str, dest_path: str, verify: bool = True) -> bool:
        """
        Restore a snapshot to destination.

        Args:
            snapshot_id: Snapshot ID to restore
            dest_path: Destination path
            verify: Verify snapshot integrity before restore

        Returns:
            True if successful, False otherwise

        Raises:
            SnapshotError: If restore fails
        """
        if snapshot_id not in self.snapshots:
            raise SnapshotError(
                f"Snapshot not found: {snapshot_id}",
                error_code="SNAPSHOT_NOT_FOUND",
                details={"snapshot_id": snapshot_id},
            )

        metadata = self.snapshots[snapshot_id]
        snapshot_path = Path(metadata.snapshot_path)

        if not snapshot_path.exists():
            raise SnapshotError(
                f"Snapshot file not found: {snapshot_path}",
                error_code="SNAPSHOT_FILE_NOT_FOUND",
                details={"path": str(snapshot_path)},
            )

        # Verify checksum if requested
        if verify and metadata.checksum and metadata.format != SnapshotFormat.RSYNC:
            logger.info(f"Verifying snapshot checksum: {snapshot_id}")
            checksum = self._calculate_checksum(snapshot_path)
            if checksum != metadata.checksum:
                raise SnapshotError(
                    "Snapshot checksum mismatch",
                    error_code="CHECKSUM_MISMATCH",
                    details={"expected": metadata.checksum, "actual": checksum},
                )

        dest = Path(dest_path)
        dest.mkdir(parents=True, exist_ok=True)

        try:
            if metadata.format in [
                SnapshotFormat.TAR,
                SnapshotFormat.TAR_GZ,
                SnapshotFormat.TAR_BZ2,
                SnapshotFormat.TAR_XZ,
            ]:
                logger.info(f"Restoring tar snapshot: {snapshot_id} to {dest_path}")
                with tarfile.open(snapshot_path, "r:*") as tar:
                    tar.extractall(dest)

            elif metadata.format == SnapshotFormat.RSYNC:
                logger.info(f"Restoring rsync snapshot: {snapshot_id} to {dest_path}")
                cmd = ["rsync", "-a", "--delete", str(snapshot_path) + "/", str(dest) + "/"]
                subprocess.run(cmd, check=True, capture_output=True, timeout=3600)

            else:
                raise SnapshotError(
                    f"Unsupported snapshot format: {metadata.format}",
                    error_code="UNSUPPORTED_FORMAT",
                )

            logger.info(f"Successfully restored snapshot: {snapshot_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore snapshot: {e}")
            raise SnapshotError(
                f"Restore failed: {e}",
                error_code="RESTORE_FAILED",
                details={"snapshot_id": snapshot_id, "error": str(e)},
            )

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete a snapshot.

        Args:
            snapshot_id: Snapshot ID to delete

        Returns:
            True if deleted, False if not found
        """
        if snapshot_id not in self.snapshots:
            logger.warning(f"Snapshot not found: {snapshot_id}")
            return False

        metadata = self.snapshots[snapshot_id]
        snapshot_path = Path(metadata.snapshot_path)

        try:
            if snapshot_path.is_file():
                snapshot_path.unlink()
            elif snapshot_path.is_dir():
                import shutil

                shutil.rmtree(snapshot_path)

            del self.snapshots[snapshot_id]
            logger.info(f"Deleted snapshot: {snapshot_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete snapshot: {e}")
            return False

    def list_snapshots(self, source_path: Optional[str] = None) -> List[SnapshotMetadata]:
        """
        List snapshots.

        Args:
            source_path: Filter by source path

        Returns:
            List of SnapshotMetadata objects
        """
        snapshots = list(self.snapshots.values())
        if source_path:
            snapshots = [s for s in snapshots if s.source_path == source_path]
        return sorted(snapshots, key=lambda s: s.created_at, reverse=True)

    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotMetadata]:
        """
        Get snapshot metadata.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            SnapshotMetadata or None if not found
        """
        return self.snapshots.get(snapshot_id)

    def verify_snapshot(self, snapshot_id: str) -> bool:
        """
        Verify snapshot integrity.

        Args:
            snapshot_id: Snapshot ID to verify

        Returns:
            True if valid, False otherwise
        """
        if snapshot_id not in self.snapshots:
            logger.warning(f"Snapshot not found: {snapshot_id}")
            return False

        metadata = self.snapshots[snapshot_id]
        snapshot_path = Path(metadata.snapshot_path)

        if not snapshot_path.exists():
            logger.error(f"Snapshot file not found: {snapshot_path}")
            return False

        # Verify checksum if available
        if metadata.checksum and metadata.format != SnapshotFormat.RSYNC:
            try:
                checksum = self._calculate_checksum(snapshot_path)
                if checksum != metadata.checksum:
                    logger.error(f"Checksum mismatch for snapshot: {snapshot_id}")
                    return False
            except Exception as e:
                logger.error(f"Checksum verification failed: {e}")
                return False

        logger.info(f"Snapshot verified: {snapshot_id}")
        return True

    def get_total_size(self) -> int:
        """
        Get total size of all snapshots.

        Returns:
            Total size in bytes
        """
        return sum(s.size_bytes for s in self.snapshots.values())

    def cleanup_old_snapshots(
        self, source_path: str, keep_count: int = 5, min_age_days: int = 0
    ) -> int:
        """
        Clean up old snapshots for a source path.

        Args:
            source_path: Source path to clean up
            keep_count: Number of snapshots to keep
            min_age_days: Minimum age in days before deletion

        Returns:
            Number of snapshots deleted
        """
        snapshots = self.list_snapshots(source_path)

        if len(snapshots) <= keep_count:
            return 0

        # Sort by age (oldest first)
        snapshots.sort(key=lambda s: s.created_at)

        deleted = 0
        for snapshot in snapshots[:-keep_count]:
            age_days = (datetime.now() - snapshot.created_at).days
            if age_days >= min_age_days:
                if self.delete_snapshot(snapshot.snapshot_id):
                    deleted += 1

        logger.info(f"Cleaned up {deleted} old snapshots for {source_path}")
        return deleted
