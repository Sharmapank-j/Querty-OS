# Snapshot System

System snapshot and rollback functionality for Querty-OS.

## Overview

The snapshot system provides safety-first update and configuration management by maintaining system snapshots and enabling quick rollback to previous states.

## Features

### Snapshot Management
- **Create Snapshots**: Capture system state at any point
- **Automatic Snapshots**: Before updates, boot changes, or on schedule
- **Manual Snapshots**: User-initiated system backups
- **Incremental Snapshots**: Efficient storage using incremental changes
- **Snapshot Metadata**: Track snapshot details and descriptions

### Rollback Capability
- **One-Click Rollback**: Restore to any previous snapshot
- **Safe Rollback**: Automatic backup before rollback
- **Selective Restore**: Restore specific components
- **Verification**: Verify snapshot integrity before restore

### Last-Known-Good
- **Auto-Detection**: Mark stable states automatically
- **Manual Marking**: User can mark current state as good
- **Quick Recovery**: Fast rollback to last stable state
- **Boot Protection**: Automatic fallback on boot failure

### Snapshot Types

1. **Manual**: User-initiated snapshots
2. **Auto Boot**: Before boot configuration changes
3. **Auto Update**: Before system updates
4. **Scheduled**: Regular scheduled backups

## Architecture

```
snapshot-system/
├── snapshot_system.py      # Main snapshot implementation
├── filesystem_snapshot.py  # Filesystem-level snapshots (TODO)
├── incremental_backup.py   # Incremental backup engine (TODO)
└── rollback_manager.py     # Rollback orchestration (TODO)
```

## Usage

```python
from core.snapshot_system import SnapshotSystem, SnapshotType

# Create snapshot system
snapshots = SnapshotSystem()

# Create manual snapshot
snapshot = snapshots.create_snapshot(
    name="Before Major Update",
    snapshot_type=SnapshotType.MANUAL,
    description="Backup before installing new features"
)

# Mark as last-known-good
snapshots.mark_as_last_known_good(snapshot.id)

# List all snapshots
for snap in snapshots.list_snapshots():
    print(f"{snap.name}: {snap.timestamp}")

# Rollback to snapshot
snapshots.rollback_to_snapshot(snapshot.id)

# Cleanup old snapshots
snapshots.cleanup_old_snapshots(keep_count=5)
```

## Snapshot Workflow

### Before System Update
```
1. Create automatic snapshot
2. Perform system update
3. Verify system stability
4. Mark as last-known-good OR rollback
```

### Manual Backup
```
1. User initiates snapshot
2. System captures current state
3. Snapshot stored with metadata
4. User can add description/tags
```

### Rollback Process
```
1. User selects snapshot to restore
2. System creates pre-rollback backup
3. Files restored from snapshot
4. System prepares for restart
5. Restart with restored configuration
```

## Storage Strategy

### Full Snapshots
- Complete system state
- Used for first snapshot
- Larger storage requirement

### Incremental Snapshots
- Only changed files
- Reference previous snapshot
- Efficient storage usage
- Faster snapshot creation

### Compression
- Snapshots are compressed
- Reduces storage requirements
- Decompression on restore

## Snapshot Scope

Default snapshot includes:
- System configuration (`/system`)
- User data (`/data/data`)
- Installed apps (`/data/app`)
- Querty-OS configuration (`/etc/querty-os`)

Optional (configurable):
- User files
- Media
- Download cache

## Safety Features

- **Pre-Rollback Backup**: Always backup before rollback
- **Verification**: Verify snapshot integrity
- **Protected Snapshots**: Can't delete last-known-good
- **Space Management**: Automatic cleanup of old snapshots
- **Atomic Operations**: Snapshot operations are atomic

## Configuration

Settings in `/etc/querty-os/snapshot-system.conf`:
- Snapshot directory
- Automatic snapshot schedule
- Retention policy (how many to keep)
- Compression level
- Paths to include/exclude

## Filesystem Support

Optimized for:
- **btrfs**: Native snapshot support
- **LVM**: Logical volume snapshots
- **ext4**: File-based snapshots
- **F2FS**: Android flash-friendly filesystem

## Performance

- **Fast Creation**: Snapshots complete in seconds
- **Minimal Space**: Incremental snapshots save space
- **Background Operation**: Non-blocking snapshot creation
- **Quick Rollback**: Restore in minutes

## Development Status

- [x] Snapshot system structure
- [x] Snapshot creation/deletion
- [x] Last-known-good tracking
- [x] Snapshot listing
- [ ] Actual filesystem snapshot implementation
- [ ] Incremental backup system
- [ ] Rollback implementation
- [ ] Compression
- [ ] Scheduled snapshots
- [ ] Space management
