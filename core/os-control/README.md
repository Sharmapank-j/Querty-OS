# OS Control

Multi-OS control modules for Android, Linux (chroot), and Windows apps (Wine).

## Overview

The OS control system enables unified management of applications and commands across three different operating system environments on a single Android device.

## Supported Environments

### 1. Android Control
Native Android system and application control:
- **App Management**: Launch, stop, install, uninstall
- **System Commands**: Execute shell commands
- **Intent Handling**: Send and receive Android intents
- **Permission Management**: Grant/revoke app permissions
- **Service Control**: Start/stop system services

### 2. Linux Control (Chroot)
Full Linux environment in chroot:
- **Package Management**: Install/remove Linux packages
- **Command Execution**: Run Linux commands and scripts
- **File System**: Access Linux file system
- **Services**: Manage systemd/init services
- **Development Tools**: Access to full Linux toolchain

### 3. Wine Control
Windows application support via Wine:
- **App Execution**: Run Windows .exe files
- **Installation**: Install Windows applications
- **Registry Access**: Configure Wine registry
- **DirectX Support**: Run games and graphics apps
- **COM Support**: Windows component integration

## Architecture

```
os-control/
├── os_control.py         # Main OS control implementation
├── android_api.py        # Android API integration (TODO)
├── linux_chroot.py       # Chroot management (TODO)
├── wine_wrapper.py       # Wine integration (TODO)
└── app_bridge.py         # Cross-OS app communication (TODO)
```

## Usage

```python
from core.os_control import OSControlManager

# Create control manager
manager = OSControlManager()
manager.start_all()

# Android: Launch app
android = manager.get_controller('android')
android.launch_app('com.example.myapp')

# Linux: Run command
linux = manager.get_controller('linux')
result = linux.execute_command('apt update')

# Wine: Launch Windows app
wine = manager.get_controller('wine')
wine.launch_app('/data/wine/drive_c/Program Files/MyApp/app.exe')

manager.stop_all()
```

## Cross-OS Workflows

### Example: Process file with Linux tools
```
1. Select file in Android
2. Transfer to Linux chroot
3. Process with Linux command-line tools
4. Return result to Android app
```

### Example: Run Windows game
```
1. Install game via Wine
2. Configure graphics settings
3. Launch through Android UI
4. Monitor performance
```

## Environment Setup

### Linux Chroot
```bash
# Create chroot environment
mkdir -p /data/linux
# Install base system (Debian/Ubuntu)
debootstrap stable /data/linux
# Configure mounts
mount -t proc proc /data/linux/proc
mount -t sysfs sys /data/linux/sys
```

### Wine Configuration
```bash
# Initialize Wine prefix
export WINEPREFIX=/data/wine
winecfg
# Install Wine dependencies
winetricks vcrun2019 dotnet48
```

## Security Considerations

- **Sandboxing**: Each environment is isolated
- **Permission Control**: Explicit permissions required
- **Resource Limits**: CPU/memory limits per environment
- **File Access**: Controlled file system access
- **Network Isolation**: Optional network restrictions

## Performance

- **Resource Sharing**: Efficient resource allocation
- **Process Priority**: Fair scheduling across environments
- **Memory Management**: Dynamic memory allocation
- **Storage**: Shared storage with quotas

## Configuration

Settings in `/etc/querty-os/os-control.conf`:
- Chroot path
- Wine prefix location
- Resource limits
- Default environment
- Auto-start options

## Development Status

- [x] OS controller architecture
- [x] Manager implementation
- [ ] Android API integration
- [ ] Linux chroot implementation
- [ ] Wine wrapper
- [ ] Cross-OS communication
- [ ] Resource management
- [ ] Security hardening
