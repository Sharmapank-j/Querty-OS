# Changelog

All notable changes to Querty-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-02-15

### Added

#### Documentation
- Added comprehensive badges to README.md (CI status, license, Python version, code style)
- Created `libs/` directory with README and __init__.py for shared libraries
- Reorganized 13 documentation files from root to `docs/` directory
- Updated all internal documentation links to reflect new structure

#### Core Module Implementations
- **AI Daemon Enhancements**
  - `service_manager.py` - Service lifecycle management with health checks and priority control
  - `event_bus.py` - Pub/sub event bus for inter-service communication
  - `state_manager.py` - JSON-based state persistence with atomic writes and backup

- **LLM Service**
  - `model_loader.py` - Multi-format model loader (GGUF, ONNX, TFLite) with plugin architecture
  - `tokenizer.py` - Unified tokenizer wrapper supporting HuggingFace, SentencePiece, and basic tokenization

- **Input Handlers**
  - `text_parser.py` - Natural language command parser with intent and entity extraction
  - `input_fusion.py` - Multi-modal input fusion with configurable strategies

- **Agent Automation**
  - `action_executor.py` - Action execution engine with dry-run, rollback, and logging
  - `workflow_templates.py` - Predefined workflows (system update, backup, cleanup, security scan, etc.)

- **OS Control**
  - `android_api.py` - Android API wrapper for ADB/shell commands and app management
  - `linux_chroot.py` - Linux chroot management with multi-distro package support
  - `app_bridge.py` - Cross-OS file transfer and communication bridge

- **Network Management**
  - `firewall_control.py` - iptables-based firewall for per-app network control
  - `vpn_manager.py` - Multi-protocol VPN manager (OpenVPN, WireGuard)
  - `traffic_monitor.py` - Network traffic monitoring with per-app statistics

- **Snapshot System**
  - `filesystem_snapshot.py` - Filesystem snapshots using tar/rsync
  - `incremental_backup.py` - Incremental backup with change tracking
  - `rollback_manager.py` - Rollback orchestration with safety checks

#### CI/CD Enhancements
- Added Dependabot configuration for automated dependency updates
  - Python dependencies (weekly)
  - GitHub Actions versions (weekly)
  - Docker images (weekly)
- Enhanced Python CI workflow with coverage reporting
- Added Codecov integration for coverage tracking

### Changed
- Cleaned up README.md by removing duplicate sections
  - Merged duplicate "Quick Start" sections
  - Merged duplicate "Development" sections
  - Consolidated getting started flow
- Updated Roadmap to reflect completed CI/CD workflows
- Reorganized repository root for cleaner structure (moved status docs to docs/)

### Fixed
- Fixed `libs/` directory reference in architecture tree (was missing, now created)
- Updated all documentation links to use new `docs/` paths


## [0.1.0] - Initial Release

### Added
- Initial architecture for Querty-OS
- AI daemon with boot integration
- LLM service with deterministic and creative modes
- Multi-modal input handlers (voice, text, camera)
- Agent automation framework
- OS control modules (Android, Linux, Wine)
- Network management with internet on/off control
- Snapshot and rollback system
- Boot initialization scripts
- Basic documentation

### Documentation
- README.md with comprehensive overview
- ARCHITECTURE.md with technical details
- TESTING.md with testing procedures
- PROJECT_SUMMARY.md with project summary
- Module-level documentation for all components

### Device Support
- Poco X4 Pro 5G tri-boot system
- Native Linux boot support (not proot)
- Windows ARM native execution
- Evolution OS and GrapheneOS compatibility

---

## Legend

- `Added`: New features
- `Changed`: Changes in existing functionality
- `Deprecated`: Soon-to-be removed features
- `Removed`: Removed features
- `Fixed`: Bug fixes
- `Security`: Security improvements
