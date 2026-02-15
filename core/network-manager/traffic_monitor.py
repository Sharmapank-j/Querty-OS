"""
Network traffic monitoring and statistics.
Provides real-time and historical network usage tracking.
"""

import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

from core.exceptions import NetworkError

logger = logging.getLogger(__name__)


class TrafficDirection(Enum):
    """Traffic direction."""

    SENT = "sent"
    RECEIVED = "received"
    BOTH = "both"


class TimeWindow(Enum):
    """Time window for statistics."""

    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800


@dataclass
class InterfaceStats:
    """Network interface statistics."""

    interface: str
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    errors_sent: int = 0
    errors_received: int = 0
    drops_sent: int = 0
    drops_received: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def total_bytes(self) -> int:
        """Total bytes (sent + received)."""
        return self.bytes_sent + self.bytes_received

    @property
    def total_packets(self) -> int:
        """Total packets (sent + received)."""
        return self.packets_sent + self.packets_received


@dataclass
class AppTrafficStats:
    """Application traffic statistics."""

    app_name: str
    uid: int
    bytes_sent: int = 0
    bytes_received: int = 0
    connections_active: int = 0
    connections_total: int = 0
    last_activity: Optional[float] = None

    @property
    def total_bytes(self) -> int:
        """Total bytes (sent + received)."""
        return self.bytes_sent + self.bytes_received


@dataclass
class TrafficSnapshot:
    """Point-in-time traffic snapshot."""

    timestamp: float
    interface_stats: Dict[str, InterfaceStats]
    app_stats: Dict[str, AppTrafficStats]
    total_bytes_sent: int = 0
    total_bytes_received: int = 0


class TrafficMonitor:
    """Network traffic monitoring and statistics."""

    def __init__(
        self,
        history_size: int = 1000,
        sample_interval: int = 5,
        proc_net_dev: str = "/proc/net/dev",
    ):
        """
        Initialize traffic monitor.

        Args:
            history_size: Number of snapshots to keep in history
            sample_interval: Sampling interval in seconds
            proc_net_dev: Path to /proc/net/dev
        """
        self.history_size = history_size
        self.sample_interval = sample_interval
        self.proc_net_dev = Path(proc_net_dev)

        self.interface_history: Deque[Dict[str, InterfaceStats]] = deque(maxlen=history_size)
        self.app_history: Deque[Dict[str, AppTrafficStats]] = deque(maxlen=history_size)
        self.snapshots: Deque[TrafficSnapshot] = deque(maxlen=history_size)

        self.current_interface_stats: Dict[str, InterfaceStats] = {}
        self.current_app_stats: Dict[str, AppTrafficStats] = {}
        self._baseline_stats: Dict[str, InterfaceStats] = {}

        logger.info(f"Initialized TrafficMonitor (interval={sample_interval}s)")

    def _read_interface_stats(self) -> Dict[str, InterfaceStats]:
        """
        Read interface statistics from /proc/net/dev.

        Returns:
            Dictionary mapping interface name to InterfaceStats
        """
        stats = {}

        if not self.proc_net_dev.exists():
            logger.warning(f"/proc/net/dev not found: {self.proc_net_dev}")
            return stats

        try:
            with open(self.proc_net_dev, "r") as f:
                lines = f.readlines()

            # Skip header lines
            for line in lines[2:]:
                parts = line.split(":")
                if len(parts) != 2:
                    continue

                interface = parts[0].strip()
                values = parts[1].split()

                if len(values) < 16:
                    continue

                stats[interface] = InterfaceStats(
                    interface=interface,
                    bytes_received=int(values[0]),
                    packets_received=int(values[1]),
                    errors_received=int(values[2]),
                    drops_received=int(values[3]),
                    bytes_sent=int(values[8]),
                    packets_sent=int(values[9]),
                    errors_sent=int(values[10]),
                    drops_sent=int(values[11]),
                )

        except Exception as e:
            logger.error(f"Failed to read interface stats: {e}")

        return stats

    def _read_app_stats(self) -> Dict[str, AppTrafficStats]:
        """
        Read application traffic statistics.

        Note: This requires Android-specific APIs or xt_qtaguid kernel module.
        This is a simplified implementation.

        Returns:
            Dictionary mapping app name to AppTrafficStats
        """
        stats = {}

        # On Android, would read from /proc/net/xt_qtaguid/stats
        qtaguid_stats = Path("/proc/net/xt_qtaguid/stats")

        if not qtaguid_stats.exists():
            # Not on Android or xt_qtaguid not available
            return stats

        try:
            with open(qtaguid_stats, "r") as f:
                lines = f.readlines()

            # Parse qtaguid stats
            # Format: idx iface acct_tag_hex uid_tag_int cnt_set rx_bytes rx_packets ...
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) < 8:
                    continue

                uid = int(parts[3])
                rx_bytes = int(parts[5])
                tx_bytes = int(parts[7]) if len(parts) > 7 else 0

                # Would map UID to app name in real implementation
                app_name = f"uid_{uid}"

                if app_name in stats:
                    stats[app_name].bytes_received += rx_bytes
                    stats[app_name].bytes_sent += tx_bytes
                else:
                    stats[app_name] = AppTrafficStats(
                        app_name=app_name,
                        uid=uid,
                        bytes_received=rx_bytes,
                        bytes_sent=tx_bytes,
                        last_activity=time.time(),
                    )

        except Exception as e:
            logger.error(f"Failed to read app stats: {e}")

        return stats

    def sample(self) -> TrafficSnapshot:
        """
        Take a traffic sample.

        Returns:
            TrafficSnapshot object
        """
        # Read current stats
        interface_stats = self._read_interface_stats()
        app_stats = self._read_app_stats()

        # Calculate totals
        total_sent = sum(s.bytes_sent for s in interface_stats.values())
        total_received = sum(s.bytes_received for s in interface_stats.values())

        # Create snapshot
        snapshot = TrafficSnapshot(
            timestamp=time.time(),
            interface_stats=interface_stats,
            app_stats=app_stats,
            total_bytes_sent=total_sent,
            total_bytes_received=total_received,
        )

        # Update current stats
        self.current_interface_stats = interface_stats
        self.current_app_stats = app_stats

        # Add to history
        self.interface_history.append(interface_stats.copy())
        self.app_history.append(app_stats.copy())
        self.snapshots.append(snapshot)

        logger.debug(f"Sampled traffic: {len(interface_stats)} interfaces, {len(app_stats)} apps")
        return snapshot

    def get_interface_stats(self, interface: str) -> Optional[InterfaceStats]:
        """
        Get current statistics for an interface.

        Args:
            interface: Interface name

        Returns:
            InterfaceStats or None if interface not found
        """
        return self.current_interface_stats.get(interface)

    def get_app_stats(self, app_name: str) -> Optional[AppTrafficStats]:
        """
        Get current statistics for an application.

        Args:
            app_name: Application name

        Returns:
            AppTrafficStats or None if app not found
        """
        return self.current_app_stats.get(app_name)

    def list_interfaces(self) -> List[str]:
        """
        List monitored interfaces.

        Returns:
            List of interface names
        """
        return list(self.current_interface_stats.keys())

    def list_apps(self) -> List[str]:
        """
        List applications with traffic.

        Returns:
            List of application names
        """
        return list(self.current_app_stats.keys())

    def get_interface_rate(
        self, interface: str, window: TimeWindow = TimeWindow.MINUTE
    ) -> Tuple[float, float]:
        """
        Calculate data rate for an interface.

        Args:
            interface: Interface name
            window: Time window for calculation

        Returns:
            Tuple of (send_rate_bps, receive_rate_bps) or (0.0, 0.0) if not enough data
        """
        if len(self.snapshots) < 2:
            return (0.0, 0.0)

        # Find snapshots within time window
        now = time.time()
        window_start = now - window.value

        relevant_snapshots = [s for s in self.snapshots if s.timestamp >= window_start]

        if len(relevant_snapshots) < 2:
            return (0.0, 0.0)

        # Calculate rate from first to last snapshot in window
        first_snapshot = relevant_snapshots[0]
        last_snapshot = relevant_snapshots[-1]

        first_stats = first_snapshot.interface_stats.get(interface)
        last_stats = last_snapshot.interface_stats.get(interface)

        if not first_stats or not last_stats:
            return (0.0, 0.0)

        time_delta = last_snapshot.timestamp - first_snapshot.timestamp
        if time_delta == 0:
            return (0.0, 0.0)

        send_rate = (last_stats.bytes_sent - first_stats.bytes_sent) / time_delta
        recv_rate = (last_stats.bytes_received - first_stats.bytes_received) / time_delta

        return (send_rate, recv_rate)

    def get_app_rate(
        self, app_name: str, window: TimeWindow = TimeWindow.MINUTE
    ) -> Tuple[float, float]:
        """
        Calculate data rate for an application.

        Args:
            app_name: Application name
            window: Time window for calculation

        Returns:
            Tuple of (send_rate_bps, receive_rate_bps) or (0.0, 0.0) if not enough data
        """
        if len(self.snapshots) < 2:
            return (0.0, 0.0)

        now = time.time()
        window_start = now - window.value

        relevant_snapshots = [s for s in self.snapshots if s.timestamp >= window_start]

        if len(relevant_snapshots) < 2:
            return (0.0, 0.0)

        first_snapshot = relevant_snapshots[0]
        last_snapshot = relevant_snapshots[-1]

        first_stats = first_snapshot.app_stats.get(app_name)
        last_stats = last_snapshot.app_stats.get(app_name)

        if not first_stats or not last_stats:
            return (0.0, 0.0)

        time_delta = last_snapshot.timestamp - first_snapshot.timestamp
        if time_delta == 0:
            return (0.0, 0.0)

        send_rate = (last_stats.bytes_sent - first_stats.bytes_sent) / time_delta
        recv_rate = (last_stats.bytes_received - first_stats.bytes_received) / time_delta

        return (send_rate, recv_rate)

    def get_total_usage(
        self, interface: Optional[str] = None, since: Optional[float] = None
    ) -> Tuple[int, int]:
        """
        Get total usage for interface or all interfaces.

        Args:
            interface: Interface name, or None for all
            since: Unix timestamp to calculate from, or None for current totals

        Returns:
            Tuple of (bytes_sent, bytes_received)
        """
        if not since:
            # Return current totals
            if interface:
                stats = self.current_interface_stats.get(interface)
                if stats:
                    return (stats.bytes_sent, stats.bytes_received)
                return (0, 0)
            else:
                total_sent = sum(s.bytes_sent for s in self.current_interface_stats.values())
                total_recv = sum(s.bytes_received for s in self.current_interface_stats.values())
                return (total_sent, total_recv)

        # Calculate usage since timestamp
        relevant_snapshots = [s for s in self.snapshots if s.timestamp >= since]

        if not relevant_snapshots:
            return (0, 0)

        first_snapshot = relevant_snapshots[0]
        last_snapshot = relevant_snapshots[-1]

        if interface:
            first_stats = first_snapshot.interface_stats.get(interface)
            last_stats = last_snapshot.interface_stats.get(interface)

            if not first_stats or not last_stats:
                return (0, 0)

            bytes_sent = last_stats.bytes_sent - first_stats.bytes_sent
            bytes_recv = last_stats.bytes_received - first_stats.bytes_received
            return (max(0, bytes_sent), max(0, bytes_recv))
        else:
            bytes_sent = last_snapshot.total_bytes_sent - first_snapshot.total_bytes_sent
            bytes_recv = last_snapshot.total_bytes_received - first_snapshot.total_bytes_received
            return (max(0, bytes_sent), max(0, bytes_recv))

    def get_top_apps(
        self, limit: int = 10, direction: TrafficDirection = TrafficDirection.BOTH
    ) -> List[AppTrafficStats]:
        """
        Get top applications by traffic usage.

        Args:
            limit: Maximum number of apps to return
            direction: Traffic direction to consider

        Returns:
            List of AppTrafficStats sorted by usage
        """
        apps = list(self.current_app_stats.values())

        if direction == TrafficDirection.SENT:
            apps.sort(key=lambda x: x.bytes_sent, reverse=True)
        elif direction == TrafficDirection.RECEIVED:
            apps.sort(key=lambda x: x.bytes_received, reverse=True)
        else:  # BOTH
            apps.sort(key=lambda x: x.total_bytes, reverse=True)

        return apps[:limit]

    def reset_baseline(self, interface: Optional[str] = None) -> None:
        """
        Reset baseline for relative measurements.

        Args:
            interface: Interface to reset, or None for all
        """
        if interface:
            if interface in self.current_interface_stats:
                self._baseline_stats[interface] = self.current_interface_stats[interface]
                logger.info(f"Reset baseline for interface: {interface}")
        else:
            self._baseline_stats = self.current_interface_stats.copy()
            logger.info("Reset baseline for all interfaces")

    def get_usage_since_baseline(self, interface: str) -> Tuple[int, int]:
        """
        Get usage since baseline was set.

        Args:
            interface: Interface name

        Returns:
            Tuple of (bytes_sent, bytes_received) since baseline
        """
        current = self.current_interface_stats.get(interface)
        baseline = self._baseline_stats.get(interface)

        if not current or not baseline:
            return (0, 0)

        bytes_sent = current.bytes_sent - baseline.bytes_sent
        bytes_recv = current.bytes_received - baseline.bytes_received

        return (max(0, bytes_sent), max(0, bytes_recv))

    def clear_history(self) -> None:
        """Clear all historical data."""
        self.interface_history.clear()
        self.app_history.clear()
        self.snapshots.clear()
        logger.info("Cleared traffic history")

    def export_stats(self, output_file: str) -> bool:
        """
        Export statistics to file.

        Args:
            output_file: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, "w") as f:
                f.write("# Network Traffic Statistics\n")
                f.write(f"# Timestamp: {time.time()}\n\n")

                # Write interface stats
                f.write("## Interface Statistics\n")
                for iface, stats in self.current_interface_stats.items():
                    f.write(f"\n### {iface}\n")
                    f.write(f"Bytes Sent: {stats.bytes_sent}\n")
                    f.write(f"Bytes Received: {stats.bytes_received}\n")
                    f.write(f"Packets Sent: {stats.packets_sent}\n")
                    f.write(f"Packets Received: {stats.packets_received}\n")

                # Write app stats
                f.write("\n## Application Statistics\n")
                for app_name, stats in self.current_app_stats.items():
                    f.write(f"\n### {app_name}\n")
                    f.write(f"UID: {stats.uid}\n")
                    f.write(f"Bytes Sent: {stats.bytes_sent}\n")
                    f.write(f"Bytes Received: {stats.bytes_received}\n")

            logger.info(f"Exported traffic stats to: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export stats: {e}")
            return False
