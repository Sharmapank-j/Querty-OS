"""
Boot Profiles Module
Manages different boot modes: Safe, AI-full, Minimal, Dev
"""

from .boot_profiles import BootProfile, BootProfileManager, ProfileType

__all__ = ["BootProfile", "BootProfileManager", "ProfileType"]
