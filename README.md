# Querty-OS

**AI-First System Layer for Android**

Querty-OS is an Android-based AI-first system layer (not a ROM) where a local administrator AI serves as the primary interface. It enables voice/text/camera control, automation, multi-OS workflows (Android, Linux, Windows apps), safe updates, and rollback — strictly on user command.

## 📋 Quick Links

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Termux Setup Guide](TERMUX_SETUP.md)** - Development setup for Android Termux users
- **[Sandbox Setup](SANDBOX_SETUP.md)** - Test in virtual environments (Docker, QEMU, Android Emulator)
- **[Device Deployment](POCO_X4_PRO_DEPLOYMENT.md)** - Install on Poco X4 Pro 5G
- **[Quick Reference](SETUP_QUICK_REFERENCE.md)** - All commands in one place
- **[Architecture](ARCHITECTURE_VERIFICATION.md)** - System design and verification
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## Overview

Querty-OS transforms your Android device into an intelligent, autonomous system capable of:
- Running a local LLM for on-device AI processing
- Supporting both deterministic (step-bound) and creative AI modes
- Handling multi-modal input (voice, text, camera)
- Performing agent-based automation tasks
- Controlling Android, Linux (chroot), and Windows apps (Wine)
- Managing network connectivity (internet on/off)
- Executing boot-switch scripts for system customization
- Maintaining last-known-good snapshots with rollback capability

## Architecture

```
Querty-OS/
├── core/                      # Core system components
│   ├── ai-daemon/            # System AI daemon (starts on boot)
│   ├── llm-service/          # Local LLM service (deterministic & creative modes)
│   ├── input-handlers/       # Voice, text, and camera input processing
│   ├── agent-automation/     # Agent-based task automation
│   ├── os-control/           # Android, Linux, and Wine control modules
│   ├── network-manager/      # Network connectivity management
│   └── snapshot-system/      # Snapshot creation and rollback
├── config/                    # System configuration files
├── scripts/                   # System scripts
│   ├── boot/                 # Boot initialization scripts
│   └── utils/                # Utility scripts
├── docs/                      # Documentation
└── libs/                      # Shared libraries
```

## 🚀 Getting Started

### For Termux Users (Android)

If you're developing on Android using Termux, follow our dedicated guide:

**[TERMUX_SETUP.md](TERMUX_SETUP.md)** - Complete Termux setup with copy-paste commands

Quick Termux setup:
```bash
# Install dependencies
pkg update && pkg upgrade -y
pkg install -y python git make

# Clone and setup
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Install dev dependencies (REQUIRED before running tests!)
make install-dev

# Run tests
make test
```

### Test in Sandbox First (Highly Recommended)

For desktop/laptop development:

```bash
# Clone repository
git clone https://github.com/Sharmapank-j/Querty-OS.git
cd Querty-OS

# Install development dependencies (REQUIRED!)
make install-dev
# Or manually: pip3 install -r requirements-dev.txt && pip3 install -e .

# Run comprehensive sandbox tests
bash virtualization/sandbox/test-sandbox.sh
# Expected: ✓ All tests passed! (18/18)
```

**Sandbox Options:**
1. **Docker** - Fastest, recommended for development
2. **QEMU/KVM** - Full system virtualization
3. **Android Emulator** - Android-specific testing

See **[SANDBOX_SETUP.md](SANDBOX_SETUP.md)** for complete virtualization guide.

### Deploy to Poco X4 Pro 5G

⚠️ **Only after successful sandbox testing!**

Complete step-by-step guide: **[POCO_X4_PRO_DEPLOYMENT.md](POCO_X4_PRO_DEPLOYMENT.md)**

Quick overview:
1. Unlock bootloader (⚠️ erases all data)
2. Install TWRP recovery
3. Create comprehensive backups
4. Setup tri-boot (Android/Linux/Windows)
5. Install Querty-OS
6. Test and create snapshots

### Quick Commands

```bash
# Docker quick start
docker-compose up querty-os

# System dashboard
python3 scripts/dashboard.py

# Run all tests
make test

# View logs
tail -f /var/log/querty-ai-daemon.log
```

See **[SETUP_QUICK_REFERENCE.md](SETUP_QUICK_REFERENCE.md)** for all commands.

## Key Features

### 1. AI Daemon
The system AI daemon starts on boot and serves as the central intelligence layer:
- Initializes at system boot
- Manages all AI operations
- Coordinates between different system components
- Maintains system state and context

### 2. Local LLM Service
On-device large language model with dual modes:
- **Deterministic Mode**: Step-bound execution with predictable, reproducible outputs
- **Creative Mode**: Enhanced creativity and flexibility for complex tasks

### 3. Multi-Modal Input Processing
- **Voice Input**: Speech recognition and processing
- **Text Input**: Command-line and text-based interactions
- **Camera Input**: Visual scene understanding and image processing

### 4. Agent Automation
Autonomous agent system capable of:
- Task planning and execution
- Multi-step workflow automation
- Context-aware decision making
- Learning from user preferences

### 5. Multi-OS Control
- **Android Control**: Native Android app and system control
- **Linux Control**: Chroot environment for Linux applications
- **Windows Apps**: Wine integration for Windows application support

### 6. Network Management
- Toggle internet connectivity on/off
- Per-app network control
- VPN and proxy support
- Offline mode optimization

### 7. Boot Scripts
- Custom boot initialization
- System configuration on startup
- Service orchestration
- Health checks and diagnostics

### 8. Snapshot & Rollback
Safety-first update system:
- Automatic snapshot creation before changes
- Last-known-good configuration tracking
- One-click rollback capability
- Incremental snapshot support

## Installation

### Local development install

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install --no-build-isolation -e .
```

### Poco X4 Pro (fresh MIUI/HyperOS) pre-install verification

Run the host-side verifier to confirm files, tools, and device state before flashing steps:

```bash
bash devices/poco-x4-pro-5g/scripts/fresh_mirom_setup.sh
```

Then continue with the full deployment playbook in [POCO_X4_PRO_DEPLOYMENT.md](POCO_X4_PRO_DEPLOYMENT.md).

## Usage

Use the interactive dashboard and daemon entrypoint:

```bash
python3 scripts/dashboard.py
querty-daemon
```

## Development

### Prerequisites
- Android device with root access
- Android SDK
- Python 3.8+
- Required system permissions

### Building from Source
*Build instructions will be added as the system is developed.*

### Contributing
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Security & Privacy

Querty-OS is designed with privacy as a core principle:
- All AI processing happens locally on-device
- No cloud dependencies for core functionality
- User data never leaves the device without explicit consent
- Transparent operation with full user control

## License

See [LICENSE](LICENSE) for details.

## Priority System

**AI > Android > Linux > Windows**

Querty-OS enforces a strict resource allocation priority:

- **AI (Highest)**: 40% default allocation - LLM models, cache, embeddings
- **Android**: 35% allocation - Native apps and system services
- **Linux**: 15% allocation - Chroot environment and packages
- **Windows (Lowest)**: 10% allocation - Wine prefix and applications

See `docs/ERROR_HANDLING.md` for comprehensive priority system documentation.

## Quick Start

```bash
# Install dependencies
make install-dev

# View system status
python3 scripts/dashboard.py

# Run tests
make test

# Format code
make format
```

See [QUICKSTART.md](QUICKSTART.md) for detailed getting started guide.

## Development

### Available Commands

```bash
make help              # Show all commands
make test              # Run all tests
make test-cov          # Run tests with coverage
make lint              # Run all linters
make format            # Format code
make ci                # Run all CI checks
```

### Testing

- 23+ unit tests for core modules
- Integration tests for system components
- >80% code coverage target
- Run with: `make test`

### Code Quality

- Black code formatting (100 char line)
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security scanning
- Pre-commit hooks available: `make pre-commit`

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Roadmap

- [x] Initial architecture design
- [x] Priority system implementation (AI > Android > Linux > Windows)
- [x] Custom exception hierarchy
- [x] Testing infrastructure (pytest, 23+ tests)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Development tools (Makefile, dashboard, validation)
- [x] Comprehensive documentation (5 guides)
- [x] Code quality tools (black, isort, flake8, mypy, bandit)
- [ ] Core AI daemon implementation
- [ ] LLM service integration
- [ ] Input handler modules
- [ ] Agent automation framework
- [ ] OS control modules
- [ ] Network management
- [ ] Snapshot system
- [ ] Boot script system
- [ ] Performance optimization
- [ ] Device deployment

## Support

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/Sharmapank-j/Querty-OS).
