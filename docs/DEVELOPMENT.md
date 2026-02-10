# Development Guide

## Getting Started

### Prerequisites

1. **Android Device**
   - Android 8.0+ (API level 26+)
   - Root access required
   - 4GB+ RAM recommended
   - 10GB+ free storage

2. **Development Tools**
   - Python 3.8+
   - Android SDK
   - ADB (Android Debug Bridge)
   - Git

3. **Optional**
   - Android NDK (for native code)
   - Wine (for testing Wine integration)
   - Linux chroot environment

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Install Python dependencies (TODO: requirements.txt)
pip3 install -r requirements.txt

# Connect Android device
adb devices

# Push to device
adb push . /data/local/querty-os/

# Make scripts executable
adb shell "chmod +x /data/local/querty-os/scripts/boot/*.sh"
```

## Project Structure

```
Querty-OS/
├── core/                  # Core system modules
│   ├── ai-daemon/        # System AI daemon
│   ├── llm-service/      # LLM service
│   ├── input-handlers/   # Input processing
│   ├── agent-automation/ # Agent framework
│   ├── os-control/       # OS control modules
│   ├── network-manager/  # Network management
│   └── snapshot-system/  # Snapshot & rollback
├── config/               # Configuration files
├── scripts/              # System scripts
│   ├── boot/            # Boot scripts
│   └── utils/           # Utility scripts
├── docs/                 # Documentation
└── libs/                 # Shared libraries
```

## Development Workflow

### 1. Make Changes

Edit files in your local repository:
```bash
# Edit daemon
nano core/ai-daemon/daemon.py

# Edit configuration
nano config/querty-os.conf
```

### 2. Test Locally (if possible)

```bash
# Test Python modules locally
python3 core/ai-daemon/daemon.py
python3 core/llm-service/llm_service.py
```

### 3. Push to Device

```bash
# Push changes to device
adb push core/ai-daemon/daemon.py /data/local/querty-os/core/ai-daemon/

# Or push entire directory
adb push . /data/local/querty-os/
```

### 4. Test on Device

```bash
# Connect to device shell
adb shell

# Become root
su

# Run daemon
python3 /data/local/querty-os/core/ai-daemon/daemon.py

# Check logs
cat /data/querty-os/logs/daemon.log
```

## Coding Standards

### Python Style

Follow PEP 8:
- 4 spaces for indentation
- Max line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

Example:
```python
def create_snapshot(name: str, description: str = "") -> Optional[Snapshot]:
    """
    Create a new system snapshot.
    
    Args:
        name: Snapshot name
        description: Optional description
        
    Returns:
        Created snapshot or None on failure
    """
    # Implementation
    pass
```

### Shell Scripts

- Use `#!/system/bin/sh` for Android compatibility
- Add error checking (`set -e`)
- Use meaningful variable names
- Add comments for complex logic
- Test on actual device

### Documentation

- README.md in each module directory
- Inline comments for complex logic
- Docstrings for all public functions
- Architecture documentation for major changes

## Testing

### Unit Tests

(TODO: Test framework setup)

```python
# Example test structure
import unittest
from core.llm_service import LLMService

class TestLLMService(unittest.TestCase):
    def test_mode_switching(self):
        service = LLMService()
        service.set_mode(LLMMode.DETERMINISTIC)
        self.assertEqual(service.mode, LLMMode.DETERMINISTIC)
```

### Integration Tests

Test on actual Android device:
1. Install Querty-OS
2. Run boot scripts
3. Test each component
4. Verify interactions
5. Check logs for errors

### Manual Testing Checklist

- [ ] Boot scripts execute successfully
- [ ] Daemon starts and runs
- [ ] LLM service initializes
- [ ] Input handlers respond
- [ ] Agent automation works
- [ ] OS control functions
- [ ] Network manager operates
- [ ] Snapshots create/restore

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Logs

```bash
# Real-time log viewing
adb shell tail -f /data/querty-os/logs/daemon.log

# Boot logs
adb shell cat /data/local/tmp/querty-boot.log

# System logs
adb logcat | grep Querty
```

### Common Issues

1. **Permission Denied**
   - Ensure root access
   - Check file permissions
   - Verify SELinux status

2. **Module Not Found**
   - Check Python path
   - Verify file locations
   - Install missing dependencies

3. **Daemon Won't Start**
   - Check Python version
   - Review daemon.log
   - Verify dependencies

## Contributing

### Workflow

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Pull Request Guidelines

- Clear description of changes
- Reference related issues
- Include tests (when available)
- Update documentation
- Follow coding standards

### Commit Messages

Format:
```
[Component] Brief description

Detailed explanation if needed.

Fixes #123
```

Example:
```
[LLM Service] Add creative mode temperature control

Implemented configurable temperature settings for creative mode
to allow fine-tuning of output diversity.

Fixes #42
```

## Building Documentation

(TODO: Documentation build system)

```bash
# Generate documentation
python3 scripts/generate_docs.py

# View locally
python3 -m http.server 8000
# Open http://localhost:8000/docs/
```

## Release Process

1. Update version number
2. Update CHANGELOG
3. Run full test suite
4. Create release branch
5. Tag release
6. Build release package
7. Publish release notes

## Resources

- [Android Documentation](https://developer.android.com/)
- [Python Documentation](https://docs.python.org/)
- [Linux Chroot Guide](https://wiki.debian.org/chroot)
- [Wine Documentation](https://wiki.winehq.org/)

## Getting Help

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Wiki: Community documentation
