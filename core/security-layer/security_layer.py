#!/usr/bin/env python3
"""
Querty-OS Security Layer
Provides sandboxing, prompt filtering, audit logging, and permission management.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("querty-security-layer")


class SecurityLevel(Enum):
    """Security levels for operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Represents a security event."""

    event_id: str
    event_type: str
    timestamp: datetime
    level: SecurityLevel
    source: str
    description: str
    metadata: Dict[str, Any]
    action_taken: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "source": self.source,
            "description": self.description,
            "metadata": self.metadata,
            "action_taken": self.action_taken,
        }


class PromptFirewall:
    """Filters dangerous or malicious prompts."""

    def __init__(self):
        """Initialize prompt firewall."""
        self.blocked_patterns = self._load_blocked_patterns()
        self.suspicious_keywords = self._load_suspicious_keywords()
        self.block_count = 0
        logger.info("PromptFirewall initialized")

    def _load_blocked_patterns(self) -> List[re.Pattern]:
        """Load patterns for dangerous prompts."""
        patterns = [
            (
                r"(?i)(ignore|disregard|forget)\s+(previous|all|your)\s+"
                r"(instructions|rules|directives)"
            ),
            r"(?i)system\s*prompt",
            r"(?i)sudo\s+rm\s+-rf",
            r"(?i)drop\s+table",
            r"(?i)exec\(|eval\(",
            r"(?i)__import__",
            r"(?i)\/etc\/passwd",
            r"(?i)\/proc\/",
        ]
        return [re.compile(p) for p in patterns]

    def _load_suspicious_keywords(self) -> Set[str]:
        """Load suspicious keywords."""
        return {
            "password",
            "token",
            "api_key",
            "secret",
            "private_key",
            "credentials",
            "exploit",
            "backdoor",
            "injection",
        }

    def check_prompt(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Check if prompt is safe.

        Args:
            prompt: User prompt to check

        Returns:
            Tuple of (is_safe, reason_if_blocked)
        """
        for pattern in self.blocked_patterns:
            if pattern.search(prompt):
                self.block_count += 1
                reason = f"Blocked: matches dangerous pattern {pattern.pattern}"
                logger.warning(f"Prompt blocked: {reason}")
                return False, reason

        prompt_lower = prompt.lower()
        suspicious_found = [kw for kw in self.suspicious_keywords if kw in prompt_lower]

        if len(suspicious_found) >= 3:
            self.block_count += 1
            reason = f"Blocked: contains multiple suspicious keywords: {suspicious_found}"
            logger.warning(f"Prompt blocked: {reason}")
            return False, reason

        return True, None

    def sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize prompt by removing potentially dangerous content.

        Args:
            prompt: Prompt to sanitize

        Returns:
            Sanitized prompt
        """
        sanitized = prompt

        # Remove script tags with a permissive pattern that handles
        # various whitespace and malformed tags, though technically
        # HTML closing tags don't support attributes
        sanitized = re.sub(
            r"<script\b[^>]*>.*?</\s*script[^>]*>", "", sanitized, flags=re.DOTALL | re.IGNORECASE
        )
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"on\w+\s*=", "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    def add_blocked_pattern(self, pattern: str):
        """
        Add a new blocked pattern.

        Args:
            pattern: Regex pattern to block
        """
        self.blocked_patterns.append(re.compile(pattern))
        logger.info(f"Added blocked pattern: {pattern}")

    def get_stats(self) -> Dict[str, Any]:
        """Get firewall statistics."""
        return {
            "blocked_patterns": len(self.blocked_patterns),
            "suspicious_keywords": len(self.suspicious_keywords),
            "total_blocked": self.block_count,
        }


class AuditLogger:
    """Logs security events for auditing."""

    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize audit logger.

        Args:
            log_path: Path for audit logs
        """
        self.log_path = log_path or Path.home() / ".querty" / "security" / "audit.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: List[SecurityEvent] = []
        logger.info(f"AuditLogger initialized at {self.log_path}")

    def log_event(
        self,
        event_type: str,
        level: SecurityLevel,
        source: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        action_taken: Optional[str] = None,
    ):
        """
        Log a security event.

        Args:
            event_type: Type of event
            level: Security level
            source: Source component
            description: Event description
            metadata: Additional metadata
            action_taken: Action taken in response
        """
        event = SecurityEvent(
            event_id=f"evt_{datetime.now().timestamp()}",
            event_type=event_type,
            timestamp=datetime.now(),
            level=level,
            source=source,
            description=description,
            metadata=metadata or {},
            action_taken=action_taken,
        )

        self.events.append(event)
        self._write_to_file(event)

        if level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            logger.warning(f"Security event [{level.value}]: {description}")
        else:
            logger.info(f"Security event [{level.value}]: {description}")

    def _write_to_file(self, event: SecurityEvent):
        """Write event to audit log file."""
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Error writing to audit log: {e}")

    def get_events(
        self,
        level: Optional[SecurityLevel] = None,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """
        Retrieve security events.

        Args:
            level: Filter by security level
            event_type: Filter by event type
            since: Filter by timestamp
            limit: Maximum number of events

        Returns:
            List of matching events
        """
        filtered_events = self.events

        if level:
            filtered_events = [e for e in filtered_events if e.level == level]

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        if since:
            filtered_events = [e for e in filtered_events if e.timestamp >= since]

        return filtered_events[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        """Get audit log summary."""
        level_counts = {}
        for level in SecurityLevel:
            level_counts[level.value] = sum(1 for e in self.events if e.level == level)

        return {
            "total_events": len(self.events),
            "by_level": level_counts,
            "latest_event": self.events[-1].to_dict() if self.events else None,
        }


class PermissionManager:
    """Manages permissions for operations and resources."""

    def __init__(self):
        """Initialize permission manager."""
        self.permissions: Dict[str, Set[str]] = {}
        self.roles: Dict[str, Set[str]] = {}
        self._initialize_default_roles()
        logger.info("PermissionManager initialized")

    def _initialize_default_roles(self):
        """Initialize default roles and permissions."""
        self.roles["user"] = {
            "task.execute",
            "task.view",
            "memory.read",
            "logs.read",
        }

        self.roles["admin"] = {
            "task.execute",
            "task.view",
            "task.cancel",
            "memory.read",
            "memory.write",
            "memory.clear",
            "logs.read",
            "logs.clear",
            "service.start",
            "service.stop",
            "service.restart",
            "config.read",
            "config.write",
        }

        self.roles["system"] = {
            "task.execute",
            "task.view",
            "task.cancel",
            "memory.read",
            "memory.write",
            "memory.clear",
            "logs.read",
            "logs.write",
            "logs.clear",
            "service.start",
            "service.stop",
            "service.restart",
            "config.read",
            "config.write",
            "system.update",
            "system.snapshot",
            "security.audit",
        }

    def grant_permission(self, subject: str, permission: str):
        """
        Grant permission to subject.

        Args:
            subject: Subject identifier (user, service, etc.)
            permission: Permission to grant
        """
        if subject not in self.permissions:
            self.permissions[subject] = set()

        self.permissions[subject].add(permission)
        logger.info(f"Granted permission '{permission}' to '{subject}'")

    def revoke_permission(self, subject: str, permission: str):
        """
        Revoke permission from subject.

        Args:
            subject: Subject identifier
            permission: Permission to revoke
        """
        if subject in self.permissions:
            self.permissions[subject].discard(permission)
            logger.info(f"Revoked permission '{permission}' from '{subject}'")

    def assign_role(self, subject: str, role: str):
        """
        Assign role to subject.

        Args:
            subject: Subject identifier
            role: Role name
        """
        if role not in self.roles:
            logger.error(f"Role '{role}' does not exist")
            return

        if subject not in self.permissions:
            self.permissions[subject] = set()

        self.permissions[subject].update(self.roles[role])
        logger.info(f"Assigned role '{role}' to '{subject}'")

    def check_permission(self, subject: str, permission: str) -> bool:
        """
        Check if subject has permission.

        Args:
            subject: Subject identifier
            permission: Permission to check

        Returns:
            True if subject has permission
        """
        subject_perms = self.permissions.get(subject, set())
        has_permission = permission in subject_perms

        logger.debug(f"Permission check: {subject} -> {permission} = {has_permission}")
        return has_permission

    def get_permissions(self, subject: str) -> Set[str]:
        """
        Get all permissions for subject.

        Args:
            subject: Subject identifier

        Returns:
            Set of permissions
        """
        return self.permissions.get(subject, set()).copy()

    def create_role(self, role_name: str, permissions: Set[str]):
        """
        Create a new role.

        Args:
            role_name: Name of the role
            permissions: Set of permissions
        """
        self.roles[role_name] = permissions.copy()
        logger.info(f"Created role '{role_name}' with {len(permissions)} permissions")

    def get_role_permissions(self, role_name: str) -> Optional[Set[str]]:
        """
        Get permissions for a role.

        Args:
            role_name: Name of the role

        Returns:
            Set of permissions or None if role doesn't exist
        """
        return self.roles.get(role_name, set()).copy() if role_name in self.roles else None


def create_sandbox_environment() -> Dict[str, Any]:
    """
    Create a sandboxed environment configuration.

    Returns:
        Sandbox configuration
    """
    sandbox_config = {
        "filesystem": {
            "read_only": ["/sys", "/proc"],
            "no_access": ["/root", "/etc/shadow", "/etc/passwd"],
            "writable": ["/tmp", "/home/user/.querty/sandbox"],
        },
        "network": {
            "allowed_hosts": ["api.querty-os.local"],
            "blocked_ports": [22, 23, 3389],
        },
        "resources": {
            "max_memory_mb": 512,
            "max_cpu_percent": 50,
            "max_processes": 10,
        },
        "capabilities": {
            "allow_exec": False,
            "allow_network": True,
            "allow_file_write": True,
        },
    }

    logger.info("Sandbox environment configuration created")
    return sandbox_config
