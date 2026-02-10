# Poco X4 Pro 5G Tri-Boot Installation Guide

Complete step-by-step guide for setting up tri-boot on Poco X4 Pro 5G (veux/peux).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Preparation](#phase-1-preparation)
3. [Phase 2: Backup Critical Partitions](#phase-2-backup-critical-partitions)
4. [Phase 3: Partition Setup](#phase-3-partition-setup)
5. [Phase 4: Install Operating Systems](#phase-4-install-operating-systems)
6. [Phase 5: Setup Tri-Boot Script](#phase-5-setup-tri-boot-script)
7. [Usage](#usage)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Hardware
- Poco X4 Pro 5G (veux/peux) with **unlocked bootloader**
- High-quality USB cable
- PC with ADB and Fastboot tools
- Minimum 128GB storage (256GB recommended)

### Required Software
- Modified TWRP/OrangeFox recovery (with parted utility)
- Stock MIUI ROM (for recovery)
- MiFlash tool (for emergency recovery)
- ADB and Fastboot drivers

### Required Knowledge
- Experience with Android flashing
- Understanding of partition tables
- Familiarity with command-line tools
- Awareness of risks involved

### Check Bootloader Status
```bash
# Boot to fastboot mode: Power Off → Hold Vol Down + Power
# On PC:
fastboot oem device-info
```

Should show: `Device unlocked: true`

---

## Phase 1: Preparation

### Step 1.1: Download Required Files

1. **Modified TWRP Recovery**
   - Search XDA Forums for veux/peux TWRP
   - Ensure it includes `parted` utility
   - Recommended: OrangeFox or TWRP 3.7+

2. **Stock Firmware**
   - Download from Xiaomi Firmware site
   - Keep Fastboot ROM version handy
   - Store on PC for emergency recovery

3. **OS Images** (to be obtained later):
   - Android ROM (LineageOS, PixelOS, etc.)
   - Windows ARM UEFI (if available for SD695)
   - Linux distribution (postmarketOS, if ported)

### Step 1.2: Backup Android Data

```bash
# From Android with root
su
# Backup important data
tar -czf /sdcard/android_backup.tar.gz /data/media/0/DCIM /data/media/0/Documents

# Or use ADB
adb backup -all -apk -shared -f backup.ab
```

**Also backup:**
- Photos and videos
- App data (Titanium Backup, Swift Backup)
- SMS/Call logs
- Contacts (export to Google/VCF)

### Step 1.3: Prepare Tools on PC

```bash
# Verify ADB/Fastboot
adb version
fastboot --version

# Test connection
adb devices
```

---

## Phase 2: Backup Critical Partitions

### Step 2.1: Boot to TWRP

```bash
# From Android
adb reboot recovery

# Or from Fastboot
fastboot boot twrp.img
```

### Step 2.2: Transfer Backup Script

```bash
# On PC
cd path/to/Querty-OS/devices/poco-x4-pro-5g
adb push scripts/backup_partitions.sh /sdcard/
```

### Step 2.3: Run Backup Script

In TWRP Terminal (Advanced → Terminal):

```bash
sh /sdcard/backup_partitions.sh
```

**This will backup:**
- boot_a, boot_b (boot partitions)
- dtbo_a, dtbo_b (device tree)
- vbmeta partitions (all variants)
- modemst1, modemst2, fsg, fsc (CRITICAL!)
- persist (sensor calibration, etc.)
- metadata, misc

### Step 2.4: Copy Backups to PC

```bash
# On PC - this may take several minutes
adb pull /sdcard/triboot_backup_YYYYMMDD_HHMMSS ./backup_poco_x4_pro
```

### Step 2.5: Verify Backups

```bash
cd backup_poco_x4_pro
sh verify_backup.sh
```

**IMPORTANT:**
- Store backups in multiple locations
- Copy to external USB drive
- Upload to cloud storage
- Verify checksums after copying

---

## Phase 3: Partition Setup

### Step 3.1: Preview Partition Changes

```bash
# In TWRP Terminal
sh /sdcard/scripts/partition_setup.sh --device veux --dry-run
```

Review the planned layout:
- ESP: 1GB (Windows EFI)
- Windows: 50GB (adjustable)
- Linux: 20GB (adjustable)
- Android: Remaining space

### Step 3.2: Adjust Partition Sizes (Optional)

```bash
# Custom sizes
sh /sdcard/scripts/partition_setup.sh --device veux \
  --windows-size 40 \
  --linux-size 30 \
  --dry-run
```

### Step 3.3: Apply Partition Changes

⚠️ **POINT OF NO RETURN** - This erases all data!

```bash
sh /sdcard/scripts/partition_setup.sh --device veux
```

Confirmation prompts:
1. Type: `YES I UNDERSTAND`
2. Type: `DESTROY DATA`

Process takes 5-10 minutes.

### Step 3.4: Reboot to TWRP

```bash
reboot recovery
```

Verify partitions in TWRP:
- Mount → Select partitions
- Advanced → Terminal → `parted /dev/block/sda print`

---

## Phase 4: Install Operating Systems

### Step 4.1: Install Android ROM

1. **Format Data** (if not already done):
   - Wipe → Format Data
   - Type "yes" to confirm

2. **Flash Android ROM**:
   ```bash
   # Copy ROM to device
   adb push lineageos-20-veux.zip /sdcard/

   # In TWRP
   # Install → Select ROM → Swipe to Flash
   # Flash GApps (optional)
   # Flash Magisk/KernelSU (for root)
   ```

3. **Backup Android Boot Image**:
   ```bash
   # Boot to Android
   # With root access
   su
   dd if=/dev/block/by-name/boot of=/sdcard/boot_android.img bs=4M
   ```

4. **Copy to triboot location**:
   ```bash
   # In TWRP Terminal or rooted Android
   mkdir -p /data/triboot/images
   cp /sdcard/boot_android.img /data/triboot/images/
   ```

### Step 4.2: Install Windows ARM (Experimental)

⚠️ **Note**: Windows ARM on SD695 is highly experimental!

1. **Check for UEFI availability**:
   - Search for Renegade Project UEFI for veux/peux
   - Windows support may be limited

2. **If UEFI is available**:
   ```bash
   # Format ESP and Windows partitions
   mkfs.vfat -F 32 /dev/block/by-name/esp
   # NTFS formatting may require Windows or special tools
   
   # Mount partitions
   mkdir -p /mnt/esp /mnt/win
   mount /dev/block/by-name/esp /mnt/esp
   mount /dev/block/by-name/win /mnt/win
   
   # Copy UEFI files to ESP
   # Copy Windows ARM files to win partition
   # (Follow Renegade Project instructions)
   ```

3. **Copy UEFI boot image**:
   ```bash
   cp /sdcard/uefi_boot.img /data/triboot/images/boot_windows.img
   ```

### Step 4.3: Install Linux

⚠️ **Note**: Linux support for veux/peux may be limited

If postmarketOS or Ubuntu Touch is available:

1. **Format Linux partition**:
   ```bash
   mkfs.ext4 -L "Linux" /dev/block/by-name/linux
   ```

2. **Install Linux rootfs**:
   ```bash
   mkdir -p /mnt/linux
   mount /dev/block/by-name/linux /mnt/linux
   
   # Extract rootfs
   tar -xzf postmarketos-veux.tar.gz -C /mnt/linux
   
   # Or use dd for image files
   dd if=ubuntu-touch-veux.img of=/dev/block/by-name/linux bs=4M
   ```

3. **Copy Linux boot image**:
   ```bash
   cp /sdcard/pmos_boot.img /data/triboot/images/boot_linux.img
   ```

---

## Phase 5: Setup Tri-Boot Script

### Step 5.1: Install Triboot Script

```bash
# Copy script to device
adb push scripts/triboot.sh /sdcard/

# In TWRP Terminal
mkdir -p /data/triboot/scripts
cp /sdcard/triboot.sh /data/triboot/scripts/
chmod +x /data/triboot/scripts/triboot.sh

# Create symlink for easy access
ln -s /data/triboot/scripts/triboot.sh /sbin/triboot
```

### Step 5.2: Verify Setup

```bash
# In TWRP Terminal
triboot status
```

Should show:
- Device detected
- Boot images present
- Partition status

---

## Usage

### Switching Between OSes

#### From TWRP Recovery

```bash
# Boot to TWRP
adb reboot recovery

# In TWRP Terminal
triboot           # Show menu
triboot android   # Boot to Android
triboot windows   # Boot to Windows ARM
triboot linux     # Boot to Linux
```

#### From Android (with Root)

```bash
# Via Terminal Emulator or ADB Shell
su
/data/triboot/scripts/triboot.sh android
# Device will reboot to Android

# Or use Tasker/Termux for automation
```

### Daily Workflow

1. **Primary OS (Android)**:
   - Boot normally
   - To switch: Reboot to TWRP → run triboot

2. **Windows/Linux**:
   - Reboot to TWRP
   - Run triboot script
   - Select desired OS

---

## Troubleshooting

### Device Won't Boot

**Symptom**: Stuck at boot logo or bootloop

**Solution**:
```bash
# Method 1: Boot to TWRP
# Hold Vol Down + Power → Select Recovery
# In Terminal:
dd if=/data/triboot/images/boot_android.img of=/dev/block/by-name/boot
reboot

# Method 2: From Fastboot
fastboot flash boot boot_stock.img
fastboot reboot
```

### No Cellular/Modem Not Working

**Symptom**: No network, "No SIM", emergency calls only

**Solution - Restore Modem Partitions**:
```bash
# In TWRP
dd if=/sdcard/backup/modemst1.img of=/dev/block/by-name/modemst1
dd if=/sdcard/backup/modemst2.img of=/dev/block/by-name/modemst2
dd if=/sdcard/backup/fsg.img of=/dev/block/by-name/fsg
dd if=/sdcard/backup/fsc.img of=/dev/block/by-name/fsc
reboot
```

### TWRP Not Accessible

**Symptom**: Can't boot to TWRP

**Solution**:
```bash
# From Fastboot
fastboot flash recovery twrp.img
fastboot reboot recovery
```

### Partition Not Found

**Symptom**: Script can't find esp/win/linux partitions

**Solution**:
```bash
# Verify partitions exist
parted /dev/block/sda print

# Check partition links
ls -la /dev/block/by-name/

# Re-run partition setup if needed
```

### Windows Won't Boot / BSOD

**Symptom**: Blue screen or boot failure

**Possible Causes**:
- Incorrect UEFI for SD695
- Missing drivers
- Corrupted Windows installation

**Solution**:
- Verify UEFI version matches device
- Reinstall Windows
- Check Renegade Project forums

### Linux Kernel Panic

**Symptom**: Linux won't boot, kernel panic

**Possible Causes**:
- Wrong kernel for veux/peux
- Missing device tree
- Root filesystem issues

**Solution**:
- Verify kernel compatibility
- Check boot.img matches device
- Verify rootfs is properly installed

---

## Advanced: Manual Recovery

### Complete Wipe and Restore

If all else fails:

```bash
# 1. Boot to Fastboot
# Power Off → Hold Vol Down + Power

# 2. Flash Stock ROM via MiFlash
# Use "clean all" option
# This will restore all partitions

# 3. Unlock bootloader again (if locked)
# 4. Flash TWRP
# 5. Start over from Phase 1
```

### Restore Individual Partitions

```bash
# In TWRP Terminal
dd if=/sdcard/backup/boot_a.img of=/dev/block/by-name/boot_a
dd if=/sdcard/backup/boot_b.img of=/dev/block/by-name/boot_b
# Repeat for other partitions as needed
```

---

## Tips and Best Practices

1. **Keep Backups Updated**:
   - Backup boot image after ROM updates
   - Keep modem backups safe
   - Regular TWRP backups

2. **OS Updates**:
   - Android: Update normally, backup boot after
   - Windows: OTA updates may work
   - Linux: Follow distro-specific procedures

3. **Storage Management**:
   - Keep files on microSD card
   - Use Android's adopted storage
   - Don't fill partitions completely

4. **Performance**:
   - Some OSes may have battery drain
   - Not all hardware features work in all OSes
   - Camera/sensors may not work in Windows/Linux

---

## Support and Resources

- **XDA Forums**: Search for Poco X4 Pro 5G (veux/peux)
- **Telegram Groups**: Poco X4 Pro development groups
- **GitHub**: File issues on Querty-OS repository
- **Querty-OS Docs**: Main project documentation

---

## Credits

- Inspired by [Poco F1 tri-boot](https://github.com/orailnoor/poco-f1-tri-boot)
- Poco X4 Pro 5G developers and community
- Project Renegade / WOA Project
- postmarketOS team

---

**Remember**: Always maintain backups, understand the risks, and have a recovery plan!
