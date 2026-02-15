#!/system/bin/sh
# Partition Setup Script for Poco X4 Pro 5G (veux/peux)
# WARNING: This script will DESTROY all data on userdata partition!
# Part of Querty-OS Tri-Boot System

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DEVICE=""
DRY_RUN=0
LINUX_SIZE_GB=20
WINDOWS_SIZE_GB=50

log_info() {
    echo "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║${NC}   Partition Setup - Poco X4 Pro 5G Tri-Boot             ${CYAN}║${NC}"
    echo "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --device <codename>    Device codename (veux or peux)"
    echo "  --dry-run              Preview changes without applying"
    echo "  --linux-size <GB>      Linux partition size (default: 20GB)"
    echo "  --windows-size <GB>    Windows partition size (default: 50GB)"
    echo "  --help                 Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --device veux --dry-run"
    echo "  $0 --device veux --linux-size 30 --windows-size 60"
    echo ""
}

# Check root
if [ "$(id -u)" != "0" ]; then
    log_error "This script must be run as root"
    exit 1
fi

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --linux-size)
            LINUX_SIZE_GB="$2"
            shift 2
            ;;
        --windows-size)
            WINDOWS_SIZE_GB="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

print_banner

# Detect device if not specified
if [ -z "$DEVICE" ]; then
    DEVICE=$(getprop ro.product.device 2>/dev/null)
    log_info "Detected device: $DEVICE"
fi

# Verify device
if [ "$DEVICE" != "veux" ] && [ "$DEVICE" != "peux" ]; then
    log_error "Unsupported device: $DEVICE"
    log_error "This script is only for Poco X4 Pro 5G (veux/peux)"
    exit 1
fi

# Check if parted is available
if ! command -v parted >/dev/null 2>&1; then
    log_error "parted utility not found!"
    log_error "Please use a modified TWRP/OrangeFox recovery with parted included"
    exit 1
fi

# Main storage device
MAIN_DEV="/dev/block/sda"

if [ ! -e "$MAIN_DEV" ]; then
    log_error "Main storage device not found: $MAIN_DEV"
    exit 1
fi

# Display current partition layout
echo ""
log_info "${CYAN}Current Partition Layout:${NC}"
echo ""
parted "$MAIN_DEV" print
echo ""

if [ $DRY_RUN -eq 1 ]; then
    log_warn "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Calculate partition sizes
log_info "Planned partition layout:"
echo ""
echo "  ${CYAN}Windows (ESP + System):${NC} ${WINDOWS_SIZE_GB}GB + 1GB (ESP)"
echo "  ${CYAN}Linux:${NC}                  ${LINUX_SIZE_GB}GB"
echo "  ${CYAN}Android (userdata):${NC}     Remaining space"
echo ""

# Get total device size
TOTAL_SIZE=$(parted "$MAIN_DEV" unit GB print | grep "Disk $MAIN_DEV" | awk '{print $3}' | sed 's/GB//')
log_info "Total device size: ${TOTAL_SIZE}GB"

# Calculate remaining space for Android
ANDROID_SIZE=$(echo "$TOTAL_SIZE - $WINDOWS_SIZE_GB - 1 - $LINUX_SIZE_GB - 10" | bc)
log_info "Estimated Android userdata: ${ANDROID_SIZE}GB"

if [ "$(echo "$ANDROID_SIZE < 20" | bc)" -eq 1 ]; then
    log_error "Not enough space for Android!"
    log_error "Reduce Windows or Linux partition sizes"
    exit 1
fi

echo ""
log_warn "${RED}═══════════════════════════════════════════════════════${NC}"
log_warn "${RED}        CRITICAL WARNING - DATA WILL BE DESTROYED       ${NC}"
log_warn "${RED}═══════════════════════════════════════════════════════${NC}"
echo ""
log_warn "This operation will:"
log_warn "  • Delete the userdata partition (ALL ANDROID DATA)"
log_warn "  • Create new partitions for Windows and Linux"
log_warn "  • Recreate a smaller userdata partition"
echo ""
log_warn "Before proceeding:"
log_warn "  ✓ Backup all important data"
log_warn "  ✓ Backup critical partitions (modem, persist, boot, etc.)"
log_warn "  ✓ Ensure you have stock firmware to restore if needed"
log_warn "  ✓ Verify you have TWRP backup or can reflash ROM"
echo ""

if [ $DRY_RUN -eq 0 ]; then
    echo "${RED}Type 'YES I UNDERSTAND' to proceed:${NC}"
    read -r confirmation

    if [ "$confirmation" != "YES I UNDERSTAND" ]; then
        log_info "Operation cancelled"
        exit 0
    fi

    echo ""
    log_warn "Last chance! Type 'DESTROY DATA' to confirm:"
    read -r final_confirm

    if [ "$final_confirm" != "DESTROY DATA" ]; then
        log_info "Operation cancelled"
        exit 0
    fi
fi

echo ""
log_info "${CYAN}Starting partition modifications...${NC}"
echo ""

if [ $DRY_RUN -eq 1 ]; then
    log_info "[DRY RUN] Would execute the following:"
    echo ""
    echo "1. Unmount userdata partition"
    echo "2. Remove current userdata partition"
    echo "3. Create ESP partition (1GB, FAT32) for Windows UEFI"
    echo "4. Create Windows partition (${WINDOWS_SIZE_GB}GB, NTFS)"
    echo "5. Create Linux partition (${LINUX_SIZE_GB}GB, ext4)"
    echo "6. Create new userdata partition (remaining space, f2fs)"
    echo "7. Format all new partitions"
    echo ""
    log_info "[DRY RUN] No actual changes made"
    echo ""
    log_info "To apply changes, run without --dry-run flag"
    exit 0
fi

# Actual partition modification
log_warn "Beginning partition modifications..."

# Find userdata partition number
USERDATA_PARTNUM=$(parted "$MAIN_DEV" print | grep "userdata" | awk '{print $1}')

if [ -z "$USERDATA_PARTNUM" ]; then
    log_error "Cannot find userdata partition"
    exit 1
fi

log_info "Found userdata at partition $USERDATA_PARTNUM"

# Unmount userdata if mounted
log_info "Unmounting userdata..."
umount /data 2>/dev/null
umount /dev/block/by-name/userdata 2>/dev/null

# Start parted
log_info "Removing userdata partition..."
parted "$MAIN_DEV" rm "$USERDATA_PARTNUM" || {
    log_error "Failed to remove userdata partition"
    exit 1
}

# Get start sector (where userdata was)
START_SECTOR=$(parted "$MAIN_DEV" unit s print free | grep "Free Space" | tail -1 | awk '{print $1}' | sed 's/s//')

if [ -z "$START_SECTOR" ]; then
    log_error "Cannot determine start sector"
    exit 1
fi

log_info "Start sector: $START_SECTOR"

# Convert GB to sectors (assuming 512 byte sectors)
SECTOR_SIZE=512
GB_TO_SECTORS=2097152  # (1024*1024*1024)/512

ESP_SIZE_SECTORS=$((1 * GB_TO_SECTORS))
WIN_SIZE_SECTORS=$((WINDOWS_SIZE_GB * GB_TO_SECTORS))
LINUX_SIZE_SECTORS=$((LINUX_SIZE_GB * GB_TO_SECTORS))

ESP_START=$START_SECTOR
ESP_END=$((ESP_START + ESP_SIZE_SECTORS))

WIN_START=$ESP_END
WIN_END=$((WIN_START + WIN_SIZE_SECTORS))

LINUX_START=$WIN_END
LINUX_END=$((LINUX_START + LINUX_SIZE_SECTORS))

USERDATA_START=$LINUX_END

# Create partitions
log_info "Creating ESP partition..."
parted "$MAIN_DEV" mkpart esp fat32 "${ESP_START}s" "${ESP_END}s" || {
    log_error "Failed to create ESP partition"
    exit 1
}

log_info "Creating Windows partition..."
parted "$MAIN_DEV" mkpart win ntfs "${WIN_START}s" "${WIN_END}s" || {
    log_error "Failed to create Windows partition"
    exit 1
}

log_info "Creating Linux partition..."
parted "$MAIN_DEV" mkpart linux ext4 "${LINUX_START}s" "${LINUX_END}s" || {
    log_error "Failed to create Linux partition"
    exit 1
}

log_info "Creating new userdata partition..."
parted "$MAIN_DEV" mkpart userdata ext4 "${USERDATA_START}s" 100% || {
    log_error "Failed to create userdata partition"
    exit 1
}

# Set partition flags
log_info "Setting partition flags..."
parted "$MAIN_DEV" set "$(parted "$MAIN_DEV" print | grep "esp" | awk '{print $1}')" esp on

# Wait for kernel to recognize partitions
log_info "Waiting for kernel to recognize new partitions..."
sleep 3
partprobe "$MAIN_DEV"
sleep 2

# Format partitions
log_info "Formatting partitions..."

log_info "  Formatting ESP (FAT32)..."
mkfs.vfat -F 32 -n "ESP" /dev/block/by-name/esp || log_warn "ESP format failed"

log_info "  Formatting Windows partition (NTFS)..."
# NTFS formatting might not be available in TWRP, will need to be done later
# mkfs.ntfs -f -L "Windows" /dev/block/by-name/win 2>/dev/null || log_warn "NTFS format not available, format from Windows"

log_info "  Formatting Linux partition (ext4)..."
mkfs.ext4 -F -L "Linux" /dev/block/by-name/linux || log_warn "Linux format failed"

log_info "  Formatting userdata (f2fs)..."
mkfs.f2fs -f -l userdata /dev/block/by-name/userdata || {
    log_warn "f2fs format failed, trying ext4..."
    mkfs.ext4 -F -L "userdata" /dev/block/by-name/userdata
}

echo ""
log_info "${GREEN}═══════════════════════════════════════════════════════${NC}"
log_info "${GREEN}Partition setup completed successfully!${NC}"
log_info "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Display new partition layout
log_info "New partition layout:"
echo ""
parted "$MAIN_DEV" print
echo ""

log_info "Next steps:"
echo "  1. Reboot to TWRP to ensure partitions are recognized"
echo "  2. Format userdata in TWRP (if needed)"
echo "  3. Install Android ROM to userdata"
echo "  4. Install Windows to 'win' partition"
echo "  5. Install Linux to 'linux' partition"
echo "  6. Install triboot script"
echo ""

log_warn "Reboot recommended before proceeding with OS installations"
