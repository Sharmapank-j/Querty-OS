# Poco X4 Pro 5G Device Configuration

## Device Information

```yaml
device:
  name: "Poco X4 Pro 5G"
  codename: ["veux", "peux"]
  manufacturer: "Xiaomi"

specs:
  soc: "Qualcomm Snapdragon 695 5G"
  soc_model: "SM6375"
  cpu: "Kryo 660 (2x2.2 GHz Cortex-A78 & 6x1.8 GHz Cortex-A55)"
  gpu: "Adreno 619"
  ram: ["6GB", "8GB"]
  storage: ["128GB", "256GB"]
  storage_type: "UFS 2.2"
  display: "6.67\" AMOLED, 1080x2400, 120Hz"

android:
  launch_version: "Android 11"
  current_version: "Android 13"
  miui_version: ["MIUI 13", "MIUI 14"]

bootloader:
  type: "Qualcomm Secure Boot"
  slots: "A/B"
  unlock: "Required - Via Mi Unlock Tool"
```

## Partition Layout

### Standard MIUI Partition Table

```
Partition Name       Size      Type      Mount Point
──────────────────────────────────────────────────────
xbl_a                ~2MB      raw       -
xbl_b                ~2MB      raw       -
abl_a                ~1MB      raw       -
abl_b                ~1MB      raw       -
boot_a               128MB     raw       -
boot_b               128MB     raw       -
dtbo_a               25MB      raw       -
dtbo_b               25MB      raw       -
vbmeta_a             1MB       raw       -
vbmeta_b             1MB       raw       -
vbmeta_system_a      1MB       raw       -
vbmeta_system_b      1MB       raw       -
vendor_boot_a        100MB     raw       -
vendor_boot_b        100MB     raw       -
system_a             ~3GB      ext4      /system
system_b             ~3GB      ext4      -
vendor_a             ~1.5GB    ext4      /vendor
vendor_b             ~1.5GB    ext4      -
product_a            ~2GB      ext4      /product
product_b            ~2GB      ext4      -
modemst1             3MB       raw       - (CRITICAL)
modemst2             3MB       raw       - (CRITICAL)
fsg                  3MB       raw       - (CRITICAL)
fsc                  1MB       raw       - (CRITICAL)
persist              60MB      ext4      /persist
metadata             16MB      raw       -
misc                 1MB       raw       -
userdata             ~110GB    f2fs      /data
```

### Tri-Boot Modified Layout

After tri-boot setup (128GB device):

```
Partition Name       Size      Type      Mount Point      Purpose
───────────────────────────────────────────────────────────────────
[All standard partitions above remain unchanged]
esp                  1GB       vfat      -               Windows EFI
win                  50GB      ntfs      -               Windows System
linux                20GB      ext4      -               Linux Root
userdata             ~45GB     f2fs      /data           Android Data
```

## Block Device Paths

### Main Storage Device
```bash
/dev/block/sda  # Main UFS storage
```

### By-Name Links
```bash
/dev/block/by-name/boot       -> ../sda22 (or similar)
/dev/block/by-name/boot_a     -> ../sda22
/dev/block/by-name/boot_b     -> ../sda23
/dev/block/by-name/userdata   -> ../sda45
/dev/block/by-name/modemst1   -> ../sda31
/dev/block/by-name/modemst2   -> ../sda32
```

## Boot Image Specifications

### Android Boot Image
```
Format: Android Boot Image v3/v4
Header Version: 3 or 4
Page Size: 4096 bytes
Kernel: 64-bit ARM (aarch64)
Ramdisk: gzip compressed
DTB: Included or separate DTBO partition
Cmdline: console=ttyMSM0,115200n8 ...
```

### Windows UEFI Image
```
Format: UEFI Boot Image
Architecture: ARM64
UEFI Version: EDK2-based
Panel Support: Required for veux/peux
Status: Experimental for SD695
```

### Linux Boot Image
```
Format: Android Boot Image v3
Kernel: Mainline or Android kernel
DTB: Required for veux/peux
Ramdisk: initramfs with systemd/busybox
```

## Critical Partitions

### DO NOT MODIFY
```bash
# Bootloader
xbl_a, xbl_b         # Primary bootloader
abl_a, abl_b         # Android bootloader

# Modem (CRITICAL!)
modemst1, modemst2   # Modem NV storage
fsg, fsc             # Modem calibration

# Device-specific
persist              # Calibration data, WiFi MAC, sensors
```

### Safe to Modify (for tri-boot)
```bash
boot_a, boot_b       # Boot images
dtbo_a, dtbo_b       # Device tree (if needed)
userdata             # Can be resized/recreated
vbmeta_*             # Can be disabled
```

## Recovery

### TWRP/OrangeFox
```
Recommended Version: 3.7.0+
Requirements:
  - parted utility (for partition management)
  - F2FS support
  - Decryption support
  - MTP support

Known Working Builds:
  - OrangeFox R11.1+ for veux
  - TWRP 3.7.0+ for peux
```

### Stock Recovery
```
Limited functionality
Not recommended for tri-boot
Use TWRP/OrangeFox instead
```

## Firmware

### Stock MIUI
```
Latest Stable: MIUI 14 (Android 13)
Fastboot ROM: Required for emergency recovery
Download: xiaomifirmware.com or xiaomirom.com

Codename in ROM:
  - veux (India variant)
  - peux (Global variant)
```

### Custom ROMs
```
Supported:
  - LineageOS 20/21
  - PixelExperience
  - ArrowOS
  - EvolutionX
  - etc.

All custom ROMs compatible with veux/peux should work
```

## Known Issues

### Tri-Boot Specific
```
✓ Boot slot management working
✓ A/B partitioning handled
⚠ Windows ARM highly experimental on SD695
⚠ Linux support limited (no official postmarketOS)
✓ Android ROMs fully compatible
```

### Device Specific
```
✓ Display: Working (120Hz supported)
✓ Touch: Working
✓ Audio: Working
✓ Bluetooth: Working
✓ WiFi: Working (2.4/5GHz)
✓ Cellular: Working (if modem intact)
✓ GPS: Working
✓ Cameras: Working in Android
⚠ Cameras: May not work in Linux/Windows
⚠ Fingerprint: May not work in Linux/Windows
✓ Charging: Working
✓ USB: Working (OTG supported)
```

## Compatibility

### Tested with:
```
Android:
  ✓ Evolution OS (Recommended - privacy-focused)
  ✓ GrapheneOS (If ported - maximum security)
  ✓ MIUI 13/14
  ✓ LineageOS 20/21
  ✓ PixelExperience Plus
  ✓ ArrowOS
  ✓ crDroid
  ✓ Paranoid Android

Windows ARM:
  ⚠ Windows 11 ARM64 (Experimental on SD695)
  ⚠ Requires UEFI firmware port
  ✓ Native ARM64 app execution
  ✓ x64 app emulation (by Windows)

Linux (Native Boot, NOT proot):
  ⚠ postmarketOS (Not yet available)
  ⚠ Ubuntu Touch (If ported)
  ✓ Fedora ARM (May work)
  ✓ Arch Linux ARM (May work)
  ✓ Debian ARM64 (May work)
  ✓ Generic ARM64 distros (May work)

  Note: Full kernel boot, NOT containerized
```

## Resources

### Official
```
Xiaomi Forums: https://c.mi.com/
MIUI Downloads: https://www.mi.com/global/service/download/
Mi Unlock: https://en.miui.com/unlock/
```

### Community
```
XDA Forums: forum.xda-developers.com/f/poco-x4-pro-5g.12551/
Telegram: t.me/pocox4pro5g (various groups)
Reddit: r/PocoPhones
GitHub: github.com/topics/poco-x4-pro-5g
```

### Recovery
```
TWRP: twrp.me/Devices/Xiaomi/
OrangeFox: orangefox.download/device/veux
LineageOS Recovery: download.lineageos.org
```

### Firmware
```
Xiaomi Firmware: xiaomifirmware.com
Xiaomi ROM: xiaomirom.com
MIUI Updates: c.mi.com/miui/forum-684-1.html
```

## Fastboot Commands Reference

### Device Info
```bash
fastboot getvar all                    # All device info
fastboot oem device-info              # Bootloader status
fastboot getvar current-slot          # Current active slot
fastboot getvar slot-count            # Number of slots (should be 2)
```

### Flashing
```bash
fastboot flash boot_a boot.img        # Flash to specific slot
fastboot flash boot_b boot.img
fastboot set_active a                  # Set active slot
fastboot set_active b
```

### Common Operations
```bash
fastboot reboot                        # Reboot device
fastboot reboot-recovery              # Boot to recovery
fastboot reboot-bootloader            # Reboot to bootloader
fastboot erase userdata               # Wipe userdata
fastboot format userdata              # Format userdata
```

## Build Information

When reporting issues, include:
```bash
# Device info
getprop ro.product.device
getprop ro.product.model
getprop ro.build.fingerprint

# Android version
getprop ro.build.version.release
getprop ro.build.version.security_patch

# MIUI/ROM version
getprop ro.miui.ui.version.name
getprop ro.build.version.incremental
```

---

**Last Updated**: 2024
**Device Support**: Active
**Tri-Boot Status**: Beta / Experimental
