#!/usr/bin/env python3
"""Tests for boot profiles system."""

import pytest
from core.boot_profiles import BootProfile, BootProfileManager, ProfileType


class TestBootProfileManager:
    """Test boot profile manager functionality."""

    def test_initialization(self):
        """Test manager initialization with default profiles."""
        manager = BootProfileManager()
        assert manager is not None
        assert len(manager.profiles) == 4  # safe, ai_full, minimal, dev
        assert manager.current_profile is None

    def test_get_profile(self):
        """Test getting a profile by name."""
        manager = BootProfileManager()
        profile = manager.get_profile("safe")
        assert profile is not None
        assert profile.name == "Safe Mode"
        assert profile.profile_type == ProfileType.SAFE

    def test_set_current_profile(self):
        """Test setting current profile."""
        manager = BootProfileManager()
        result = manager.set_current_profile("minimal")
        assert result is True
        assert manager.current_profile is not None
        assert manager.current_profile.profile_type == ProfileType.MINIMAL

    def test_set_invalid_profile(self):
        """Test setting invalid profile returns False."""
        manager = BootProfileManager()
        result = manager.set_current_profile("nonexistent")
        assert result is False
        assert manager.current_profile is None

    def test_list_profiles(self):
        """Test listing all profiles."""
        manager = BootProfileManager()
        profiles = manager.list_profiles()
        assert len(profiles) == 4
        assert "safe" in profiles
        assert "ai_full" in profiles
        assert "minimal" in profiles
        assert "dev" in profiles

    def test_is_feature_enabled(self):
        """Test checking if feature is enabled."""
        manager = BootProfileManager()
        manager.set_current_profile("ai_full")
        assert manager.is_feature_enabled("voice_input") is True
        assert manager.is_feature_enabled("camera_input") is True
        assert manager.is_feature_enabled("plugins") is True

    def test_feature_disabled_in_safe_mode(self):
        """Test features are disabled in safe mode."""
        manager = BootProfileManager()
        manager.set_current_profile("safe")
        assert manager.is_feature_enabled("ai_enabled") is False
        assert manager.is_feature_enabled("voice_input") is False
        assert manager.is_feature_enabled("plugins") is False

    def test_profile_resource_limits(self):
        """Test profile resource limits."""
        manager = BootProfileManager()
        safe_profile = manager.get_profile("safe")
        assert safe_profile.resource_limits["cpu_percent"] == 50
        assert safe_profile.resource_limits["ram_mb"] == 512

        ai_full_profile = manager.get_profile("ai_full")
        assert ai_full_profile.resource_limits["cpu_percent"] == 100
        assert ai_full_profile.resource_limits["ram_mb"] == 4096

    def test_profile_enabled_services(self):
        """Test profile enabled services."""
        manager = BootProfileManager()
        minimal_profile = manager.get_profile("minimal")
        assert "core" in minimal_profile.enabled_services
        assert "llm" in minimal_profile.enabled_services
        assert "plugins" not in minimal_profile.enabled_services


class TestBootProfile:
    """Test boot profile data structure."""

    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = BootProfile(
            name="Test",
            profile_type=ProfileType.DEV,
            enabled_services=["test"],
            resource_limits={"cpu": 50},
            features={"test": True},
            description="Test profile",
        )
        data = profile.to_dict()
        assert data["name"] == "Test"
        assert data["type"] == "dev"
        assert data["enabled_services"] == ["test"]
        assert data["description"] == "Test profile"
