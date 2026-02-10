# Querty-OS Architecture

## System Overview

Querty-OS is an AI-first system layer for Android that provides a local AI administrator interface for comprehensive device control and automation.

## Core Components

### 1. AI Daemon (`core/ai-daemon/`)
The central service that starts on boot and coordinates all system operations.

**Responsibilities:**
- System initialization
- Service lifecycle management
- Event routing
- State management
- Error recovery

**Key Files:**
- `daemon.py` - Main daemon implementation
- Service manager (TODO)
- Event bus (TODO)
- State persistence (TODO)

### 2. LLM Service (`core/llm-service/`)
Manages the local large language model for AI operations.

**Features:**
- Dual mode operation (deterministic/creative)
- On-device inference
- Context management
- Token optimization

**Modes:**
- **Deterministic**: Zero temperature, reproducible outputs for system tasks
- **Creative**: Higher temperature, varied outputs for user interaction

### 3. Input Handlers (`core/input-handlers/`)
Multi-modal input processing for natural interaction.

**Supported Inputs:**
- **Voice**: Speech recognition, wake word detection
- **Text**: Command-line interface, natural language
- **Camera**: Scene understanding, OCR, object detection

### 4. Agent Automation (`core/agent-automation/`)
Autonomous agent system for task execution.

**Capabilities:**
- Task planning and decomposition
- Multi-step execution
- Learning from feedback
- Context awareness

**Modes:**
- **Autonomous**: Fully automated execution
- **Supervised**: User confirmation per step
- **Interactive**: Step-by-step with guidance

### 5. OS Control (`core/os-control/`)
Unified control across multiple operating system environments.

**Environments:**
- **Android**: Native app and system control
- **Linux**: Chroot environment for Linux apps
- **Wine**: Windows application support

### 6. Network Manager (`core/network-manager/`)
Fine-grained network connectivity control.

**Features:**
- Global internet on/off
- Per-app access control
- VPN management
- Traffic monitoring

### 7. Snapshot System (`core/snapshot-system/`)
Safety-first update and rollback capability.

**Features:**
- Automatic snapshots before changes
- Last-known-good tracking
- One-click rollback
- Incremental backups

## Data Flow

```
User Input → Input Handlers → LLM Service → Agent Automation
                                    ↓
                              OS Control
                                    ↓
                          System Operations
                                    ↓
                          Snapshot System (if needed)
```

## Boot Sequence

1. Android system completes boot
2. `init-querty.sh` executes
3. Directories and filesystems set up
4. AI Daemon starts
5. LLM service initializes
6. Input handlers activate
7. System ready for commands

## Configuration

All configuration in `/etc/querty-os/` or `/data/querty-os/config/`:
- `querty-os.conf` - Main system configuration
- `llm-service.conf` - LLM settings
- `network-manager.conf` - Network settings
- `snapshot-system.conf` - Snapshot settings

## Security Model

- **On-device Processing**: All AI runs locally
- **User Control**: Explicit permission required
- **Sandboxing**: Components isolated
- **Audit Logging**: All operations logged
- **Rollback**: Safe recovery from changes

## Development Principles

1. **Privacy First**: No cloud dependencies
2. **User Control**: AI assists, user decides
3. **Safety**: Snapshots before changes
4. **Modularity**: Independent components
5. **Extensibility**: Plugin architecture (TODO)

## Technology Stack

- **Language**: Python 3.8+
- **AI**: Local LLM (GGUF/ONNX/TFLite)
- **Platform**: Android with root access
- **Chroot**: Debian/Ubuntu Linux
- **Wine**: Windows compatibility layer

## Future Architecture

### Planned Components

1. **Plugin System**: Third-party extensions
2. **Web Interface**: Browser-based control
3. **Cloud Sync**: Optional cloud backup
4. **Multi-Device**: Sync across devices
5. **Voice Assistant**: Always-listening mode
6. **Computer Vision**: Advanced camera processing
7. **Scheduler**: Time-based automation
8. **Backup System**: Comprehensive backup solution

### Performance Optimization

- Model quantization for efficiency
- Lazy loading of components
- Caching frequently used data
- Asynchronous operations
- Resource pooling

### Scalability

- Support for multiple LLM models
- Plugin-based input handlers
- Extensible OS controllers
- Modular agent capabilities
