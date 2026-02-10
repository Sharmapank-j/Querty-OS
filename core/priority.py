"""
Querty-OS Priority Management System
Manages resource allocation priority: AI > Android > Linux > Windows
"""

import logging
from enum import IntEnum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SystemPriority(IntEnum):
    """
    System component priorities (higher value = higher priority).
    Priority order: AI > Android > Linux > Windows
    """

    WINDOWS = 1  # Lowest priority - Wine/Windows apps
    LINUX = 2  # Third priority - Linux chroot
    ANDROID = 3  # Second priority - Android native
    AI = 4  # Highest priority - AI/LLM services

    @classmethod
    def get_name(cls, priority: int) -> str:
        """Get human-readable name for priority level."""
        names = {
            cls.WINDOWS: "Windows",
            cls.LINUX: "Linux",
            cls.ANDROID: "Android",
            cls.AI: "AI",
        }
        return names.get(priority, "Unknown")


class ResourcePriority:
    """Manages resource allocation based on system priorities."""

    # Default resource allocation percentages by priority
    DEFAULT_ALLOCATIONS = {
        SystemPriority.AI: 40,  # 40% for AI/LLM
        SystemPriority.ANDROID: 35,  # 35% for Android
        SystemPriority.LINUX: 15,  # 15% for Linux
        SystemPriority.WINDOWS: 10,  # 10% for Windows
    }

    # Minimum guaranteed allocations (cannot go below)
    MINIMUM_ALLOCATIONS = {
        SystemPriority.AI: 30,  # At least 30% for AI
        SystemPriority.ANDROID: 25,  # At least 25% for Android
        SystemPriority.LINUX: 5,  # At least 5% for Linux
        SystemPriority.WINDOWS: 5,  # At least 5% for Windows
    }

    def __init__(self):
        """Initialize resource priority manager."""
        self.allocations = self.DEFAULT_ALLOCATIONS.copy()
        logger.info("Resource priority initialized with AI > Android > Linux > Windows")

    def get_allocation(self, priority: SystemPriority) -> int:
        """
        Get resource allocation percentage for a priority level.

        Args:
            priority: System priority level

        Returns:
            Allocation percentage (0-100)
        """
        return self.allocations.get(priority, 0)

    def set_allocation(self, priority: SystemPriority, percentage: int) -> bool:
        """
        Set resource allocation for a priority level.
        Ensures minimum allocations are maintained.

        Args:
            priority: System priority level
            percentage: Desired allocation percentage

        Returns:
            True if allocation was set successfully
        """
        min_alloc = self.MINIMUM_ALLOCATIONS.get(priority, 0)

        if percentage < min_alloc:
            logger.warning(
                f"Cannot set {SystemPriority.get_name(priority)} allocation below "
                f"minimum {min_alloc}%. Requested: {percentage}%"
            )
            return False

        self.allocations[priority] = percentage
        logger.info(f"Set {SystemPriority.get_name(priority)} allocation to {percentage}%")
        return True

    def rebalance_resources(self, available_percentage: int) -> Dict[SystemPriority, int]:
        """
        Rebalance resources when total available changes.
        Maintains priority order: AI > Android > Linux > Windows

        Args:
            available_percentage: Total available resource percentage

        Returns:
            Dictionary of priority to allocated percentage
        """
        # Start with minimum allocations
        new_allocations = self.MINIMUM_ALLOCATIONS.copy()
        remaining = available_percentage - sum(new_allocations.values())

        if remaining <= 0:
            logger.warning("Insufficient resources to meet minimum allocations")
            return new_allocations

        # Distribute remaining resources by priority (highest first)
        priorities_sorted = sorted(SystemPriority, key=lambda x: x.value, reverse=True)

        for priority in priorities_sorted:
            min_alloc = self.MINIMUM_ALLOCATIONS[priority]
            default_alloc = self.DEFAULT_ALLOCATIONS[priority]
            additional = min(remaining, default_alloc - min_alloc)

            new_allocations[priority] = min_alloc + additional
            remaining -= additional

            if remaining <= 0:
                break

        # If there's still remaining, give to AI (highest priority)
        if remaining > 0:
            new_allocations[SystemPriority.AI] += remaining

        self.allocations = new_allocations
        logger.info(f"Rebalanced resources: {self._format_allocations()}")
        return new_allocations

    def get_priority_order(self) -> list:
        """
        Get components in priority order (highest to lowest).

        Returns:
            List of priorities in descending order
        """
        return sorted(SystemPriority, key=lambda x: x.value, reverse=True)

    def should_preempt(
        self, current_priority: SystemPriority, requesting_priority: SystemPriority
    ) -> bool:
        """
        Determine if a requesting component should preempt current one.

        Args:
            current_priority: Priority of current resource holder
            requesting_priority: Priority of requesting component

        Returns:
            True if requesting component should preempt
        """
        return requesting_priority.value > current_priority.value

    def _format_allocations(self) -> str:
        """Format current allocations for logging."""
        parts = []
        for priority in self.get_priority_order():
            name = SystemPriority.get_name(priority)
            percentage = self.allocations.get(priority, 0)
            parts.append(f"{name}={percentage}%")
        return ", ".join(parts)


class StoragePriorityManager:
    """Manages storage allocation based on priority system."""

    def __init__(self, total_storage_gb: float):
        """
        Initialize storage priority manager.

        Args:
            total_storage_gb: Total available storage in GB
        """
        self.total_storage = total_storage_gb
        self.resource_priority = ResourcePriority()
        logger.info(f"Storage priority initialized with {total_storage_gb}GB total")

    def get_storage_allocation(self, priority: SystemPriority) -> float:
        """
        Get storage allocation in GB for a priority level.

        Args:
            priority: System priority level

        Returns:
            Storage allocation in GB
        """
        percentage = self.resource_priority.get_allocation(priority)
        return (percentage / 100.0) * self.total_storage

    def get_all_allocations(self) -> Dict[str, float]:
        """
        Get storage allocations for all priorities.

        Returns:
            Dictionary mapping priority names to storage in GB
        """
        allocations = {}
        for priority in SystemPriority:
            name = SystemPriority.get_name(priority)
            gb = self.get_storage_allocation(priority)
            allocations[name] = gb
        return allocations

    def suggest_partition_sizes(self) -> Dict[str, dict]:
        """
        Suggest partition sizes based on priority system.

        Returns:
            Dictionary with partition suggestions for each component
        """
        allocations = self.get_all_allocations()

        suggestions = {
            "AI": {
                "size_gb": allocations["AI"],
                "priority": SystemPriority.AI,
                "description": "AI models, LLM cache, embeddings",
                "mount_point": "/data/querty-ai",
                "order": 1,
            },
            "Android": {
                "size_gb": allocations["Android"],
                "priority": SystemPriority.ANDROID,
                "description": "Android apps, data, cache",
                "mount_point": "/data/android",
                "order": 2,
            },
            "Linux": {
                "size_gb": allocations["Linux"],
                "priority": SystemPriority.LINUX,
                "description": "Linux chroot, packages, data",
                "mount_point": "/data/linux",
                "order": 3,
            },
            "Windows": {
                "size_gb": allocations["Windows"],
                "priority": SystemPriority.WINDOWS,
                "description": "Wine prefix, Windows apps, data",
                "mount_point": "/data/wine",
                "order": 4,
            },
        }

        return suggestions

    def validate_allocation(
        self, requested: Dict[SystemPriority, float]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if requested storage allocation respects priority rules.

        Args:
            requested: Dictionary of priority to requested GB

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check total doesn't exceed available
        total_requested = sum(requested.values())
        if total_requested > self.total_storage:
            return (
                False,
                f"Total requested ({total_requested}GB) exceeds available ({self.total_storage}GB)",
            )

        # Check minimum allocations are met for higher priorities
        for priority in SystemPriority:
            min_percentage = ResourcePriority.MINIMUM_ALLOCATIONS.get(priority, 0)
            min_gb = (min_percentage / 100.0) * self.total_storage
            actual_gb = requested.get(priority, 0)

            if actual_gb < min_gb:
                name = SystemPriority.get_name(priority)
                return False, f"{name} allocation ({actual_gb}GB) below minimum ({min_gb}GB)"

        # Verify priority order is maintained (higher priority gets at least minimum)
        priorities_sorted = sorted(SystemPriority, key=lambda x: x.value, reverse=True)
        for i, priority in enumerate(priorities_sorted):
            if i == 0:
                continue  # Skip first (highest priority)

            higher_priority = priorities_sorted[i - 1]
            if requested.get(priority, 0) > requested.get(higher_priority, 0):
                high_name = SystemPriority.get_name(higher_priority)
                low_name = SystemPriority.get_name(priority)
                logger.warning(
                    f"{low_name} has more storage than {high_name}, "
                    f"which violates priority order"
                )

        return True, None
