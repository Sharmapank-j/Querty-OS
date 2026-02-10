"""
Querty-OS Custom Exceptions
Provides structured error handling across all modules.
"""


class QuertyOSError(Exception):
    """Base exception for all Querty-OS errors."""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize QuertyOS exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
        """
        self.message = message
        self.error_code = error_code or "QUERTY_UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


# AI/LLM Related Exceptions
class AIServiceError(QuertyOSError):
    """Base exception for AI service errors."""

    pass


class LLMLoadError(AIServiceError):
    """Error loading LLM model."""

    pass


class LLMInferenceError(AIServiceError):
    """Error during LLM inference."""

    pass


class LLMConfigError(AIServiceError):
    """Error in LLM configuration."""

    pass


# Input Handler Exceptions
class InputHandlerError(QuertyOSError):
    """Base exception for input handler errors."""

    pass


class VoiceInputError(InputHandlerError):
    """Error in voice input processing."""

    pass


class CameraInputError(InputHandlerError):
    """Error in camera input processing."""

    pass


class TextInputError(InputHandlerError):
    """Error in text input processing."""

    pass


# OS Control Exceptions
class OSControlError(QuertyOSError):
    """Base exception for OS control errors."""

    pass


class AndroidControlError(OSControlError):
    """Error controlling Android system."""

    pass


class LinuxControlError(OSControlError):
    """Error controlling Linux chroot."""

    pass


class WineControlError(OSControlError):
    """Error controlling Wine/Windows apps."""

    pass


# Network Exceptions
class NetworkError(QuertyOSError):
    """Base exception for network errors."""

    pass


class NetworkStateError(NetworkError):
    """Error managing network state."""

    pass


class NetworkConfigError(NetworkError):
    """Error in network configuration."""

    pass


# Storage and Snapshot Exceptions
class StorageError(QuertyOSError):
    """Base exception for storage errors."""

    pass


class SnapshotError(StorageError):
    """Error in snapshot operations."""

    pass


class RollbackError(StorageError):
    """Error during rollback operations."""

    pass


class InsufficientStorageError(StorageError):
    """Insufficient storage space."""

    pass


class StoragePriorityError(StorageError):
    """Error with storage priority allocation."""

    pass


# Agent Automation Exceptions
class AgentError(QuertyOSError):
    """Base exception for agent errors."""

    pass


class TaskPlanningError(AgentError):
    """Error in task planning."""

    pass


class TaskExecutionError(AgentError):
    """Error in task execution."""

    pass


class AgentTimeoutError(AgentError):
    """Agent task timeout."""

    pass


# Configuration Exceptions
class ConfigurationError(QuertyOSError):
    """Base exception for configuration errors."""

    pass


class InvalidConfigError(ConfigurationError):
    """Invalid configuration provided."""

    pass


class MissingConfigError(ConfigurationError):
    """Required configuration missing."""

    pass


# Daemon Exceptions
class DaemonError(QuertyOSError):
    """Base exception for daemon errors."""

    pass


class ServiceInitializationError(DaemonError):
    """Error initializing a service."""

    pass


class ServiceNotReadyError(DaemonError):
    """Service is not ready for operations."""

    pass


# Priority and Resource Exceptions
class ResourceError(QuertyOSError):
    """Base exception for resource errors."""

    pass


class PriorityViolationError(ResourceError):
    """Resource allocation violates priority rules."""

    pass


class ResourceAllocationError(ResourceError):
    """Error allocating resources."""

    pass


class ResourceExhaustedError(ResourceError):
    """System resources exhausted."""

    pass
