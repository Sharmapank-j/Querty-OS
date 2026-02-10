"""
Test fixtures for Querty-OS test suite.
"""

from unittest.mock import MagicMock, Mock

import pytest

from core.priority import ResourcePriority, StoragePriorityManager, SystemPriority


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def resource_priority():
    """Resource priority instance."""
    return ResourcePriority()


@pytest.fixture
def storage_manager():
    """Storage priority manager with 100GB storage."""
    return StoragePriorityManager(total_storage_gb=100.0)


@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "daemon": {
            "log_level": "INFO",
            "log_file": "/tmp/test-daemon.log",
            "pid_file": "/tmp/test-daemon.pid",
        },
        "llm": {
            "model_path": "/tmp/test-model.gguf",
            "default_mode": "deterministic",
        },
        "priority": {
            "ai_allocation": 40,
            "android_allocation": 35,
            "linux_allocation": 15,
            "windows_allocation": 10,
        },
    }


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    service = Mock()
    service.load_model.return_value = True
    service.generate.return_value = "Test response"
    return service


@pytest.fixture
def mock_input_handler():
    """Mock input handler."""
    handler = Mock()
    handler.start.return_value = True
    handler.stop.return_value = None
    handler.process_input.return_value = {
        "type": "text",
        "content": "test input",
    }
    return handler
