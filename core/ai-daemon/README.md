# AI Daemon

The Querty-OS AI Daemon is the core system service that starts on boot and manages all AI operations.

## Overview

The AI daemon serves as the central intelligence layer, coordinating all system components and maintaining the overall system state.

## Features

- **Boot Initialization**: Automatically starts when the system boots
- **Service Coordination**: Manages all Querty-OS services
- **Event Processing**: Handles system events and user requests
- **State Management**: Maintains system context and state
- **Graceful Shutdown**: Properly cleans up resources on shutdown

## Architecture

```
ai-daemon/
├── daemon.py          # Main daemon implementation
├── service_manager.py # Service lifecycle management (TODO)
├── event_bus.py       # Inter-service communication (TODO)
└── state_manager.py   # System state persistence (TODO)
```

## Running the Daemon

```bash
# Run in foreground (for testing)
python3 core/ai-daemon/daemon.py

# Run as systemd service (production)
systemctl start querty-ai-daemon
```

## Configuration

Configuration is loaded from `/etc/querty-os/daemon.conf`

## Logging

Logs are written to `/var/log/querty-ai-daemon.log`

## Development Status

- [x] Basic daemon structure
- [x] Signal handling
- [x] Logging setup
- [ ] Service integration
- [ ] Event bus implementation
- [ ] State persistence
- [ ] Health monitoring
- [ ] Auto-restart on failure
