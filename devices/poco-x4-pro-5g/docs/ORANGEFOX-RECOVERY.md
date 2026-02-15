# OrangeFox Recovery Installation Guide for Poco X4 Pro 5G

Complete step-by-step guide for installing OrangeFox Recovery on Poco X4 Pro 5G (veux/peux).

## Why OrangeFox Instead of TWRP?

OrangeFox Recovery offers superior features compared to TWRP:

✅ **Advanced Features:**
- Built-in Magisk support
- Advanced file manager with more options
- Built-in password/pattern unlock for encrypted devices
- Aromatherapy theme engine with multiple themes
- Better backup and restore options
- ADB support even when device is locked
- Built-in terminal emulator
- OTA updates support
- Built-in app installer
- Better partition management

✅ **Better UI/UX:**
- Modern Material Design interface
- Smoother animations
- Better touch response
- More intuitive navigation
- Dark mode by default

✅ **Additional Tools:**
- Automatic TWRP backup conversion
- AromaFM file manager
- Advanced wipe options
- Built-in flashlight
- Screenshot capability
- Better logging

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Download OrangeFox](#download-orangefox)
3. [Installation Methods](#installation-methods)
4. [First Boot & Setup](#first-boot--setup)
5. [Essential OrangeFox Features](#essential-orangefox-features)
6. [Backup & Restore](#backup--restore)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Requirements

- ✅ Bootloader unlocked (see main deployment guide)
- ✅ ADB and Fastboot installed
- ✅ USB debugging enabled
- ✅ Computer with USB cable
- ✅ Battery 80%+ charged
- ✅ Backup of all important data

### Verify Device

```bash
# Connect phone with USB debugging enabled
adb devices

# Check device codename
adb shell getprop ro.product.device
# Should output: veux or peux

# Check Android version
adb shell getprop ro.build.version.release
# Should output: 11, 12, or 13
```

---

## Download OrangeFox

### Official Download Links

**For Poco X4 Pro 5G (veux/peux):**

#### Primary Sources (Official)

1. **OrangeFox Official Website**
   - URL: https://orangefox.download/device/veux
   - Direct link: https://orangefox.download/release/
   - Choose: `veux` or `peux` depending on your variant

2. **SourceForge (Mirror)**
   - URL: https://sourceforge.net/projects/orangefox/files/veux/
   - Alternative: https://sourceforge.net/projects/orangefox/files/peux/

3. **GitHub Releases (Latest builds)**
   - URL: https://github.com/OrangeFoxRecovery/device_xiaomi_veux/releases
   - Check for latest stable release

#### Download the Correct Version

**File naming convention:**
```
OrangeFox-R11.1_X-Stable-veux-<date>.zip
or
OrangeFox-R11.1_X-Stable-peux-<date>.zip
```

**Example:**
```
OrangeFox-R11.1_1-Stable-veux-20231215.zip
```

#### Recommended Version

For Poco X4 Pro 5G, download:
- **Latest R11.1 Stable** (Android 12/13 base)
- File size: ~60-80 MB
- Build date: Latest available (check for most recent)

### Download Command

```bash
# Create downloads directory
mkdir -p ~/Downloads/orangefox
cd ~/Downloads/orangefox

# Method 1: Download from OrangeFox Official (replace with actual URL)
wget https://orangefox.download/releases/veux/OrangeFox-R11.1_X-Stable-veux-YYYYMMDD.zip

# Method 2: Download from SourceForge
wget https://sourceforge.net/projects/orangefox/files/veux/OrangeFox-R11.1_X-Stable-veux-YYYYMMDD.zip/download

# Verify download (should be 60-80 MB)
ls -lh OrangeFox*.zip
```

### Verify Download Integrity

```bash
# Check MD5 sum (if provided on download page)
md5sum OrangeFox-R11.1_X-Stable-veux-*.zip

# Compare with MD5 on official website
# Should match exactly
```

### Extract Recovery Image

```bash
# Extract the recovery.img from the zip
unzip OrangeFox-R11.1_X-Stable-veux-*.zip recovery.img

# Verify extraction
ls -lh recovery.img
# Should be ~60-100 MB
```

---

## Installation Methods

### Method 1: Flash via Fastboot (Recommended)

**Steps:**

1. **Boot into Fastboot Mode**

   ```bash
   # Method A: Via ADB
   adb reboot bootloader

   # Method B: Manual (phone powered off)
   # Hold Volume Down + Power button until Fastboot appears
   ```

2. **Verify Fastboot Connection**

   ```bash
   fastboot devices
   # Should show your device serial number
   ```

3. **Flash OrangeFox Recovery**

   ```bash
   # Flash recovery to recovery partition
   fastboot flash recovery recovery.img

   # Wait for "OKAY" message
   # Output should show:
   # Sending 'recovery' (XXXXX KB)    OKAY
   # Writing 'recovery'               OKAY
   # Finished. Total time: X.XXXs
   ```

4. **Boot into OrangeFox**

   ```bash
   # Method A: Via fastboot command
   fastboot reboot recovery

   # Method B: Manual
   # Hold Volume Up + Power button until OrangeFox logo appears
   ```

5. **Verification**

   - OrangeFox splash screen should appear (orange fox logo)
   - Touch screen should be responsive
   - Main menu should load with Material Design UI

### Method 2: Flash via Existing Recovery

If you already have TWRP or another recovery:

1. **Copy OrangeFox zip to device**

   ```bash
   adb push OrangeFox-R11.1_X-Stable-veux-*.zip /sdcard/
   ```

2. **Boot into existing recovery**

   ```bash
   adb reboot recovery
   ```

3. **Install from zip**
   - In TWRP: Install > Select OrangeFox zip > Swipe to flash
   - Reboot to recovery
   - OrangeFox should now load

### Method 3: Temporary Boot (Testing)

Test OrangeFox without permanently flashing:

```bash
# Boot recovery temporarily (doesn't replace existing recovery)
fastboot boot recovery.img

# OrangeFox will boot for this session only
# Useful for testing before permanent installation
```

---

## First Boot & Setup

### Initial OrangeFox Setup

1. **First Boot Screen**
   - OrangeFox splash screen (orange fox logo)
   - Loading animation
   - May take 30-60 seconds on first boot

2. **Password/Pattern Screen** (if device was encrypted)
   - Enter your device password/pattern/PIN
   - OrangeFox will decrypt /data partition
   - This is your lock screen password

3. **Main Menu**
   - Touch the screen to enter main menu
   - Orange/dark themed interface
   - Several option buttons

4. **Initial Configuration**
   - **Language**: Settings > Language (if needed)
   - **Time Zone**: Will sync from device
   - **Theme**: Settings > Theme (multiple options available)

### Essential First Steps

1. **Create Full Backup** (Immediately!)

   ```
   OrangeFox Main Menu:
   1. Tap "Backup"
   2. Select partitions:
      ✓ Boot
      ✓ System
      ✓ Data
      ✓ EFS (CRITICAL!)
      ✓ Persist
      ✓ Vendor
   3. Swipe to backup
   4. Wait for completion (10-30 minutes)
   5. Verify backup created in /Fox/Backups/
   ```

2. **Test ADB Connection**

   ```bash
   # From computer
   adb devices
   # Should show device in recovery mode

   # Test shell access
   adb shell
   # Should get root shell in OrangeFox
   ```

3. **Verify Partitions**

   ```
   OrangeFox Menu:
   1. Tap "Mount"
   2. Check available partitions:
      - System
      - Vendor
      - Data
      - Cache
      - Internal Storage
   3. All should be mountable
   ```

---

## Essential OrangeFox Features

### File Manager (AromaFM)

**Access:**
- Main Menu > File Manager
- Or swipe from right edge

**Features:**
- Navigate all partitions
- Copy/Move/Delete files
- Change permissions (chmod)
- Extract/Create archives
- Text editor
- Image viewer

**Usage Example:**
```
1. Tap "File Manager"
2. Navigate to /sdcard/
3. Long-press file for options:
   - Copy
   - Move
   - Delete
   - Permissions
   - Properties
```

### Advanced Terminal

**Access:**
- Main Menu > Terminal
- Or swipe up from bottom

**Features:**
- Full root shell access
- Command history
- Auto-completion
- Multiple tabs

**Useful Commands:**
```bash
# Check partitions
df -h

# View mounted filesystems
mount | grep /dev/block

# Check battery level
cat /sys/class/power_supply/battery/capacity

# View logs
logcat | grep -i error

# Exit terminal
exit
```

### Magisk Installation

**Built-in Magisk Support:**

1. **Install Magisk**
   ```
   OrangeFox Menu:
   1. Tap "Magisk"
   2. Select "Install Magisk"
   3. Choose version (stable/canary)
   4. Swipe to install
   5. Reboot to system
   ```

2. **Verify Magisk**
   ```bash
   # After reboot to Android
   adb shell su -c "magisk -v"
   # Should show Magisk version
   ```

### Backup Management

**Create Backups:**

```
Main Menu > Backup:

1. Name Backup:
   Format: YYYY-MM-DD_HH-MM_<name>
   Example: 2026-02-10_12-00_before-querty-os

2. Select Partitions:
   ✓ Boot (essential)
   ✓ System (optional, large)
   ✓ Data (your files)
   ✓ EFS (CRITICAL - IMEI info)
   ✓ Persist (sensors, calibration)
   ✓ Vendor (drivers)
   ✓ Userdata (internal storage)

3. Compression:
   - Enable compression (saves space)
   - Disable for faster backup

4. Storage Location:
   - Internal Storage: /Fox/Backups/
   - SD Card: /external_sd/Fox/Backups/
   - USB OTG: /usb-otg/Fox/Backups/

5. Swipe to Backup
```

**Restore Backups:**

```
Main Menu > Restore:

1. Select Backup:
   - Browse backup folders
   - Choose backup by date/name

2. Select Partitions:
   - Check what to restore
   - Can restore selective partitions

3. Swipe to Restore

4. Reboot after restore
```

### OTA Updates

**Update OrangeFox:**

```
Main Menu > Settings > OrangeFox:

1. Check for Updates
2. If available, download
3. Install automatically
4. Reboot to updated recovery
```

---

## Backup & Restore

### Critical Backups to Create

#### 1. EFS Backup (MOST IMPORTANT!)

EFS contains IMEI and radio calibration. Loss = no network!

```
Method 1: OrangeFox
1. Backup > Select only EFS
2. Name: EFS-backup-YYYYMMDD
3. Swipe to backup
4. Copy to computer immediately!

Method 2: ADB (Manual)
adb shell
dd if=/dev/block/bootdevice/by-name/modem_fs1 of=/sdcard/modem_fs1.img
dd if=/dev/block/bootdevice/by-name/modem_fs2 of=/sdcard/modem_fs2.img
dd if=/dev/block/bootdevice/by-name/fsg of=/sdcard/fsg.img
exit

# Pull to computer
adb pull /sdcard/modem_fs1.img
adb pull /sdcard/modem_fs2.img
adb pull /sdcard/fsg.img

# Store in SAFE LOCATION (multiple copies!)
```

#### 2. Persist Backup

Contains sensor calibration, fingerprint data:

```
OrangeFox:
1. Backup > Select Persist
2. Name: persist-backup-YYYYMMDD
3. Swipe to backup
4. Copy to computer
```

#### 3. Full System Backup (Before Modifications)

```
OrangeFox Full Backup:
1. Backup > Select All Partitions
2. Name: full-backup-stock-YYYYMMDD
3. Compression: Enabled
4. Swipe to backup
5. Wait 20-40 minutes (depending on data size)
6. Verify backup completed successfully
7. Copy to computer:
   adb pull /sdcard/Fox/Backups/ ~/backups/
```

### Backup Storage Locations

**Recommended Backup Strategy:**

1. **Primary**: Internal Storage (`/sdcard/Fox/Backups/`)
   - Quick access
   - Survives data wipe if external storage is mounted

2. **Secondary**: SD Card (if available)
   - Physical backup
   - Remove and store separately

3. **Tertiary**: Computer
   ```bash
   # Pull all backups to computer
   adb pull /sdcard/Fox/Backups/ ~/poco-x4-backups/

   # Verify integrity
   ls -lh ~/poco-x4-backups/
   ```

4. **Quaternary**: Cloud Storage
   - Upload EFS backup to multiple cloud services
   - Encrypt before uploading (contains IMEI)

### Verify Backups

```bash
# In OrangeFox Terminal
cd /sdcard/Fox/Backups/
ls -lh

# Check backup size (should be reasonable)
du -sh *

# Verify critical files exist
ls -la */efs.ext4.win*
ls -la */persist.ext4.win*
ls -la */boot.emmc.win*
```

---

## Troubleshooting

### Common Issues

#### Issue 1: OrangeFox Won't Boot

**Symptoms**: Black screen, stuck at logo, bootloop

**Solutions:**

1. **Re-flash Recovery**
   ```bash
   # Boot to fastboot
   fastboot reboot bootloader

   # Re-flash
   fastboot flash recovery recovery.img
   fastboot reboot recovery
   ```

2. **Check Recovery Partition**
   ```bash
   # Verify partition exists
   fastboot getvar all | grep recovery
   ```

3. **Try Different Build**
   - Download different OrangeFox version
   - Try older stable build
   - Or try TWRP temporarily

#### Issue 2: Touch Screen Not Working

**Solutions:**

1. **Use Volume Buttons**
   - Volume Down: Move selection down
   - Volume Up: Move selection up
   - Power: Confirm selection

2. **Calibrate Touch**
   ```
   Settings > Touch > Calibrate Touch
   ```

3. **Re-flash with Newer Build**
   - Newer builds have better touch support

#### Issue 3: Can't Decrypt /data

**Symptoms**: Password doesn't work, stuck at decryption

**Solutions:**

1. **Ensure Correct Password**
   - Use device lock screen password/PIN/pattern
   - Try default PIN if forgotten

2. **Disable Encryption** (Last Resort - WIPES DATA!)
   ```
   WARNING: This erases everything!

   Main Menu > Wipe > Format Data
   Type: yes
   Swipe to format

   This removes encryption
   ```

3. **Check Android Version Compatibility**
   - OrangeFox must match Android version
   - Android 13 device needs Android 13-based OrangeFox

#### Issue 4: ADB Not Working in Recovery

**Solutions:**

1. **Enable ADB in OrangeFox**
   ```
   Settings > Enable ADB
   Swipe to enable
   ```

2. **Reconnect USB**
   ```bash
   # On computer
   adb kill-server
   adb start-server
   adb devices
   ```

3. **Check USB Cable**
   - Use different USB port
   - Try different cable
   - Avoid USB hubs

#### Issue 5: Installation Failed

**Error**: "Failed to mount /system" or similar

**Solutions:**

1. **Wipe Cache**
   ```
   Wipe > Advanced Wipe > Cache
   Swipe to wipe
   ```

2. **Check Partitions**
   ```
   Mount > Deselect all > Select needed partitions
   ```

3. **Repair File System**
   ```
   Advanced > File Manager > Long-press partition
   > Repair or Change File System
   ```

#### Issue 6: Cannot Access Internal Storage

**Solutions:**

1. **Mount Internal Storage**
   ```
   Mount > Enable MTP
   ```

2. **In OrangeFox Terminal**
   ```bash
   mount -a
   ls /sdcard/
   ```

3. **Check from Computer**
   ```bash
   adb shell ls /sdcard/
   adb push file.zip /sdcard/
   ```

### Emergency Recovery

#### If OrangeFox Breaks Your Device:

1. **Boot to Fastboot**
   ```
   Power off > Hold Vol Down + Power
   ```

2. **Flash Stock Boot Image**
   ```bash
   # Download stock boot.img for your ROM
   fastboot flash boot boot.img
   fastboot reboot
   ```

3. **Flash Different Recovery**
   ```bash
   # Try TWRP or other recovery
   fastboot flash recovery twrp.img
   fastboot reboot recovery
   ```

4. **Restore from Backup**
   ```
   In new recovery > Restore > Select backup
   ```

5. **Last Resort: Flash Stock ROM**
   - Use Mi Flash Tool
   - Flash complete stock ROM
   - Start over

---

## Advanced Features

### Themes

**Change OrangeFox Theme:**

```
Settings > Theme:
- OrangeFox (default)
- TWRP
- Red Fox
- Material Dark
- Custom themes (install from zip)
```

### Add-ons

**Install OrangeFox Add-ons:**

1. Download add-ons from OrangeFox website
2. Flash in OrangeFox like any zip
3. Available add-ons:
   - Additional themes
   - Extra tools
   - Language packs

### Partition Management

**Advanced Partition Operations:**

```
Advanced > Partition Manager:
- Resize partitions (be careful!)
- Change file system
- Repair file systems
- Create new partitions (advanced users only)
```

---

## Integration with Querty-OS

### OrangeFox for Querty-OS Setup

**Advantages:**

1. Better backup management (important for snapshots)
2. Advanced file manager (manage Querty-OS files)
3. Built-in Magisk (if needed for Querty-OS)
4. Better terminal (for debugging)
5. OTA support (future Querty-OS updates)

**Recommended Workflow:**

```
1. Install OrangeFox (this guide)
2. Create full backup
3. Setup tri-boot partitions (see main guide)
4. Install Querty-OS components
5. Use OrangeFox for:
   - Creating snapshots before updates
   - Restoring if issues occur
   - Managing boot configurations
   - Installing updates
```

### Tri-Boot with OrangeFox

OrangeFox works perfectly with tri-boot setup:

```
1. Use OrangeFox to:
   - Backup each OS separately
   - Switch boot images
   - Manage partition layouts
   - Flash OS updates

2. Create separate backups:
   - Android OS backup
   - Linux partition backup
   - Wine/Windows backup
   - Querty-OS config backup
```

---

## Resources

### Official Links

- **OrangeFox Website**: https://orangefox.download/
- **OrangeFox Telegram**: https://t.me/OrangeFoxRecovery
- **GitHub**: https://github.com/OrangeFoxRecovery
- **XDA Thread**: Search "OrangeFox Poco X4 Pro" on XDA Forums

### Poco X4 Pro 5G Specific

- **Device Tree**: https://github.com/OrangeFoxRecovery/device_xiaomi_veux
- **Telegram Group**: https://t.me/pocox4pro5g
- **XDA Forum**: https://forum.xda-developers.com/f/poco-x4-pro-5g.12615/

### Documentation

- **OrangeFox Wiki**: https://wiki.orangefox.tech/
- **Building Guide**: https://wiki.orangefox.tech/en/dev/building
- **FAQ**: https://wiki.orangefox.tech/en/faq

---

## Comparison: OrangeFox vs TWRP

| Feature | OrangeFox | TWRP |
|---------|-----------|------|
| UI Design | Modern Material Design | Basic Touch UI |
| Built-in Magisk | ✅ Yes | ❌ No (manual) |
| File Manager | Advanced (AromaFM) | Basic |
| Password Support | Excellent | Basic |
| Themes | Multiple built-in | Limited |
| Terminal | Advanced with tabs | Basic |
| ADB Support | Better (works when locked) | Standard |
| Backup Compression | Better algorithms | Standard |
| OTA Updates | ✅ Yes | ❌ No |
| Screenshot | ✅ Yes | ❌ No |
| Flashlight | ✅ Yes | ❌ No |
| App Installer | ✅ Built-in | ❌ No |
| Boot Slot Switch | Easy one-tap | Manual |
| Log Viewer | Enhanced | Basic |
| Performance | Optimized | Standard |

**Winner**: OrangeFox for most users ✅

---

## Next Steps

After installing OrangeFox:

1. ✅ **Create comprehensive backups** (EFS, persist, full system)
2. ✅ **Copy backups to computer** (multiple locations)
3. ✅ **Test OrangeFox features** (file manager, terminal, ADB)
4. ✅ **Proceed to main deployment guide** (POCO_X4_PRO_DEPLOYMENT.md)
5. ✅ **Setup tri-boot** (using OrangeFox)
6. ✅ **Install Querty-OS** (with OrangeFox's help)

---

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Join OrangeFox Telegram group
3. Search XDA Poco X4 Pro forums
4. Create issue on OrangeFox GitHub
5. Join Querty-OS community

**Remember**: Always have backups before proceeding with any modifications!

---

**Guide Version**: 1.0
**Last Updated**: 2026-02-10
**Device**: Poco X4 Pro 5G (veux/peux)
**Recovery**: OrangeFox R11.1+

**Status**: ✅ Production Ready
