"""
Unit tests for Querty-OS priority management system.
"""

import pytest
from core.priority import (
    SystemPriority,
    ResourcePriority,
    StoragePriorityManager,
)


class TestSystemPriority:
    """Test SystemPriority enum."""
    
    def test_priority_values(self):
        """Test priority values are in correct order."""
        assert SystemPriority.AI > SystemPriority.ANDROID
        assert SystemPriority.ANDROID > SystemPriority.LINUX
        assert SystemPriority.LINUX > SystemPriority.WINDOWS
    
    def test_priority_order(self):
        """Test priorities are ordered correctly."""
        assert SystemPriority.AI.value == 4
        assert SystemPriority.ANDROID.value == 3
        assert SystemPriority.LINUX.value == 2
        assert SystemPriority.WINDOWS.value == 1
    
    def test_get_name(self):
        """Test getting human-readable names."""
        assert SystemPriority.get_name(SystemPriority.AI) == "AI"
        assert SystemPriority.get_name(SystemPriority.ANDROID) == "Android"
        assert SystemPriority.get_name(SystemPriority.LINUX) == "Linux"
        assert SystemPriority.get_name(SystemPriority.WINDOWS) == "Windows"


class TestResourcePriority:
    """Test ResourcePriority class."""
    
    def test_default_allocations(self):
        """Test default resource allocations."""
        rp = ResourcePriority()
        
        assert rp.get_allocation(SystemPriority.AI) == 40
        assert rp.get_allocation(SystemPriority.ANDROID) == 35
        assert rp.get_allocation(SystemPriority.LINUX) == 15
        assert rp.get_allocation(SystemPriority.WINDOWS) == 10
    
    def test_set_allocation(self):
        """Test setting resource allocation."""
        rp = ResourcePriority()
        
        # Should succeed
        assert rp.set_allocation(SystemPriority.AI, 50) is True
        assert rp.get_allocation(SystemPriority.AI) == 50
    
    def test_minimum_allocation_enforcement(self):
        """Test minimum allocations are enforced."""
        rp = ResourcePriority()
        
        # Should fail - below minimum
        assert rp.set_allocation(SystemPriority.AI, 20) is False
        # Should still be at default
        assert rp.get_allocation(SystemPriority.AI) == 40
    
    def test_get_priority_order(self):
        """Test getting priorities in order."""
        rp = ResourcePriority()
        order = rp.get_priority_order()
        
        assert order[0] == SystemPriority.AI
        assert order[1] == SystemPriority.ANDROID
        assert order[2] == SystemPriority.LINUX
        assert order[3] == SystemPriority.WINDOWS
    
    def test_should_preempt(self):
        """Test preemption logic."""
        rp = ResourcePriority()
        
        # AI should preempt Windows
        assert rp.should_preempt(
            SystemPriority.WINDOWS,
            SystemPriority.AI
        ) is True
        
        # Windows should not preempt AI
        assert rp.should_preempt(
            SystemPriority.AI,
            SystemPriority.WINDOWS
        ) is False
        
        # Android should preempt Linux
        assert rp.should_preempt(
            SystemPriority.LINUX,
            SystemPriority.ANDROID
        ) is True
    
    def test_rebalance_resources(self):
        """Test resource rebalancing."""
        rp = ResourcePriority()
        
        # Test with 80% available
        allocations = rp.rebalance_resources(80)
        
        # All priorities should get something
        assert all(allocations[p] > 0 for p in SystemPriority)
        
        # AI should get the most
        assert allocations[SystemPriority.AI] >= allocations[SystemPriority.ANDROID]
        assert allocations[SystemPriority.ANDROID] >= allocations[SystemPriority.LINUX]
        assert allocations[SystemPriority.LINUX] >= allocations[SystemPriority.WINDOWS]
        
        # Total should be 80%
        assert sum(allocations.values()) == 80


class TestStoragePriorityManager:
    """Test StoragePriorityManager class."""
    
    def test_initialization(self):
        """Test storage manager initialization."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        assert spm.total_storage == 100.0
    
    def test_get_storage_allocation(self):
        """Test getting storage allocation."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        
        # AI should get 40% of 100GB = 40GB
        ai_storage = spm.get_storage_allocation(SystemPriority.AI)
        assert ai_storage == 40.0
        
        # Android should get 35% of 100GB = 35GB
        android_storage = spm.get_storage_allocation(SystemPriority.ANDROID)
        assert android_storage == 35.0
    
    def test_get_all_allocations(self):
        """Test getting all allocations."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        allocations = spm.get_all_allocations()
        
        assert "AI" in allocations
        assert "Android" in allocations
        assert "Linux" in allocations
        assert "Windows" in allocations
        
        # Total should be 100GB
        assert sum(allocations.values()) == 100.0
    
    def test_suggest_partition_sizes(self):
        """Test partition size suggestions."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        suggestions = spm.suggest_partition_sizes()
        
        # All components should have suggestions
        assert "AI" in suggestions
        assert "Android" in suggestions
        assert "Linux" in suggestions
        assert "Windows" in suggestions
        
        # AI should be first in order
        assert suggestions["AI"]["order"] == 1
        assert suggestions["Android"]["order"] == 2
        
        # Check mount points are defined
        assert suggestions["AI"]["mount_point"] == "/data/querty-ai"
        assert suggestions["Linux"]["mount_point"] == "/data/linux"
    
    def test_validate_allocation_success(self):
        """Test validation of valid allocation."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        
        requested = {
            SystemPriority.AI: 40.0,
            SystemPriority.ANDROID: 35.0,
            SystemPriority.LINUX: 15.0,
            SystemPriority.WINDOWS: 10.0,
        }
        
        is_valid, error = spm.validate_allocation(requested)
        assert is_valid is True
        assert error is None
    
    def test_validate_allocation_exceeds_total(self):
        """Test validation fails when exceeding total."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        
        requested = {
            SystemPriority.AI: 50.0,
            SystemPriority.ANDROID: 50.0,
            SystemPriority.LINUX: 20.0,
            SystemPriority.WINDOWS: 20.0,
        }
        
        is_valid, error = spm.validate_allocation(requested)
        assert is_valid is False
        assert "exceeds available" in error
    
    def test_validate_allocation_below_minimum(self):
        """Test validation fails when below minimum."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        
        requested = {
            SystemPriority.AI: 20.0,  # Below 30% minimum
            SystemPriority.ANDROID: 40.0,
            SystemPriority.LINUX: 20.0,
            SystemPriority.WINDOWS: 20.0,
        }
        
        is_valid, error = spm.validate_allocation(requested)
        assert is_valid is False
        assert "below minimum" in error
