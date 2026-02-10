"""Querty-OS OS Control Package"""

from .os_control import (
    AndroidController,
    LinuxController,
    OSController,
    OSControlManager,
    WineController,
)

__version__ = "0.1.0"
__all__ = [
    "OSController",
    "AndroidController",
    "LinuxController",
    "WineController",
    "OSControlManager",
]
