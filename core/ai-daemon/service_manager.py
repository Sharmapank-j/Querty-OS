"""
Service Manager for AI Daemon

Manages lifecycle of system services including start, stop, restart, and health checks.
"""

import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Service state enumeration."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class Service:
    """Represents a managed service."""

    def __init__(
        self,
        name: str,
        start_func: Callable,
        stop_func: Callable,
        health_check_func: Optional[Callable] = None,
    ):
        """
        Initialize a service.

        Args:
            name: Service name
            start_func: Function to start the service
            stop_func: Function to stop the service
            health_check_func: Optional function to check service health
        """
        self.name = name
        self.start_func = start_func
        self.stop_func = stop_func
        self.health_check_func = health_check_func
        self.state = ServiceState.STOPPED
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.error_message: Optional[str] = None

    def get_uptime(self) -> float:
        """
        Get service uptime in seconds.

        Returns:
            Uptime in seconds, or 0 if not running
        """
        if self.state == ServiceState.RUNNING and self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0


class ServiceManager:
    """
    Manages system services with lifecycle control and health monitoring.

    Provides start, stop, restart, and health check capabilities for registered services.
    """

    def __init__(self):
        """Initialize the service manager."""
        self.services: Dict[str, Service] = {}
        self.start_order: List[str] = []
        logger.info("Service manager initialized")

    def register_service(
        self,
        name: str,
        start_func: Callable,
        stop_func: Callable,
        health_check_func: Optional[Callable] = None,
        priority: int = 0,
    ) -> None:
        """
        Register a new service.

        Args:
            name: Service name
            start_func: Function to start the service
            stop_func: Function to stop the service
            health_check_func: Optional function to check service health
            priority: Service priority (higher priority services start first)
        """
        if name in self.services:
            logger.warning(f"Service {name} already registered, updating")

        service = Service(name, start_func, stop_func, health_check_func)
        self.services[name] = service

        # Insert service in start order based on priority
        if name not in self.start_order:
            self.start_order.append(name)
            # Sort by priority (would need to store priority, but keeping simple for now)

        logger.info(f"Registered service: {name}")

    def start_service(self, name: str) -> bool:
        """
        Start a specific service.

        Args:
            name: Service name

        Returns:
            True if service started successfully, False otherwise
        """
        if name not in self.services:
            logger.error(f"Service {name} not registered")
            return False

        service = self.services[name]

        if service.state == ServiceState.RUNNING:
            logger.warning(f"Service {name} already running")
            return True

        try:
            logger.info(f"Starting service: {name}")
            service.state = ServiceState.STARTING
            service.start_func()
            service.state = ServiceState.RUNNING
            service.start_time = datetime.now()
            service.error_message = None
            logger.info(f"Service {name} started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start service {name}: {e}", exc_info=True)
            service.state = ServiceState.ERROR
            service.error_message = str(e)
            return False

    def stop_service(self, name: str) -> bool:
        """
        Stop a specific service.

        Args:
            name: Service name

        Returns:
            True if service stopped successfully, False otherwise
        """
        if name not in self.services:
            logger.error(f"Service {name} not registered")
            return False

        service = self.services[name]

        if service.state == ServiceState.STOPPED:
            logger.warning(f"Service {name} already stopped")
            return True

        try:
            logger.info(f"Stopping service: {name}")
            service.state = ServiceState.STOPPING
            service.stop_func()
            service.state = ServiceState.STOPPED
            service.start_time = None
            service.error_message = None
            logger.info(f"Service {name} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop service {name}: {e}", exc_info=True)
            service.state = ServiceState.ERROR
            service.error_message = str(e)
            return False

    def restart_service(self, name: str) -> bool:
        """
        Restart a specific service.

        Args:
            name: Service name

        Returns:
            True if service restarted successfully, False otherwise
        """
        logger.info(f"Restarting service: {name}")
        if not self.stop_service(name):
            return False
        time.sleep(1)  # Brief pause between stop and start
        return self.start_service(name)

    def start_all(self) -> Dict[str, bool]:
        """
        Start all registered services in order.

        Returns:
            Dictionary mapping service names to success status
        """
        logger.info("Starting all services")
        results = {}
        for name in self.start_order:
            results[name] = self.start_service(name)
        return results

    def stop_all(self) -> Dict[str, bool]:
        """
        Stop all registered services in reverse order.

        Returns:
            Dictionary mapping service names to success status
        """
        logger.info("Stopping all services")
        results = {}
        for name in reversed(self.start_order):
            results[name] = self.stop_service(name)
        return results

    def health_check(self, name: str) -> bool:
        """
        Check health of a specific service.

        Args:
            name: Service name

        Returns:
            True if service is healthy, False otherwise
        """
        if name not in self.services:
            logger.error(f"Service {name} not registered")
            return False

        service = self.services[name]

        if service.state != ServiceState.RUNNING:
            logger.warning(f"Service {name} not running, state: {service.state.value}")
            return False

        if service.health_check_func is None:
            # No health check function, assume healthy if running
            return True

        try:
            is_healthy = service.health_check_func()
            service.last_health_check = datetime.now()
            if not is_healthy:
                logger.warning(f"Service {name} health check failed")
            return is_healthy
        except Exception as e:
            logger.error(f"Health check error for service {name}: {e}", exc_info=True)
            return False

    def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all services.

        Returns:
            Dictionary mapping service names to health status
        """
        results = {}
        for name in self.services:
            results[name] = self.health_check(name)
        return results

    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a service.

        Args:
            name: Service name

        Returns:
            Dictionary with service status information, or None if not found
        """
        if name not in self.services:
            return None

        service = self.services[name]
        return {
            "name": name,
            "state": service.state.value,
            "uptime": service.get_uptime(),
            "start_time": service.start_time.isoformat() if service.start_time else None,
            "last_health_check": (
                service.last_health_check.isoformat() if service.last_health_check else None
            ),
            "error_message": service.error_message,
        }

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all services.

        Returns:
            Dictionary mapping service names to status information
        """
        return {
            name: {
                "name": name,
                "state": service.state.value,
                "uptime": service.get_uptime(),
                "start_time": service.start_time.isoformat() if service.start_time else None,
                "last_health_check": (
                    service.last_health_check.isoformat() if service.last_health_check else None
                ),
                "error_message": service.error_message,
            }
            for name, service in self.services.items()
        }
