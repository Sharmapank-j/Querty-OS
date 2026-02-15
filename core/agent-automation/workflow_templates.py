"""
Workflow Templates for Common Automation Tasks

Predefined workflow templates for system updates, backups, cleanup, and more.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    name: str
    action: str
    params: Dict[str, Any]
    description: str = ""
    optional: bool = False
    retry_count: int = 0


@dataclass
class WorkflowTemplate:
    """Template for a workflow with multiple steps."""

    name: str
    description: str
    steps: List[WorkflowStep]
    prerequisites: List[str] = None
    estimated_duration_minutes: int = 0
    category: str = "general"

    def __post_init__(self):
        """Initialize default values."""
        if self.prerequisites is None:
            self.prerequisites = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "name": step.name,
                    "action": step.action,
                    "params": step.params,
                    "description": step.description,
                    "optional": step.optional,
                }
                for step in self.steps
            ],
            "prerequisites": self.prerequisites,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "category": self.category,
        }


class WorkflowTemplates:
    """
    Collection of predefined workflow templates.

    Provides ready-to-use templates for common tasks like system updates,
    backups, cleanup, and maintenance.
    """

    @staticmethod
    def system_update() -> WorkflowTemplate:
        """
        System update workflow.

        Returns:
            Workflow template for system updates
        """
        return WorkflowTemplate(
            name="system_update",
            description="Update system packages and components",
            category="maintenance",
            estimated_duration_minutes=15,
            prerequisites=["root_access", "internet_connection"],
            steps=[
                WorkflowStep(
                    name="create_snapshot",
                    action="snapshot.create",
                    params={"type": "full", "label": "pre_update"},
                    description="Create system snapshot before update",
                ),
                WorkflowStep(
                    name="update_package_list",
                    action="system.exec",
                    params={"command": "apt-get update"},
                    description="Update package lists",
                ),
                WorkflowStep(
                    name="upgrade_packages",
                    action="system.exec",
                    params={"command": "apt-get upgrade -y"},
                    description="Upgrade installed packages",
                ),
                WorkflowStep(
                    name="cleanup",
                    action="system.exec",
                    params={"command": "apt-get autoremove -y && apt-get autoclean"},
                    description="Clean up unused packages",
                    optional=True,
                ),
                WorkflowStep(
                    name="verify_system",
                    action="system.health_check",
                    params={},
                    description="Verify system health after update",
                ),
            ],
        )

    @staticmethod
    def backup_system() -> WorkflowTemplate:
        """
        System backup workflow.

        Returns:
            Workflow template for system backup
        """
        return WorkflowTemplate(
            name="backup_system",
            description="Create comprehensive system backup",
            category="backup",
            estimated_duration_minutes=30,
            prerequisites=["storage_space"],
            steps=[
                WorkflowStep(
                    name="check_storage",
                    action="storage.check_space",
                    params={"required_gb": 10},
                    description="Verify sufficient storage space",
                ),
                WorkflowStep(
                    name="backup_user_data",
                    action="backup.create",
                    params={"source": "/home", "type": "incremental"},
                    description="Backup user data",
                ),
                WorkflowStep(
                    name="backup_system_config",
                    action="backup.create",
                    params={"source": "/etc", "type": "full"},
                    description="Backup system configuration",
                ),
                WorkflowStep(
                    name="backup_application_data",
                    action="backup.create",
                    params={"source": "/var/lib", "type": "incremental"},
                    description="Backup application data",
                ),
                WorkflowStep(
                    name="create_snapshot",
                    action="snapshot.create",
                    params={"type": "full", "compress": True},
                    description="Create system snapshot",
                ),
                WorkflowStep(
                    name="verify_backup",
                    action="backup.verify",
                    params={},
                    description="Verify backup integrity",
                ),
            ],
        )

    @staticmethod
    def cleanup_system() -> WorkflowTemplate:
        """
        System cleanup workflow.

        Returns:
            Workflow template for system cleanup
        """
        return WorkflowTemplate(
            name="cleanup_system",
            description="Clean up temporary files and free disk space",
            category="maintenance",
            estimated_duration_minutes=10,
            prerequisites=[],
            steps=[
                WorkflowStep(
                    name="clear_temp_files",
                    action="system.exec",
                    params={"command": "rm -rf /tmp/*"},
                    description="Clear temporary files",
                ),
                WorkflowStep(
                    name="clear_cache",
                    action="system.exec",
                    params={"command": "rm -rf /var/cache/apt/archives/*.deb"},
                    description="Clear package cache",
                ),
                WorkflowStep(
                    name="clear_logs",
                    action="log.rotate",
                    params={"keep_days": 7},
                    description="Rotate and compress old logs",
                    optional=True,
                ),
                WorkflowStep(
                    name="remove_orphaned_packages",
                    action="system.exec",
                    params={"command": "apt-get autoremove -y"},
                    description="Remove orphaned packages",
                ),
                WorkflowStep(
                    name="report_space_freed",
                    action="storage.report",
                    params={},
                    description="Report freed disk space",
                ),
            ],
        )

    @staticmethod
    def security_scan() -> WorkflowTemplate:
        """
        Security scan workflow.

        Returns:
            Workflow template for security scanning
        """
        return WorkflowTemplate(
            name="security_scan",
            description="Perform security scan and vulnerability check",
            category="security",
            estimated_duration_minutes=20,
            prerequisites=[],
            steps=[
                WorkflowStep(
                    name="update_virus_definitions",
                    action="security.update_definitions",
                    params={},
                    description="Update antivirus definitions",
                    optional=True,
                ),
                WorkflowStep(
                    name="scan_filesystem",
                    action="security.scan",
                    params={"target": "/", "deep": False},
                    description="Scan filesystem for threats",
                ),
                WorkflowStep(
                    name="check_vulnerabilities",
                    action="security.vulnerability_scan",
                    params={},
                    description="Check for known vulnerabilities",
                ),
                WorkflowStep(
                    name="audit_permissions",
                    action="security.audit_permissions",
                    params={},
                    description="Audit file permissions",
                ),
                WorkflowStep(
                    name="generate_report",
                    action="security.report",
                    params={"format": "summary"},
                    description="Generate security report",
                ),
            ],
        )

    @staticmethod
    def network_optimization() -> WorkflowTemplate:
        """
        Network optimization workflow.

        Returns:
            Workflow template for network optimization
        """
        return WorkflowTemplate(
            name="network_optimization",
            description="Optimize network settings and performance",
            category="optimization",
            estimated_duration_minutes=5,
            prerequisites=["root_access"],
            steps=[
                WorkflowStep(
                    name="clear_dns_cache",
                    action="network.clear_cache",
                    params={"type": "dns"},
                    description="Clear DNS cache",
                ),
                WorkflowStep(
                    name="optimize_tcp_settings",
                    action="network.optimize",
                    params={"protocol": "tcp"},
                    description="Optimize TCP parameters",
                ),
                WorkflowStep(
                    name="restart_network_services",
                    action="service.restart",
                    params={"service": "networking"},
                    description="Restart network services",
                ),
                WorkflowStep(
                    name="test_connectivity",
                    action="network.test",
                    params={"targets": ["8.8.8.8", "1.1.1.1"]},
                    description="Test network connectivity",
                ),
            ],
        )

    @staticmethod
    def database_maintenance() -> WorkflowTemplate:
        """
        Database maintenance workflow.

        Returns:
            Workflow template for database maintenance
        """
        return WorkflowTemplate(
            name="database_maintenance",
            description="Perform routine database maintenance",
            category="maintenance",
            estimated_duration_minutes=25,
            prerequisites=["database_access"],
            steps=[
                WorkflowStep(
                    name="backup_database",
                    action="database.backup",
                    params={"compress": True},
                    description="Backup database",
                ),
                WorkflowStep(
                    name="analyze_tables",
                    action="database.analyze",
                    params={},
                    description="Analyze database tables",
                ),
                WorkflowStep(
                    name="optimize_tables",
                    action="database.optimize",
                    params={},
                    description="Optimize database tables",
                ),
                WorkflowStep(
                    name="rebuild_indexes",
                    action="database.rebuild_indexes",
                    params={},
                    description="Rebuild database indexes",
                ),
                WorkflowStep(
                    name="vacuum_database",
                    action="database.vacuum",
                    params={},
                    description="Vacuum database",
                    optional=True,
                ),
            ],
        )

    @staticmethod
    def get_all_templates() -> List[WorkflowTemplate]:
        """
        Get all available workflow templates.

        Returns:
            List of all workflow templates
        """
        return [
            WorkflowTemplates.system_update(),
            WorkflowTemplates.backup_system(),
            WorkflowTemplates.cleanup_system(),
            WorkflowTemplates.security_scan(),
            WorkflowTemplates.network_optimization(),
            WorkflowTemplates.database_maintenance(),
        ]

    @staticmethod
    def get_template_by_name(name: str) -> Optional[WorkflowTemplate]:
        """
        Get a workflow template by name.

        Args:
            name: Template name

        Returns:
            Workflow template, or None if not found
        """
        templates = {t.name: t for t in WorkflowTemplates.get_all_templates()}
        return templates.get(name)

    @staticmethod
    def get_templates_by_category(category: str) -> List[WorkflowTemplate]:
        """
        Get workflow templates by category.

        Args:
            category: Category name

        Returns:
            List of matching templates
        """
        return [t for t in WorkflowTemplates.get_all_templates() if t.category == category]

    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all available template categories.

        Returns:
            List of category names
        """
        categories = set()
        for template in WorkflowTemplates.get_all_templates():
            categories.add(template.category)
        return sorted(list(categories))
