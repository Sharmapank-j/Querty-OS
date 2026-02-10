# Quick Reference - Poco X4 Pro 5G Tri-Boot

Quick command reference and troubleshooting cheat sheet.

## Quick Commands

### Triboot Operations

```bash
# Show menu
triboot

# Boot to specific OS
triboot android
triboot windows
triboot linux

# Check status
triboot status

# Backup current boot
triboot backup

# Help
triboot help
```

### Boot to Recovery/Fastboot

```bash
# From Android (with root)
su
reboot recovery        # Boot to TWRP
reboot bootloader      # Boot to Fastboot

# From ADB
adb reboot recovery
adb reboot bootloader

# Hardware keys
# Power Off → Vol Down + Power → Select with Volume keys
```

### Partition Management

```bash
# View partition table
parted /dev/block/sda print

# List partition links
ls -la /dev/block/by-name/

# Check partition sizes
df -h

# Mount partition
mount /dev/block/by-name/linux /mnt/linux
```

### Backup Operations

```bash
# Backup all critical partitions
sh /sdcard/scripts/backup_partitions.sh

# Backup single partition
dd if=/dev/block/by-name/boot of=/sdcard/boot_backup.img bs=4M

# Restore partition
dd if=/sdcard/boot_backup.img of=/dev/block/by-name/boot bs=4M

# Verify backup
md5sum /sdcard/backup/*.img
```

---

## File Locations

### Triboot Files

```
/data/triboot/
├── images/
│   ├── boot_android.img    # Android boot image
│   ├── boot_windows.img    # Windows UEFI image
│   ├── boot_linux.img      # Linux boot image
│   └── boot_backup_*.img   # Auto backups
├── scripts/
│   └── triboot.sh          # Main script
└── config/
    ├── current_os.txt      # Current OS state
    └── last_android_slot.txt # Last Android slot
```

### Important Partitions

```
/dev/block/by-name/
├── boot_a, boot_b          # Boot partitions
├── dtbo_a, dtbo_b          # Device tree
├── vbmeta_a, vbmeta_b      # AVB metadata
├── esp                     # Windows EFI
├── win                     # Windows system
├── linux                   # Linux root
├── userdata                # Android data
├── modemst1, modemst2      # CRITICAL: Modem
└── persist                 # Calibration data
```

---

## Common Issues

### Boot Loop

```bash
# In TWRP Terminal
dd if=/data/triboot/images/boot_android.img of=/dev/block/by-name/boot
reboot
```

### No Cellular

```bash
# Restore modem partitions
dd if=/sdcard/backup/modemst1.img of=/dev/block/by-name/modemst1
dd if=/sdcard/backup/modemst2.img of=/dev/block/by-name/modemst2
reboot
```

### Can't Access TWRP

```bash
# From Fastboot
fastboot flash recovery twrp.img
fastboot reboot recovery
```

### Script Not Found

```bash
# Reinstall script
cp /sdcard/triboot.sh /data/triboot/scripts/
chmod +x /data/triboot/scripts/triboot.sh
```

### Wrong OS Boots

```bash
# In TWRP, flash correct boot image
dd if=/data/triboot/images/boot_android.img of=/dev/block/by-name/boot
reboot
```

---

## ADB/Fastboot Quick Reference

### ADB Commands

```bash
# Check connection
adb devices

# Push file
adb push file.zip /sdcard/

# Pull file
adb pull /sdcard/file.zip ./

# Shell access
adb shell

# Reboot options
adb reboot
adb reboot recovery
adb reboot bootloader

# Install APK
adb install app.apk

# Logcat
adb logcat
```

### Fastboot Commands

```bash
# Check connection
fastboot devices

# Flash partition
fastboot flash boot boot.img
fastboot flash recovery twrp.img

# Erase partition
fastboot erase userdata

# Boot image without flashing
fastboot boot twrp.img

# Reboot
fastboot reboot
```

---

## Partition Size Calculator

For 128GB device (~115GB usable):

```
System partitions: ~15GB (fixed)
ESP (Windows):     1GB
Windows:           40-60GB (recommended: 50GB)
Linux:             20-30GB (recommended: 20GB)
Android:           Remaining (30-50GB)
```

For 256GB device (~240GB usable):

```
System partitions: ~15GB (fixed)
ESP (Windows):     1GB
Windows:           60-80GB (recommended: 70GB)
Linux:             30-40GB (recommended: 30GB)
Android:           Remaining (120-140GB)
```

---

## Verification Checklist

Before declaring setup complete:

- [ ] All OSes boot successfully
- [ ] Can switch between OSes via triboot script
- [ ] Cellular/modem works in Android
- [ ] WiFi works in all OSes
- [ ] Backups stored safely on PC
- [ ] Recovery method tested (TWRP accessible)
- [ ] Stock firmware available for emergency

---

## Emergency Recovery Procedure

### Level 1: TWRP Accessible
```bash
# Boot to TWRP
# Flash Android boot image
# Restore from backup if needed
```

### Level 2: Fastboot Accessible
```bash
# Boot to Fastboot (Vol Down + Power)
fastboot flash boot boot_stock.img
fastboot flash recovery twrp.img
fastboot reboot recovery
```

### Level 3: Complete Brick
```bash
# Use MiFlash with stock firmware
# "Clean all" option
# This wipes everything
# Start over from scratch
```

---

## Performance Tips

### Battery Life
- Windows/Linux may drain battery faster
- Disable unnecessary services
- Use airplane mode when not needed

### Storage Management
- Keep 10% free space on each partition
- Use microSD for media files
- Regular cleanup of cache

### Boot Speed
- First boot after OS switch is slower
- Subsequent boots are faster
- SSD-like performance on UFS 2.2

---

## Hotkeys Reference

### Poco X4 Pro 5G

```
Power Off → Vol Down + Power = Fastboot Mode
Power Off → Vol Up + Power   = Recovery Mode (if set as default)

From Fastboot:
- Vol Up/Down = Navigate
- Power = Select
```

---

## Useful Properties

```bash
# Check device
getprop ro.product.device    # veux or peux
getprop ro.product.model     # 22041216G or similar

# Check Android version
getprop ro.build.version.release

# Check active slot
getprop ro.boot.slot_suffix

# Check security patch
getprop ro.build.version.security_patch
```

---

## Script Options

### partition_setup.sh

```bash
--device <codename>     # veux or peux
--dry-run              # Preview without changes
--linux-size <GB>      # Linux partition size
--windows-size <GB>    # Windows partition size
--help                 # Show help
```

### triboot.sh

```bash
android    # Boot Android
windows    # Boot Windows ARM
linux      # Boot Linux
backup     # Backup current boot
status     # Show detailed status
help       # Show help menu
```

---

## Support Channels

- **XDA Forum**: Poco X4 Pro 5G section
- **Telegram**: Poco X4 Pro development groups
- **GitHub Issues**: Querty-OS repository
- **Reddit**: r/PocoPhones

---

## Update Procedures

### Updating Android ROM

```bash
1. Backup current boot image
2. Flash new ROM in TWRP
3. Backup new boot image
4. Copy to /data/triboot/images/boot_android.img
5. Test boot before relying on it
```

### Updating Windows

```bash
# If Windows Update works:
- Updates should apply normally
- UEFI boot image usually unchanged

# Manual update:
- Flash new UEFI if available
- Copy to /data/triboot/images/boot_windows.img
```

### Updating Linux

```bash
# Package updates:
- Use distribution's package manager
- Kernel updates may need new boot.img

# Kernel update:
- Extract new boot.img
- Copy to /data/triboot/images/boot_linux.img
```

---

**Remember**: When in doubt, boot to TWRP and run `triboot status` to check your setup!
