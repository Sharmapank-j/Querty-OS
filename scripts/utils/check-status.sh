#!/system/bin/sh
# Querty-OS Status Check Utility
# Quick health check of Querty-OS system

echo "======================================"
echo "Querty-OS Status Check"
echo "======================================"
echo ""

# Check if daemon is running
if [ -f "/data/querty-os/daemon.pid" ]; then
    PID=$(cat /data/querty-os/daemon.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "✓ AI Daemon: Running (PID: $PID)"
    else
        echo "✗ AI Daemon: Not running (stale PID file)"
    fi
else
    echo "✗ AI Daemon: Not running (no PID file)"
fi

# Check directories
echo ""
echo "Directory Status:"
for dir in /data/querty-os /data/linux /data/wine; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir missing"
    fi
done

# Check logs
echo ""
echo "Recent Logs:"
if [ -f "/data/querty-os/logs/daemon.log" ]; then
    echo "  Last 5 daemon log entries:"
    tail -n 5 /data/querty-os/logs/daemon.log | sed 's/^/    /'
else
    echo "  No daemon log found"
fi

# Check snapshots
echo ""
echo "Snapshot System:"
if [ -d "/data/querty-os/snapshots" ]; then
    SNAPSHOT_COUNT=$(ls -1 /data/querty-os/snapshots | grep -c "^snapshot_" || echo "0")
    echo "  Snapshots: $SNAPSHOT_COUNT"
else
    echo "  Snapshot directory not found"
fi

# Check chroot mounts
echo ""
echo "Linux Chroot Mounts:"
if mount | grep -q "/data/linux/proc"; then
    echo "  ✓ /proc mounted"
else
    echo "  ✗ /proc not mounted"
fi

if mount | grep -q "/data/linux/sys"; then
    echo "  ✓ /sys mounted"
else
    echo "  ✗ /sys not mounted"
fi

echo ""
echo "======================================"
