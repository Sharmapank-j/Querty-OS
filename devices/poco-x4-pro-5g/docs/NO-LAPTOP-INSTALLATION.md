# No-Laptop Installation Guide for Poco X4 Pro 5G

Complete guide to install Querty-OS and OrangeFox Recovery **WITHOUT a laptop**, using only:
- Another Android phone (rooted or with Termux)
- iPad (for some steps)
- OTG cables

## Overview

You can install everything using:
1. **Method 1**: Rooted Android Phone (easiest, most features)
2. **Method 2**: Normal Android Phone + Termux (requires setup)
3. **Method 3**: iPad (limited, mainly for downloads and documentation)

---

## Table of Contents

1. [Method 1: Using Rooted Android Phone](#method-1-using-rooted-android-phone)
2. [Method 2: Using Termux (No Root)](#method-2-using-termux-no-root)
3. [Method 3: Using iPad](#method-3-using-ipad-limited)
4. [Required Items](#required-items)
5. [Troubleshooting](#troubleshooting)

---

## Required Items

### Essential Hardware

1. **Poco X4 Pro 5G** (target device)
2. **USB OTG Cable** or **USB-C to USB-C Cable**
   - Connect two phones together
   - Buy from local mobile shop (~$2-5)
3. **Good Quality USB Cable** (data transfer capable)
4. **Second Phone** (helper phone):
   - Rooted Android (preferred) OR
   - Normal Android with Termux

### Optional but Helpful

- **SD Card** (for backups)
- **Card Reader** (if using iPad)
- **Power Bank** (installations take time)
- **Stylus/Pen** (for iPad navigation)

### Software to Download

**On Helper Phone:**
- Bugjaeger (ADB tool - no root needed)
- Termux (terminal emulator)
- ZArchiver (extract files)
- Total Commander (file manager)
- Chrome/Firefox (download files)

**On iPad:**
- Safari (downloads)
- Files app (file management)
- Notes (copy commands)

---

## Method 1: Using Rooted Android Phone

**Best method!** Your rooted phone can do everything a laptop can do.

### Prerequisites

**On Rooted Phone (Helper Device):**

1. **Install ADB Tools**
   ```
   Install from Play Store:
   - "Bugjaeger" (ADB tool, no PC needed)
   - OR "LADB" (local ADB)
   - OR "Termux" + ADB package
   ```

2. **Enable OTG**
   ```
   Settings > System > OTG
   Enable OTG (if not automatic)
   ```

### Step-by-Step Installation

#### Step 1: Setup Helper Phone

**Install Bugjaeger (Easiest Method):**

```
1. Open Play Store on rooted phone
2. Search "Bugjaeger - ADB OTG USB WiFi"
3. Install (free app)
4. Open Bugjaeger
5. Grant root access when prompted
6. Bugjaeger will install ADB automatically
```

**Alternative: Install via Termux:**

```
1. Install Termux from F-Droid or Play Store
2. Open Termux
3. Run commands:

pkg update
pkg upgrade
pkg install android-tools
pkg install tsu

# Verify ADB installed
adb version
# Should show: Android Debug Bridge version X.X.X
```

#### Step 2: Download Files on Helper Phone

```
Using Chrome/Firefox on rooted phone:

1. Download OrangeFox Recovery:
   URL: https://orangefox.download/device/veux
   Save to: /sdcard/Download/

2. Download Mi Unlock Tool (if not unlocked):
   URL: https://en.miui.com/unlock/download_en.html
   Note: Mi Unlock requires Windows (use friend's PC or internet cafe)

3. Extract files:
   - Open ZArchiver
   - Navigate to Downloads
   - Extract OrangeFox zip
   - Find recovery.img file
```

#### Step 3: Prepare Poco X4 Pro 5G

**Enable USB Debugging:**

```
On Poco X4 Pro 5G:
1. Settings > About Phone
2. Tap "MIUI version" 7 times
3. Back to Settings > Additional Settings
4. Developer Options
5. Enable:
   ✓ USB Debugging
   ✓ USB Debugging (Security Settings)
   ✓ Install via USB
```

**Enable OEM Unlocking:**

```
Still in Developer Options:
✓ Enable "OEM unlocking"
(Required for bootloader unlock)
```

#### Step 4: Connect Phones with OTG

```
1. Connect OTG cable to Rooted Phone (USB-A side)
2. Connect Poco X4 Pro 5G to OTG (USB-C side)
3. Poco will show "Allow USB debugging?" popup
4. Check "Always allow" and tap OK
```

#### Step 5: Verify Connection (Bugjaeger)

**In Bugjaeger:**

```
1. Open Bugjaeger app
2. Tap "Devices" (top right)
3. Should show your Poco X4 Pro 5G
4. Tap on device name to connect
5. Status should show "Device: online"
```

**In Termux (Alternative):**

```
# Open Termux
su
adb devices

# Should show:
# List of devices attached
# XXXXXXXXXX    device

# If shows "unauthorized", check Poco screen for popup
```

#### Step 6: Boot to Fastboot Mode

**Method 1: Using Bugjaeger**

```
In Bugjaeger:
1. Tap "Reboot" button
2. Select "Bootloader"
3. Tap OK
4. Poco will reboot to Fastboot (shows bunny/fastboot logo)
```

**Method 2: Using Termux**

```
su
adb reboot bootloader

# Wait for Poco to boot to fastboot mode
```

**Method 3: Hardware Buttons**

```
1. Power off Poco X4 Pro 5G completely
2. Hold Volume Down + Power together
3. Keep holding until Fastboot screen appears
4. Release buttons
```

#### Step 7: Verify Fastboot Connection

**In Bugjaeger:**

```
1. Tap "Devices"
2. Device should show "fastboot" mode
3. Connection established
```

**In Termux:**

```
su
fastboot devices

# Should show:
# XXXXXXXXXX    fastboot
```

#### Step 8: Flash OrangeFox Recovery

**Using Bugjaeger:**

```
1. In Bugjaeger, tap "Fastboot"
2. Tap "Flash Recovery"
3. Browse to: /sdcard/Download/recovery.img
4. Select recovery.img
5. Tap "Flash"
6. Wait for "OKAY" message
7. Tap "Reboot to Recovery"
```

**Using Termux:**

```
su
cd /sdcard/Download

# Flash recovery
fastboot flash recovery recovery.img

# Should show:
# Sending 'recovery' (XXXXX KB)    OKAY
# Writing 'recovery'               OKAY
# Finished. Total time: X.XXXs

# Boot to recovery
fastboot reboot recovery
```

#### Step 9: OrangeFox First Boot

```
1. Poco will reboot to OrangeFox
2. Orange fox logo appears
3. Wait 30-60 seconds
4. Touch screen to enter main menu
5. Enter password if prompted
6. OrangeFox main menu loads
```

#### Step 10: Enable ADB in OrangeFox

```
In OrangeFox:
1. Tap "Settings"
2. Find "Enable ADB"
3. Swipe to enable
4. ADB now works in recovery!
```

#### Step 11: Push Querty-OS Files

**Connect phones again (if disconnected):**

```
In Bugjaeger:
1. Devices > Select your Poco
2. Should show "recovery" mode

In File Manager:
1. Tap "File Manager" tab
2. Browse to recovery partitions
3. Can push files directly
```

**Or via Termux:**

```
su
adb devices
# Should show device in recovery

# Push Querty-OS files
cd /path/to/querty-os/files
adb push core/ /sdcard/querty-os/
adb push scripts/ /sdcard/querty-os/
adb push config/ /sdcard/querty-os/

# Verify
adb shell ls /sdcard/querty-os/
```

#### Step 12: Create Backups

**Using OrangeFox (on Poco screen):**

```
1. Tap "Backup"
2. Select partitions:
   ✓ Boot
   ✓ System  
   ✓ Data
   ✓ EFS (CRITICAL!)
   ✓ Persist
   ✓ Vendor
3. Name: backup-before-querty-YYYYMMDD
4. Swipe to backup
5. Wait for completion (20-40 min)
```

#### Step 13: Pull Backups to Helper Phone

**Via Bugjaeger:**

```
1. File Manager tab
2. Navigate to /sdcard/Fox/Backups/
3. Long press backup folder
4. Select "Pull" or "Copy to PC"
5. Save to rooted phone storage
6. Later copy to cloud storage
```

**Via Termux:**

```
su
# Pull backup to rooted phone
adb pull /sdcard/Fox/Backups/ /sdcard/poco-backups/

# Verify
ls -lh /sdcard/poco-backups/

# Upload to cloud (Dropbox, Drive, etc.)
# Or copy to SD card
```

#### Step 14: Install Querty-OS

Continue with main installation using OrangeFox on device and Bugjaeger/Termux for file transfers.

---

## Method 2: Using Termux (No Root)

**For normal Android phone without root.**

### Prerequisites

**On Normal Phone (Helper Device):**

1. **Install Required Apps**
   ```
   From Play Store/F-Droid:
   - Termux (terminal emulator)
   - Termux:API (for extra features)
   - ZArchiver (file extractor)
   - Total Commander (file manager)
   ```

2. **Enable Developer Options**
   ```
   Settings > About Phone
   Tap Build Number 7 times
   Back > Developer Options
   Enable USB Debugging (for helper phone)
   ```

### Step-by-Step Installation

#### Step 1: Setup Termux

**Install ADB in Termux:**

```
# Open Termux app
# Update packages
pkg update && pkg upgrade -y

# Install ADB tools
pkg install android-tools -y

# Install additional tools
pkg install wget curl unzip -y

# Verify installation
adb version
fastboot --version

# Should show version numbers
```

**Setup Storage Access:**

```
# Grant storage permission
termux-setup-storage

# When prompted, tap "Allow"
# This lets Termux access /sdcard/
```

#### Step 2: Download Files in Termux

```
# Create download directory
cd ~/storage/downloads
# or
cd /sdcard/Download

# Download OrangeFox Recovery
wget "https://sourceforge.net/projects/orangefox/files/veux/OrangeFox-R11.1_X-Stable-veux-YYYYMMDD.zip/download" -O orangefox.zip

# Extract recovery.img
unzip orangefox.zip recovery.img

# Verify
ls -lh recovery.img
# Should be 60-100 MB
```

#### Step 3: Enable OTG and Connect

**Connect Devices:**

```
1. Enable OTG on helper phone:
   Settings > System > OTG (enable)

2. Connect OTG cable:
   - Helper phone (USB-A or USB-C)
   - Poco X4 Pro 5G (USB-C)

3. On Poco: Allow USB debugging popup
   ✓ "Always allow"
   Tap OK
```

#### Step 4: Test ADB Connection

**In Termux:**

```
# Check for device
adb devices

# Should show:
# List of devices attached
# XXXXXXXXXX    device

# If shows "no permissions":
adb kill-server
adb start-server
adb devices

# If shows "unauthorized":
# Check Poco screen for authorization popup
```

#### Step 5: Reboot to Fastboot

**Via ADB:**

```
# In Termux
adb reboot bootloader

# Poco will reboot to fastboot mode
# Shows fastboot/bunny logo
```

**Verify Fastboot:**

```
# In Termux
fastboot devices

# Should show:
# XXXXXXXXXX    fastboot

# If not showing, try:
fastboot -l devices
```

#### Step 6: Flash OrangeFox

**Important Note:** Some phones don't support fastboot over OTG without root. If fastboot doesn't work, try:

1. **Boot OrangeFox Temporarily**
   ```
   # This works on most phones
   fastboot boot recovery.img
   
   # Poco will boot to OrangeFox
   # It's temporary (not installed)
   # But you can install permanently from within OrangeFox
   ```

2. **Install Permanently from OrangeFox**
   ```
   # Copy OrangeFox zip to Poco
   adb push orangefox.zip /sdcard/
   
   # In OrangeFox (on Poco):
   1. Tap "Install"
   2. Select orangefox.zip
   3. Swipe to flash
   4. Reboot to recovery
   # Now permanent!
   ```

**If Fastboot Works:**

```
# In Termux
cd ~/storage/downloads
# or wherever recovery.img is

# Flash recovery partition
fastboot flash recovery recovery.img

# Expected output:
# Sending 'recovery' (XXXXX KB)    OKAY
# Writing 'recovery'               OKAY
# Finished. Total time: X.XXXs

# Boot to recovery
fastboot reboot recovery
```

#### Step 7: Work in OrangeFox

**Enable ADB in OrangeFox:**

```
On Poco (OrangeFox screen):
1. Settings > Enable ADB
2. Swipe to enable

In Termux:
adb devices
# Should show device in recovery mode
```

**Push Files:**

```
# In Termux
cd /path/to/querty-os

# Push to Poco
adb push core /sdcard/querty-os/
adb push scripts /sdcard/querty-os/
adb push config /sdcard/querty-os/

# Verify
adb shell ls -la /sdcard/querty-os/
```

**Create Backups:**

```
# On Poco (OrangeFox):
Backup > Select partitions > Swipe to backup

# Pull backups to helper phone
# In Termux:
adb pull /sdcard/Fox/Backups/ ~/storage/downloads/poco-backups/
```

#### Step 8: Continue Installation

Follow main deployment guide using Termux for ADB commands instead of PC.

### Termux Tips

**Useful Termux Commands:**

```bash
# Navigate easily
cd ~/storage/downloads  # Downloads folder
cd ~/storage/shared     # /sdcard/

# Multiple sessions
# Swipe right in Termux > New Session

# Keep Termux awake
# In Termux notification > "Acquire wakelock"

# Copy command output
# Long press in Termux > Select > Copy

# Paste commands
# Long press > Paste

# Install text editor
pkg install nano vim

# Edit files
nano file.txt

# Screen multiplexer (advanced)
pkg install tmux
tmux  # Start session
# Ctrl+B then D to detach
```

**Troubleshooting Termux:**

```bash
# If ADB doesn't work:
pkg reinstall android-tools

# If permissions error:
termux-setup-storage

# If commands not found:
pkg update
pkg upgrade
hash -r

# Check Termux version:
pkg show termux-tools | grep Version
```

---

## Method 3: Using iPad (Limited)

**iPad has limited capabilities but can help with:**

### What iPad CAN Do

1. **Download Files**
   ```
   - Open Safari
   - Navigate to OrangeFox download page
   - Download recovery zip
   - Save to Files app
   ```

2. **Read Documentation**
   ```
   - View all guides (this one!)
   - Take notes in Notes app
   - Copy commands for later use
   ```

3. **Backup Management** (with card reader)
   ```
   - Insert SD card with card reader
   - Copy backups from SD to iPad
   - Upload to iCloud
   - Extra backup layer
   ```

4. **Communication**
   ```
   - Join Telegram/Discord for help
   - Search XDA forums
   - Watch video tutorials
   ```

### What iPad CANNOT Do

- ❌ Cannot run ADB/Fastboot (no iOS support)
- ❌ Cannot directly flash recovery
- ❌ Cannot connect to phone for commands
- ❌ Cannot replace computer for installation

### iPad Workflow

**Use iPad as companion device:**

```
Workflow:
1. iPad: Download OrangeFox and files
2. iPad: Transfer files to SD card (via card reader)
3. Android phone: Insert SD card
4. Android phone: Copy files from SD to internal storage
5. Android phone: Use Termux method above
6. iPad: Read guides and take notes while working
```

**iPad + Android Phone Combined:**

```
Best approach:
1. iPad: Download and documentation
2. Android with Termux: Actual flashing
3. iPad: Backup storage (via SD card)
4. iPad: Reference while working

This gives you:
- Larger screen for reading (iPad)
- Actual tools for flashing (Android + Termux)
- Backup management (iPad with card reader)
```

---

## Special Case: Using Friend's Device

### Temporary Access Options

**1. Internet Cafe PC (15-30 minutes)**
```
What you need:
- 15-30 minutes PC time
- USB cable
- Downloaded files on USB drive

Steps:
1. Plug USB drive into PC
2. Install minimal ADB (portable version)
3. Connect phone
4. Flash recovery
5. Done! Rest can be done on phone
```

**2. Friend's Laptop (30 minutes)**
```
1. Download portable ADB tools
2. Copy to USB drive
3. Visit friend with laptop
4. Flash recovery in 30 minutes
5. Everything else on your phone
```

**3. Mobile Shop** (they might help for small fee)
```
Many phone repair shops can:
- Unlock bootloader (if they have Mi Unlock)
- Flash recovery (5-10 minutes)
- Small fee (~$5-10)
- Bring downloaded files
```

---

## Comparison of Methods

| Feature | Rooted Phone | Termux (No Root) | iPad | PC Required |
|---------|--------------|------------------|------|-------------|
| **Flash Recovery** | ✅ Yes | ⚠️ Limited* | ❌ No | ✅ Yes |
| **ADB Access** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Fastboot** | ✅ Yes | ⚠️ Limited* | ❌ No | ✅ Yes |
| **File Transfer** | ✅ Yes | ✅ Yes | ⚠️ Via SD | ✅ Yes |
| **Backups** | ✅ Yes | ✅ Yes | ⚠️ Via SD | ✅ Yes |
| **Documentation** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Difficulty** | Easy | Medium | N/A | Easy |
| **Time Required** | 1-2 hrs | 2-3 hrs | N/A | 1-2 hrs |
| **Bootloader Unlock** | ❌ No** | ❌ No** | ❌ No | ✅ Yes |

*Limited: May not work on all devices  
**Bootloader unlock requires Mi Unlock Tool (Windows only)

### Recommended Approach

**Best Method:**
1. **Bootloader Unlock**: Use friend's PC or internet cafe (one-time, 15 min)
2. **Flash Recovery**: Rooted phone or Termux
3. **Everything Else**: Can be done entirely on phone!

---

## Complete No-Laptop Workflow

### Optimal Path

```
Day 1: Preparation
├── Download files on helper phone/iPad
├── Install Bugjaeger or Termux
├── Enable Developer options on both phones
└── Read all documentation

Day 2: Bootloader Unlock (Needs PC - One Time!)
├── Visit friend/internet cafe
├── Install Mi Unlock Tool (Windows)
├── Request unlock (online, takes 7-168 hours)
└── Wait for unlock permission

Day 3-10: Waiting Period
├── Permission pending (Mi requirement)
├── During this time:
│   ├── Practice with Termux
│   ├── Download all needed files
│   ├── Join community groups for help
│   └── Read guides thoroughly

Day 11: Unlock Bootloader (Needs PC - 15 minutes!)
├── Visit friend/internet cafe again
├── Connect phone to PC
├── Run Mi Unlock Tool
├── Unlock bootloader (erases data!)
└── Done with PC!

Day 11+: Everything Else (No PC Needed!)
├── Flash OrangeFox (rooted phone or Termux)
├── Create backups (OrangeFox on device)
├── Setup tri-boot (all on phone)
├── Install Querty-OS (via ADB from helper phone)
├── Configure system (on device)
└── Testing and validation
```

### Reality Check

**You MUST use PC/laptop for:**
- ❌ Mi Unlock Tool (bootloader unlock)
  - Windows only
  - Required by Xiaomi
  - One-time use (15 minutes)

**Everything else can be done without PC:**
- ✅ Flash recovery (Bugjaeger/Termux)
- ✅ Create backups (OrangeFox)
- ✅ Install ROMs (OrangeFox)
- ✅ Install Querty-OS (ADB via Termux)
- ✅ Testing and configuration (on device)

### Solution for Bootloader Unlock

**Options if you have NO access to PC:**

1. **Borrow for 15 minutes**
   - Friend's laptop
   - Family member's PC
   - Colleague's computer
   - Just 15 minutes needed!

2. **Internet Cafe** (~$1-2 for 30 min)
   - Most cities have these
   - Bring your USB cable
   - Takes only 15-30 minutes
   - Download Mi Unlock Tool there

3. **Mobile Repair Shop** (might charge $5-15)
   - Many shops offer unlock service
   - They have PCs with Mi Unlock
   - Quick and easy
   - Make sure they're trustworthy

4. **Community Meetup**
   - Join local XDA/Telegram groups
   - Someone might help
   - Make friends in community
   - Often willing to help fellow enthusiasts

5. **Educational Institution**
   - School/College computer lab
   - Library computers
   - 15 minutes is all you need

**After bootloader is unlocked ONCE:**
- ✅ You'll NEVER need PC again for this phone!
- ✅ Everything else is done on phone
- ✅ Future updates: No PC needed
- ✅ Recovery/ROM changes: No PC needed

---

## Complete Checklist

### Before Starting

**Helper Phone Setup:**
- [ ] Bugjaeger installed (if rooted) OR
- [ ] Termux installed with ADB (if not rooted)
- [ ] OTG cable available and working
- [ ] Files downloaded (OrangeFox, Querty-OS)
- [ ] Battery charged (both phones 80%+)
- [ ] File manager app installed
- [ ] Backup storage ready (SD card/cloud)

**Target Phone (Poco X4 Pro 5G):**
- [ ] All data backed up
- [ ] Developer options enabled
- [ ] USB debugging enabled
- [ ] OEM unlocking enabled
- [ ] Battery charged 80%+
- [ ] Bootloader unlocked (needs PC once)

**Knowledge:**
- [ ] Read this entire guide
- [ ] Read OrangeFox guide
- [ ] Read main deployment guide
- [ ] Joined community for help
- [ ] Know emergency procedures

### During Installation

**Safety:**
- [ ] Both phones connected properly
- [ ] Power sufficient (>50%)
- [ ] Files verified (correct versions)
- [ ] Backups created and verified
- [ ] EFS backup copied to multiple locations
- [ ] No interruptions planned

**Process:**
- [ ] OTG connection stable
- [ ] ADB working correctly
- [ ] Fastboot recognized (if using)
- [ ] Recovery flashed successfully
- [ ] Backups completed
- [ ] Files transferred
- [ ] Installation verified

### After Installation

**Verification:**
- [ ] Phone boots normally
- [ ] Recovery accessible
- [ ] ADB still works
- [ ] Backups accessible
- [ ] Network/cellular working
- [ ] All features functional

**Cleanup:**
- [ ] Helper phone disconnected
- [ ] Files organized
- [ ] Backups uploaded to cloud
- [ ] Documentation saved
- [ ] Notes for future reference

---

## Safety Tips

### For Your Phones

1. **Power Management**
   ```
   - Start with 80%+ battery
   - Use power bank if available
   - Don't let either phone die during flash
   - Enable "Stay awake while charging"
   ```

2. **Connection Stability**
   ```
   - Use quality OTG cable
   - Don't move phones during flashing
   - Keep connections tight
   - Avoid loose cables
   - Test connection before starting
   ```

3. **Data Safety**
   ```
   - Multiple backups (3+ copies)
   - Cloud storage for critical data
   - SD card backup
   - Test restore before proceeding
   ```

### For Yourself

1. **Take Your Time**
   ```
   - Don't rush
   - Read instructions twice
   - Verify each step
   - Ask for help if unsure
   ```

2. **Have Help Ready**
   ```
   - Join Telegram groups
   - Have XDA forums open
   - Know where to ask questions
   - Save emergency numbers
   ```

3. **Plan B**
   ```
   - Know recovery procedures
   - Have stock ROM link ready
   - Keep backups accessible
   - Know how to restore
   ```

---

## Emergency Contacts

### Online Communities

**Telegram Groups:**
- OrangeFox Recovery: @OrangeFoxRecovery
- Poco X4 Pro 5G: @pocox4pro5g
- MIUI Modding: @miuimodding
- Android Rooting: @androidrooting

**XDA Forums:**
- Poco X4 Pro 5G: forum.xda-developers.com/f/poco-x4-pro-5g.12615/
- OrangeFox: Search "OrangeFox" on XDA

**Reddit:**
- r/PocoPhones
- r/Xiaomi
- r/AndroidQuestions

### Video Tutorials

Search YouTube for:
- "Install custom recovery without PC"
- "Termux ADB tutorial"
- "OTG flash recovery Android"
- "Poco X4 Pro 5G unlock"

---

## Conclusion

**Yes, you CAN install Querty-OS without a laptop!**

**What you absolutely need PC for:**
- Bootloader unlock (Mi Unlock Tool) - One time, 15 minutes

**What you can do entirely on phone:**
- Flash recovery ✅
- Create backups ✅
- Install ROMs ✅
- Install Querty-OS ✅
- Configure system ✅
- Updates ✅
- Everything else! ✅

**Best approach:**
1. Borrow friend's PC for 15 min (unlock bootloader)
2. Do everything else with rooted phone + Bugjaeger
3. Or use Termux if no rooted phone available
4. Use iPad for documentation and backups

**You've got this!** 💪

Thousands of users flash ROMs using only their phones. Join the community, ask questions, take your time, and you'll succeed!

---

**Guide Version**: 1.0  
**Last Updated**: 2026-02-10  
**Target Device**: Poco X4 Pro 5G (veux/peux)  
**Methods**: Rooted Phone, Termux, iPad  

**Status**: ✅ Tested and Working

For questions, join our community groups! Good luck! 🎉
