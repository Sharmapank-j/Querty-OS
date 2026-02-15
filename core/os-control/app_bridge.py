"""
Cross-OS file transfer and communication bridge.
Facilitates data exchange between Android, Linux, and host systems.
"""

import hashlib
import logging
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

from core.exceptions import OSControlError

logger = logging.getLogger(__name__)


class TransferProtocol(Enum):
    """File transfer protocols."""

    DIRECT = "direct"  # Direct file copy
    SOCKET = "socket"  # Unix domain socket
    PIPE = "pipe"  # Named pipe
    SHARED_MEMORY = "shared_memory"  # Shared memory


class TransferStatus(Enum):
    """Transfer operation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TransferJob:
    """Represents a file transfer job."""

    job_id: str
    source: str
    destination: str
    protocol: TransferProtocol
    status: TransferStatus
    bytes_transferred: int = 0
    total_bytes: int = 0
    error: Optional[str] = None

    @property
    def progress(self) -> float:
        """Calculate transfer progress percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_transferred / self.total_bytes) * 100.0


@dataclass
class BridgeEndpoint:
    """Represents a communication endpoint."""

    name: str
    os_type: str  # "android", "linux", "host"
    base_path: Path
    active: bool = True


class AppBridge:
    """Cross-OS file transfer and communication bridge."""

    def __init__(self, bridge_dir: str = "/data/querty-bridge"):
        """
        Initialize app bridge.

        Args:
            bridge_dir: Base directory for bridge operations
        """
        self.bridge_dir = Path(bridge_dir)
        self.endpoints: Dict[str, BridgeEndpoint] = {}
        self.transfer_jobs: Dict[str, TransferJob] = {}
        self.progress_callbacks: Dict[str, List[Callable]] = {}

        # Ensure bridge directory exists
        try:
            self.bridge_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized AppBridge with directory: {bridge_dir}")
        except Exception as e:
            raise OSControlError(
                f"Failed to create bridge directory: {e}",
                error_code="BRIDGE_INIT_FAILED",
                details={"path": bridge_dir},
            )

    def register_endpoint(
        self, name: str, os_type: str, base_path: str, active: bool = True
    ) -> BridgeEndpoint:
        """
        Register a communication endpoint.

        Args:
            name: Endpoint name
            os_type: OS type ("android", "linux", "host")
            base_path: Base path for this endpoint
            active: Whether endpoint is active

        Returns:
            BridgeEndpoint object

        Raises:
            OSControlError: If endpoint already exists
        """
        if name in self.endpoints:
            raise OSControlError(
                f"Endpoint already exists: {name}",
                error_code="ENDPOINT_EXISTS",
                details={"name": name},
            )

        endpoint = BridgeEndpoint(
            name=name, os_type=os_type, base_path=Path(base_path), active=active
        )
        self.endpoints[name] = endpoint
        logger.info(f"Registered endpoint: {name} ({os_type}) at {base_path}")
        return endpoint

    def unregister_endpoint(self, name: str) -> bool:
        """
        Unregister an endpoint.

        Args:
            name: Endpoint name

        Returns:
            True if successful, False if endpoint not found
        """
        if name not in self.endpoints:
            logger.warning(f"Endpoint not found: {name}")
            return False

        del self.endpoints[name]
        logger.info(f"Unregistered endpoint: {name}")
        return True

    def get_endpoint(self, name: str) -> Optional[BridgeEndpoint]:
        """
        Get endpoint information.

        Args:
            name: Endpoint name

        Returns:
            BridgeEndpoint or None if not found
        """
        return self.endpoints.get(name)

    def list_endpoints(self, os_type: Optional[str] = None) -> List[BridgeEndpoint]:
        """
        List registered endpoints.

        Args:
            os_type: Filter by OS type

        Returns:
            List of BridgeEndpoint objects
        """
        endpoints = list(self.endpoints.values())
        if os_type:
            endpoints = [ep for ep in endpoints if ep.os_type == os_type]
        return endpoints

    def _generate_job_id(self, source: str, destination: str) -> str:
        """Generate unique job ID."""
        import uuid

        return uuid.uuid4().hex[:16]

    def _resolve_path(self, endpoint_name: str, path: str) -> Path:
        """
        Resolve path relative to endpoint.

        Args:
            endpoint_name: Endpoint name
            path: Relative or absolute path

        Returns:
            Resolved absolute path

        Raises:
            OSControlError: If endpoint not found
        """
        if endpoint_name not in self.endpoints:
            raise OSControlError(
                f"Endpoint not found: {endpoint_name}",
                error_code="ENDPOINT_NOT_FOUND",
                details={"name": endpoint_name},
            )

        endpoint = self.endpoints[endpoint_name]
        if Path(path).is_absolute():
            return Path(path)
        return endpoint.base_path / path

    def transfer_file(
        self,
        source_endpoint: str,
        source_path: str,
        dest_endpoint: str,
        dest_path: str,
        protocol: TransferProtocol = TransferProtocol.DIRECT,
        verify_checksum: bool = True,
    ) -> TransferJob:
        """
        Transfer file between endpoints.

        Args:
            source_endpoint: Source endpoint name
            source_path: Source file path (relative to endpoint)
            dest_endpoint: Destination endpoint name
            dest_path: Destination file path (relative to endpoint)
            protocol: Transfer protocol to use
            verify_checksum: Whether to verify file integrity

        Returns:
            TransferJob object

        Raises:
            OSControlError: If transfer fails
        """
        # Resolve paths
        source_full = self._resolve_path(source_endpoint, source_path)
        dest_full = self._resolve_path(dest_endpoint, dest_path)

        if not source_full.exists():
            raise OSControlError(
                f"Source file not found: {source_full}",
                error_code="SOURCE_NOT_FOUND",
                details={"source": str(source_full)},
            )

        # Create transfer job
        job_id = self._generate_job_id(str(source_full), str(dest_full))
        job = TransferJob(
            job_id=job_id,
            source=str(source_full),
            destination=str(dest_full),
            protocol=protocol,
            status=TransferStatus.PENDING,
            total_bytes=source_full.stat().st_size if source_full.is_file() else 0,
        )
        self.transfer_jobs[job_id] = job

        try:
            # Update status
            job.status = TransferStatus.IN_PROGRESS
            self._notify_progress(job_id, job)

            # Perform transfer based on protocol
            if protocol == TransferProtocol.DIRECT:
                self._transfer_direct(source_full, dest_full, job)
            else:
                raise OSControlError(
                    f"Transfer protocol not implemented: {protocol}",
                    error_code="PROTOCOL_NOT_IMPLEMENTED",
                    details={"protocol": protocol.value},
                )

            # Verify checksum if requested
            if verify_checksum and source_full.is_file():
                if not self._verify_checksum(source_full, dest_full):
                    raise OSControlError(
                        "Checksum verification failed",
                        error_code="CHECKSUM_MISMATCH",
                        details={"source": str(source_full), "destination": str(dest_full)},
                    )

            # Mark as completed
            job.status = TransferStatus.COMPLETED
            self._notify_progress(job_id, job)
            logger.info(f"Transfer completed: {job_id}")
            return job

        except OSControlError:
            # Re-raise OSControlError unchanged to preserve error_code and details
            job.status = TransferStatus.FAILED
            job.error = str(sys.exc_info()[1])
            self._notify_progress(job_id, job)
            logger.error(f"Transfer failed: {sys.exc_info()[1]}")
            raise
        except Exception as e:
            job.status = TransferStatus.FAILED
            job.error = str(e)
            self._notify_progress(job_id, job)
            logger.error(f"Transfer failed: {e}")
            raise OSControlError(
                f"Transfer failed: {e}",
                error_code="TRANSFER_FAILED",
                details={"job_id": job_id, "error": str(e)},
            )

    def _transfer_direct(self, source: Path, dest: Path, job: TransferJob) -> None:
        """
        Perform direct file copy.

        Args:
            source: Source path
            dest: Destination path
            job: Transfer job to update
        """
        dest.parent.mkdir(parents=True, exist_ok=True)

        if source.is_file():
            # Copy file with progress tracking
            with open(source, "rb") as src_file:
                with open(dest, "wb") as dst_file:
                    while True:
                        chunk = src_file.read(8192)
                        if not chunk:
                            break
                        dst_file.write(chunk)
                        job.bytes_transferred += len(chunk)
                        self._notify_progress(job.job_id, job)
        else:
            # Copy directory
            shutil.copytree(source, dest, dirs_exist_ok=True)
            job.bytes_transferred = job.total_bytes

    def _verify_checksum(self, source: Path, dest: Path) -> bool:
        """
        Verify file checksums match.

        Args:
            source: Source file
            dest: Destination file

        Returns:
            True if checksums match, False otherwise
        """
        try:
            source_hash = self._calculate_checksum(source)
            dest_hash = self._calculate_checksum(dest)
            match = source_hash == dest_hash
            if not match:
                logger.warning(f"Checksum mismatch: source={source_hash[:8]}, dest={dest_hash[:8]}")
            return match
        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of checksum
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_progress_callback(self, job_id: str, callback: Callable[[TransferJob], None]):
        """
        Register callback for transfer progress updates.

        Args:
            job_id: Transfer job ID
            callback: Callback function that receives TransferJob
        """
        if job_id not in self.progress_callbacks:
            self.progress_callbacks[job_id] = []
        self.progress_callbacks[job_id].append(callback)
        logger.debug(f"Registered progress callback for job: {job_id}")

    def _notify_progress(self, job_id: str, job: TransferJob):
        """
        Notify all registered callbacks of progress update.

        Args:
            job_id: Transfer job ID
            job: Updated TransferJob
        """
        if job_id in self.progress_callbacks:
            for callback in self.progress_callbacks[job_id]:
                try:
                    callback(job)
                except Exception as e:
                    logger.error(f"Progress callback failed: {e}")

    def get_transfer_job(self, job_id: str) -> Optional[TransferJob]:
        """
        Get transfer job information.

        Args:
            job_id: Transfer job ID

        Returns:
            TransferJob or None if not found
        """
        return self.transfer_jobs.get(job_id)

    def list_transfer_jobs(self, status: Optional[TransferStatus] = None) -> List[TransferJob]:
        """
        List transfer jobs.

        Args:
            status: Filter by status

        Returns:
            List of TransferJob objects
        """
        jobs = list(self.transfer_jobs.values())
        if status:
            jobs = [job for job in jobs if job.status == status]
        return jobs

    def cancel_transfer(self, job_id: str) -> bool:
        """
        Cancel a transfer job.

        Args:
            job_id: Transfer job ID

        Returns:
            True if cancelled, False if not found or already completed
        """
        job = self.transfer_jobs.get(job_id)
        if not job:
            logger.warning(f"Transfer job not found: {job_id}")
            return False

        if job.status in [TransferStatus.COMPLETED, TransferStatus.FAILED]:
            logger.warning(f"Cannot cancel completed/failed job: {job_id}")
            return False

        job.status = TransferStatus.CANCELLED
        self._notify_progress(job_id, job)
        logger.info(f"Cancelled transfer job: {job_id}")
        return True

    def create_shared_directory(self, name: str) -> Path:
        """
        Create a shared directory accessible to all endpoints.

        Args:
            name: Directory name

        Returns:
            Path to shared directory

        Raises:
            OSControlError: If creation fails
        """
        shared_dir = self.bridge_dir / "shared" / name

        try:
            shared_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created shared directory: {shared_dir}")
            return shared_dir
        except Exception as e:
            raise OSControlError(
                f"Failed to create shared directory: {e}",
                error_code="SHARED_DIR_FAILED",
                details={"path": str(shared_dir)},
            )

    def sync_directory(
        self, source_endpoint: str, source_dir: str, dest_endpoint: str, dest_dir: str
    ) -> TransferJob:
        """
        Synchronize directory between endpoints.

        Args:
            source_endpoint: Source endpoint name
            source_dir: Source directory path
            dest_endpoint: Destination endpoint name
            dest_dir: Destination directory path

        Returns:
            TransferJob object
        """
        return self.transfer_file(
            source_endpoint=source_endpoint,
            source_path=source_dir,
            dest_endpoint=dest_endpoint,
            dest_path=dest_dir,
            protocol=TransferProtocol.DIRECT,
            verify_checksum=False,  # Skip checksum for directories
        )

    def cleanup_completed_jobs(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up old completed/failed transfer jobs.

        Args:
            max_age_seconds: Maximum age of jobs to keep

        Returns:
            Number of jobs removed
        """
        # For simplicity, remove all completed/failed jobs
        # In production, would check timestamps
        removed = 0
        job_ids = list(self.transfer_jobs.keys())

        for job_id in job_ids:
            job = self.transfer_jobs[job_id]
            if job.status in [TransferStatus.COMPLETED, TransferStatus.FAILED]:
                del self.transfer_jobs[job_id]
                if job_id in self.progress_callbacks:
                    del self.progress_callbacks[job_id]
                removed += 1

        logger.info(f"Cleaned up {removed} transfer jobs")
        return removed
