#!/usr/bin/env python3
"""
Boot Profiles System
Manages different boot modes with varying feature sets and resource usage.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger("querty-boot-profiles")


class ProfileType(Enum):
    """Boot profile types."""

    SAFE = "safe"
    AI_FULL = "ai_full"
    MINIMAL = "minimal"
    DEV = "dev"


@dataclass
class BootProfile:
    """Boot profile configuration."""

    name: str
    profile_type: ProfileType
    enabled_services: List[str]
    resource_limits: Dict[str, any]
    features: Dict[str, bool]
    description: str

    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return {
            "name": self.name,
            "type": self.profile_type.value,
            "enabled_services": self.enabled_services,
            "resource_limits": self.resource_limits,
            "features": self.features,
            "description": self.description,
        }


class BootProfileManager:
    """Manages boot profiles and switching between them."""

    def __init__(self):
        """Initialize boot profile manager."""
        self.profiles = {}
        self.current_profile = None
        self._initialize_default_profiles()
        logger.info("Boot Profile Manager initialized")

    def _initialize_default_profiles(self):
        """Initialize default boot profiles."""
        # Safe Mode
        self.profiles["safe"] = BootProfile(
            name="Safe Mode",
            profile_type=ProfileType.SAFE,
            enabled_services=["core", "network", "snapshot"],
            resource_limits={"cpu_percent": 50, "ram_mb": 512, "storage_mb": 1024},
            features={
                "ai_enabled": False,
                "voice_input": False,
                "camera_input": False,
                "automation": False,
                "plugins": False,
                "wine": False,
                "chroot": False,
            },
            description="Minimal features for troubleshooting and recovery",
        )

        # AI-Full Mode
        self.profiles["ai_full"] = BootProfile(
            name="AI-Full Mode",
            profile_type=ProfileType.AI_FULL,
            enabled_services=[
                "core",
                "llm",
                "input_handlers",
                "agent_automation",
                "os_control",
                "network",
                "snapshot",
                "plugins",
                "memory_manager",
            ],
            resource_limits={
                "cpu_percent": 100,
                "ram_mb": 4096,
                "storage_mb": 10240,
            },
            features={
                "ai_enabled": True,
                "voice_input": True,
                "camera_input": True,
                "automation": True,
                "plugins": True,
                "wine": True,
                "chroot": True,
                "creative_mode": True,
            },
            description="All AI features and maximum capabilities",
        )

        # Minimal Mode
        self.profiles["minimal"] = BootProfile(
            name="Minimal Mode",
            profile_type=ProfileType.MINIMAL,
            enabled_services=["core", "llm", "network"],
            resource_limits={"cpu_percent": 60, "ram_mb": 1024, "storage_mb": 2048},
            features={
                "ai_enabled": True,
                "voice_input": False,
                "camera_input": False,
                "automation": False,
                "plugins": False,
                "wine": False,
                "chroot": False,
                "deterministic_only": True,
            },
            description="Essential AI features with low resource usage",
        )

        # Dev Mode
        self.profiles["dev"] = BootProfile(
            name="Dev Mode",
            profile_type=ProfileType.DEV,
            enabled_services=[
                "core",
                "llm",
                "input_handlers",
                "network",
                "cli_api",
                "debug",
            ],
            resource_limits={
                "cpu_percent": 80,
                "ram_mb": 2048,
                "storage_mb": 4096,
            },
            features={
                "ai_enabled": True,
                "voice_input": True,
                "camera_input": True,
                "automation": False,
                "plugins": True,
                "wine": False,
                "chroot": True,
                "debug_mode": True,
                "cli_enabled": True,
                "api_enabled": True,
                "verbose_logging": True,
            },
            description="Development mode with debugging and API access",
        )

        logger.info(f"Initialized {len(self.profiles)} default boot profiles")

    def get_profile(self, profile_name: str) -> Optional[BootProfile]:
        """Get boot profile by name."""
        return self.profiles.get(profile_name)

    def set_current_profile(self, profile_name: str) -> bool:
        """Set the current active boot profile."""
        profile = self.get_profile(profile_name)
        if not profile:
            logger.error(f"Profile '{profile_name}' not found")
            return False

        self.current_profile = profile
        logger.info(
            f"Switched to boot profile: {profile.name} ({profile.profile_type.value})"
        )
        return True

    def get_current_profile(self) -> Optional[BootProfile]:
        """Get the current active boot profile."""
        return self.current_profile

    def list_profiles(self) -> List[str]:
        """List all available boot profile names."""
        return list(self.profiles.keys())

    def is_feature_enabled(
        self, feature_name: str, profile_name: Optional[str] = None
    ) -> bool:
        """Check if a feature is enabled in a profile."""
        profile = (
            self.get_profile(profile_name) if profile_name else self.current_profile
        )
        if not profile:
            return False
        return profile.features.get(feature_name, False)
