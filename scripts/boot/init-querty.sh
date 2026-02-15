#!/system/bin/sh
# Querty-OS Boot Initialization Script
# This script runs at system boot to initialize Querty-OS services

LOG_FILE="/data/local/tmp/querty-boot.log"
QUERTY_DIR="/data/local/querty-os"
DAEMON_SCRIPT="$QUERTY_DIR/core/ai-daemon/daemon.py"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "======================================"
log "Querty-OS Boot Initialization Starting"
log "======================================"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log "ERROR: Boot script must run as root"
    exit 1
fi

# Create necessary directories
log "Creating Querty-OS directories..."
mkdir -p /data/querty-os/{config,logs,snapshots,tmp}
mkdir -p /data/linux
mkdir -p /data/wine

# Set permissions
chmod 755 /data/querty-os
chmod 755 /data/linux
chmod 755 /data/wine

log "Directories created successfully"

# Mount necessary filesystems for Linux chroot (if needed)
log "Setting up Linux chroot environment..."
if [ -d "/data/linux" ]; then
    # Mount proc, sys, dev if not already mounted
    if ! mount | grep -q "/data/linux/proc"; then
        mount -t proc proc /data/linux/proc 2>/dev/null
        log "Mounted /proc in chroot"
    fi

    if ! mount | grep -q "/data/linux/sys"; then
        mount -t sysfs sys /data/linux/sys 2>/dev/null
        log "Mounted /sys in chroot"
    fi

    if ! mount | grep -q "/data/linux/dev"; then
        mount -o bind /dev /data/linux/dev 2>/dev/null
        log "Mounted /dev in chroot"
    fi
fi

# Check for last-known-good snapshot
log "Checking system state..."
if [ -f "/data/querty-os/snapshots/system_state.json" ]; then
    log "Found system state file"
    # TODO: Verify boot success and update last-known-good if stable
else
    log "No system state file found (first boot?)"
fi

# Start the AI daemon
log "Starting Querty AI Daemon..."
if [ -f "$DAEMON_SCRIPT" ]; then
    # Start daemon in background
    python3 "$DAEMON_SCRIPT" > /data/querty-os/logs/daemon.log 2>&1 &
    DAEMON_PID=$!

    # Save PID
    echo "$DAEMON_PID" > /data/querty-os/daemon.pid

    log "AI Daemon started with PID: $DAEMON_PID"
else
    log "WARNING: AI Daemon script not found at $DAEMON_SCRIPT"
fi

# Execute custom boot scripts (if any)
log "Executing custom boot scripts..."
if [ -d "/data/querty-os/config/boot-scripts" ]; then
    for script in /data/querty-os/config/boot-scripts/*.sh; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            log "Executing: $script"
            "$script" >> "$LOG_FILE" 2>&1
        fi
    done
else
    log "No custom boot scripts directory found"
fi

# Health check
log "Performing health check..."
sleep 2

if [ -f "/data/querty-os/daemon.pid" ]; then
    DAEMON_PID=$(cat /data/querty-os/daemon.pid)
    if kill -0 "$DAEMON_PID" 2>/dev/null; then
        log "Health check PASSED: Daemon is running"
    else
        log "WARNING: Daemon process not found"
    fi
fi

log "======================================"
log "Querty-OS Boot Initialization Complete"
log "======================================"

exit 0
