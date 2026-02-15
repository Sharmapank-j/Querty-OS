# Shared Libraries

This directory contains shared libraries and utilities used across the Querty-OS system.

## Purpose

The `libs/` directory is for:
- Shared utility functions used by multiple core modules
- Common helper libraries
- Third-party library wrappers and adapters
- Cross-cutting concerns (logging, configuration, etc.)

## Organization

Libraries should be organized by functionality:
- `utils/` - General utility functions
- `wrappers/` - Third-party library wrappers
- `common/` - Common shared code

## Usage

Import shared libraries using:
```python
from libs.utils import some_utility
from libs.wrappers import SomeWrapper
```

## Guidelines

- Keep libraries focused and single-purpose
- Document all public APIs
- Add tests for library code
- Avoid circular dependencies with core modules
