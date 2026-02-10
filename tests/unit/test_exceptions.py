"""
Unit tests for Querty-OS custom exceptions.
"""

import pytest

from core.exceptions import (
    AIServiceError,
    LLMLoadError,
    PriorityViolationError,
    QuertyOSError,
    StorageError,
    StoragePriorityError,
)


class TestQuertyOSError:
    """Test base exception class."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        error = QuertyOSError("Test error")
        assert str(error) == "Test error"
        assert error.error_code == "QUERTY_UNKNOWN_ERROR"
        assert error.details == {}

    def test_exception_with_code(self):
        """Test exception with error code."""
        error = QuertyOSError("Test error", error_code="TEST_001")
        assert error.error_code == "TEST_001"

    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"component": "test", "action": "testing"}
        error = QuertyOSError("Test error", details=details)
        assert error.details == details

    def test_exception_to_dict(self):
        """Test exception serialization."""
        error = QuertyOSError("Test error", error_code="TEST_001", details={"key": "value"})
        result = error.to_dict()

        assert result["error_type"] == "QuertyOSError"
        assert result["message"] == "Test error"
        assert result["error_code"] == "TEST_001"
        assert result["details"] == {"key": "value"}


class TestAIExceptions:
    """Test AI-related exceptions."""

    def test_ai_service_error(self):
        """Test AI service error."""
        error = AIServiceError("AI service failed")
        assert isinstance(error, QuertyOSError)
        assert str(error) == "AI service failed"

    def test_llm_load_error(self):
        """Test LLM load error."""
        error = LLMLoadError("Failed to load model", error_code="LLM_001")
        assert isinstance(error, AIServiceError)
        assert error.error_code == "LLM_001"


class TestStorageExceptions:
    """Test storage-related exceptions."""

    def test_storage_error(self):
        """Test storage error."""
        error = StorageError("Storage operation failed")
        assert isinstance(error, QuertyOSError)

    def test_storage_priority_error(self):
        """Test storage priority error."""
        error = StoragePriorityError("Priority violation", error_code="STORAGE_PRI_001")
        assert isinstance(error, StorageError)
        assert error.error_code == "STORAGE_PRI_001"


class TestPriorityExceptions:
    """Test priority-related exceptions."""

    def test_priority_violation_error(self):
        """Test priority violation error."""
        details = {"requested_by": "Windows", "blocked_by": "AI"}
        error = PriorityViolationError(
            "Cannot allocate resources", error_code="PRIORITY_001", details=details
        )

        assert str(error) == "Cannot allocate resources"
        assert error.details["requested_by"] == "Windows"
        assert error.details["blocked_by"] == "AI"
