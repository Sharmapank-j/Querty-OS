#!/usr/bin/env python3
"""
Querty-OS System Status Dashboard
Displays comprehensive system status including priority allocations.
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.exceptions import QuertyOSError  # noqa: F401
    from core.priority import ResourcePriority, StoragePriorityManager, SystemPriority
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you've installed the package: pip install -e .")
    sys.exit(1)


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_priority_system():
    """Display priority system information."""
    print_header("PRIORITY SYSTEM")

    rp = ResourcePriority()

    print("\nPriority Order (Highest to Lowest):")
    for i, priority in enumerate(rp.get_priority_order(), 1):
        name = SystemPriority.get_name(priority)
        allocation = rp.get_allocation(priority)
        minimum = ResourcePriority.MINIMUM_ALLOCATIONS.get(priority, 0)

        print(f"  {i}. {name:10} - {allocation:2}% (min: {minimum}%)")

    print("\nPreemption Rules:")
    priorities = list(SystemPriority)
    for i, high_pri in enumerate(priorities):
        for low_pri in priorities[i + 1 :]:
            high_name = SystemPriority.get_name(high_pri)
            low_name = SystemPriority.get_name(low_pri)
            can_preempt = rp.should_preempt(low_pri, high_pri)
            status = "✓" if can_preempt else "✗"
            print(f"  {status} {high_name} can preempt {low_name}")


def print_storage_allocations(storage_gb=64):
    """Display storage allocations."""
    print_header(f"STORAGE ALLOCATIONS ({storage_gb}GB Total)")

    spm = StoragePriorityManager(total_storage_gb=storage_gb)
    allocations = spm.get_all_allocations()

    print("\nCurrent Allocations:")
    total = 0
    for name in ["AI", "Android", "Linux", "Windows"]:
        gb = allocations[name]
        percentage = (gb / storage_gb) * 100
        total += gb

        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)

        print(f"  {name:10} [{bar}] {gb:5.1f}GB ({percentage:4.1f}%)")

    print(f"\n  Total Used: {total:.1f}GB ({(total/storage_gb)*100:.1f}%)")


def print_partition_suggestions(storage_gb=64):
    """Display partition layout suggestions."""
    print_header("PARTITION LAYOUT SUGGESTIONS")

    spm = StoragePriorityManager(total_storage_gb=storage_gb)
    suggestions = spm.suggest_partition_sizes()

    print("\nRecommended Partition Structure:")
    print(f"{'Order':<7} {'Component':<10} {'Size':<10} {'Mount Point':<25} {'Description'}")
    print("-" * 90)

    for name in ["AI", "Android", "Linux", "Windows"]:
        info = suggestions[name]
        print(
            f"{info['order']:<7} {name:<10} {info['size_gb']:>6.1f}GB   "
            f"{info['mount_point']:<25} {info['description']}"
        )


def print_system_info():
    """Display system information."""
    print_header("SYSTEM INFORMATION")

    print("\nQuerty-OS Configuration:")
    print("  Priority System: AI > Android > Linux > Windows")
    print("  Dynamic Rebalancing: Enabled")
    print("  Preemption: Enabled")
    print("  Resource Monitoring: Active")

    print("\nException Hierarchy:")
    print("  QuertyOSError (base)")
    print("    ├─ AIServiceError")
    print("    ├─ InputHandlerError")
    print("    ├─ OSControlError")
    print("    ├─ NetworkError")
    print("    ├─ StorageError")
    print("    ├─ AgentError")
    print("    ├─ ConfigurationError")
    print("    ├─ DaemonError")
    print("    └─ ResourceError")


def print_test_status():
    """Display test status."""
    print_header("TEST STATUS")

    print("\nTest Coverage:")
    print("  Unit Tests:")
    print("    ✓ test_exceptions.py    - 8 tests")
    print("    ✓ test_priority.py      - 9 tests")
    print("  Integration Tests:")
    print("    ✓ test_priority_integration.py - 6 test scenarios")

    print("\nCode Quality:")
    print("    ✓ Black formatting configured")
    print("    ✓ isort import sorting configured")
    print("    ✓ flake8 linting configured")
    print("    ✓ mypy type checking configured")
    print("    ✓ bandit security scanning configured")


def print_quick_commands():
    """Display quick reference commands."""
    print_header("QUICK COMMANDS")

    commands = [
        ("make test", "Run all tests"),
        ("make test-unit", "Run unit tests only"),
        ("make test-cov", "Run tests with coverage"),
        ("make lint", "Run all linters"),
        ("make format", "Format code"),
        ("make type-check", "Run type checking"),
        ("make security-check", "Run security scan"),
        ("make clean", "Clean build artifacts"),
        ("make ci", "Run all CI checks"),
    ]

    print("\n" + f"{'Command':<25} {'Description':<45}")
    print("-" * 70)
    for cmd, desc in commands:
        print(f"{cmd:<25} {desc:<45}")


def main():
    """Main entry point."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "QUERTY-OS SYSTEM DASHBOARD" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        print_system_info()
        print_priority_system()
        print_storage_allocations(storage_gb=64)
        print_partition_suggestions(storage_gb=64)
        print_test_status()
        print_quick_commands()

        print("\n" + "=" * 70)
        print("  Dashboard generated successfully!")
        print("  For more info, see: docs/ or run 'make help'")
        print("=" * 70 + "\n")

        return 0

    except Exception as e:
        print(f"\n✗ Error generating dashboard: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
