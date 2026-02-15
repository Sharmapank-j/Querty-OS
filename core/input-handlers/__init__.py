"""Querty-OS Input Handlers Package"""

from .input_fusion import (
    FusedResult,
    FusionStrategy,
    InputFusion,
    InputModality,
    InputResult,
)
from .input_handlers import (
    CameraInputHandler,
    InputHandler,
    InputManager,
    TextInputHandler,
    VoiceInputHandler,
)
from .text_parser import Entity, Intent, ParsedCommand, TextParser

__version__ = "0.1.0"
__all__ = [
    "InputHandler",
    "VoiceInputHandler",
    "TextInputHandler",
    "CameraInputHandler",
    "InputManager",
    "TextParser",
    "Intent",
    "Entity",
    "ParsedCommand",
    "InputFusion",
    "InputResult",
    "FusedResult",
    "InputModality",
    "FusionStrategy",
]
