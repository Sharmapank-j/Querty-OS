# Network Manager

Network connectivity management with per-app internet control for Querty-OS.

## Overview

The network manager provides fine-grained control over internet connectivity, enabling users to manage network access at the system and per-app level.

## Features

### Global Network Control
- **Enable/Disable Internet**: Toggle internet for entire system
- **Network Modes**: Full access, selective, or offline
- **Quick Toggle**: Instant offline mode activation

### Per-App Control
- **Selective Access**: Allow specific apps while blocking others
- **Allow List**: Whitelist apps for internet access
- **Block List**: Blacklist apps from internet access
- **Real-time Updates**: Apply rules without restart

### VPN Support
- **VPN Integration**: Enable/disable VPN connections
- **VPN Status**: Monitor VPN connection state
- **Split Tunneling**: Route specific apps through VPN (TODO)

### Traffic Monitoring
- **Bandwidth Usage**: Track data usage per app
- **Traffic Statistics**: Monitor packets and bytes
- **Usage History**: Historical traffic data (TODO)

## Network Modes

### 1. Full Access Mode
All apps have internet access by default, except explicitly blocked apps.
```
Default: ✓ Internet for all
Blocked apps: ✗ No internet
```

### 2. Selective Mode
Only explicitly allowed apps have internet access.
```
Default: ✗ No internet
Allowed apps: ✓ Internet access
```

### 3. Offline Mode
Complete internet shutdown, no apps have access.
```
All apps: ✗ No internet
System: ✗ No internet
```

## Architecture

```
network-manager/
├── network_manager.py    # Main network manager implementation
├── firewall_control.py   # Firewall/iptables integration (TODO)
├── vpn_manager.py        # VPN management (TODO)
├── traffic_monitor.py    # Traffic monitoring (TODO)
└── dns_manager.py        # DNS configuration (TODO)
```

## Usage

```python
from core.network_manager import NetworkManager, NetworkMode

# Create network manager
nm = NetworkManager()

# Disable all internet
nm.disable_internet()

# Enable selective mode
nm.set_mode(NetworkMode.SELECTIVE)
nm.allow_app('com.android.chrome')
nm.allow_app('com.example.email')

# Check app access
if nm.is_app_allowed('com.android.chrome'):
    print("Chrome has internet access")

# Enable VPN
nm.enable_vpn({'server': 'vpn.example.com'})

# Monitor traffic
stats = nm.monitor_traffic('com.android.chrome')
print(f"Chrome usage: {stats['bytes_sent']} bytes sent")

# Re-enable full internet
nm.enable_internet()
```

## Use Cases

### Focus Mode
Block all distracting apps:
```python
nm.set_mode(NetworkMode.SELECTIVE)
nm.allow_app('com.example.worktool')
nm.allow_app('com.example.productivity')
```

### Privacy Mode
Disable internet for privacy-sensitive apps:
```python
nm.block_app('com.example.social')
nm.block_app('com.example.tracker')
```

### Emergency Offline
Quickly go completely offline:
```python
nm.disable_internet()
```

### Data Saver
Limit background data:
```python
nm.set_mode(NetworkMode.SELECTIVE)
# Only allow foreground app
```

## Implementation Details

### Android Integration
- Uses Android `ConnectivityManager`
- Configures `NetworkPolicyManager`
- Implements firewall via iptables

### Firewall Rules
```bash
# Block app by UID
iptables -A OUTPUT -m owner --uid-owner <APP_UID> -j REJECT

# Allow app by UID
iptables -A OUTPUT -m owner --uid-owner <APP_UID> -j ACCEPT
```

### Permissions Required
- `android.permission.INTERNET`
- `android.permission.ACCESS_NETWORK_STATE`
- `android.permission.CHANGE_NETWORK_STATE`
- Root access for iptables manipulation

## Configuration

Settings in `/etc/querty-os/network-manager.conf`:
- Default network mode
- Persistent allow/block lists
- VPN settings
- Traffic monitoring interval
- DNS servers

## Development Status

- [x] Network manager structure
- [x] Mode switching
- [x] Per-app control logic
- [ ] Firewall integration (iptables)
- [ ] VPN implementation
- [ ] Traffic monitoring
- [ ] Persistence (save/load state)
- [ ] UI integration
