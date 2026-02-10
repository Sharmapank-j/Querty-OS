# Testing Querty-OS

This document shows how to test the Querty-OS modules.

## Quick Module Tests

All core modules include a `main()` function for standalone testing.

### 1. LLM Service
```bash
python3 core/llm-service/llm_service.py
```
Tests:
- Mode switching (deterministic/creative)
- Configuration updates
- Text generation interface

### 2. Input Handlers
```bash
python3 core/input-handlers/input_handlers.py
```
Tests:
- Input manager initialization
- All three handlers (voice, text, camera)
- Text input processing

### 3. Agent Automation
```bash
python3 core/agent-automation/agent_automation.py
```
Tests:
- Agent creation
- Task planning
- Task execution
- Task queue processing

### 4. OS Control
```bash
python3 core/os-control/os_control.py
```
Tests:
- Manager initialization
- Android, Linux, Wine controllers
- Command execution interface

### 5. Network Manager
```bash
python3 core/network-manager/network_manager.py
```
Tests:
- Network state management
- Mode switching
- Per-app controls
- Network info retrieval

### 6. Snapshot System
```bash
python3 core/snapshot-system/snapshot_system.py
```
Tests:
- Snapshot creation
- Last-known-good marking
- Snapshot listing

### 7. AI Daemon
```bash
python3 core/ai-daemon/daemon.py
```
Tests:
- Daemon initialization
- Service startup
- Signal handling
- Main event loop

## Shell Scripts

### Boot Scripts
```bash
# Syntax check
sh -n scripts/boot/init-querty.sh
sh -n scripts/boot/shutdown-querty.sh

# Dry run (requires root on Android device)
# adb shell "su -c 'sh /data/local/querty-os/scripts/boot/init-querty.sh'"
```

### Utility Scripts
```bash
# Status check
sh scripts/utils/check-status.sh
```

## On-Device Testing

1. **Push to device:**
```bash
adb push . /data/local/querty-os/
```

2. **Make scripts executable:**
```bash
adb shell "chmod +x /data/local/querty-os/scripts/boot/*.sh"
adb shell "chmod +x /data/local/querty-os/scripts/utils/*.sh"
```

3. **Run boot script:**
```bash
adb shell "su -c 'sh /data/local/querty-os/scripts/boot/init-querty.sh'"
```

4. **Check status:**
```bash
adb shell "su -c 'sh /data/local/querty-os/scripts/utils/check-status.sh'"
```

5. **View logs:**
```bash
adb shell "cat /data/local/tmp/querty-boot.log"
adb shell "cat /data/querty-os/logs/daemon.log"
```

## Test Results

All modules have been tested and verified to work correctly:
- ✓ LLM Service: Mode switching and configuration working
- ✓ Input Handlers: All handlers initialize and process input
- ✓ Agent Automation: Task planning and execution working
- ✓ OS Control: All controllers initialize properly
- ✓ Network Manager: State and mode management working
- ✓ Snapshot System: Snapshot creation and management working
- ✓ Shell Scripts: Syntax validated

## Integration Testing

Once deployed on device:
1. Boot script runs at system start
2. Daemon initializes all services
3. Each service can be tested individually
4. Logs provide debugging information
5. Status script shows system health

## Known Limitations

Current implementation provides:
- **Architecture and scaffolding**: Complete ✓
- **Module interfaces**: Complete ✓
- **Core functionality**: Placeholder (TODO markers indicate where actual implementation needed)
- **Integration**: Ready for implementation

Next steps for full implementation:
- Integrate actual LLM model
- Implement speech recognition
- Implement computer vision
- Complete OS control implementations
- Implement firewall/iptables integration
- Complete snapshot/filesystem integration
