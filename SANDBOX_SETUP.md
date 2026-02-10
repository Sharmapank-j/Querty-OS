# Querty-OS Sandbox & Virtual Environment Setup Guide

Complete guide for testing Querty-OS in sandbox/virtual environments before deploying to physical devices.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Option 1: Docker Sandbox](#option-1-docker-sandbox)
4. [Option 2: QEMU/KVM Virtual Machine](#option-2-qemukvm-virtual-machine)
5. [Option 3: Android Emulator](#option-3-android-emulator)
6. [Running Sandbox Tests](#running-sandbox-tests)
7. [Verification & Validation](#verification--validation)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps: Device Deployment](#next-steps-device-deployment)

---

## Overview

Querty-OS can run in multiple virtualized/sandboxed environments for safe testing before device deployment:

- **Docker**: Isolated containers (recommended for development)
- **QEMU/KVM**: Full system virtualization
- **Android Emulator**: Android-specific testing

### Why Test in Sandbox?

✅ **Safe Testing**: No risk to physical device  
✅ **Easy Rollback**: Snapshots and quick resets  
✅ **Rapid Development**: Fast iteration cycles  
✅ **Resource Control**: Test with different configurations  
✅ **CI/CD Ready**: Automated testing pipeline

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores (2.0 GHz+)
- RAM: 8 GB
- Storage: 20 GB free space
- OS: Linux (Ubuntu 20.04+, Debian 11+, Arch, etc.)

**Recommended:**
- CPU: 8 cores with virtualization support (Intel VT-x/AMD-V)
- RAM: 16 GB
- Storage: 50 GB+ SSD
- GPU: For Android emulator acceleration

### Software Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install base requirements
sudo apt install -y \
    git \
    python3 python3-pip python3-venv \
    build-essential \
    curl wget

# For Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# For QEMU/KVM
sudo apt install -y qemu-system qemu-kvm libvirt-daemon-system

# For Android development
# Download Android Studio or cmdline-tools from:
# https://developer.android.com/studio
```

### Clone Repository

```bash
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS
```

---

## Option 1: Docker Sandbox

Docker provides the easiest and most portable sandbox environment.

### 1.1 Quick Start

```bash
# Build and run production container
docker-compose up querty-os

# Or for development with live code changes
docker-compose up querty-dev

# Run in background
docker-compose up -d querty-os
```

### 1.2 Manual Docker Build

```bash
# Build production image
docker build -t querty-os:latest .

# Run container
docker run -d \
    --name querty-os \
    -v $(pwd)/data/production:/data/querty \
    -p 8080:8080 \
    -p 8081:8081 \
    querty-os:latest

# View logs
docker logs -f querty-os

# Execute commands in container
docker exec -it querty-os bash
```

### 1.3 Development Mode

```bash
# Build development image
docker build -f Dockerfile.dev -t querty-os:dev .

# Run with live code mounting
docker run -it \
    --name querty-dev \
    -v $(pwd):/opt/querty-os \
    -v $(pwd)/data/development:/data/querty \
    -p 8082:8080 \
    querty-os:dev \
    /bin/bash

# Inside container
cd /opt/querty-os
make install-dev
make test
python3 scripts/dashboard.py
```

### 1.4 Docker Compose Services

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up querty-os
docker-compose up querty-dev

# With monitoring
docker-compose --profile monitoring up

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### 1.5 Docker Testing

```bash
# Run tests inside container
docker exec querty-os python3 -m pytest tests/

# Run sandbox test suite
docker exec querty-os bash virtualization/sandbox/test-sandbox.sh

# Check system status
docker exec querty-os python3 scripts/dashboard.py
```

---

## Option 2: QEMU/KVM Virtual Machine

Full system virtualization for comprehensive testing.

### 2.1 Setup QEMU VM

```bash
cd virtualization/qemu
bash setup-qemu.sh
```

This creates:
- 64GB virtual disk
- VM with 8GB RAM, 4 CPUs
- Network forwarding for SSH and API access

### 2.2 Install OS (First Time Only)

```bash
# Download Ubuntu Server ISO
wget https://releases.ubuntu.com/22.04/ubuntu-22.04-server-amd64.iso
export ISO_PATH=ubuntu-22.04-server-amd64.iso

# Install OS
./install-os.sh

# Follow Ubuntu installation prompts
# Create user: querty
# Set password
# Install OpenSSH server
```

### 2.3 Start VM

```bash
./start-vm.sh

# VM will boot, connect via SSH in another terminal:
ssh -p 2222 querty@localhost
```

### 2.4 Install Querty-OS in VM

Inside the VM (via SSH):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y git python3 python3-pip python3-venv \
    build-essential psmisc

# Clone repository
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Install
make install-dev

# Run tests
make test

# Start daemon
sudo ./scripts/boot/init-querty.sh

# View dashboard
python3 scripts/dashboard.py
```

### 2.5 VM Management

```bash
# Stop VM: Press Ctrl+A then X (or Ctrl+C)

# Create snapshot
qemu-img snapshot -c snapshot1 querty-os-vm.qcow2

# List snapshots
qemu-img snapshot -l querty-os-vm.qcow2

# Restore snapshot
qemu-img snapshot -a snapshot1 querty-os-vm.qcow2

# Delete snapshot
qemu-img snapshot -d snapshot1 querty-os-vm.qcow2
```

---

## Option 3: Android Emulator

Test Querty-OS on Android without physical device.

### 3.1 Setup Android Emulator

```bash
# Set Android SDK location
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator

# Run setup script
cd virtualization/android-emulator
bash setup-emulator.sh
```

### 3.2 Start Emulator

```bash
# Start emulator
$ANDROID_HOME/emulator/emulator -avd Querty_OS_Test \
    -memory 8192 \
    -cores 4 \
    -partition-size 8192 \
    -gpu swiftshader_indirect &

# Wait for boot
adb wait-for-device
```

### 3.3 Deploy Querty-OS

```bash
# Root the emulator
adb root

# Create directories
adb shell "mkdir -p /data/querty-os"

# Push files
adb push ../../ /data/querty-os/

# Set permissions
adb shell "chmod -R 755 /data/querty-os"

# Install dependencies (if Python available on emulator)
adb shell "cd /data/querty-os && pip3 install -r requirements.txt"

# Start daemon
adb shell "cd /data/querty-os && ./scripts/boot/init-querty.sh &"

# View logs
adb logcat | grep querty
```

---

## Running Sandbox Tests

### Comprehensive Test Suite

```bash
# Run full sandbox test suite
cd virtualization/sandbox
bash test-sandbox.sh
```

This tests:
- ✅ Python environment
- ✅ Module imports
- ✅ Priority system
- ✅ Unit tests
- ✅ Integration tests
- ✅ Script syntax
- ✅ Configuration validation
- ✅ Device-specific scripts

### Manual Testing

```bash
# Test priority system
python3 scripts/dashboard.py

# Test core modules
python3 -c "from core.priority import ResourcePriority; print(ResourcePriority.validate())"

# Run unit tests
make test-unit

# Run integration tests
make test

# Run with coverage
make test-cov

# Test daemon initialization
sudo python3 core/ai-daemon/daemon.py --test-mode
```

---

## Verification & Validation

### System Health Check

```bash
# Check all services
python3 scripts/dashboard.py

# Run status check
bash scripts/utils/check-status.sh

# Validate configuration
python3 scripts/validate.py

# Test priority allocation
python3 -c "
from core.priority import StoragePriorityManager
mgr = StoragePriorityManager(64)
print(mgr.suggest_partition_sizes())
"
```

### Expected Output

✅ **All tests passing**  
✅ **Priority system: AI (40%) > Android (35%) > Linux (15%) > Windows (10%)**  
✅ **No import errors**  
✅ **Configuration valid**  
✅ **Scripts executable**  

---

## Troubleshooting

### Docker Issues

**Problem**: Docker daemon not running
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**Problem**: Permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker  # or logout and login again
```

**Problem**: Port already in use
```bash
# Change ports in docker-compose.yml
# Or stop conflicting service
sudo lsof -i :8080
sudo kill -9 <PID>
```

### QEMU/KVM Issues

**Problem**: KVM not available
```bash
# Check virtualization support
egrep -c '(vmx|svm)' /proc/cpuinfo  # Should be > 0

# Load KVM module
sudo modprobe kvm
sudo modprobe kvm_intel  # or kvm_amd
```

**Problem**: Network not working in VM
```bash
# Use user networking (default)
# Or configure bridge networking:
sudo apt install bridge-utils
```

### Android Emulator Issues

**Problem**: Emulator slow
```bash
# Use hardware acceleration
$ANDROID_HOME/emulator/emulator -avd Querty_OS_Test -accel on

# Or use x86_64 instead of ARM
```

**Problem**: ADB not detecting device
```bash
adb kill-server
adb start-server
adb devices
```

### Python/Dependency Issues

**Problem**: Module not found
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
pip3 install -e .

# Or in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

**Problem**: Permission errors
```bash
# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/querty-ai-daemon.log
sudo chmod 666 /var/log/querty-ai-daemon.log
```

---

## Next Steps: Device Deployment

Once sandbox testing is complete and successful:

### ✅ Pre-deployment Checklist

- [ ] All sandbox tests passing
- [ ] Priority system validated
- [ ] Core modules functional
- [ ] Scripts executable
- [ ] Configuration verified
- [ ] No critical errors in logs
- [ ] Documentation reviewed

### 📱 Deploy to Poco X4 Pro 5G

**See**: `POCO_X4_PRO_DEPLOYMENT.md` for complete device deployment guide

Quick overview:
1. Unlock bootloader
2. Flash custom recovery (TWRP)
3. Backup existing partitions
4. Setup tri-boot (Android/Linux/Windows)
5. Install Querty-OS
6. Configure and test

### Deployment Command

```bash
# After device is prepared (see POCO_X4_PRO_DEPLOYMENT.md)
adb root
adb push . /data/querty-os/
adb shell "cd /data/querty-os && ./scripts/boot/init-querty.sh"
```

---

## Additional Resources

- **Main README**: `README.md`
- **Architecture**: `ARCHITECTURE_VERIFICATION.md`
- **Quick Start**: `QUICKSTART.md`
- **Development**: `CONTRIBUTING.md`
- **Device Setup**: `POCO_X4_PRO_DEPLOYMENT.md`
- **Tri-boot Guide**: `devices/poco-x4-pro-5g/docs/TRI-BOOT-GUIDE.md`
- **Error Handling**: `docs/ERROR_HANDLING.md`

---

## Summary

### Sandbox Options Comparison

| Feature | Docker | QEMU/KVM | Android Emulator |
|---------|--------|----------|------------------|
| **Setup Time** | 5 min | 30 min | 20 min |
| **Resource Usage** | Low | Medium | High |
| **Android Support** | Limited | Full | Native |
| **Isolation** | Good | Excellent | Good |
| **Development** | Best | Good | Moderate |
| **Production Testing** | Good | Excellent | Moderate |

### Recommended Workflow

1. **Development**: Use Docker (fast iteration)
2. **Integration Testing**: Use QEMU/KVM (full system)
3. **Android Testing**: Use Android Emulator (native Android)
4. **Final Validation**: Run all sandbox tests
5. **Device Deployment**: Deploy to Poco X4 Pro 5G

---

**Status**: ✅ Sandbox environment ready for Querty-OS testing

For device deployment instructions, proceed to: **POCO_X4_PRO_DEPLOYMENT.md**
