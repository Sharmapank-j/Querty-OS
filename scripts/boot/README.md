# Boot Scripts

Boot initialization and shutdown scripts for Querty-OS.

## Overview

The boot scripts handle system initialization and graceful shutdown, ensuring all Querty-OS services start correctly and shut down cleanly.

## Scripts

### init-querty.sh
Main boot initialization script that:
- Creates necessary directories
- Sets up Linux chroot environment
- Mounts required filesystems
- Starts the AI daemon
- Executes custom boot scripts
- Performs health checks

**Usage:**
```bash
# Run at system boot (requires root)
/system/bin/sh /path/to/init-querty.sh
```

### shutdown-querty.sh
Graceful shutdown script that:
- Stops the AI daemon
- Unmounts chroot filesystems
- Executes custom shutdown scripts
- Cleans up resources

**Usage:**
```bash
# Run at system shutdown (requires root)
/system/bin/sh /path/to/shutdown-querty.sh
```

## Integration with Android

### Method 1: init.rc (System Integration)
Add to `/system/etc/init/querty-os.rc`:
```
service querty-os /system/bin/sh /data/local/querty-os/scripts/boot/init-querty.sh
    class late_start
    user root
    group root
    oneshot
    disabled

on property:sys.boot_completed=1
    start querty-os
```

### Method 2: Magisk Module
Create a Magisk module with post-fs-data script:
```bash
# /data/adb/modules/querty-os/post-fs-data.sh
/system/bin/sh /data/local/querty-os/scripts/boot/init-querty.sh
```

### Method 3: Boot Script Apps
Use apps like:
- Init.d scripts
- Tasker with root
- Boot Manager

## Custom Boot Scripts

Place custom scripts in `/data/querty-os/config/boot-scripts/`:
```bash
# Example: /data/querty-os/config/boot-scripts/01-network.sh
#!/system/bin/sh
# Set up network configuration
echo "Configuring network..."
```

Scripts are executed in alphabetical order. Use numeric prefixes to control order (01-, 02-, etc.).

## Custom Shutdown Scripts

Place custom scripts in `/data/querty-os/config/shutdown-scripts/`:
```bash
# Example: /data/querty-os/config/shutdown-scripts/01-backup.sh
#!/system/bin/sh
# Backup critical data before shutdown
echo "Creating backup..."
```

## Logging

All boot and shutdown activities are logged to:
- Boot: `/data/local/tmp/querty-boot.log`
- Shutdown: `/data/local/tmp/querty-shutdown.log`
- Daemon: `/data/querty-os/logs/daemon.log`

View logs:
```bash
# Boot log
cat /data/local/tmp/querty-boot.log

# Daemon log
cat /data/querty-os/logs/daemon.log
```

## Health Checks

The boot script performs health checks:
1. Verify daemon process is running
2. Check PID file exists
3. Confirm essential services started

If health checks fail, review logs for errors.

## Troubleshooting

### Daemon doesn't start
```bash
# Check if Python 3 is available
which python3

# Check if daemon script exists
ls -la /data/local/querty-os/core/ai-daemon/daemon.py

# Check permissions
ls -la /data/querty-os/
```

### Chroot mount fails
```bash
# Check if chroot directory exists
ls -la /data/linux/

# Check if already mounted
mount | grep linux

# Check permissions
ls -ld /data/linux/
```

### Scripts don't execute
```bash
# Ensure scripts are executable
chmod +x /path/to/script.sh

# Check script syntax
sh -n /path/to/script.sh
```

## Boot Sequence

1. Android system boots
2. Boot completed event fires
3. `init-querty.sh` executes
4. Directories created
5. Chroot environment set up
6. AI daemon starts
7. Custom scripts run
8. Health check performed
9. System ready

## Directory Structure

```
/data/querty-os/
├── config/
│   ├── boot-scripts/      # Custom boot scripts
│   └── shutdown-scripts/  # Custom shutdown scripts
├── logs/
│   └── daemon.log         # Daemon log file
├── snapshots/             # System snapshots
├── tmp/                   # Temporary files
└── daemon.pid             # Daemon process ID
```

## Security

- Scripts must run as root
- Validate script sources
- Review custom scripts before execution
- Monitor logs for suspicious activity

## Development Status

- [x] Boot initialization script
- [x] Shutdown script
- [x] Directory creation
- [x] Daemon startup
- [x] Health checks
- [x] Custom script support
- [ ] Systemd service files
- [ ] Automatic recovery on failure
- [ ] Boot performance optimization
