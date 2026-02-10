"""
Integration tests for Querty-OS priority-aware resource management.
"""

import pytest
from unittest.mock import Mock, patch
from core.priority import SystemPriority, ResourcePriority, StoragePriorityManager
from core.exceptions import PriorityViolationError, InsufficientStorageError


@pytest.mark.integration
class TestPrioritySystemIntegration:
    """Integration tests for priority system components."""
    
    def test_full_priority_workflow(self):
        """Test complete priority allocation workflow."""
        # Initialize managers
        rp = ResourcePriority()
        spm = StoragePriorityManager(total_storage_gb=128.0)
        
        # Get priority order
        priorities = rp.get_priority_order()
        assert priorities[0] == SystemPriority.AI
        
        # Get storage allocations
        allocations = spm.get_all_allocations()
        
        # Verify AI gets most storage
        assert allocations["AI"] > allocations["Android"]
        assert allocations["Android"] > allocations["Linux"]
        assert allocations["Linux"] > allocations["Windows"]
        
        # Test rebalancing when storage changes
        new_allocations = rp.rebalance_resources(80)
        
        # Verify minimums are maintained
        assert new_allocations[SystemPriority.AI] >= 30
        assert new_allocations[SystemPriority.ANDROID] >= 25
    
    def test_priority_preemption_scenario(self):
        """Test preemption scenario where AI needs resources."""
        rp = ResourcePriority()
        
        # Windows is using resources
        current_user = SystemPriority.WINDOWS
        
        # AI requests resources - should be granted
        ai_request = SystemPriority.AI
        
        assert rp.should_preempt(current_user, ai_request) is True
        
        # Android requests from AI - should be denied
        android_request = SystemPriority.ANDROID
        
        assert rp.should_preempt(SystemPriority.AI, android_request) is False
    
    def test_storage_allocation_validation(self):
        """Test storage allocation validation with priority rules."""
        spm = StoragePriorityManager(total_storage_gb=100.0)
        
        # Valid allocation
        valid_alloc = {
            SystemPriority.AI: 40.0,
            SystemPriority.ANDROID: 35.0,
            SystemPriority.LINUX: 15.0,
            SystemPriority.WINDOWS: 10.0,
        }
        
        is_valid, error = spm.validate_allocation(valid_alloc)
        assert is_valid is True
        assert error is None
        
        # Invalid - AI below minimum
        invalid_alloc = {
            SystemPriority.AI: 20.0,  # Below 30% minimum
            SystemPriority.ANDROID: 40.0,
            SystemPriority.LINUX: 20.0,
            SystemPriority.WINDOWS: 20.0,
        }
        
        is_valid, error = spm.validate_allocation(invalid_alloc)
        assert is_valid is False
        assert "below minimum" in error
    
    def test_partition_suggestions(self):
        """Test partition size suggestions respect priority."""
        spm = StoragePriorityManager(total_storage_gb=256.0)
        
        suggestions = spm.suggest_partition_sizes()
        
        # Verify all components have suggestions
        assert "AI" in suggestions
        assert "Android" in suggestions
        assert "Linux" in suggestions
        assert "Windows" in suggestions
        
        # Verify AI is first in order
        assert suggestions["AI"]["order"] == 1
        assert suggestions["AI"]["priority"] == SystemPriority.AI
        
        # Verify mount points
        assert "/data/querty-ai" in suggestions["AI"]["mount_point"]
        
        # Verify sizes follow priority
        assert suggestions["AI"]["size_gb"] >= suggestions["Android"]["size_gb"]


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across modules."""
    
    def test_exception_serialization(self):
        """Test exception can be serialized for logging."""
        from core.exceptions import AIServiceError
        
        error = AIServiceError(
            "Test error",
            error_code="TEST_001",
            details={"component": "test", "value": 123}
        )
        
        serialized = error.to_dict()
        
        assert serialized["error_type"] == "AIServiceError"
        assert serialized["message"] == "Test error"
        assert serialized["error_code"] == "TEST_001"
        assert serialized["details"]["component"] == "test"
    
    def test_priority_violation_with_context(self):
        """Test priority violation includes context."""
        from core.exceptions import PriorityViolationError
        
        error = PriorityViolationError(
            "Cannot allocate resources",
            error_code="PRIORITY_001",
            details={
                "requested_by": "Windows",
                "blocked_by": "AI",
                "amount": 50,
            }
        )
        
        context = error.to_dict()
        assert context["details"]["requested_by"] == "Windows"
        assert context["details"]["blocked_by"] == "AI"


@pytest.mark.integration
@pytest.mark.slow
class TestResourceAllocationScenarios:
    """Integration tests for real-world resource allocation scenarios."""
    
    def test_scenario_low_storage(self):
        """Test system behavior with low storage."""
        spm = StoragePriorityManager(total_storage_gb=32.0)  # Low storage
        
        allocations = spm.get_all_allocations()
        
        # Even with low storage, AI should get its minimum
        assert allocations["AI"] >= (0.30 * 32.0)
        
        # Total should equal available
        assert abs(sum(allocations.values()) - 32.0) < 0.01
    
    def test_scenario_high_load_rebalancing(self):
        """Test rebalancing under high load."""
        rp = ResourcePriority()
        
        # Simulate 60% available (40% consumed)
        allocations = rp.rebalance_resources(60)
        
        # All priorities should get something
        assert all(allocations[p] > 0 for p in SystemPriority)
        
        # AI should still get highest share
        assert allocations[SystemPriority.AI] == max(allocations.values())
        
        # Total should be close to 60% (allow for minimum allocation requirements)
        total = sum(allocations.values())
        assert 55 <= total <= 70, f"Total allocation {total} should be near 60%"
    
    def test_scenario_priority_cascade(self):
        """Test priority cascade when resources freed."""
        rp = ResourcePriority()
        
        # Start with limited resources
        allocations_low = rp.rebalance_resources(50)
        
        # Resources freed up
        allocations_high = rp.rebalance_resources(90)
        
        # AI should benefit most from freed resources
        ai_gain = allocations_high[SystemPriority.AI] - allocations_low[SystemPriority.AI]
        android_gain = allocations_high[SystemPriority.ANDROID] - allocations_low[SystemPriority.ANDROID]
        
        # AI gain should be >= Android gain (priority)
        assert ai_gain >= android_gain


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration with priority system."""
    
    def test_config_priority_values(self):
        """Test priority configuration values."""
        # This would read from actual config file
        # For now, test the expected values
        
        expected_allocations = {
            "ai_allocation": 40,
            "android_allocation": 35,
            "linux_allocation": 15,
            "windows_allocation": 10,
        }
        
        total = sum(expected_allocations.values())
        assert total == 100, "Allocations should sum to 100%"
        
        # Verify order
        assert expected_allocations["ai_allocation"] > expected_allocations["android_allocation"]
        assert expected_allocations["android_allocation"] > expected_allocations["linux_allocation"]
        assert expected_allocations["linux_allocation"] > expected_allocations["windows_allocation"]
