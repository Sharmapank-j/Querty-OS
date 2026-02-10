#!/usr/bin/env python3
"""
Querty-OS REST API
Provides HTTP API for system control and monitoring.
"""

import logging
from datetime import datetime

logger = logging.getLogger("querty-api")


class QuertyAPI:
    """REST API server for Querty-OS."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Initialize API server.

        Args:
            host: Server host address
            port: Server port
        """
        self.host = host
        self.port = port
        self.app = None
        logger.info(f"QuertyAPI initialized on {host}:{port}")

    def _create_app(self):
        """Create Flask application."""
        try:
            from flask import Flask, jsonify, request

            app = Flask("querty-os")

            @app.route("/api/v1/status", methods=["GET"])
            def get_status():
                """Get system status."""
                return jsonify(
                    {
                        "status": "running",
                        "timestamp": datetime.now().isoformat(),
                        "services": {
                            "ai_daemon": "running",
                            "memory_manager": "running",
                            "input_handlers": "running",
                        },
                    }
                )

            @app.route("/api/v1/services", methods=["GET"])
            def list_services():
                """List all services."""
                return jsonify(
                    {
                        "services": [
                            {"name": "ai_daemon", "status": "running"},
                            {"name": "memory_manager", "status": "running"},
                            {"name": "input_handlers", "status": "running"},
                        ]
                    }
                )

            @app.route("/api/v1/services/<service_name>", methods=["POST"])
            def control_service(service_name: str):
                """Control a service (start/stop/restart)."""
                action = request.json.get("action")
                logger.info(f"Service control: {service_name} - {action}")
                return jsonify({"service": service_name, "action": action, "status": "success"})

            @app.route("/api/v1/tasks", methods=["GET"])
            def list_tasks():
                """List active tasks."""
                return jsonify(
                    {
                        "tasks": [
                            {
                                "id": "001",
                                "description": "Process camera input",
                                "status": "running",
                            }
                        ]
                    }
                )

            @app.route("/api/v1/tasks", methods=["POST"])
            def execute_task():
                """Execute a new task."""
                data = request.json
                task_id = f"task_{datetime.now().timestamp()}"
                logger.info(f"New task: {task_id} - {data.get('description')}")
                return jsonify({"task_id": task_id, "status": "queued", "data": data}), 201

            @app.route("/api/v1/tasks/<task_id>", methods=["DELETE"])
            def cancel_task(task_id: str):
                """Cancel a task."""
                logger.info(f"Cancelling task: {task_id}")
                return jsonify({"task_id": task_id, "status": "cancelled"})

            @app.route("/api/v1/logs", methods=["GET"])
            def get_logs():
                """Get system logs."""
                lines = request.args.get("lines", 50, type=int)
                service = request.args.get("service")
                return jsonify(
                    {"lines": lines, "service": service, "logs": ["Log entry 1", "Log entry 2"]}
                )

            @app.route("/api/v1/memory", methods=["GET"])
            def get_memory_info():
                """Get memory information."""
                return jsonify(
                    {
                        "total_tasks": 42,
                        "current_tokens": 6234,
                        "max_tokens": 8192,
                        "utilization": 0.76,
                    }
                )

            @app.route("/api/v1/memory/optimize", methods=["POST"])
            def optimize_memory():
                """Optimize memory usage."""
                logger.info("Memory optimization requested")
                return jsonify({"status": "success", "freed_tokens": 1024})

            @app.route("/api/v1/config", methods=["GET"])
            def get_config():
                """Get current configuration."""
                return jsonify(
                    {
                        "llm_mode": "deterministic",
                        "max_context_tokens": 8192,
                        "storage_path": "~/.querty",
                    }
                )

            @app.route("/api/v1/config", methods=["PUT"])
            def update_config():
                """Update configuration."""
                data = request.json
                logger.info(f"Config update: {data}")
                return jsonify({"status": "success", "config": data})

            return app

        except ImportError:
            logger.error("Flask not available - API disabled")
            return None

    def run(self, debug: bool = False):
        """
        Run the API server.

        Args:
            debug: Enable debug mode
        """
        if self.app is None:
            self.app = self._create_app()

        if self.app is None:
            logger.error("Cannot start API server - Flask not available")
            return

        logger.info(f"Starting API server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)

    def stop(self):
        """Stop the API server."""
        logger.info("Stopping API server")


def create_api(host: str = "127.0.0.1", port: int = 5000) -> QuertyAPI:
    """
    Factory function to create API instance.

    Args:
        host: Server host address
        port: Server port

    Returns:
        QuertyAPI instance
    """
    return QuertyAPI(host=host, port=port)
