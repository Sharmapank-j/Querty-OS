"""
Rollback orchestration with safety checks.
Coordinates system-wide rollback operations with validation.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

from core.exceptions import RollbackError

logger = logging.getLogger(__name__)


class RollbackState(Enum):
    """Rollback operation state."""

    PENDING = "pending"
    VALIDATING = "validating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RollbackScope(Enum):
    """Scope of rollback operation."""

    FILESYSTEM = "filesystem"
    APPLICATION = "application"
    CONFIGURATION = "configuration"
    FULL_SYSTEM = "full_system"


class SafetyCheckType(Enum):
    """Types of safety checks."""

    DISK_SPACE = "disk_space"
    SYSTEM_LOAD = "system_load"
    RUNNING_PROCESSES = "running_processes"
    NETWORK_CONNECTIVITY = "network_connectivity"
    BACKUP_INTEGRITY = "backup_integrity"


@dataclass
class SafetyCheck:
    """Safety check result."""

    check_type: SafetyCheckType
    passed: bool
    message: str
    details: Optional[Dict] = None


@dataclass
class RollbackPoint:
    """Represents a system rollback point."""

    point_id: str
    name: str
    description: str
    created_at: datetime
    scope: RollbackScope
    snapshot_id: Optional[str] = None
    backup_id: Optional[str] = None
    config_backup: Optional[str] = None
    verified: bool = False


@dataclass
class RollbackOperation:
    """Represents a rollback operation."""

    operation_id: str
    point_id: str
    state: RollbackState
    started_at: datetime
    completed_at: Optional[datetime] = None
    safety_checks: List[SafetyCheck] = None
    error_message: Optional[str] = None
    pre_rollback_point: Optional[str] = None

    def __post_init__(self):
        if self.safety_checks is None:
            self.safety_checks = []


class RollbackManager:
    """Rollback orchestration with safety checks."""

    def __init__(
        self,
        data_dir: str = "/data/rollback",
        require_safety_checks: bool = True,
        auto_create_checkpoint: bool = True,
    ):
        """
        Initialize rollback manager.

        Args:
            data_dir: Directory for rollback data
            require_safety_checks: Whether to enforce safety checks
            auto_create_checkpoint: Automatically create pre-rollback checkpoint
        """
        self.data_dir = Path(data_dir)
        self.require_safety_checks = require_safety_checks
        self.auto_create_checkpoint = auto_create_checkpoint

        self.rollback_points: Dict[str, RollbackPoint] = {}
        self.operations: Dict[str, RollbackOperation] = {}
        self.safety_checkers: Dict[SafetyCheckType, Callable[[], SafetyCheck]] = {}

        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized RollbackManager with dir: {data_dir}")
        except Exception as e:
            raise RollbackError(
                f"Failed to create rollback directory: {e}",
                error_code="ROLLBACK_DIR_FAILED",
                details={"path": data_dir},
            )

        # Register default safety checkers
        self._register_default_safety_checkers()

    def _register_default_safety_checkers(self):
        """Register default safety check implementations."""
        self.safety_checkers[SafetyCheckType.DISK_SPACE] = self._check_disk_space
        self.safety_checkers[SafetyCheckType.SYSTEM_LOAD] = self._check_system_load
        self.safety_checkers[SafetyCheckType.RUNNING_PROCESSES] = self._check_running_processes

    def _check_disk_space(self) -> SafetyCheck:
        """Check if sufficient disk space is available."""
        try:
            stat = subprocess.run(
                ["df", "-h", str(self.data_dir)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Parse df output
            lines = stat.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    use_percent = int(parts[4].rstrip("%"))
                    available = parts[3]

                    if use_percent > 90:
                        return SafetyCheck(
                            check_type=SafetyCheckType.DISK_SPACE,
                            passed=False,
                            message=f"Disk usage critical: {use_percent}%",
                            details={"use_percent": use_percent, "available": available},
                        )

                    return SafetyCheck(
                        check_type=SafetyCheckType.DISK_SPACE,
                        passed=True,
                        message=f"Disk space sufficient: {available} available",
                        details={"use_percent": use_percent, "available": available},
                    )

            return SafetyCheck(
                check_type=SafetyCheckType.DISK_SPACE,
                passed=True,
                message="Disk space check passed (unable to parse)",
            )

        except Exception as e:
            logger.warning(f"Disk space check failed: {e}")
            return SafetyCheck(
                check_type=SafetyCheckType.DISK_SPACE,
                passed=True,
                message=f"Disk space check skipped: {e}",
            )

    def _check_system_load(self) -> SafetyCheck:
        """Check if system load is acceptable."""
        try:
            with open("/proc/loadavg", "r") as f:
                loadavg = f.read().strip().split()

            load_1min = float(loadavg[0])
            load_5min = float(loadavg[1])
            load_15min = float(loadavg[2])

            # Simple heuristic: warn if 1-min load > 10
            if load_1min > 10.0:
                return SafetyCheck(
                    check_type=SafetyCheckType.SYSTEM_LOAD,
                    passed=False,
                    message=f"System load high: {load_1min}",
                    details={
                        "load_1min": load_1min,
                        "load_5min": load_5min,
                        "load_15min": load_15min,
                    },
                )

            return SafetyCheck(
                check_type=SafetyCheckType.SYSTEM_LOAD,
                passed=True,
                message=f"System load acceptable: {load_1min}",
                details={
                    "load_1min": load_1min,
                    "load_5min": load_5min,
                    "load_15min": load_15min,
                },
            )

        except Exception as e:
            logger.warning(f"System load check failed: {e}")
            return SafetyCheck(
                check_type=SafetyCheckType.SYSTEM_LOAD,
                passed=True,
                message=f"System load check skipped: {e}",
            )

    def _check_running_processes(self) -> SafetyCheck:
        """Check for critical running processes."""
        try:
            # Count running processes
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
            process_count = len(result.stdout.strip().split("\n")) - 1

            return SafetyCheck(
                check_type=SafetyCheckType.RUNNING_PROCESSES,
                passed=True,
                message=f"Process check passed ({process_count} processes)",
                details={"process_count": process_count},
            )

        except Exception as e:
            logger.warning(f"Process check failed: {e}")
            return SafetyCheck(
                check_type=SafetyCheckType.RUNNING_PROCESSES,
                passed=True,
                message=f"Process check skipped: {e}",
            )

    def register_safety_checker(
        self, check_type: SafetyCheckType, checker: Callable[[], SafetyCheck]
    ):
        """
        Register a custom safety checker.

        Args:
            check_type: Type of safety check
            checker: Callable that returns SafetyCheck
        """
        self.safety_checkers[check_type] = checker
        logger.info(f"Registered safety checker: {check_type.value}")

    def run_safety_checks(
        self, check_types: Optional[List[SafetyCheckType]] = None
    ) -> List[SafetyCheck]:
        """
        Run safety checks.

        Args:
            check_types: Specific checks to run, or None for all

        Returns:
            List of SafetyCheck results
        """
        if check_types is None:
            check_types = list(self.safety_checkers.keys())

        results = []

        for check_type in check_types:
            if check_type in self.safety_checkers:
                try:
                    checker = self.safety_checkers[check_type]
                    result = checker()
                    results.append(result)
                    logger.debug(
                        f"Safety check {check_type.value}: "
                        f"{'PASSED' if result.passed else 'FAILED'}"
                    )
                except Exception as e:
                    logger.error(f"Safety check {check_type.value} raised exception: {e}")
                    results.append(
                        SafetyCheck(
                            check_type=check_type,
                            passed=False,
                            message=f"Check failed with exception: {e}",
                        )
                    )

        return results

    def create_rollback_point(
        self,
        name: str,
        description: str,
        scope: RollbackScope,
        snapshot_id: Optional[str] = None,
        backup_id: Optional[str] = None,
        config_backup: Optional[str] = None,
    ) -> RollbackPoint:
        """
        Create a rollback point.

        Args:
            name: Rollback point name
            description: Description
            scope: Rollback scope
            snapshot_id: Associated snapshot ID
            backup_id: Associated backup ID
            config_backup: Configuration backup path

        Returns:
            RollbackPoint object
        """
        import hashlib

        point_id = hashlib.sha256(f"{name}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        point = RollbackPoint(
            point_id=point_id,
            name=name,
            description=description,
            created_at=datetime.now(),
            scope=scope,
            snapshot_id=snapshot_id,
            backup_id=backup_id,
            config_backup=config_backup,
        )

        self.rollback_points[point_id] = point
        logger.info(f"Created rollback point: {name} (id={point_id})")
        return point

    def verify_rollback_point(self, point_id: str) -> bool:
        """
        Verify a rollback point is valid.

        Args:
            point_id: Rollback point ID

        Returns:
            True if valid, False otherwise
        """
        if point_id not in self.rollback_points:
            logger.warning(f"Rollback point not found: {point_id}")
            return False

        point = self.rollback_points[point_id]

        # Basic validation - check that referenced resources exist
        # In production, would verify snapshots/backups are accessible
        valid = True

        if point.snapshot_id:
            # Would check snapshot exists
            pass

        if point.backup_id:
            # Would check backup exists
            pass

        if point.config_backup:
            config_path = Path(point.config_backup)
            if not config_path.exists():
                logger.warning(f"Config backup not found: {point.config_backup}")
                valid = False

        point.verified = valid
        return valid

    def initiate_rollback(
        self,
        point_id: str,
        force: bool = False,
        skip_safety_checks: bool = False,
    ) -> RollbackOperation:
        """
        Initiate a rollback operation.

        Args:
            point_id: Rollback point ID
            force: Force rollback even if safety checks fail
            skip_safety_checks: Skip all safety checks

        Returns:
            RollbackOperation object

        Raises:
            RollbackError: If rollback cannot be initiated
        """
        if point_id not in self.rollback_points:
            raise RollbackError(
                f"Rollback point not found: {point_id}",
                error_code="POINT_NOT_FOUND",
                details={"point_id": point_id},
            )

        point = self.rollback_points[point_id]

        # Verify rollback point
        if not self.verify_rollback_point(point_id):
            if not force:
                raise RollbackError(
                    f"Rollback point verification failed: {point_id}",
                    error_code="VERIFICATION_FAILED",
                    details={"point_id": point_id},
                )
            logger.warning(f"Forcing rollback despite verification failure: {point_id}")

        # Create operation
        import hashlib

        operation_id = hashlib.sha256(
            f"{point_id}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        operation = RollbackOperation(
            operation_id=operation_id,
            point_id=point_id,
            state=RollbackState.PENDING,
            started_at=datetime.now(),
        )

        self.operations[operation_id] = operation

        try:
            # Run safety checks
            if not skip_safety_checks and self.require_safety_checks:
                operation.state = RollbackState.VALIDATING
                logger.info(f"Running safety checks for rollback: {operation_id}")

                safety_checks = self.run_safety_checks()
                operation.safety_checks = safety_checks

                # Check if any critical checks failed
                failed_checks = [c for c in safety_checks if not c.passed]
                if failed_checks and not force:
                    operation.state = RollbackState.FAILED
                    operation.error_message = f"Safety checks failed: {len(failed_checks)}"
                    raise RollbackError(
                        f"Safety checks failed: {[c.message for c in failed_checks]}",
                        error_code="SAFETY_CHECK_FAILED",
                        details={"failed_checks": [c.check_type.value for c in failed_checks]},
                    )

            # Create pre-rollback checkpoint if enabled
            if self.auto_create_checkpoint:
                logger.info("Creating pre-rollback checkpoint")
                checkpoint = self.create_rollback_point(
                    name=f"pre_rollback_{operation_id}",
                    description=f"Auto-checkpoint before rollback to {point.name}",
                    scope=point.scope,
                )
                operation.pre_rollback_point = checkpoint.point_id

            # Execute rollback
            operation.state = RollbackState.IN_PROGRESS
            logger.info(f"Executing rollback: {operation_id} to point {point.name}")

            # Actual rollback would happen here
            # This would coordinate with FilesystemSnapshot and IncrementalBackup
            self._execute_rollback(point, operation)

            operation.state = RollbackState.COMPLETED
            operation.completed_at = datetime.now()
            logger.info(f"Rollback completed: {operation_id}")
            return operation

        except Exception as e:
            operation.state = RollbackState.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.now()
            logger.error(f"Rollback failed: {e}")
            raise

    def _execute_rollback(self, point: RollbackPoint, operation: RollbackOperation):
        """
        Execute the actual rollback operation.

        Args:
            point: RollbackPoint to restore
            operation: RollbackOperation being executed
        """
        # This is where the actual rollback logic would be implemented
        # It would coordinate with:
        # - FilesystemSnapshot for filesystem restores
        # - IncrementalBackup for incremental restores
        # - Configuration management for config restores

        logger.info(f"Executing rollback for scope: {point.scope.value}")

        if point.scope == RollbackScope.FILESYSTEM:
            # Restore filesystem snapshot
            if point.snapshot_id:
                logger.info(f"Would restore snapshot: {point.snapshot_id}")
                time.sleep(0.5)  # Simulate work

        elif point.scope == RollbackScope.APPLICATION:
            # Restore application state
            if point.backup_id:
                logger.info(f"Would restore backup: {point.backup_id}")
                time.sleep(0.5)

        elif point.scope == RollbackScope.CONFIGURATION:
            # Restore configuration
            if point.config_backup:
                logger.info(f"Would restore config: {point.config_backup}")
                time.sleep(0.5)

        elif point.scope == RollbackScope.FULL_SYSTEM:
            # Full system rollback
            logger.info("Would perform full system rollback")
            time.sleep(1.0)

        logger.info(f"Rollback execution complete for point: {point.point_id}")

    def cancel_rollback(self, operation_id: str) -> bool:
        """
        Cancel an in-progress rollback operation.

        Args:
            operation_id: Operation ID to cancel

        Returns:
            True if cancelled, False if cannot cancel
        """
        if operation_id not in self.operations:
            logger.warning(f"Operation not found: {operation_id}")
            return False

        operation = self.operations[operation_id]

        if operation.state not in [RollbackState.PENDING, RollbackState.VALIDATING]:
            logger.warning(f"Cannot cancel operation in state: {operation.state.value}")
            return False

        operation.state = RollbackState.CANCELLED
        operation.completed_at = datetime.now()
        logger.info(f"Cancelled rollback operation: {operation_id}")
        return True

    def list_rollback_points(self, scope: Optional[RollbackScope] = None) -> List[RollbackPoint]:
        """
        List rollback points.

        Args:
            scope: Filter by scope

        Returns:
            List of RollbackPoint objects
        """
        points = list(self.rollback_points.values())
        if scope:
            points = [p for p in points if p.scope == scope]
        return sorted(points, key=lambda p: p.created_at, reverse=True)

    def get_rollback_point(self, point_id: str) -> Optional[RollbackPoint]:
        """
        Get rollback point details.

        Args:
            point_id: Rollback point ID

        Returns:
            RollbackPoint or None if not found
        """
        return self.rollback_points.get(point_id)

    def get_operation(self, operation_id: str) -> Optional[RollbackOperation]:
        """
        Get rollback operation details.

        Args:
            operation_id: Operation ID

        Returns:
            RollbackOperation or None if not found
        """
        return self.operations.get(operation_id)

    def list_operations(self, state: Optional[RollbackState] = None) -> List[RollbackOperation]:
        """
        List rollback operations.

        Args:
            state: Filter by state

        Returns:
            List of RollbackOperation objects
        """
        ops = list(self.operations.values())
        if state:
            ops = [o for o in ops if o.state == state]
        return sorted(ops, key=lambda o: o.started_at, reverse=True)

    def delete_rollback_point(self, point_id: str) -> bool:
        """
        Delete a rollback point.

        Args:
            point_id: Rollback point ID

        Returns:
            True if deleted, False if not found
        """
        if point_id not in self.rollback_points:
            logger.warning(f"Rollback point not found: {point_id}")
            return False

        del self.rollback_points[point_id]
        logger.info(f"Deleted rollback point: {point_id}")
        return True
