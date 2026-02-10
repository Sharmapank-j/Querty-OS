# Input Handlers

Multi-modal input processing system for Querty-OS.

## Overview

The input handlers module provides a unified interface for processing voice, text, and camera input, enabling natural interaction with the AI system.

## Supported Input Types

### 1. Voice Input
- **Speech Recognition**: Convert voice to text
- **Wake Word Detection**: Hands-free activation
- **Continuous Listening**: Always-on mode (optional)
- **Multi-language Support**: Support for various languages
- **Noise Cancellation**: Background noise filtering

### 2. Text Input
- **Command-line Interface**: Direct text commands
- **Natural Language Processing**: Understand intent
- **Command History**: Track previous commands
- **Autocomplete**: Command suggestions
- **Scripting Support**: Batch command execution

### 3. Camera Input
- **Scene Understanding**: Analyze visual context
- **Object Detection**: Identify objects in view
- **Text Recognition (OCR)**: Read text from images
- **QR/Barcode Scanning**: Quick information capture
- **Privacy Controls**: User-controlled image processing

## Architecture

```
input-handlers/
├── input_handlers.py    # Main input handlers implementation
├── voice_processor.py   # Speech recognition (TODO)
├── text_parser.py       # Natural language parsing (TODO)
├── vision_processor.py  # Computer vision (TODO)
└── input_fusion.py      # Multi-modal input fusion (TODO)
```

## Usage

```python
from core.input_handlers import InputManager

# Create input manager
manager = InputManager()
manager.start_all()

# Process voice input
voice_handler = manager.get_handler('voice')
result = voice_handler.process_input(audio_data)

# Process text input
text_handler = manager.get_handler('text')
result = text_handler.process_input("show me running apps")

# Process camera input
camera_handler = manager.get_handler('camera')
frame = camera_handler.capture_frame()
result = camera_handler.analyze_scene(frame)

manager.stop_all()
```

## Input Processing Pipeline

1. **Raw Input Capture**: Capture from device (mic, keyboard, camera)
2. **Preprocessing**: Noise reduction, normalization
3. **Recognition/Analysis**: Convert to structured data
4. **Intent Detection**: Understand user intention
5. **Context Integration**: Combine with system state
6. **Action Routing**: Send to appropriate handler

## Privacy & Security

- **On-device Processing**: All processing happens locally
- **User Control**: Explicit permission for each input type
- **Data Retention**: Configurable retention policies
- **Secure Storage**: Encrypted storage for sensitive data

## Configuration

Settings in `/etc/querty-os/input-handlers.conf`:
- Enable/disable specific handlers
- Wake word configuration
- Camera resolution and FPS
- Privacy settings

## Development Status

- [x] Handler architecture
- [x] Input manager
- [ ] Voice recognition implementation
- [ ] Vision processing implementation
- [ ] Multi-modal fusion
- [ ] Privacy controls
- [ ] Performance optimization
