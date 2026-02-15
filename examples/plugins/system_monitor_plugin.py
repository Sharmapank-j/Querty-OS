#!/usr/bin/env python3
"""
Example System Monitor Plugin
Demonstrates a sensor plugin that monitors system resources.
"""

import psutil

from core.plugin_system import Plugin, PluginType


class SystemMonitorPlugin(Plugin):
    """System monitoring sensor plugin."""

    def __init__(self):
        super().__init__(name="System Monitor", version="1.0.0", plugin_type=PluginType.SENSOR)
        self.metadata = {
            "author": "Querty-OS Team",
            "description": "Monitor CPU, memory, and disk usage",
            "metrics": ["cpu", "memory", "disk", "all"],
        }

    def initialize(self) -> bool:
        """Initialize the system monitor plugin."""
        self.enabled = True
        return True

    def execute(self, **kwargs) -> any:
        """Get system metrics."""
        metric = kwargs.get("metric", "all")

        if metric == "cpu":
            return {"cpu_percent": psutil.cpu_percent(interval=1), "cpu_count": psutil.cpu_count()}
        elif metric == "memory":
            mem = psutil.virtual_memory()
            return {
                "total_mb": mem.total / (1024**2),
                "used_mb": mem.used / (1024**2),
                "percent": mem.percent,
            }
        elif metric == "disk":
            disk = psutil.disk_usage("/")
            return {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "percent": disk.percent,
            }
        elif metric == "all":
            return {
                "cpu": self.execute(metric="cpu"),
                "memory": self.execute(metric="memory"),
                "disk": self.execute(metric="disk"),
            }
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def shutdown(self):
        """Shutdown the system monitor plugin."""
        self.enabled = False


# Example usage
if __name__ == "__main__":
    monitor = SystemMonitorPlugin()
    monitor.initialize()

    print(f"Plugin: {monitor.get_info()}")
    print("\nSystem Metrics:")
    metrics = monitor.execute(metric="all")
    print(f"CPU: {metrics['cpu']['cpu_percent']}%")
    print(f"Memory: {metrics['memory']['percent']}%")
    print(f"Disk: {metrics['disk']['percent']}%")
