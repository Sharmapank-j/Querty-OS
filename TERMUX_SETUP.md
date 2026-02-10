# Termux Setup Guide for Querty-OS Development

This guide provides step-by-step instructions for setting up Querty-OS development environment in Termux on Android.

## Prerequisites

- Termux installed from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or [GitHub](https://github.com/termux/termux-app/releases)
- At least 2GB of free storage
- Stable internet connection

## Quick Setup (Copy-Paste Commands)

### 1. Update Termux Packages

```bash
pkg update && pkg upgrade -y
```

### 2. Install Required Packages

```bash
pkg install -y python git openssh
```

### 3. Clone the Repository

```bash
cd ~
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS
```

### 4. Install Development Dependencies

**This is the crucial step that fixes the "No module named pytest" error!**

```bash
pip install -r requirements-dev.txt
pip install -e .
```

Or use the Makefile:

```bash
make install-dev
```

### 5. Verify Installation

```bash
python3 -m pytest --version
```

Expected output:
```
pytest 9.0.2 (or higher)
```

### 6. Run Tests

Now you can run tests successfully:

```bash
make test
```

Or run specific test types:

```bash
make test-unit          # Unit tests only
make test-cov           # Tests with coverage report
```

## Common Issues and Solutions

### Issue: "No module named pytest"

**Cause**: Development dependencies not installed.

**Solution**:
```bash
pip install -r requirements-dev.txt
```

### Issue: "Permission denied" errors

**Cause**: Storage permission not granted to Termux.

**Solution**:
```bash
termux-setup-storage
```
Then allow the permission when prompted.

### Issue: "pip: command not found"

**Cause**: Python pip not installed.

**Solution**:
```bash
pkg install python-pip
```

### Issue: Out of storage space

**Cause**: Termux has limited storage in Android.

**Solution**:
```bash
# Check available space
df -h

# Clean up package cache
pkg clean

# Clean Python cache (safer method)
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Development Workflow in Termux

### Running the AI Daemon

```bash
python3 core/ai-daemon/daemon.py
```

### Code Formatting

```bash
make format          # Format code
make format-check    # Check formatting without changes
```

### Linting

```bash
make lint
```

### Running Specific Tests

```bash
# Run tests in a specific file
python3 -m pytest tests/test_priority.py -v

# Run tests matching a pattern
python3 -m pytest tests/ -k "test_priority" -v
```

## Performance Tips for Termux

1. **Use parallel testing** (if device has enough RAM):
   ```bash
   python3 -m pytest tests/ -v -n auto
   ```

2. **Run lightweight tests first**:
   ```bash
   make test-unit
   ```

3. **Skip slow tests** during development:
   ```bash
   python3 -m pytest tests/ -v -m "not slow"
   ```

4. **Use wake lock** to prevent device sleep during long operations:
   ```bash
   termux-wake-lock
   # Run your commands
   termux-wake-unlock
   ```

## Additional Termux-Specific Packages

If you need additional functionality:

```bash
# Git GUI (tig)
pkg install tig

# Better terminal multiplexer
pkg install tmux

# Text editors
pkg install vim nano

# File browsing
pkg install tree
```

## Updating Your Setup

To keep your development environment up to date:

```bash
# Update Termux packages
pkg update && pkg upgrade -y

# Update Python packages
pip install --upgrade -r requirements-dev.txt

# Pull latest code
git pull origin main
```

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review the [QUICKSTART.md](QUICKSTART.md) for general setup
3. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
4. Open an issue on GitHub with:
   - Your Termux version: `termux-info`
   - Python version: `python3 --version`
   - Error message and full traceback

## Next Steps

After successful setup:

1. Read [QUICKSTART.md](QUICKSTART.md) for project overview
2. Review [ARCHITECTURE_VERIFICATION.md](ARCHITECTURE_VERIFICATION.md) for system architecture
3. Check [CONTRIBUTING.md](CONTRIBUTING.md) before making changes
4. Run the validation script:
   ```bash
   python3 scripts/validate.py
   ```

## Summary of Essential Commands

```bash
# Initial setup (one-time)
pkg update && pkg upgrade -y
pkg install -y python git openssh
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS
make install-dev

# Daily development workflow
git pull                # Update code
make test-unit          # Quick tests
make lint               # Check code quality
make format             # Format code
git add .               # Stage changes
git commit -m "message" # Commit changes
git push                # Push changes
```

---

**Note**: Termux runs in userspace without root access by default. Some system-level features of Querty-OS may require a rooted device or may not work in Termux. This setup is primarily for **development and testing**, not for running the full Querty-OS system layer.
