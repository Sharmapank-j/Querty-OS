#!/system/bin/sh
# Triboot Script for Poco X4 Pro 5G (veux/peux)
# Multi-boot OS selector for Android, Windows ARM, and Linux
# Adapted from Poco F1 tri-boot by orailnoor
# Part of Querty-OS project

# Configuration
TRIBOOT_DIR="/data/triboot"
IMAGES_DIR="${TRIBOOT_DIR}/images"
CONFIG_DIR="${TRIBOOT_DIR}/config"
SCRIPTS_DIR="${TRIBOOT_DIR}/scripts"

# Boot image paths
BOOT_ANDROID="${IMAGES_DIR}/boot_android.img"
BOOT_WINDOWS="${IMAGES_DIR}/boot_windows.img"
BOOT_LINUX="${IMAGES_DIR}/boot_linux.img"

# DTBO paths (optional, some OSes don't need different DTBO)
DTBO_ANDROID="${IMAGES_DIR}/dtbo_android.img"
DTBO_LINUX="${IMAGES_DIR}/dtbo_linux.img"

# Partition block devices for Poco X4 Pro 5G
# These paths are for veux/peux (Snapdragon 695)
BOOT_PARTITION="/dev/block/by-name/boot"
BOOT_A="/dev/block/by-name/boot_a"
BOOT_B="/dev/block/by-name/boot_b"
DTBO_PARTITION="/dev/block/by-name/dtbo"
DTBO_A="/dev/block/by-name/dtbo_a"
DTBO_B="/dev/block/by-name/dtbo_b"
VBMETA_A="/dev/block/by-name/vbmeta_a"
VBMETA_B="/dev/block/by-name/vbmeta_b"
VBMETA_SYSTEM_A="/dev/block/by-name/vbmeta_system_a"
VBMETA_SYSTEM_B="/dev/block/by-name/vbmeta_system_b"

# State files
CURRENT_OS_FILE="${CONFIG_DIR}/current_os.txt"
LAST_ANDROID_SLOT="${CONFIG_DIR}/last_android_slot.txt"

# Device identification
DEVICE_CODENAME="veux"  # Can be veux or peux

# Colors for output (TWRP terminal supports basic ANSI)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

print_banner() {
    echo ""
    echo "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║${NC}  ${GREEN}TRIBOOT${NC} - Poco X4 Pro 5G Multi-Boot Selector           ${CYAN}║${NC}"
    echo "${CYAN}║${NC}        Android │ Windows ARM │ Linux                       ${CYAN}║${NC}"
    echo "${CYAN}║${NC}        Device: ${YELLOW}veux/peux${NC} | ${BLUE}Snapdragon 695${NC}               ${CYAN}║${NC}"
    echo "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_info() {
    echo "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$(id -u)" != "0" ]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Detect device
detect_device() {
    # Try to get device codename from various sources
    local device=$(getprop ro.product.device 2>/dev/null)

    if [ -z "$device" ]; then
        device=$(getprop ro.build.product 2>/dev/null)
    fi

    case "$device" in
        veux|peux)
            DEVICE_CODENAME="$device"
            log_info "Detected device: ${YELLOW}Poco X4 Pro 5G ($device)${NC}"
            return 0
            ;;
        *)
            log_warn "Unknown device: $device"
            log_warn "Expected veux or peux (Poco X4 Pro 5G)"
            log_warn "Proceeding anyway - use at your own risk!"
            return 1
            ;;
    esac
}

# Initialize directory structure
init_dirs() {
    mkdir -p "${IMAGES_DIR}"
    mkdir -p "${CONFIG_DIR}"
    mkdir -p "${SCRIPTS_DIR}"
}

# Get current active slot (a or b)
get_active_slot() {
    # Try using getprop first (works in Android/recovery)
    SLOT=$(getprop ro.boot.slot_suffix 2>/dev/null | tr -d '_')

    if [ -z "$SLOT" ]; then
        # Fallback: check bootctl
        if command -v bootctl >/dev/null 2>&1; then
            SLOT=$(bootctl get-current-slot 2>/dev/null)
            case "$SLOT" in
                0) SLOT="a" ;;
                1) SLOT="b" ;;
                *) SLOT="a" ;; # Default to a
            esac
        else
            SLOT="a"  # Default fallback
        fi
    fi

    echo "$SLOT"
}

# Set active slot
set_active_slot() {
    local slot="$1"

    log_step "Setting active slot to: $slot"

    # Try bootctl first (Android 7.0+)
    if command -v bootctl >/dev/null 2>&1; then
        case "$slot" in
            a|A) bootctl set-active-boot-slot 0 2>/dev/null ;;
            b|B) bootctl set-active-boot-slot 1 2>/dev/null ;;
        esac
    fi

    # Also try via setprop if available
    if command -v setprop >/dev/null 2>&1; then
        setprop ro.boot.slot_suffix "_${slot}" 2>/dev/null
    fi
}

# Check if boot image exists
check_image() {
    local image="$1"
    local name="$2"

    if [ ! -f "$image" ]; then
        log_error "$name boot image not found: $image"
        log_warn "Please copy the boot image to: $image"
        return 1
    fi

    # Verify it's a valid boot image (check for ANDROID! magic)
    if ! head -c 8 "$image" 2>/dev/null | grep -q "ANDROID!"; then
        log_warn "$name image may not be a valid Android boot image"
        log_warn "This might be a UEFI image or corrupted - proceeding anyway"
    fi

    local size=$(ls -lh "$image" | awk '{print $5}')
    log_info "$name image size: $size"

    return 0
}

# Flash boot image to partition
flash_boot() {
    local image="$1"
    local target="$2"

    log_step "Flashing boot image..."
    log_info "Source: $image"
    log_info "Target: $target"

    # Verify source exists
    if [ ! -f "$image" ]; then
        log_error "Source image not found: $image"
        return 1
    fi

    # Verify target exists
    if [ ! -e "$target" ]; then
        log_error "Target partition not found: $target"
        return 1
    fi

    # Get image size
    local img_size=$(stat -c%s "$image" 2>/dev/null)
    local part_size=$(blockdev --getsize64 "$target" 2>/dev/null)

    if [ -n "$img_size" ] && [ -n "$part_size" ]; then
        if [ "$img_size" -gt "$part_size" ]; then
            log_error "Image size ($img_size) exceeds partition size ($part_size)"
            return 1
        fi
    fi

    # Flash the image
    dd if="$image" of="$target" bs=4M 2>/dev/null
    local result=$?

    if [ $result -eq 0 ]; then
        sync
        log_info "Boot image flashed successfully"
        return 0
    else
        log_error "Failed to flash boot image (dd returned $result)"
        return 1
    fi
}

# Flash DTBO if provided
flash_dtbo() {
    local image="$1"
    local target="$2"

    if [ ! -f "$image" ]; then
        log_info "No DTBO image provided, skipping"
        return 0
    fi

    log_step "Flashing DTBO..."
    dd if="$image" of="$target" bs=4M 2>/dev/null
    local result=$?

    if [ $result -eq 0 ]; then
        sync
        log_info "DTBO flashed successfully"
        return 0
    else
        log_warn "Failed to flash DTBO (non-critical)"
        return 1
    fi
}

# Disable AVB verification
disable_avb() {
    log_step "Ensuring AVB is disabled..."

    # Poco X4 Pro 5G has both vbmeta and vbmeta_system partitions
    for vbmeta in "$VBMETA_A" "$VBMETA_B" "$VBMETA_SYSTEM_A" "$VBMETA_SYSTEM_B"; do
        if [ -e "$vbmeta" ]; then
            # Read current AVB flags
            current=$(dd if="$vbmeta" bs=1 skip=123 count=1 2>/dev/null | od -An -tx1 | tr -d ' ')

            if [ "$current" != "02" ] && [ "$current" != "03" ]; then
                log_warn "AVB may not be fully disabled on $vbmeta (current: $current)"
                log_warn "Consider flashing vbmeta-disabled.img"
            fi
        fi
    done

    log_info "AVB check complete"
}

# Save current OS state
save_state() {
    local os="$1"
    echo "$os" > "$CURRENT_OS_FILE"
    log_info "State saved: $os"
}

# Get current OS state
get_state() {
    if [ -f "$CURRENT_OS_FILE" ]; then
        cat "$CURRENT_OS_FILE"
    else
        echo "unknown"
    fi
}

# Backup current boot image
backup_current_boot() {
    local slot=$(get_active_slot)
    local backup_file="${IMAGES_DIR}/boot_backup_$(date +%Y%m%d_%H%M%S).img"

    log_step "Backing up current boot image..."

    case "$slot" in
        a|A) dd if="$BOOT_A" of="$backup_file" bs=4M 2>/dev/null ;;
        b|B) dd if="$BOOT_B" of="$backup_file" bs=4M 2>/dev/null ;;
        *)   dd if="$BOOT_A" of="$backup_file" bs=4M 2>/dev/null ;;
    esac

    if [ $? -eq 0 ]; then
        log_info "Backup saved: $backup_file"
        return 0
    else
        log_error "Backup failed"
        return 1
    fi
}

# ============================================================================
# Boot Functions
# ============================================================================

boot_android() {
    print_banner
    log_info "Preparing to boot: ${GREEN}Android${NC}"
    echo ""

    # Check image
    if ! check_image "$BOOT_ANDROID" "Android"; then
        log_error "Cannot proceed without Android boot image"
        echo ""
        log_info "To create Android boot image backup, boot to your ROM and run:"
        echo "  su"
        echo "  dd if=/dev/block/by-name/boot of=/sdcard/boot_android.img bs=4M"
        echo "  cp /sdcard/boot_android.img ${BOOT_ANDROID}"
        return 1
    fi

    # Get target slot (restore last used Android slot if available)
    local slot="a"
    if [ -f "$LAST_ANDROID_SLOT" ]; then
        slot=$(cat "$LAST_ANDROID_SLOT")
    fi

    local boot_target="$BOOT_A"
    local dtbo_target="$DTBO_A"
    case "$slot" in
        b|B)
            boot_target="$BOOT_B"
            dtbo_target="$DTBO_B"
            ;;
    esac

    log_info "Using slot: $slot"

    # Flash boot
    if ! flash_boot "$BOOT_ANDROID" "$boot_target"; then
        return 1
    fi

    # Flash DTBO if exists
    if [ -f "$DTBO_ANDROID" ]; then
        flash_dtbo "$DTBO_ANDROID" "$dtbo_target"
    fi

    # Set active slot
    set_active_slot "$slot"

    # Ensure AVB is handled
    disable_avb

    # Save state
    save_state "android"

    echo ""
    log_info "${GREEN}Ready to boot Android!${NC}"
    log_info "Rebooting in 3 seconds..."
    sleep 3

    reboot
}

boot_windows() {
    print_banner
    log_info "Preparing to boot: ${BLUE}Windows ARM${NC}"
    echo ""

    log_warn "${YELLOW}WARNING:${NC} Windows ARM on Snapdragon 695 is experimental!"
    log_warn "Ensure you have the correct UEFI build for veux/peux"
    echo ""

    # Check image
    if ! check_image "$BOOT_WINDOWS" "Windows UEFI"; then
        log_error "Cannot proceed without Windows UEFI boot image"
        echo ""
        log_info "Windows UEFI boot image must be built for Snapdragon 695"
        log_info "Check Project WOA or Renegade Project for UEFI builds"
        log_info "Copy the UEFI boot image to:"
        echo "  ${BOOT_WINDOWS}"
        return 1
    fi

    # Save current Android slot before switching
    local current_slot=$(get_active_slot)
    echo "$current_slot" > "$LAST_ANDROID_SLOT"
    log_info "Saved Android slot: $current_slot"

    # Windows typically uses slot A
    local boot_target="$BOOT_A"

    # Flash UEFI boot image
    if ! flash_boot "$BOOT_WINDOWS" "$boot_target"; then
        return 1
    fi

    # Windows doesn't use Android DTBO - no need to flash

    # Set slot A active for Windows
    set_active_slot "a"

    # Disable AVB
    disable_avb

    # Save state
    save_state "windows"

    echo ""
    log_info "${BLUE}Ready to boot Windows ARM!${NC}"
    log_warn "First boot may take several minutes"
    log_info "Rebooting in 5 seconds..."
    sleep 5

    reboot
}

boot_linux() {
    print_banner
    log_info "Preparing to boot: ${YELLOW}Linux${NC}"
    echo ""

    # Check image
    if ! check_image "$BOOT_LINUX" "Linux"; then
        log_error "Cannot proceed without Linux boot image"
        echo ""
        log_info "Linux support for veux/peux is limited"
        log_info "Check postmarketOS or Ubuntu Touch ports"
        log_info "Copy the Linux boot.img to:"
        echo "  ${BOOT_LINUX}"
        return 1
    fi

    # Save current Android slot before switching
    local current_slot=$(get_active_slot)
    echo "$current_slot" > "$LAST_ANDROID_SLOT"
    log_info "Saved Android slot: $current_slot"

    # Use slot B for Linux to keep Android on slot A
    local boot_target="$BOOT_B"
    local dtbo_target="$DTBO_B"

    # Flash boot
    if ! flash_boot "$BOOT_LINUX" "$boot_target"; then
        return 1
    fi

    # Flash DTBO if exists
    if [ -f "$DTBO_LINUX" ]; then
        flash_dtbo "$DTBO_LINUX" "$dtbo_target"
    fi

    # Set slot B active for Linux
    set_active_slot "b"

    # Disable AVB
    disable_avb

    # Save state
    save_state "linux"

    echo ""
    log_info "${YELLOW}Ready to boot Linux!${NC}"
    log_warn "Ensure your Linux partition is properly set up"
    log_info "Rebooting in 3 seconds..."
    sleep 3

    reboot
}

# ============================================================================
# Menu and Main Functions
# ============================================================================

show_menu() {
    print_banner

    local current=$(get_state)
    log_info "Current OS: ${CYAN}$current${NC}"
    local slot=$(get_active_slot)
    log_info "Active slot: ${CYAN}$slot${NC}"

    echo ""
    echo "${CYAN}Available Commands:${NC}"
    echo ""
    echo "  ${GREEN}triboot android${NC}  - Boot to Android"
    echo "  ${BLUE}triboot windows${NC}  - Boot to Windows ARM"
    echo "  ${YELLOW}triboot linux${NC}    - Boot to Linux"
    echo ""
    echo "  ${MAGENTA}triboot backup${NC}   - Backup current boot image"
    echo "  ${MAGENTA}triboot status${NC}   - Show detailed status"
    echo "  ${MAGENTA}triboot help${NC}     - Show this menu"
    echo ""
}

show_status() {
    print_banner
    log_info "System Status"
    echo ""

    detect_device

    local current=$(get_state)
    local slot=$(get_active_slot)

    echo "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo "${GREEN}Current OS:${NC}    $current"
    echo "${GREEN}Active Slot:${NC}   $slot"
    echo "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""

    echo "${YELLOW}Boot Images:${NC}"
    [ -f "$BOOT_ANDROID" ] && echo "  ✓ Android:  $(ls -lh $BOOT_ANDROID | awk '{print $5}')" || echo "  ✗ Android:  Not found"
    [ -f "$BOOT_WINDOWS" ] && echo "  ✓ Windows:  $(ls -lh $BOOT_WINDOWS | awk '{print $5}')" || echo "  ✗ Windows:  Not found"
    [ -f "$BOOT_LINUX" ] && echo "  ✓ Linux:    $(ls -lh $BOOT_LINUX | awk '{print $5}')" || echo "  ✗ Linux:    Not found"
    echo ""

    echo "${YELLOW}DTBO Images:${NC}"
    [ -f "$DTBO_ANDROID" ] && echo "  ✓ Android:  $(ls -lh $DTBO_ANDROID | awk '{print $5}')" || echo "  - Android:  Not found (optional)"
    [ -f "$DTBO_LINUX" ] && echo "  ✓ Linux:    $(ls -lh $DTBO_LINUX | awk '{print $5}')" || echo "  - Linux:    Not found (optional)"
    echo ""

    echo "${YELLOW}Partitions:${NC}"
    [ -e "$BOOT_A" ] && echo "  ✓ boot_a exists" || echo "  ✗ boot_a missing"
    [ -e "$BOOT_B" ] && echo "  ✓ boot_b exists" || echo "  ✗ boot_b missing"
    [ -e "$DTBO_A" ] && echo "  ✓ dtbo_a exists" || echo "  ✗ dtbo_a missing"
    [ -e "$DTBO_B" ] && echo "  ✓ dtbo_b exists" || echo "  ✗ dtbo_b missing"
    echo ""
}

show_help() {
    print_banner
    echo "${CYAN}Triboot Help${NC}"
    echo ""
    echo "${YELLOW}Usage:${NC}"
    echo "  triboot [command]"
    echo ""
    echo "${YELLOW}Commands:${NC}"
    echo "  ${GREEN}android${NC}   - Boot to Android ROM"
    echo "  ${BLUE}windows${NC}   - Boot to Windows ARM (experimental)"
    echo "  ${YELLOW}linux${NC}     - Boot to Linux distribution"
    echo "  ${MAGENTA}backup${NC}    - Backup current boot partition"
    echo "  ${MAGENTA}status${NC}    - Show system and image status"
    echo "  ${MAGENTA}help${NC}      - Show this help message"
    echo ""
    echo "${YELLOW}Examples:${NC}"
    echo "  triboot android  # Switch to Android"
    echo "  triboot windows  # Switch to Windows ARM"
    echo "  triboot status   # Check system status"
    echo ""
    echo "${YELLOW}Notes:${NC}"
    echo "  - Always ensure you have backups before switching OSes"
    echo "  - Boot images must be present in $IMAGES_DIR"
    echo "  - Windows ARM support on SD695 is experimental"
    echo "  - First boot after OS switch may take longer"
    echo ""
}

# Main function
main() {
    # Check root
    check_root

    # Initialize directories
    init_dirs

    # Parse command
    case "$1" in
        android)
            boot_android
            ;;
        windows)
            boot_windows
            ;;
        linux)
            boot_linux
            ;;
        backup)
            print_banner
            backup_current_boot
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_menu
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
