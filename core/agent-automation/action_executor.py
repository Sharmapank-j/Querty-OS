"""
Action Executor for Agent Automation

Executes actions with dry-run support, rollback capability, and comprehensive logging.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.exceptions import TaskExecutionError

logger = logging.getLogger(__name__)


class ActionStatus(Enum):
    """Action execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    DRY_RUN = "dry_run"


@dataclass
class ActionResult:
    """Result of an action execution."""

    action_id: str
    status: ActionStatus
    output: Any = None
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    rollback_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
        }


class Action(ABC):
    """Abstract base class for executable actions."""

    def __init__(self, action_id: str, description: str = ""):
        """
        Initialize action.

        Args:
            action_id: Unique action identifier
            description: Human-readable description
        """
        self.action_id = action_id
        self.description = description

    @abstractmethod
    def execute(self) -> Any:
        """
        Execute the action.

        Returns:
            Action output

        Raises:
            TaskExecutionError: If execution fails
        """
        pass

    @abstractmethod
    def rollback(self, rollback_data: Dict[str, Any]) -> None:
        """
        Rollback the action.

        Args:
            rollback_data: Data needed for rollback

        Raises:
            TaskExecutionError: If rollback fails
        """
        pass

    @abstractmethod
    def dry_run(self) -> Dict[str, Any]:
        """
        Simulate execution without making changes.

        Returns:
            Dictionary describing what would be done
        """
        pass


class CommandAction(Action):
    """Action that executes a shell command."""

    def __init__(self, action_id: str, command: str, description: str = ""):
        """
        Initialize command action.

        Args:
            action_id: Unique action identifier
            command: Shell command to execute
            description: Human-readable description
        """
        super().__init__(action_id, description)
        self.command = command

    def execute(self) -> str:
        """Execute the command."""
        import subprocess

        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                raise TaskExecutionError(
                    f"Command failed: {result.stderr}",
                    error_code="COMMAND_FAILED",
                )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise TaskExecutionError(
                f"Command timed out: {self.command}",
                error_code="COMMAND_TIMEOUT",
            )
        except Exception as e:
            raise TaskExecutionError(
                f"Command execution error: {e}",
                error_code="COMMAND_ERROR",
            )

    def rollback(self, rollback_data: Dict[str, Any]) -> None:
        """Rollback command (no-op for most commands)."""
        logger.info(f"Rollback not implemented for command: {self.command}")

    def dry_run(self) -> Dict[str, Any]:
        """Simulate command execution."""
        return {
            "action": "execute_command",
            "command": self.command,
            "description": self.description,
        }


class ActionExecutor:
    """
    Action execution engine with dry-run, rollback, and logging capabilities.

    Manages execution of actions with support for transaction-like rollback
    if any action in a sequence fails.
    """

    def __init__(self, dry_run_mode: bool = False):
        """
        Initialize action executor.

        Args:
            dry_run_mode: If True, simulate actions without executing
        """
        self.dry_run_mode = dry_run_mode
        self.execution_history: List[ActionResult] = []
        self.max_history_size = 1000
        logger.info(f"Action executor initialized (dry_run={dry_run_mode})")

    def execute_action(self, action: Action) -> ActionResult:
        """
        Execute a single action.

        Args:
            action: Action to execute

        Returns:
            Action result
        """
        result = ActionResult(action_id=action.action_id, status=ActionStatus.PENDING)

        try:
            if self.dry_run_mode:
                # Simulate execution
                logger.info(f"[DRY-RUN] Simulating action: {action.action_id}")
                dry_run_output = action.dry_run()
                result.status = ActionStatus.DRY_RUN
                result.output = dry_run_output
            else:
                # Real execution
                logger.info(f"Executing action: {action.action_id}")
                result.status = ActionStatus.RUNNING
                output = action.execute()
                result.status = ActionStatus.SUCCESS
                result.output = output

            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        except Exception as e:
            logger.error(f"Action {action.action_id} failed: {e}", exc_info=True)
            result.status = ActionStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        # Store in history
        self.execution_history.append(result)
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)

        return result

    def execute_sequence(
        self, actions: List[Action], rollback_on_failure: bool = True
    ) -> List[ActionResult]:
        """
        Execute a sequence of actions.

        Args:
            actions: List of actions to execute
            rollback_on_failure: Whether to rollback on failure

        Returns:
            List of action results
        """
        results = []
        successful_actions = []

        for action in actions:
            result = self.execute_action(action)
            results.append(result)

            if result.status == ActionStatus.SUCCESS:
                successful_actions.append((action, result))
            elif result.status == ActionStatus.FAILED:
                logger.error(f"Action sequence failed at: {action.action_id}")

                if rollback_on_failure:
                    logger.info("Rolling back successful actions...")
                    self._rollback_actions(successful_actions)

                break

        return results

    def _rollback_actions(self, actions: List[tuple[Action, ActionResult]]) -> None:
        """
        Rollback a list of successfully executed actions.

        Args:
            actions: List of (action, result) tuples to rollback
        """
        # Rollback in reverse order
        for action, result in reversed(actions):
            try:
                logger.info(f"Rolling back action: {action.action_id}")
                if result.rollback_data:
                    action.rollback(result.rollback_data)
                result.status = ActionStatus.ROLLED_BACK
            except Exception as e:
                logger.error(f"Rollback failed for {action.action_id}: {e}", exc_info=True)

    def get_execution_history(
        self, limit: int = 100, status_filter: Optional[ActionStatus] = None
    ) -> List[ActionResult]:
        """
        Get execution history.

        Args:
            limit: Maximum number of results to return
            status_filter: Filter by status (None for all)

        Returns:
            List of action results
        """
        history = self.execution_history

        if status_filter:
            history = [r for r in history if r.status == status_filter]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
        logger.info("Execution history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self.execution_history)
        if total == 0:
            return {"total": 0}

        success_count = sum(1 for r in self.execution_history if r.status == ActionStatus.SUCCESS)
        failed_count = sum(1 for r in self.execution_history if r.status == ActionStatus.FAILED)
        avg_duration = sum(r.duration_seconds for r in self.execution_history) / total

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "success_rate": success_count / total if total > 0 else 0,
            "average_duration": avg_duration,
        }

    def set_dry_run_mode(self, enabled: bool) -> None:
        """
        Enable or disable dry-run mode.

        Args:
            enabled: True to enable dry-run mode
        """
        self.dry_run_mode = enabled
        logger.info(f"Dry-run mode: {'enabled' if enabled else 'disabled'}")
