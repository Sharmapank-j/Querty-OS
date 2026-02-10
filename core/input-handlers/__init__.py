"""Querty-OS Input Handlers Package"""

from .input_handlers import (
    CameraInputHandler,
    InputHandler,
    InputManager,
    TextInputHandler,
    VoiceInputHandler,
)

__version__ = "0.1.0"
__all__ = [
    "InputHandler",
    "VoiceInputHandler",
    "TextInputHandler",
    "CameraInputHandler",
    "InputManager",
]
