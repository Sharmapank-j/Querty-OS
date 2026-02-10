# Error Handling and AI-Assisted Development Guide

## Overview

This guide explains how to handle errors in Querty-OS and leverage AI assistance for debugging and development.

## Priority System

Querty-OS operates with a strict priority system:

**AI > Android > Linux > Windows**

All error handling and resource allocation follows this hierarchy.

## Custom Exceptions

### Using Custom Exceptions

```python
from core.exceptions import AIServiceError, LLMLoadError

try:
    result = load_llm_model(model_path)
except FileNotFoundError as e:
    raise LLMLoadError(
        f"Model file not found: {model_path}",
        error_code="LLM_001",
        details={"path": model_path, "error": str(e)}
    )
```

### Exception Hierarchy

```
QuertyOSError (base)
├── AIServiceError
│   ├── LLMLoadError
│   ├── LLMInferenceError
│   └── LLMConfigError
├── InputHandlerError
│   ├── VoiceInputError
│   ├── CameraInputError
│   └── TextInputError
├── OSControlError
│   ├── AndroidControlError
│   ├── LinuxControlError
│   └── WineControlError
├── NetworkError
│   ├── NetworkStateError
│   └── NetworkConfigError
├── StorageError
│   ├── SnapshotError
│   ├── RollbackError
│   ├── InsufficientStorageError
│   └── StoragePriorityError
├── AgentError
│   ├── TaskPlanningError
│   ├── TaskExecutionError
│   └── AgentTimeoutError
├── ConfigurationError
│   ├── InvalidConfigError
│   └── MissingConfigError
├── DaemonError
│   ├── ServiceInitializationError
│   └── ServiceNotReadyError
└── ResourceError
    ├── PriorityViolationError
    ├── ResourceAllocationError
    └── ResourceExhaustedError
```

## Error Handling Patterns

### 1. Service Initialization

```python
from core.exceptions import ServiceInitializationError
import logging

logger = logging.getLogger(__name__)

def initialize_service(config):
    """Initialize a service with proper error handling."""
    try:
        # Attempt initialization
        service = Service(config)
        service.start()
        logger.info("Service initialized successfully")
        return service
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}", exc_info=True)
        raise ServiceInitializationError(
            "Service initialization failed",
            error_code="SVC_INIT_001",
            details={
                "service": "ServiceName",
                "config": config,
                "error": str(e)
            }
        )
```

### 2. Resource Allocation with Priority

```python
from core.priority import SystemPriority, ResourcePriority
from core.exceptions import PriorityViolationError

def allocate_resource(requester_priority: SystemPriority, amount: int):
    """Allocate resource respecting priority."""
    rp = ResourcePriority()
    
    # Check if allocation violates priority rules
    if not rp.can_allocate(requester_priority, amount):
        raise PriorityViolationError(
            f"Cannot allocate {amount} to {requester_priority.name}",
            error_code="PRIORITY_001",
            details={
                "requested_by": requester_priority.name,
                "amount": amount,
                "reason": "Insufficient resources for priority level"
            }
        )
    
    # Perform allocation
    return perform_allocation(amount)
```

### 3. Retry with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    logger.warning(
                        f"Retry {retries}/{max_retries} after {delay}s: {e}"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def load_model():
    """Load model with automatic retry."""
    pass
```

### 4. Context Managers for Resource Cleanup

```python
from contextlib import contextmanager

@contextmanager
def managed_service(service_name):
    """Context manager for service lifecycle."""
    service = None
    try:
        logger.info(f"Starting {service_name}")
        service = initialize_service(service_name)
        yield service
        
    except Exception as e:
        logger.error(f"Error in {service_name}: {e}")
        raise
        
    finally:
        if service:
            logger.info(f"Stopping {service_name}")
            service.stop()

# Usage
with managed_service("LLM") as llm:
    result = llm.generate("test prompt")
```

## AI-Assisted Error Resolution

### 1. Error Reporting Format

When reporting errors to AI for assistance:

```python
error_report = {
    "timestamp": "2024-02-10T12:00:00Z",
    "component": "LLM Service",
    "priority": "AI",  # AI > Android > Linux > Windows
    "error_type": "LLMLoadError",
    "error_code": "LLM_001",
    "message": "Failed to load model",
    "details": {
        "model_path": "/path/to/model",
        "error": "FileNotFoundError",
    },
    "stack_trace": "...",
    "system_state": {
        "available_memory": "8GB",
        "storage_available": "20GB",
        "cpu_usage": "45%",
    },
}
```

### 2. Self-Healing Patterns

```python
class SelfHealingService:
    """Service with self-healing capabilities."""
    
    def __init__(self):
        self.failure_count = 0
        self.max_failures = 3
    
    def execute(self, task):
        """Execute task with self-healing."""
        try:
            return self._do_execute(task)
            
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Task failed ({self.failure_count}/{self.max_failures}): {e}")
            
            if self.failure_count < self.max_failures:
                # Attempt self-healing
                self.heal()
                return self.execute(task)  # Retry after healing
            else:
                # Give up and escalate
                raise
    
    def heal(self):
        """Attempt to heal service."""
        logger.info("Attempting self-healing...")
        # Reset state, clear caches, restart subsystems, etc.
        self.reset_state()
        self.failure_count = 0
```

### 3. Diagnostic Information

```python
def get_diagnostic_info():
    """Collect diagnostic information for AI analysis."""
    return {
        "system": {
            "os": platform.system(),
            "python_version": sys.version,
            "cpu_count": os.cpu_count(),
        },
        "resources": {
            "memory_available": psutil.virtual_memory().available,
            "disk_available": psutil.disk_usage('/').free,
        },
        "services": {
            "ai_daemon": check_service_status("ai-daemon"),
            "llm_service": check_service_status("llm-service"),
        },
        "priorities": {
            "ai_allocation": get_allocation(SystemPriority.AI),
            "android_allocation": get_allocation(SystemPriority.ANDROID),
        },
    }
```

## Logging Best Practices

### 1. Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Good: Structured with context
logger.info(
    "service_started",
    service="LLM",
    priority="AI",
    mode="deterministic",
    model="llama-7b"
)

# Bad: Unstructured string
logger.info("LLM service started in deterministic mode with llama-7b")
```

### 2. Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical system failures

### 3. Context Propagation

```python
from contextvars import ContextVar

request_id = ContextVar('request_id', default=None)

def process_request(req_id, data):
    """Process request with context."""
    request_id.set(req_id)
    
    logger.info(
        "processing_request",
        request_id=request_id.get(),
        data_size=len(data)
    )
    
    try:
        result = process(data)
        logger.info("request_completed", request_id=request_id.get())
        return result
        
    except Exception as e:
        logger.error(
            "request_failed",
            request_id=request_id.get(),
            error=str(e)
        )
        raise
```

## User Feedback Integration

### 1. Error Feedback Loop

```python
class ErrorFeedbackCollector:
    """Collect user feedback on errors for AI learning."""
    
    def report_error(self, error, user_feedback=None):
        """Report error with optional user feedback."""
        report = {
            "error": error.to_dict(),
            "timestamp": time.time(),
            "user_feedback": user_feedback,
            "resolved": False,
        }
        
        # Store for AI analysis
        self.store_feedback(report)
        
        # If user provided feedback, use it for improvement
        if user_feedback:
            self.learn_from_feedback(report)
```

### 2. Interactive Error Resolution

```python
def interactive_error_handler(error):
    """Handle error with user interaction."""
    print(f"Error occurred: {error.message}")
    print(f"Error code: {error.error_code}")
    
    # Suggest fixes based on error type
    suggestions = get_fix_suggestions(error)
    
    print("\nSuggested fixes:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    choice = input("\nSelect fix (1-{}) or 'c' to cancel: ".format(len(suggestions)))
    
    if choice.isdigit():
        apply_fix(suggestions[int(choice) - 1])
    
    return None
```

## Testing Error Handling

### 1. Test Exception Raising

```python
def test_llm_load_error():
    """Test LLM load error handling."""
    with pytest.raises(LLMLoadError) as exc_info:
        load_invalid_model()
    
    assert exc_info.value.error_code == "LLM_001"
    assert "not found" in str(exc_info.value)
```

### 2. Test Recovery Mechanisms

```python
def test_service_recovery():
    """Test service recovers from failure."""
    service = SelfHealingService()
    
    # Simulate failure
    with patch.object(service, '_do_execute', side_effect=Exception("Test error")):
        # First few attempts should trigger healing
        service.failure_count = 0
        
        # Should recover after healing
        with patch.object(service, 'heal'):
            # Test recovery logic
            pass
```

## Priority System Testing

```python
def test_priority_enforcement():
    """Test priority system is enforced."""
    rp = ResourcePriority()
    
    # AI should preempt Windows
    assert rp.should_preempt(
        SystemPriority.WINDOWS,
        SystemPriority.AI
    ) is True
    
    # Windows should not preempt AI
    assert rp.should_preempt(
        SystemPriority.AI,
        SystemPriority.WINDOWS
    ) is False
```

## Summary

- Use custom exceptions for structured error handling
- Follow priority system: AI > Android > Linux > Windows
- Implement retry mechanisms for transient failures
- Use structured logging for better analysis
- Enable AI-assisted error resolution through comprehensive diagnostics
- Collect user feedback for continuous improvement
- Write comprehensive tests for error scenarios
