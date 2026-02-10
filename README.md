# Querty-OS

**AI-First System Layer for Android**

Querty-OS is an Android-based AI-first system layer (not a ROM) where a local administrator AI serves as the primary interface. It enables voice/text/camera control, automation, multi-OS workflows (Android, Linux, Windows apps), safe updates, and rollback — strictly on user command.

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

*Installation instructions will be added as the system is developed.*

## Usage

*Usage instructions will be added as the system is developed.*

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
