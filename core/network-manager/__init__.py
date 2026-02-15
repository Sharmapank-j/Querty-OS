"""Querty-OS Network Manager Package"""

from .firewall_control import (
    AppNetworkPolicy,
    Chain,
    FirewallAction,
    FirewallControl,
    FirewallRule,
    Protocol,
)
from .network_manager import NetworkManager, NetworkMode, NetworkState
from .traffic_monitor import (
    AppTrafficStats,
    InterfaceStats,
    TimeWindow,
    TrafficDirection,
    TrafficMonitor,
    TrafficSnapshot,
)
from .vpn_manager import VPNConfig, VPNConnection, VPNManager, VPNProtocol, VPNState

__version__ = "0.1.0"
__all__ = [
    "NetworkManager",
    "NetworkState",
    "NetworkMode",
    "FirewallControl",
    "FirewallRule",
    "FirewallAction",
    "Protocol",
    "Chain",
    "AppNetworkPolicy",
    "VPNManager",
    "VPNConfig",
    "VPNConnection",
    "VPNProtocol",
    "VPNState",
    "TrafficMonitor",
    "InterfaceStats",
    "AppTrafficStats",
    "TrafficSnapshot",
    "TrafficDirection",
    "TimeWindow",
]
