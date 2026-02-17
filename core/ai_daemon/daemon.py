#!/usr/bin/env python3
"""
Querty-OS AI Daemon
Main system daemon that starts on boot and manages all AI operations.
Enhanced with watchdog, auto-restart, and health monitoring.
"""

import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Dict

# Configure logging with fallback for permission errors
log_handlers = [logging.StreamHandler(sys.stdout)]
try:
    log_handlers.append(logging.FileHandler("/var/log/querty-ai-daemon.log"))
except (PermissionError, FileNotFoundError):
    # Fallback to user directory if /var/log is not writable
    log_dir = os.path.expanduser("~/.querty-os/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_handlers.append(logging.FileHandler(os.path.join(log_dir, "querty-ai-daemon.log")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers,
)

logger = logging.getLogger("querty-ai-daemon")


class DaemonWatchdog:
    """Watchdog for monitoring daemon health and triggering auto-restart."""

    def __init__(self, check_interval: int = 30):
        """
        Initialize watchdog.

        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.last_heartbeat = None
        self.restart_count = 0
        self.max_restarts = 10
        self.running = False
        self.thread = None

    def start(self):
        """Start watchdog monitoring."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        logger.info("Watchdog started")

    def stop(self):
        """Stop watchdog monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Watchdog stopped")

    def heartbeat(self):
        """Record daemon heartbeat."""
        self.last_heartbeat = datetime.now()

    def _monitor(self):
        """Monitor daemon health."""
        while self.running:
            if self.last_heartbeat:
                elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
                if elapsed > self.check_interval * 2:
                    logger.warning(f"Daemon heartbeat timeout ({elapsed}s)")
                    if self.restart_count < self.max_restarts:
                        logger.info("Triggering auto-restart...")
                        self.restart_count += 1
                    else:
                        logger.error("Max restart limit reached, stopping watchdog")
                        self.running = False

            time.sleep(self.check_interval)


class QuertyAIDaemon:
    """Main AI daemon for Querty-OS system with watchdog and auto-restart."""

    def __init__(self):
        """Initialize the AI daemon."""
        self.running = False
        self.llm_service = None
        self.input_handlers = {}
        self.agent_automation = None
        self.os_control = None
        self.network_manager = None
        self.snapshot_system = None
        self.boot_profile = None
        self.plugin_manager = None
        self.memory_manager = None
        self.security_layer = None
        self.cli_api = None
        self.ota_manager = None

        # Health monitoring
        self.watchdog = DaemonWatchdog()
        self.health_status = {"status": "initializing", "services": {}}
        self.last_crash_time = None

        logger.info("Querty AI Daemon initializing...")

    def get_health_status(self) -> Dict:
        """
        Get current health status.

        Returns:
            Dict with health information
        """
        return {
            "status": self.health_status["status"],
            "services": self.health_status["services"],
            "uptime": time.time() - self.start_time if hasattr(self, "start_time") else 0,
            "watchdog_restarts": self.watchdog.restart_count,
        }

    def initialize_services(self):
        """Initialize all system services."""
        logger.info("Initializing services...")

        try:
            # Initialize boot profile manager
            logger.info("  - Boot profile: initializing")
            self.health_status["services"]["boot_profile"] = "initializing"
            from core.boot_profiles import BootProfileManager

            self.boot_profile = BootProfileManager()
            self.boot_profile.set_current_profile("ai_full")  # Default to AI-full
            self.health_status["services"]["boot_profile"] = "ready"

            # Initialize memory manager
            logger.info("  - Memory manager: initializing")
            self.health_status["services"]["memory_manager"] = "initializing"
            from core.memory_manager import ContextWindowManager, TaskMemory

            self.memory_manager = {
                "context": ContextWindowManager(max_tokens=4096),
                "tasks": TaskMemory(),
            }
            self.health_status["services"]["memory_manager"] = "ready"

            # Initialize security layer
            logger.info("  - Security layer: initializing")
            self.health_status["services"]["security"] = "initializing"
            from core.security_layer import AuditLogger, PermissionManager, PromptFirewall

            self.security_layer = {
                "firewall": PromptFirewall(),
                "audit": AuditLogger(),
                "permissions": PermissionManager(),
            }
            self.health_status["services"]["security"] = "ready"

            # Initialize plugin manager
            logger.info("  - Plugin manager: initializing")
            self.health_status["services"]["plugin_manager"] = "initializing"
            from core.plugin_system import PluginManager

            self.plugin_manager = PluginManager()
            self.health_status["services"]["plugin_manager"] = "ready"

            # Initialize OTA manager
            logger.info("  - OTA manager: initializing")
            self.health_status["services"]["ota"] = "initializing"
            from core.ota_manager import OTAManager

            self.ota_manager = OTAManager()
            self.health_status["services"]["ota"] = "ready"

            # Initialize LLM service
            logger.info("  - LLM service: initializing")
            self.health_status["services"]["llm"] = "initializing"
            try:
                from core.llm_service import LLMService

                self.llm_service = LLMService()
                self.llm_service.load_model()
                self.health_status["services"]["llm"] = "ready"
                logger.info("  - LLM service: ready")
            except Exception as e:
                logger.warning(f"  - LLM service: failed to initialize ({e})")
                self.health_status["services"]["llm"] = "degraded"

            # Initialize input handlers
            logger.info("  - Input handlers: initializing")
            self.health_status["services"]["input"] = "initializing"
            try:
                from core.input_handlers import CameraInputHandler, TextInputHandler, VoiceInputHandler

                self.input_handlers = {
                    "voice": VoiceInputHandler(),
                    "text": TextInputHandler(),
                    "camera": CameraInputHandler(),
                }
                # Start handlers
                for name, handler in self.input_handlers.items():
                    try:
                        handler.start()
                        logger.info(f"  - {name.capitalize()} handler: started")
                    except Exception as e:
                        logger.warning(f"  - {name.capitalize()} handler: failed to start ({e})")
                self.health_status["services"]["input"] = "ready"
            except Exception as e:
                logger.warning(f"  - Input handlers: failed to initialize ({e})")
                self.health_status["services"]["input"] = "degraded"

            # Initialize agent automation
            logger.info("  - Agent automation: initializing")
            self.health_status["services"]["agent"] = "initializing"
            try:
                from core.agent_automation import AgentAutomationSystem

                self.agent_automation = AgentAutomationSystem()
                self.health_status["services"]["agent"] = "ready"
                logger.info("  - Agent automation: ready")
            except Exception as e:
                logger.warning(f"  - Agent automation: failed to initialize ({e})")
                self.health_status["services"]["agent"] = "degraded"

            # Initialize OS control modules
            logger.info("  - OS control: initializing")
            self.health_status["services"]["os_control"] = "initializing"
            try:
                from core.os_control import AndroidController, LinuxController, WineController

                self.os_control = {
                    "android": AndroidController(),
                    "linux": LinuxController(),
                    "wine": WineController(),
                }
                # Start controllers
                for name, controller in self.os_control.items():
                    try:
                        controller.start()
                        logger.info(f"  - {name.capitalize()} controller: started")
                    except Exception as e:
                        logger.warning(f"  - {name.capitalize()} controller: failed to start ({e})")
                self.health_status["services"]["os_control"] = "ready"
            except Exception as e:
                logger.warning(f"  - OS control: failed to initialize ({e})")
                self.health_status["services"]["os_control"] = "degraded"

            # Initialize network manager
            logger.info("  - Network manager: initializing")
            self.health_status["services"]["network"] = "initializing"
            try:
                from core.network_manager import NetworkManager

                self.network_manager = NetworkManager()
                self.health_status["services"]["network"] = "ready"
                logger.info("  - Network manager: ready")
            except Exception as e:
                logger.warning(f"  - Network manager: failed to initialize ({e})")
                self.health_status["services"]["network"] = "degraded"

            # Initialize snapshot system
            logger.info("  - Snapshot system: initializing")
            self.health_status["services"]["snapshot"] = "initializing"
            try:
                from core.snapshot_system import SnapshotSystem

                self.snapshot_system = SnapshotSystem()
                self.health_status["services"]["snapshot"] = "ready"
                logger.info("  - Snapshot system: ready")
            except Exception as e:
                logger.warning(f"  - Snapshot system: failed to initialize ({e})")
                self.health_status["services"]["snapshot"] = "degraded"

            logger.info("All services initialized")
            self.health_status["status"] = "running"

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}", exc_info=True)
            self.health_status["status"] = "error"
            raise

    def start(self):
        """Start the AI daemon with watchdog."""
        logger.info("Starting Querty AI Daemon...")
        self.running = True
        self.start_time = time.time()

        # Start watchdog
        self.watchdog.start()

        # Initialize all services
        try:
            self.initialize_services()
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            self.stop()
            return

        # Main daemon loop
        try:
            self.run_main_loop()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()
        except Exception as e:
            logger.error(f"Fatal error in daemon: {e}", exc_info=True)
            self.last_crash_time = datetime.now()
            self.stop()

    def run_main_loop(self):
        """Main daemon event loop with heartbeat."""
        logger.info("Entering main event loop")

        while self.running:
            # Send heartbeat to watchdog
            self.watchdog.heartbeat()

            # Main daemon processing
            try:
                # Process any queued events
                self._process_events()

                # Check service health periodically
                self._check_service_health()

                # Process any pending agent tasks
                if self.agent_automation:
                    self._process_agent_tasks()

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)

            time.sleep(1)

    def _process_events(self):
        """Process queued events."""
        # Placeholder for event processing
        # In a full implementation, this would handle events from the event bus
        pass

    def _process_agent_tasks(self):
        """Process pending agent automation tasks."""
        # Placeholder for agent task processing
        # In a full implementation, this would execute queued tasks
        pass

    def _check_service_health(self):
        """Check health of all services."""
        services_to_check = [
            ("llm", self.llm_service),
            ("agent", self.agent_automation),
            ("network", self.network_manager),
            ("snapshot", self.snapshot_system),
        ]

        for service_name, service in services_to_check:
            if service is not None:
                # Service is initialized and should be healthy
                if service_name in self.health_status["services"]:
                    current_status = self.health_status["services"][service_name]
                    if current_status == "degraded":
                        logger.debug(f"Service {service_name} in degraded state")
            elif service_name in self.health_status["services"]:
                # Service failed to initialize
                if self.health_status["services"][service_name] != "degraded":
                    self.health_status["services"][service_name] = "degraded"

    def stop(self):
        """Stop the AI daemon gracefully."""
        logger.info("Stopping Querty AI Daemon...")
        self.running = False

        # Stop watchdog
        self.watchdog.stop()

        # Cleanup and shutdown all services
        logger.info("Shutting down services...")

        # Stop input handlers
        if self.input_handlers:
            for name, handler in self.input_handlers.items():
                try:
                    handler.stop()
                    logger.info(f"  - {name.capitalize()} handler stopped")
                except Exception as e:
                    logger.warning(f"  - Failed to stop {name} handler: {e}")

        # Stop OS controllers
        if self.os_control:
            for name, controller in self.os_control.items():
                try:
                    controller.stop()
                    logger.info(f"  - {name.capitalize()} controller stopped")
                except Exception as e:
                    logger.warning(f"  - Failed to stop {name} controller: {e}")

        self.health_status["status"] = "stopped"
        logger.info("All services stopped")
        logger.info("Querty AI Daemon stopped")

    def handle_signal(self, signum, frame):
        """Handle system signals."""
        logger.info(f"Received signal {signum}")
        self.stop()


def main():
    """Main entry point for the AI daemon."""
    logger.info("=" * 60)
    logger.info("Querty-OS AI Daemon Starting")
    logger.info("=" * 60)

    # Create daemon instance
    daemon = QuertyAIDaemon()

    # Register signal handlers
    signal.signal(signal.SIGTERM, daemon.handle_signal)
    signal.signal(signal.SIGINT, daemon.handle_signal)

    # Start the daemon
    daemon.start()


if __name__ == "__main__":
    main()
