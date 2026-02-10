# Poco X4 Pro 5G (veux/peux) Tri-Boot System

A tri-boot solution for the Xiaomi Poco X4 Pro 5G enabling:
- **Android** (Primary OS)
- **Windows ARM** (via UEFI)
- **Linux** (postmarketOS or Ubuntu Touch)

Using **OrangeFox Recovery** (recommended) or TWRP as the OS selector.

**NEW**: Can be installed without a laptop! See [No-Laptop Installation Guide](docs/NO-LAPTOP-INSTALLATION.md)

[![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://www.android.com/)
[![Windows ARM](https://img.shields.io/badge/Windows_ARM-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Linux](https://img.shields.io/badge/Linux-009900?style=for-the-badge&logo=linux&logoColor=white)](https://www.linux.org/)

## ⚠️ Critical Warnings

**This setup carries significant risks:**

- ⚠️ **Risk of hard brick** - Proceed only if you understand the risks
- ⚠️ **All data will be erased** during partition modifications
- ⚠️ **Cellular/modem can be permanently damaged** if critical partitions are touched
- ⚠️ **No warranty** - Use at your own risk
- ⚠️ **Bootloader must be unlocked** - This will void warranty

**DO NOT PROCEED** unless you:
- Have experience with Android device flashing
- Understand partition tables and dd commands
- Have a backup plan (stock firmware + MiFlash)
- Accept the risk of bricking your device

## Device Specifications

- **Device**: Xiaomi Poco X4 Pro 5G
- **Codename**: veux (India), peux (Global)
- **SoC**: Qualcomm Snapdragon 695 5G (SM6375)
- **RAM**: 6GB/8GB LPDDR4X
- **Storage**: 128GB/256GB UFS 2.2
- **Display**: 6.67" AMOLED, 120Hz
- **Android Version**: Android 11/12/13 (MIUI 13/14)

## ⚡ Native Execution - No Emulation!

**This tri-boot system provides TRUE NATIVE execution:**

- ✅ **Linux runs NATIVELY** - NOT in proot/chroot/container
  - Full Linux kernel boots directly
  - Complete hardware access
  - Real root privileges
  - 100% native performance
  
- ✅ **Windows apps run NATIVELY** - NOT via Wine/emulation  
  - Real Windows 11 ARM64 OS
  - ARM64 apps run at full speed
  - Windows handles x64 emulation internally
  - Full Windows features

- ✅ **Android**: Support for Evolution OS, GrapheneOS, any ROM
  - Full ROM compatibility
  - Native Android performance
  - Switch between ROMs easily

**See [NATIVE-EXECUTION.md](docs/NATIVE-EXECUTION.md) for technical details.**

## How It Works

Since Qualcomm's secure boot chain doesn't support native multi-boot:

```
┌─────────────────────────────────────────────────────────────────┐
│               Qualcomm Snapdragon 695 Boot Chain                │
├─────────────────────────────────────────────────────────────────┤
│  PBL → XBL → ABL → boot.img → OS                               │
└─────────────────────────────────────────────────────────────────┘
                            ↑
                    ┌───────┴───────┐
                    │  TWRP Menu    │
                    │  (triboot.sh) │
                    └───────┬───────┘
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   Android   │   │  Windows    │   │    Linux    │
   │  boot.img   │   │ UEFI boot   │   │  boot.img   │
   └─────────────┘   └─────────────┘   └─────────────┘
```

**This is pre-boot OS swapping with NATIVE execution**, not emulation or containers:
1. Boot into TWRP Recovery
2. Select desired OS from menu
3. Script flashes appropriate boot.img to boot partition
4. Device reboots into selected OS
5. Each OS runs **natively** on its own partition

**Key Advantages:**
- ✅ Linux runs **natively** (NOT in proot/chroot container)
- ✅ Full kernel access and hardware control
- ✅ Windows apps run **natively** via ARM64 (NOT Wine emulation)
- ✅ Each OS is completely independent
- ✅ No performance penalty from containerization

## Current Status

### ✅ Working
- [x] Documentation framework
- [x] Script architecture
- [x] Integration with Querty-OS system

### 🚧 In Progress
- [ ] Device-specific partition layout verification
- [ ] TWRP recovery modifications
- [ ] Windows ARM UEFI port
- [ ] Linux kernel for veux/peux

### ⏳ Planned
- [ ] Automated installation wizard
- [ ] GUI-based OS selector
- [ ] OTA update support for each OS

## Prerequisites

Before proceeding, ensure you have:

1. **Unlocked Bootloader**
   ```bash
   # Check bootloader status
   fastboot oem device-info
   ```

2. **OrangeFox Recovery** (Recommended) or **TWRP Recovery**
   - OrangeFox: Better features, modern UI - See [OrangeFox Guide](docs/ORANGEFOX-RECOVERY.md)
   - TWRP: Alternative if OrangeFox has issues
   - Must include `parted` utility
   - Recommended: Latest OrangeFox or TWRP for veux/peux

3. **Required Backups** (CRITICAL!)
   - Stock boot image
   - Stock DTBO
   - Modem partitions (modemst1, modemst2, fsg, fsc)
   - Persist partition
   - EFS partition

4. **Installation Method**
   - **With Laptop**: Standard ADB/Fastboot tools
   - **Without Laptop**: Rooted phone + Bugjaeger OR Termux
   - See [No-Laptop Installation Guide](docs/NO-LAPTOP-INSTALLATION.md) for details

## Installation Methods

Choose your installation method based on available devices:

### 📱 Method 1: No Laptop Required (NEW!)

**Use if you have:**
- Another rooted Android phone, OR
- Normal Android phone with Termux, OR
- iPad (limited support)

**Guide**: [No-Laptop Installation Guide](docs/NO-LAPTOP-INSTALLATION.md)

**Highlights:**
- ✅ Flash recovery using OTG cable
- ✅ Install Querty-OS using another phone
- ✅ Create backups without PC
- ✅ Complete setup mobile-only
- ⚠️ Bootloader unlock still needs PC (one-time, 15 min)

### 💻 Method 2: With Laptop (Traditional)

**Use if you have:**
- Windows/Linux/Mac computer
- USB cable

**Guides**:
- [Complete Deployment Guide](../../POCO_X4_PRO_DEPLOYMENT.md)
- [OrangeFox Recovery Guide](docs/ORANGEFOX-RECOVERY.md)

## Quick Start

### 1. Backup Critical Partitions

```bash
# Boot to TWRP
adb reboot recovery

# In TWRP terminal
sh /sdcard/scripts/backup_partitions.sh
```

**Immediately copy backups to your PC!**

### 2. Setup Partitions

```bash
# Preview partition changes (safe)
sh /sdcard/scripts/partition_setup.sh --dry-run

# Apply changes (DESTRUCTIVE - erases userdata!)
sh /sdcard/scripts/partition_setup.sh --device veux
```

### 3. Install Boot Images

```bash
# Create boot image storage
mkdir -p /data/triboot/images

# Copy your boot images
cp /sdcard/android_boot.img /data/triboot/images/boot_android.img
cp /sdcard/uefi_boot.img /data/triboot/images/boot_windows.img
cp /sdcard/linux_boot.img /data/triboot/images/boot_linux.img
```

### 4. Install Triboot Script

```bash
# Copy and setup script
cp /sdcard/scripts/triboot.sh /data/triboot/scripts/
chmod +x /data/triboot/scripts/triboot.sh
```

### 5. Switch Between OSes

```bash
# In TWRP terminal
triboot           # Show menu
triboot android   # Boot Android
triboot windows   # Boot Windows
triboot linux     # Boot Linux
```

## Target Partition Layout

For a 128GB device:

| Partition  | Size    | Filesystem | Purpose                    |
|------------|---------|------------|----------------------------|
| boot_a     | 128MB   | raw        | Active boot partition      |
| boot_b     | 128MB   | raw        | Backup boot partition      |
| dtbo_a     | 25MB    | raw        | Device tree overlay (A)    |
| dtbo_b     | 25MB    | raw        | Device tree overlay (B)    |
| vbmeta_a   | 1MB     | raw        | AVB metadata (disabled)    |
| vbmeta_b   | 1MB     | raw        | AVB metadata (disabled)    |
| esp        | 1GB     | FAT32      | Windows EFI System         |
| win        | 50GB    | NTFS       | Windows system partition   |
| linux      | 20GB    | ext4/f2fs  | Linux root filesystem      |
| userdata   | ~45GB   | f2fs       | Android user data          |

## Documentation

- **[NATIVE-EXECUTION.md](docs/NATIVE-EXECUTION.md)** - How Linux/Windows run natively (NOT emulated)
- **[TRI-BOOT-GUIDE.md](docs/TRI-BOOT-GUIDE.md)** - Complete installation guide
- **[QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md)** - Commands cheat sheet
- **[RISK-AND-RECOVERY.md](docs/RISK-AND-RECOVERY.md)** - Risk assessment and recovery

## Scripts

- **[triboot.sh](scripts/triboot.sh)** - Main OS selector script
- **[partition_setup.sh](scripts/partition_setup.sh)** - Partition management
- **[backup_partitions.sh](scripts/backup_partitions.sh)** - Backup utility

## Integration with Querty-OS

This tri-boot system integrates with the Querty-OS AI-first system layer:

```python
# Example: Using Querty-OS to switch OSes
from core.os_control import OSControlManager

manager = OSControlManager()
triboot = manager.get_controller('triboot')
triboot.switch_os('windows')  # Prepares and reboots to Windows
```

See the main [Querty-OS documentation](../../README.md) for more details.

## Compatibility

### Operating Systems

- **Android**: Any custom ROM compatible with veux/peux
  - **Evolution OS** (recommended for privacy)
  - **GrapheneOS** (if ported to veux/peux)
  - LineageOS, PixelExperience, ArrowOS
  - MIUI (stock)
- **Windows ARM**: Windows 10/11 ARM64
  - Native UEFI boot (NOT emulation)
  - Requires UEFI port for Snapdragon 695
  - Run Windows apps natively via ARM64
  - Currently experimental on SD695
- **Linux**: 
  - **Native Linux boot** (NOT proot/chroot from Android)
  - Dedicated Linux partition with full kernel
  - postmarketOS (when available)
  - Ubuntu Touch (if ported)
  - Fedora ARM, Arch Linux ARM
  - Full desktop environment support

### Known Issues

- Windows ARM support is experimental on SD695
- Some Linux distributions may require kernel modifications
- Battery drain may be higher on non-Android OSes
- Not all hardware features work in all OSes

## Troubleshooting

### Device Won't Boot

1. Boot to fastboot: Hold Vol Down + Power from off
2. Flash stock boot:
   ```bash
   fastboot flash boot boot_stock.img
   fastboot reboot
   ```

### Stuck in TWRP

1. Flash known-good boot image in TWRP terminal:
   ```bash
   dd if=/data/triboot/images/boot_android.img of=/dev/block/by-name/boot
   reboot
   ```

### No Cellular After Changes

Restore modem partitions from backup:
```bash
dd if=/sdcard/backup/modemst1.img of=/dev/block/by-name/modemst1
dd if=/sdcard/backup/modemst2.img of=/dev/block/by-name/modemst2
```

## Recovery Plan

### Emergency Recovery

Always keep accessible:
1. **Stock MIUI firmware** (Fastboot ROM)
2. **MiFlash tool** on PC
3. **All partition backups** on external storage
4. **USB cable** and PC with drivers

### Recovery Priority

1. **Fastboot Mode** - Can reflash critical partitions
2. **EDL Mode** - Last resort (requires authorized Xiaomi account)
3. **TWRP** - Can restore from backups

## Credits

- Based on [Poco F1 tri-boot](https://github.com/orailnoor/poco-f1-tri-boot) by orailnoor
- Querty-OS team for system integration
- Poco X4 Pro 5G community on XDA
- Project WOA for Windows on ARM
- postmarketOS team

## Contributing

Contributions welcome! Please:
1. Test thoroughly on your device
2. Document any device-specific quirks
3. Submit pull requests with clear descriptions

## License

This project is provided as-is for educational purposes.
**Use at your own risk. No warranty provided.**

---

**⚠️ Remember: ALWAYS BACKUP before modifying partitions!**
**Keep backups on external storage/PC, not just on the device!**
