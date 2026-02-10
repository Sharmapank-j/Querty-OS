# Changelog

All notable changes to Querty-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Core Features
- Custom exception system with structured error handling (`core/exceptions.py`)
- Priority management system: AI > Android > Linux > Windows (`core/priority.py`)
- Storage priority manager with partition suggestions
- Resource allocation system with preemption support

#### Development Infrastructure
- Comprehensive test infrastructure with pytest
- Unit test suite for exceptions and priority system
- Integration test framework
- Test fixtures and utilities

#### Build & Dependencies
- `requirements.txt` for production dependencies
- `requirements-dev.txt` for development dependencies
- `setup.py` for package installation
- `pyproject.toml` for modern Python tooling
- `Makefile` for common development tasks

#### Code Quality
- Black code formatter configuration
- isort import sorting configuration
- flake8 linting rules
- pylint configuration
- mypy type checking setup
- bandit security scanning

#### CI/CD
- GitHub Actions workflow for automated testing
- Pre-commit hooks for code quality
- Automated security scanning
- Multi-version Python testing (3.8, 3.9, 3.10, 3.11)
- Code coverage reporting

#### Documentation
- CONTRIBUTING.md with development guidelines
- CHANGELOG.md for tracking changes
- Enhanced configuration with priority settings
- Pre-commit hooks documentation

### Changed

#### Configuration
- Updated `config/querty-os.conf` with priority system settings
- Added storage allocation configuration
- Added dynamic rebalancing options
- Added partition mount point configuration

#### Build System
- Improved .gitignore for Python projects
- Added pre-commit hook configuration
- Enhanced Makefile with comprehensive commands

### Fixed
- N/A (initial upgrade release)

### Security
- Added bandit security scanning
- Added safety dependency checking
- Implemented structured error handling
- Added security configuration in CI/CD

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
