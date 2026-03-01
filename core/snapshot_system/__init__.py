"""Querty-OS Snapshot System Package"""

from .filesystem_snapshot import (
    CompressionLevel,
    FilesystemSnapshot,
    SnapshotFormat,
    SnapshotMetadata,
)
from .incremental_backup import BackupManifest, FileMetadata, IncrementalBackup
from .rollback_manager import (
    RollbackManager,
    RollbackOperation,
    RollbackPoint,
    RollbackScope,
    RollbackState,
    SafetyCheck,
    SafetyCheckType,
)
from .snapshot_system import Snapshot, SnapshotStatus, SnapshotSystem, SnapshotType

__version__ = "0.1.0"
__all__ = [
    "SnapshotSystem",
    "Snapshot",
    "SnapshotType",
    "SnapshotStatus",
    "FilesystemSnapshot",
    "SnapshotMetadata",
    "SnapshotFormat",
    "CompressionLevel",
    "IncrementalBackup",
    "BackupManifest",
    "FileMetadata",
    "RollbackManager",
    "RollbackPoint",
    "RollbackOperation",
    "RollbackState",
    "RollbackScope",
    "SafetyCheck",
    "SafetyCheckType",
]
