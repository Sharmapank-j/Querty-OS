"""Querty-OS Input Handlers Package"""
from .input_handlers import (
    InputHandler,
    VoiceInputHandler,
    TextInputHandler,
    CameraInputHandler,
    InputManager
)

__version__ = "0.1.0"
__all__ = [
    "InputHandler",
    "VoiceInputHandler",
    "TextInputHandler",
    "CameraInputHandler",
    "InputManager"
]
