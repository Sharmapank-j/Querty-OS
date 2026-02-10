# Querty-OS Deployment Guide for Poco X4 Pro 5G

Complete step-by-step guide for installing Querty-OS on Poco X4 Pro 5G (veux/peux) after successful sandbox testing.

## ⚠️ IMPORTANT WARNINGS

**READ CAREFULLY BEFORE PROCEEDING:**

1. ⚠️ **Unlocking bootloader WILL ERASE ALL DATA**
2. ⚠️ **This process VOIDS WARRANTY**
3. ⚠️ **Risk of bricking device if not followed correctly**
4. ⚠️ **Backup EVERYTHING before starting**
5. ⚠️ **Ensure battery is 80%+ charged**
6. ⚠️ **Have a backup phone available**

**ONLY PROCEED IF:**
- ✅ You completed sandbox testing successfully
- ✅ All tests passed in virtual environment
- ✅ You understand the risks
- ✅ You have backups of important data
- ✅ You accept potential device damage

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Sandbox Testing](#phase-1-sandbox-testing-mandatory)
3. [Phase 2: Device Preparation](#phase-2-device-preparation)
4. [Phase 3: Bootloader Unlock](#phase-3-bootloader-unlock)
5. [Phase 4: Custom Recovery](#phase-4-custom-recovery-twrp)
6. [Phase 5: Backup Everything](#phase-5-backup-everything)
7. [Phase 6: Tri-Boot Setup](#phase-6-tri-boot-setup)
8. [Phase 7: Querty-OS Installation](#phase-7-querty-os-installation)
9. [Phase 8: Configuration & Testing](#phase-8-configuration--testing)
10. [Troubleshooting](#troubleshooting)
11. [Recovery & Rollback](#recovery--rollback)

---

## Prerequisites

### Required Hardware

- **Poco X4 Pro 5G** (codename: veux or peux)
- **USB Cable** (high quality, data transfer capable)
- **Computer** (Linux recommended, Windows/Mac also work)
- **Backup Phone** (in case of issues)
- **SD Card** (optional, for backups)

### Required Software

```bash
# On Linux
sudo apt install -y \
    android-tools-adb \
    android-tools-fastboot \
    python3 \
    python3-pip \
    git

# Verify installation
adb version
fastboot --version
```

### Device Information

**Poco X4 Pro 5G Specifications:**
- **Codename**: veux (Global) / peux (India)
- **SoC**: Qualcomm Snapdragon 695 5G (SM6375)
- **RAM**: 6GB / 8GB
- **Storage**: 128GB / 256GB
- **Android**: 11/12/13 (MIUI 13/14)

### Verify Device Codename

```bash
# Enable USB debugging on phone (Settings > About > Tap MIUI version 7 times > Developer options > USB debugging)
adb devices
adb shell getprop ro.product.device
# Should output: veux or peux
```

---

## Phase 1: Sandbox Testing (MANDATORY)

**DO NOT SKIP THIS STEP!**

Before touching your device, complete ALL sandbox tests:

```bash
cd /path/to/Querty-OS

# 1. Run comprehensive sandbox tests
bash virtualization/sandbox/test-sandbox.sh

# 2. Test in Docker
docker-compose up querty-os
docker exec querty-os python3 scripts/dashboard.py

# 3. Verify priority system
python3 -c "
from core.priority import StoragePriorityManager
mgr = StoragePriorityManager(128)  # Your device storage in GB
print(mgr.suggest_partition_sizes())
"

# 4. Run all unit tests
make test

# 5. Validate device scripts
bash -n devices/poco-x4-pro-5g/scripts/triboot.sh
bash -n devices/poco-x4-pro-5g/scripts/partition_setup.sh
```

**✅ Only proceed if ALL tests pass**

---

## Phase 2: Device Preparation

### 2.1 Enable Developer Options

1. Go to **Settings** > **About phone**
2. Tap **MIUI version** 7 times
3. Go back to **Settings** > **Additional settings** > **Developer options**

### 2.2 Enable Required Settings

Enable the following in Developer options:
- ✅ **OEM unlocking**
- ✅ **USB debugging**
- ✅ **USB debugging (Security settings)**
- ✅ **Install via USB**

### 2.3 Backup Your Data

**CRITICAL: Backup everything NOW**

```bash
# Create backup directory
mkdir -p ~/poco-x4-backup
cd ~/poco-x4-backup

# Backup photos, videos
adb pull /sdcard/DCIM ./DCIM

# Backup downloads
adb pull /sdcard/Download ./Download

# Backup WhatsApp (if applicable)
adb pull /sdcard/WhatsApp ./WhatsApp

# Backup app data (requires root)
adb backup -all -apk -shared -system

# Alternative: Use Xiaomi Cloud backup
# Settings > About phone > Backup & restore
```

### 2.4 Charge Battery

- Charge to **80%+**
- Keep charger connected during process

---

## Phase 3: Bootloader Unlock

### 3.1 Request Unlock Permission

1. Go to https://en.miui.com/unlock/
2. Sign in with Mi Account
3. Apply for unlock permission
4. **Wait 7-168 hours** (depending on device age)

### 3.2 Download Mi Unlock Tool

Download from: https://en.miui.com/unlock/download_en.html

### 3.3 Boot to Fastboot Mode

```bash
# Method 1: Via ADB
adb reboot bootloader

# Method 2: Manual
# Power off device
# Hold Power + Volume Down until Fastboot logo appears
```

### 3.4 Unlock Bootloader

**⚠️ THIS WILL ERASE ALL DATA**

1. Connect device to PC (in fastboot mode)
2. Run Mi Unlock Tool
3. Sign in with Mi Account
4. Click "Unlock"
5. Wait for process to complete
6. Device will reboot (takes 5-10 minutes)

```bash
# Verify unlock status
fastboot oem device-info
# Should show: Device unlocked: true
```

### 3.5 First Boot After Unlock

- Device will boot normally (takes longer first time)
- Go through setup wizard (optional, we'll wipe again later)
- Re-enable Developer options and USB debugging

---

## Phase 4: Custom Recovery (TWRP)

### 4.1 Download TWRP

Download latest TWRP for veux/peux:
```bash
# Visit: https://twrp.me/xiaomi/xiaomipocox4pro5g.html
# Or from: https://sourceforge.net/projects/twrp-for-veux/

wget https://sourceforge.net/projects/twrp-for-veux/files/latest/download -O twrp-veux.img
```

### 4.2 Boot TWRP (Temporary)

```bash
# Boot to fastboot
adb reboot bootloader

# Boot TWRP temporarily (don't flash yet)
fastboot boot twrp-veux.img

# Device will boot into TWRP recovery
```

### 4.3 Install TWRP Permanently

**In TWRP:**
1. Tap **Advanced** > **ADB Sideload**
2. Swipe to start sideload

```bash
# On PC
adb sideload twrp-veux.img
```

Or install via fastboot:
```bash
fastboot flash recovery twrp-veux.img
fastboot reboot recovery
```

---

## Phase 5: Backup Everything

**In TWRP Recovery:**

### 5.1 Backup Critical Partitions

1. Tap **Backup**
2. Select:
   - ✅ Boot
   - ✅ System
   - ✅ Vendor
   - ✅ Data
   - ✅ EFS (IMPORTANT!)
   - ✅ Persist (IMPORTANT!)
3. Swipe to backup
4. Wait for completion (30-60 minutes)

### 5.2 Copy Backup to PC

```bash
# In TWRP, mount Data partition
# Then on PC:
adb pull /data/media/0/TWRP/BACKUPS ~/poco-x4-backup/twrp/
```

### 5.3 Backup via Device Scripts

```bash
# Push our backup script to device
adb push devices/poco-x4-pro-5g/scripts/backup_partitions.sh /tmp/

# Execute in TWRP terminal or via ADB shell
adb shell "chmod +x /tmp/backup_partitions.sh"
adb shell "/tmp/backup_partitions.sh"

# Pull backups
adb pull /tmp/partition_backups ~/poco-x4-backup/partitions/
```

**⚠️ CRITICAL**: Store backups safely (external drive, cloud, etc.)

---

## Phase 6: Tri-Boot Setup

### 6.1 Understand Partition Layout

Poco X4 Pro 5G uses A/B partitioning:
- Slot A: Primary OS
- Slot B: Secondary OS (we'll use for Linux/Windows)

**Default Partitions:**
```
/dev/block/sda - User data (128GB or 256GB)
├── boot_a/boot_b - Kernel
├── system_a/system_b - Android system
├── vendor_a/vendor_b - Vendor files
└── userdata - User data
```

**Our Tri-Boot Layout:**
```
Total: 128GB (adjust based on your device)

AI & System:      51.2GB (40%)  - Highest priority
Android:          44.8GB (35%)  - Second priority
Linux:            19.2GB (15%)  - Third priority
Windows (Wine):   12.8GB (10%)  - Lowest priority
```

### 6.2 Partition Setup

```bash
# Push partition setup script
adb push devices/poco-x4-pro-5g/scripts/partition_setup.sh /tmp/
adb push devices/poco-x4-pro-5g/scripts/triboot.sh /tmp/

# Execute (in TWRP terminal or via ADB)
adb shell "chmod +x /tmp/partition_setup.sh"
adb shell "/tmp/partition_setup.sh --dry-run"

# Review output, then execute for real
adb shell "/tmp/partition_setup.sh --execute"
```

### 6.3 Install ROMs

**6.3.1 Android ROM (Evolution OS or GrapheneOS)**

Download Evolution OS for veux:
```bash
wget https://sourceforge.net/projects/evolution-x/files/veux/latest/download -O evo-veux.zip
```

Install in TWRP:
1. **Wipe** > **Advanced Wipe** > Select: System, Data, Cache, Dalvik
2. **Install** > Select evo-veux.zip
3. **Reboot** > **Recovery** (don't boot to system yet)

**6.3.2 Linux Setup (Ubuntu Touch or PostmarketOS)**

```bash
# Download Ubuntu Touch or PostmarketOS for ARM64
# Or use debootstrap to create minimal Ubuntu

# Push to device
adb push ubuntu-arm64.tar.gz /tmp/

# Extract to Linux partition
adb shell "
cd /data/linux
tar xzf /tmp/ubuntu-arm64.tar.gz
"
```

**6.3.3 Windows (Wine setup)**

```bash
# Wine will be installed on Linux partition
# Windows apps run through Wine
# Setup done in Phase 7
```

---

## Phase 7: Querty-OS Installation

### 7.1 Boot to Android

1. Reboot to system
2. Complete setup wizard
3. Enable Developer options
4. Enable USB debugging
5. Root device (use Magisk if needed)

### 7.2 Push Querty-OS Files

```bash
cd /path/to/Querty-OS

# Root ADB
adb root

# Create directories with priority-based layout
adb shell "
mkdir -p /data/querty-os
mkdir -p /data/querty-ai
mkdir -p /data/querty-android
mkdir -p /data/querty-linux
mkdir -p /data/querty-windows
mkdir -p /data/querty-snapshots
"

# Push all files
adb push . /data/querty-os/

# Set permissions
adb shell "
cd /data/querty-os
chmod -R 755 .
chmod +x scripts/boot/*.sh
chmod +x scripts/utils/*.sh
chmod +x devices/poco-x4-pro-5g/scripts/*.sh
"
```

### 7.3 Install Dependencies

```bash
# Install Termux (from F-Droid or GitHub)
# Or use Linux chroot

# In Termux or via ADB:
adb shell "
cd /data/querty-os

# Install Python packages
pip3 install -r requirements.txt
pip3 install -e .
"
```

### 7.4 Configure Querty-OS

```bash
adb shell "
cd /data/querty-os

# Edit configuration
vi config/querty-os.conf

# Update device-specific settings:
# device_model=poco-x4-pro-5g
# device_codename=veux
# total_storage=128  # Or 256
# ai_priority=40
# android_priority=35
# linux_priority=15
# windows_priority=10
"
```

### 7.5 Setup Boot Integration

```bash
# Install as system service (requires root)
adb shell "
cd /data/querty-os

# Copy boot script
cp scripts/boot/init-querty.sh /system/bin/querty-init

# Create init.d script
cat > /system/etc/init.d/99-querty <<'EOF'
#!/system/bin/sh
# Start Querty-OS daemon on boot
/system/bin/querty-init &
EOF

chmod 755 /system/etc/init.d/99-querty
"
```

### 7.6 Setup Tri-Boot Selector

```bash
adb shell "
cd /data/querty-os/devices/poco-x4-pro-5g

# Install tri-boot selector
cp scripts/triboot.sh /system/bin/triboot
chmod +x /system/bin/triboot

# Test tri-boot
triboot --status
"
```

---

## Phase 8: Configuration & Testing

### 8.1 Initial Test

```bash
# Start daemon manually
adb shell "/data/querty-os/scripts/boot/init-querty.sh"

# Check status
adb shell "python3 /data/querty-os/scripts/dashboard.py"

# View logs
adb shell "tail -f /var/log/querty-ai-daemon.log"
# Or via logcat:
adb logcat | grep querty
```

### 8.2 Test Priority System

```bash
adb shell "
cd /data/querty-os
python3 -c '
from core.priority import StoragePriorityManager
mgr = StoragePriorityManager(128)
print(mgr.suggest_partition_sizes())
'
"
```

Expected output:
```
AI:      51.2 GB at /data/querty-ai
Android: 44.8 GB at /data/querty-android
Linux:   19.2 GB at /data/querty-linux
Windows: 12.8 GB at /data/querty-windows
```

### 8.3 Test Tri-Boot

```bash
# Switch to Linux
adb shell "triboot --os linux"

# Device will reboot to Linux

# Switch back to Android
# (from Linux terminal)
/data/querty-os/devices/poco-x4-pro-5g/scripts/triboot.sh --os android

# Switch to Windows (Wine)
adb shell "triboot --os windows"
```

### 8.4 Test AI Daemon

```bash
adb shell "
cd /data/querty-os

# Test LLM service
python3 -c '
from core.llm_service.llm_service import LLMService
llm = LLMService()
print(llm.get_mode())
'

# Test input handlers
python3 -c '
from core.input_handlers.input_handlers import InputHandlerManager
mgr = InputHandlerManager()
print(mgr.get_available_handlers())
'
"
```

### 8.5 Test Snapshot System

```bash
adb shell "
cd /data/querty-os

# Create manual snapshot
python3 -c '
from core.snapshot_system.snapshot_system import SnapshotSystem
ss = SnapshotSystem()
ss.create_snapshot(\"test-snapshot\", \"manual\")
print(ss.list_snapshots())
'
"
```

### 8.6 Create First Snapshot

```bash
# Create "known good" snapshot
adb shell "
cd /data/querty-os
python3 -c '
from core.snapshot_system.snapshot_system import SnapshotSystem
ss = SnapshotSystem()
ss.create_snapshot(\"first-boot-working\", \"manual\")
ss.mark_as_known_good(\"first-boot-working\")
'
"
```

---

## Troubleshooting

### Device Won't Boot

**Solution: Boot to recovery**
```bash
# Force recovery boot
# Power off device
# Hold Power + Volume Up
# Or: adb reboot recovery
```

**Restore from backup:**
1. Boot TWRP
2. Restore > Select backup
3. Select partitions to restore
4. Swipe to restore

### Bootloop After Installation

**Solution: Clear cache**
```bash
# In TWRP
# Wipe > Advanced Wipe > Cache + Dalvik
# Reboot
```

### ADB Not Working

```bash
# Kill and restart ADB server
adb kill-server
adb start-server
adb devices

# Check USB connection
# Try different USB port/cable
```

### Permission Denied Errors

```bash
# Ensure device is rooted
adb root

# If not rooted, install Magisk:
# Flash magisk.zip in TWRP
```

### Tri-Boot Not Working

```bash
# Verify scripts
adb shell "ls -l /system/bin/triboot"

# Check logs
adb shell "cat /tmp/triboot.log"

# Re-push scripts
adb push devices/poco-x4-pro-5g/scripts/triboot.sh /system/bin/triboot
adb shell "chmod +x /system/bin/triboot"
```

### Storage Partitions Wrong Size

```bash
# Check actual storage
adb shell "df -h"

# Recalculate with correct size
adb shell "
cd /data/querty-os
python3 -c '
from core.priority import StoragePriorityManager
# Use your actual storage size
mgr = StoragePriorityManager(128)  # or 256
print(mgr.suggest_partition_sizes())
'
"
```

---

## Recovery & Rollback

### Quick Recovery

**Boot to working snapshot:**
```bash
adb shell "
cd /data/querty-os
python3 -c '
from core.snapshot_system.snapshot_system import SnapshotSystem
ss = SnapshotSystem()
ss.rollback_to_snapshot(\"first-boot-working\")
'
"
```

### Full System Restore

**From TWRP backup:**
1. Boot to TWRP recovery
2. **Restore**
3. Select backup date
4. Select partitions
5. Swipe to restore
6. Reboot

### Flash Stock ROM

**If everything fails:**
1. Download stock MIUI ROM for veux/peux from: https://xiaomifirmwareupdater.com/
2. Use Mi Flash Tool to flash: https://xiaomirom.com/download-xiaomi-flash-tool/
3. Start over (data will be lost)

### Restore from Partition Backup

```bash
# Boot to TWRP
# Push backup files
adb push ~/poco-x4-backup/partitions/* /tmp/

# Restore (example for boot partition)
adb shell "
dd if=/tmp/boot.img of=/dev/block/by-name/boot_a
dd if=/tmp/boot.img of=/dev/block/by-name/boot_b
"

# Reboot
adb reboot
```

---

## Post-Installation

### Daily Usage

```bash
# Switch OS
triboot --os linux     # Boot to Linux
triboot --os android   # Boot to Android
triboot --os windows   # Boot to Windows (Wine)

# Check system status
python3 /data/querty-os/scripts/dashboard.py

# View logs
tail -f /var/log/querty-ai-daemon.log

# Create snapshot before major changes
python3 -c '
from core.snapshot_system.snapshot_system import SnapshotSystem
ss = SnapshotSystem()
ss.create_snapshot("before-update", "manual")
'
```

### Updates

```bash
# Update Querty-OS
cd /data/querty-os
git pull
pip3 install -r requirements.txt

# Restart daemon
killall python3
./scripts/boot/init-querty.sh
```

### Monitoring

```bash
# System health
bash scripts/utils/check-status.sh

# Resource usage
python3 -c '
from core.priority import ResourcePriority
ResourcePriority.monitor_usage()
'

# View logs
adb logcat | grep querty
```

---

## Safety Tips

1. **Always have backups** before major changes
2. **Create snapshots** regularly
3. **Test in sandbox first**
4. **Keep stock ROM** available for emergency restore
5. **Charge battery** to 50%+ before operations
6. **Use quality USB cable**
7. **Don't interrupt** flashing process
8. **Keep TWRP backup** on external storage

---

## Support & Resources

- **Issues**: https://github.com/Sharmapank-j/Querty-OS/issues
- **XDA Forum**: Search for "Poco X4 Pro 5G"
- **Telegram**: MIUI/Xiaomi groups
- **Documentation**: All docs in `/docs` folder

---

## Summary Checklist

### Pre-Deployment
- [ ] ✅ Sandbox testing completed
- [ ] ✅ All tests passing
- [ ] ✅ Data backed up
- [ ] ✅ Device charged (80%+)
- [ ] ✅ Required files downloaded

### Deployment
- [ ] ✅ Bootloader unlocked
- [ ] ✅ TWRP installed
- [ ] ✅ Partitions backed up
- [ ] ✅ Tri-boot configured
- [ ] ✅ Querty-OS installed
- [ ] ✅ Tests successful
- [ ] ✅ Snapshot created

### Post-Deployment
- [ ] ✅ Daily usage working
- [ ] ✅ OS switching functional
- [ ] ✅ All features tested
- [ ] ✅ Documentation reviewed

---

**Status**: ✅ Ready for Poco X4 Pro 5G deployment

**Remember**: Sandbox test first, then deploy to device!

For sandbox testing instructions, see: **SANDBOX_SETUP.md**
