"""Compatibility package for the Querty AI daemon."""

from .daemon import DaemonWatchdog, QuertyAIDaemon, main

__all__ = ["main", "QuertyAIDaemon", "DaemonWatchdog"]
