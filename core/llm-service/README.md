# LLM Service

Local Large Language Model service with dual execution modes for Querty-OS.

## Overview

The LLM service provides on-device AI inference with two distinct modes optimized for different use cases.

## Modes

### Deterministic Mode
- **Use Case**: System automation, reproducible tasks
- **Characteristics**:
  - Step-bound execution
  - Reproducible outputs (fixed seed)
  - Zero temperature (no randomness)
  - Consistent behavior across runs
- **Best For**: System commands, scripting, critical operations

### Creative Mode
- **Use Case**: User interactions, content generation
- **Characteristics**:
  - Flexible execution
  - Varied outputs
  - Higher temperature (controlled randomness)
  - More diverse responses
- **Best For**: Conversations, creative tasks, exploration

## Architecture

```
llm-service/
├── llm_service.py       # Main LLM service implementation
├── model_loader.py      # Model loading and management (TODO)
├── inference_engine.py  # Inference optimization (TODO)
└── tokenizer.py         # Text tokenization (TODO)
```

## Usage

```python
from core.llm_service import LLMService, LLMMode

# Create service
llm = LLMService()
llm.load_model("/path/to/model")

# Deterministic mode for system tasks
llm.set_mode(LLMMode.DETERMINISTIC)
response = llm.generate("List all running services")

# Creative mode for user interaction
llm.set_mode(LLMMode.CREATIVE)
response = llm.generate("Tell me about your capabilities")
```

## Model Support

The service is designed to work with:
- GGUF quantized models
- ONNX models
- TensorFlow Lite models
- Custom optimized models

## Performance Optimization

- Model quantization (INT8, INT4)
- Batched inference
- KV cache optimization
- GPU acceleration (when available)

## Configuration

Configuration options in `/etc/querty-os/llm-service.conf`:
- Model path
- Quantization level
- Context window size
- GPU/CPU allocation
- Memory limits

## Development Status

- [x] Service structure
- [x] Mode configuration
- [ ] Model loading
- [ ] Inference engine
- [ ] GPU acceleration
- [ ] Context management
- [ ] Performance optimization
