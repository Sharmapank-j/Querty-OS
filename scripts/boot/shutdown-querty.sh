#!/system/bin/sh
# Querty-OS Shutdown Script
# Gracefully shutdown Querty-OS services

LOG_FILE="/data/local/tmp/querty-shutdown.log"
DAEMON_PID_FILE="/data/querty-os/daemon.pid"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "======================================"
log "Querty-OS Shutdown Starting"
log "======================================"

# Stop the AI daemon
if [ -f "$DAEMON_PID_FILE" ]; then
    DAEMON_PID=$(cat "$DAEMON_PID_FILE")
    log "Stopping AI Daemon (PID: $DAEMON_PID)..."

    # Send TERM signal for graceful shutdown
    kill -TERM "$DAEMON_PID" 2>/dev/null

    # Wait for daemon to stop (max 10 seconds)
    for i in 1 2 3 4 5 6 7 8 9 10; do
        if ! kill -0 "$DAEMON_PID" 2>/dev/null; then
            log "Daemon stopped gracefully"
            rm -f "$DAEMON_PID_FILE"
            break
        fi
        sleep 1
    done

    # Force kill if still running
    if kill -0 "$DAEMON_PID" 2>/dev/null; then
        log "WARNING: Force killing daemon"
        kill -KILL "$DAEMON_PID" 2>/dev/null
        rm -f "$DAEMON_PID_FILE"
    fi
else
    log "No daemon PID file found"
fi

# Unmount chroot filesystems
log "Cleaning up Linux chroot..."
umount /data/linux/proc 2>/dev/null
umount /data/linux/sys 2>/dev/null
umount /data/linux/dev 2>/dev/null
log "Chroot filesystems unmounted"

# Execute custom shutdown scripts
if [ -d "/data/querty-os/config/shutdown-scripts" ]; then
    for script in /data/querty-os/config/shutdown-scripts/*.sh; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            log "Executing: $script"
            "$script" >> "$LOG_FILE" 2>&1
        fi
    done
fi

log "======================================"
log "Querty-OS Shutdown Complete"
log "======================================"

exit 0
