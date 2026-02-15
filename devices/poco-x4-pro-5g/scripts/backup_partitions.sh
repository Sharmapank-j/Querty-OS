#!/system/bin/sh
# Backup Partitions Script for Poco X4 Pro 5G (veux/peux)
# Critical partition backup utility
# Part of Querty-OS Tri-Boot System

BACKUP_DIR="/sdcard/triboot_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║${NC}   Critical Partition Backup - Poco X4 Pro 5G            ${CYAN}║${NC}"
    echo "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check root
if [ "$(id -u)" != "0" ]; then
    log_error "This script must be run as root"
    exit 1
fi

print_banner

# Create backup directory
log_info "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Failed to create backup directory"
    exit 1
fi

# Get device info
DEVICE=$(getprop ro.product.device 2>/dev/null)
MODEL=$(getprop ro.product.model 2>/dev/null)

log_info "Device: $DEVICE"
log_info "Model: $MODEL"

# Verify device
if [ "$DEVICE" != "veux" ] && [ "$DEVICE" != "peux" ]; then
    log_warn "WARNING: Unexpected device: $DEVICE"
    log_warn "Expected: veux or peux (Poco X4 Pro 5G)"
    echo ""
    read -p "Continue anyway? (y/N): " choice
    if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
        log_info "Backup cancelled"
        exit 0
    fi
fi

# Function to backup a partition
backup_partition() {
    local partition_name="$1"
    local partition_path="/dev/block/by-name/$partition_name"
    local backup_file="${BACKUP_DIR}/${partition_name}.img"

    if [ ! -e "$partition_path" ]; then
        log_warn "Partition $partition_name not found at $partition_path"
        return 1
    fi

    log_info "Backing up: $partition_name..."

    # Get partition size
    local size=$(blockdev --getsize64 "$partition_path" 2>/dev/null)
    if [ -n "$size" ]; then
        local size_mb=$((size / 1024 / 1024))
        log_info "  Size: ${size_mb}MB"
    fi

    # Perform backup
    dd if="$partition_path" of="$backup_file" bs=4M 2>/dev/null

    if [ $? -eq 0 ]; then
        # Verify backup file
        if [ -f "$backup_file" ]; then
            local backup_size=$(ls -lh "$backup_file" | awk '{print $5}')
            log_info "  ✓ Backed up successfully ($backup_size)"
            echo "$partition_name: $backup_size" >> "${BACKUP_DIR}/manifest.txt"
            return 0
        else
            log_error "  ✗ Backup file not created"
            return 1
        fi
    else
        log_error "  ✗ Backup failed"
        return 1
    fi
}

echo ""
log_info "${CYAN}Starting partition backup...${NC}"
echo ""

# Critical boot partitions
log_info "${YELLOW}=== Boot Partitions ===${NC}"
backup_partition "boot_a"
backup_partition "boot_b"

echo ""
log_info "${YELLOW}=== DTBO Partitions ===${NC}"
backup_partition "dtbo_a"
backup_partition "dtbo_b"

echo ""
log_info "${YELLOW}=== Vbmeta Partitions ===${NC}"
backup_partition "vbmeta_a"
backup_partition "vbmeta_b"
backup_partition "vbmeta_system_a"
backup_partition "vbmeta_system_b"

echo ""
log_info "${YELLOW}=== CRITICAL: Modem Partitions ===${NC}"
log_warn "These partitions are ESSENTIAL for cellular connectivity!"
backup_partition "modemst1"
backup_partition "modemst2"
backup_partition "fsg"
backup_partition "fsc"

echo ""
log_info "${YELLOW}=== Persist & EFS ===${NC}"
backup_partition "persist"

# Additional important partitions for Poco X4 Pro 5G
echo ""
log_info "${YELLOW}=== Additional Partitions ===${NC}"
backup_partition "metadata"
backup_partition "misc"

# Create device info file
echo ""
log_info "Creating device info file..."
cat > "${BACKUP_DIR}/device_info.txt" << EOF
Backup Date: $(date)
Device: $DEVICE
Model: $MODEL
Android Version: $(getprop ro.build.version.release)
Build ID: $(getprop ro.build.id)
Security Patch: $(getprop ro.build.version.security_patch)
Kernel: $(uname -r)

Partition Layout:
$(parted /dev/block/sda print 2>/dev/null || echo "Unable to retrieve partition table")

Active Slot: $(getprop ro.boot.slot_suffix)
EOF

# Calculate total backup size
echo ""
log_info "Calculating backup size..."
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | awk '{print $1}')
log_info "Total backup size: ${CYAN}$TOTAL_SIZE${NC}"

# Create checksum file
log_info "Generating checksums..."
cd "$BACKUP_DIR" || exit 1
md5sum *.img > checksums.md5 2>/dev/null
cd - > /dev/null || exit 1

echo ""
log_info "${GREEN}═══════════════════════════════════════════════════════${NC}"
log_info "${GREEN}Backup completed successfully!${NC}"
log_info "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
log_warn "${YELLOW}IMPORTANT:${NC}"
log_warn "1. Copy the entire backup folder to your PC:"
log_warn "   ${CYAN}$BACKUP_DIR${NC}"
log_warn ""
log_warn "2. Store backups in multiple locations:"
log_warn "   - External USB drive"
log_warn "   - Cloud storage"
log_warn "   - Another computer"
log_warn ""
log_warn "3. Verify checksums after copying:"
log_warn "   cd /path/to/backup"
log_warn "   md5sum -c checksums.md5"
echo ""
log_error "${RED}DO NOT PROCEED with tri-boot setup until backups are safely stored!${NC}"
echo ""

# Suggest ADB pull command
log_info "To copy to PC via ADB:"
echo "  adb pull \"$BACKUP_DIR\" ."
echo ""

# Create a quick verification script
cat > "${BACKUP_DIR}/verify_backup.sh" << 'VERIFY_EOF'
#!/bin/bash
# Backup verification script

echo "Verifying backup integrity..."
echo ""

# Check if checksums file exists
if [ ! -f "checksums.md5" ]; then
    echo "ERROR: checksums.md5 not found!"
    exit 1
fi

# Verify checksums
if md5sum -c checksums.md5 2>/dev/null; then
    echo ""
    echo "✓ All backups verified successfully!"
    exit 0
else
    echo ""
    echo "✗ Backup verification failed!"
    echo "Some files may be corrupted or missing."
    exit 1
fi
VERIFY_EOF

chmod +x "${BACKUP_DIR}/verify_backup.sh"
log_info "Created verification script: verify_backup.sh"

echo ""
log_info "Backup process complete."
