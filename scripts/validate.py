#!/usr/bin/env python3
"""
Validation script to check code quality without running full tests.
Useful for quick validation during development.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print(f"✓ {description} passed")
            if result.stdout:
                print(result.stdout[:500])  # Show first 500 chars
            return True
        else:
            print(f"✗ {description} failed")
            print(f"Error: {result.stderr[:500]}")
            return False

    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False


def main():
    """Run all validation checks."""
    print("Querty-OS Code Validation")
    print("=" * 60)

    checks = [
        ("python3 -m py_compile core/**/*.py", "Python Syntax Check"),
        ("bash -n scripts/**/*.sh 2>&1", "Shell Script Syntax Check"),
    ]

    results = []
    for cmd, desc in checks:
        results.append(run_command(cmd, desc))

    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All validation checks passed!")
        return 0
    else:
        print(f"✗ {total - passed} checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
