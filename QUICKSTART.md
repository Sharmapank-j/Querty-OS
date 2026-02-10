# Querty-OS Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will get you up and running with Querty-OS development quickly.

## Prerequisites

- Python 3.8 or higher
- Git
- Basic terminal knowledge

**Using Termux on Android?** See **[TERMUX_SETUP.md](TERMUX_SETUP.md)** for detailed setup guide with copy-paste commands.

## 1. Clone and Setup

**⚠️ IMPORTANT**: You must install development dependencies before running tests!

```bash
# Clone the repository
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies (REQUIRED!)
make install-dev

# Or manually:
pip install -r requirements-dev.txt
pip install -e .
```

**Common Error**: If you see `No module named pytest`, it means you haven't installed development dependencies. Run `make install-dev` to fix it.

## 2. Verify Installation

```bash
# Run validation script
python3 scripts/validate.py

# Run unit tests
make test-unit

# Check code formatting
make format-check
```

## 3. Understanding Priority System

Querty-OS uses a strict priority system:

**AI > Android > Linux > Windows**

### Quick Example

```python
from core.priority import SystemPriority, StoragePriorityManager

# Initialize storage manager with 100GB
spm = StoragePriorityManager(total_storage_gb=100.0)

# Get storage allocations
allocations = spm.get_all_allocations()

print(f"AI Storage: {allocations['AI']}GB")        # 40GB
print(f"Android Storage: {allocations['Android']}GB")  # 35GB
print(f"Linux Storage: {allocations['Linux']}GB")      # 15GB
print(f"Windows Storage: {allocations['Windows']}GB")  # 10GB

# Get partition suggestions
suggestions = spm.suggest_partition_sizes()
for name, info in suggestions.items():
    print(f"{name}: {info['size_gb']}GB at {info['mount_point']}")
```

## 4. Error Handling

```python
from core.exceptions import AIServiceError, LLMLoadError

try:
    # Your code here
    load_model("/path/to/model")
except FileNotFoundError as e:
    raise LLMLoadError(
        "Model file not found",
        error_code="LLM_001",
        details={"path": "/path/to/model"}
    )
```

## 5. Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# With coverage
make test-cov

# Specific test file
pytest tests/unit/test_priority.py -v
```

## 6. Code Quality Checks

```bash
# Format code
make format

# Run all linters
make lint

# Type checking
make type-check

# Security scan
make security-check

# Run all CI checks
make ci
```

## 7. Common Development Tasks

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Write code
# ... edit files ...

# 3. Add tests
# ... create test files ...

# 4. Format and lint
make format
make lint

# 5. Run tests
make test

# 6. Commit
git add .
git commit -m "feat: add my new feature"

# 7. Push
git push origin feature/my-new-feature
```

### Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b fix/bug-description

# 2. Fix the bug
# ... edit files ...

# 3. Add regression test
# ... create test that would have caught the bug ...

# 4. Verify fix
make test

# 5. Commit and push
git commit -m "fix: resolve bug description"
git push origin fix/bug-description
```

## 8. Development Workflow

### Daily Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create/switch to feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit code ...

# 4. Run quick validation
python3 scripts/validate.py

# 5. Run tests
make test-unit

# 6. Format code
make format

# 7. Commit changes
git add .
git commit -m "feat: description"

# 8. Before pushing, run full CI
make ci

# 9. Push changes
git push origin feature/my-feature
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
make pre-commit

# Now your code will be checked automatically on git commit
```

## 9. Key Files and Directories

```
Querty-OS/
├── core/                  # Core modules
│   ├── ai-daemon/        # AI daemon
│   ├── llm-service/      # LLM service
│   ├── exceptions.py     # Custom exceptions
│   └── priority.py       # Priority system
├── tests/                # Tests
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── config/              # Configuration
│   └── querty-os.conf   # Main config
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── Makefile            # Development commands
├── pyproject.toml      # Python configuration
├── requirements.txt    # Production deps
└── requirements-dev.txt # Development deps
```

## 10. Configuration

Edit `config/querty-os.conf` to customize:

```ini
[priority]
# Adjust resource allocations (must sum to 100)
ai_allocation = 40
android_allocation = 35
linux_allocation = 15
windows_allocation = 10

[storage]
# Total available storage
total_storage_gb = 64

# Enable priority enforcement
enable_priority_enforcement = true
```

## 11. Troubleshooting

### No Module Named pytest

**Error**: `python3: No module named pytest` or `ModuleNotFoundError: No module named 'pytest'`

**Cause**: Development dependencies not installed.

**Solution**:
```bash
# Install development dependencies
make install-dev

# Or manually
pip install -r requirements-dev.txt

# Verify pytest is installed
python3 -m pytest --version
```

### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .
```

### Test Failures

```bash
# Run with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/unit/test_priority.py::TestResourcePriority::test_default_allocations -v
```

### Formatting Issues

```bash
# Auto-format all code
make format

# Check what would be changed
make format-check
```

### Type Checking Errors

```bash
# Run type checker
make type-check

# Or directly
mypy core/
```

## 12. Next Steps

1. **Read Documentation**
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
   - [ERROR_HANDLING.md](docs/ERROR_HANDLING.md) - Error handling guide

2. **Explore Code**
   - Start with `core/priority.py` to understand priority system
   - Check `core/exceptions.py` for error handling
   - Review tests to see usage examples

3. **Try Examples**
   ```bash
   # Run priority system demo
   python3 -c "
   from core.priority import StoragePriorityManager
   spm = StoragePriorityManager(100)
   for name, gb in spm.get_all_allocations().items():
       print(f'{name}: {gb}GB')
   "
   ```

4. **Join Development**
   - Check open issues
   - Read contribution guidelines
   - Submit your first PR

## 13. Useful Make Commands

```bash
make help              # Show all available commands
make install           # Install production dependencies
make install-dev       # Install development dependencies
make test              # Run all tests
make test-unit         # Run unit tests
make test-cov          # Run tests with coverage
make lint              # Run linters
make format            # Format code
make type-check        # Type checking
make security-check    # Security scanning
make clean             # Clean build artifacts
make pre-commit        # Install pre-commit hooks
make ci                # Run all CI checks
```

## 14. Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Create issue on GitHub
- **Code**: Read existing code and tests
- **Community**: Join discussions

## 15. Quick Reference

### Priority Values
- AI: 4 (highest)
- Android: 3
- Linux: 2
- Windows: 1 (lowest)

### Default Storage Allocation
- AI: 40% (min 30%)
- Android: 35% (min 25%)
- Linux: 15% (min 5%)
- Windows: 10% (min 5%)

### Exception Hierarchy
- `QuertyOSError` (base)
  - `AIServiceError`
  - `StorageError`
  - `ResourceError`
  - `PriorityViolationError`
  - And more...

## Ready to Code! 🎉

You're all set to start developing with Querty-OS. Happy coding!
