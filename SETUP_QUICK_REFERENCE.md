# Querty-OS Setup Quick Reference

## 🎯 Complete Workflow: Sandbox → Device

### Step 1: Sandbox Testing (REQUIRED)

```bash
# Clone repository
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Install dependencies
pip3 install -r requirements.txt

# Run sandbox tests
bash virtualization/sandbox/test-sandbox.sh

# Expected: ✓ All tests passed! Ready for device deployment.
```

### Step 2: Choose Sandbox Environment

#### Option A: Docker (Fastest - 5 min)
```bash
# Quick start
docker-compose up querty-os

# Development mode
docker-compose up querty-dev

# View dashboard
docker exec querty-os python3 scripts/dashboard.py
```

#### Option B: QEMU/KVM (Full System - 30 min)
```bash
cd virtualization/qemu
bash setup-qemu.sh
./start-vm.sh

# In another terminal:
ssh -p 2222 querty@localhost
```

#### Option C: Android Emulator (20 min)
```bash
export ANDROID_HOME=$HOME/Android/Sdk
cd virtualization/android-emulator
bash setup-emulator.sh
```

### Step 3: Deploy to Poco X4 Pro 5G

**⚠️ ONLY after all sandbox tests pass!**

```bash
# Follow complete guide:
# See POCO_X4_PRO_DEPLOYMENT.md

# Quick overview:
1. Enable developer options & OEM unlock
2. Unlock bootloader (⚠️ erases data)
3. Install TWRP recovery
4. Backup everything (EFS, persist, boot, system)
5. Setup tri-boot partitions
6. Install Querty-OS
7. Test and create snapshot
```

---

## 📚 Documentation Index

| Document | Purpose | Pages |
|----------|---------|-------|
| **README.md** | Project overview | Main |
| **QUICKSTART.md** | 5-minute getting started | Quick |
| **SANDBOX_SETUP.md** | Virtual environment setup | 430 lines |
| **POCO_X4_PRO_DEPLOYMENT.md** | Device installation | 715 lines |
| **ARCHITECTURE_VERIFICATION.md** | Architecture details | Technical |
| **ERROR_HANDLING.md** | Error handling guide | Reference |
| **CONTRIBUTING.md** | Development guidelines | Dev |

---

## 🧪 Sandbox Test Commands

```bash
# Full test suite
bash virtualization/sandbox/test-sandbox.sh

# Individual components
make test              # All tests
make test-unit         # Unit tests only
make test-cov          # With coverage
python3 scripts/dashboard.py  # System dashboard
python3 scripts/validate.py   # Quick validation
```

---

## 🐳 Docker Quick Commands

```bash
# Build
docker build -t querty-os .
docker build -f Dockerfile.dev -t querty-os:dev .

# Run
docker-compose up -d                    # Background
docker-compose up querty-os             # Production
docker-compose up querty-dev            # Development
docker-compose --profile monitoring up  # With monitoring

# Manage
docker-compose down         # Stop all
docker-compose down -v      # Stop and remove volumes
docker logs -f querty-os    # View logs
docker exec -it querty-os bash  # Shell access
```

---

## 📱 Device Quick Commands

```bash
# Check device
adb devices
adb shell getprop ro.product.device  # Should show: veux or peux

# Deploy Querty-OS
adb root
adb push . /data/querty-os/
adb shell "cd /data/querty-os && ./scripts/boot/init-querty.sh"

# System dashboard
adb shell "python3 /data/querty-os/scripts/dashboard.py"

# View logs
adb logcat | grep querty

# Tri-boot switching
adb shell "triboot --os linux"    # Switch to Linux
adb shell "triboot --os android"  # Switch to Android
adb shell "triboot --os windows"  # Switch to Windows (Wine)
```

---

## 🔧 Priority System

**Default Allocation (enforced everywhere):**
- AI: 40% (highest priority)
- Android: 35%
- Linux: 15%
- Windows: 10% (lowest priority)

**Check allocations:**
```bash
python3 -c "
from core.priority import StoragePriorityManager
mgr = StoragePriorityManager(128)  # Your device storage
print(mgr.suggest_partition_sizes())
"
```

---

## 📊 Expected Test Output

```
╔════════════════════════════════════════╗
║   QUERTY-OS SANDBOX TEST SUITE        ║
╚════════════════════════════════════════╝

=== Environment Tests ===
Testing: Python version check        ✓ PASSED
Testing: Python syntax validation    ✓ PASSED
Testing: Dependencies check          ✓ PASSED

=== Core Module Tests ===
Testing: Import exceptions module    ✓ PASSED
Testing: Import priority module      ✓ PASSED
Testing: Priority system validation  ✓ PASSED

=== Unit Tests ===
Testing: Exception tests             ✓ PASSED
Testing: Priority tests              ✓ PASSED

=== Integration Tests ===
Testing: Priority integration        ✓ PASSED

=== Script Validation ===
Testing: Boot script syntax          ✓ PASSED
Testing: Shutdown script syntax      ✓ PASSED
Testing: Check status script         ✓ PASSED

=== Docker Tests ===
Testing: Dockerfile validation       ✓ PASSED

=== Configuration Tests ===
Testing: Config file validation      ✓ PASSED
Testing: Priority config check       ✓ PASSED

=== Tri-boot Script Tests ===
Testing: Tri-boot script syntax      ✓ PASSED
Testing: Partition setup syntax      ✓ PASSED
Testing: Backup script syntax        ✓ PASSED

═══════════════════════════════════════
Passed: 18
Failed: 0

✓ All tests passed! Ready for device deployment.
```

---

## ⚠️ Safety Checklist

### Before Unlocking Bootloader
- [ ] All data backed up (photos, videos, documents)
- [ ] Xiaomi/Mi account synced
- [ ] Battery charged to 80%+
- [ ] Backup phone available
- [ ] Understand data will be erased

### Before Installing Querty-OS
- [ ] Sandbox tests passing (18/18)
- [ ] TWRP recovery installed
- [ ] Critical partitions backed up (EFS, persist)
- [ ] Full system backup created
- [ ] Stock ROM downloaded (for recovery)
- [ ] USB cable is high quality

### After Installation
- [ ] AI daemon starts successfully
- [ ] Priority system validated
- [ ] Tri-boot switching works
- [ ] All components tested
- [ ] "Known good" snapshot created
- [ ] Recovery procedure tested

---

## 🆘 Emergency Recovery

### If device won't boot:
```bash
# Boot to TWRP recovery
# Hold Power + Volume Up while device is off

# Or from working system:
adb reboot recovery
```

### If completely broken:
1. Boot to fastboot (Power + Volume Down)
2. Flash stock ROM using Mi Flash Tool
3. Start over

### Quick rollback:
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

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: https://github.com/Sharmapank-j/Querty-OS/issues
- **Device Guide**: See `devices/poco-x4-pro-5g/README.md`

---

## ✅ Status Check

**Current Status:**
- ✅ Architecture complete
- ✅ Testing infrastructure ready
- ✅ Sandbox environments configured
- ✅ Device deployment documented
- ✅ Priority system enforced
- ✅ All tests passing (18/18)

**You are at:** Choose your path

1. **Test in sandbox first** → See SANDBOX_SETUP.md
2. **Deploy to device** → See POCO_X4_PRO_DEPLOYMENT.md (after sandbox testing)

---

**Remember:** Always test in sandbox before deploying to your device!
