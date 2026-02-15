# Contributing to Querty-OS

Thank you for your interest in contributing to Querty-OS! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)
- [Priority System](#priority-system)

## Code of Conduct

This project follows a Code of Conduct that all contributors are expected to adhere to. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Android system architecture
- Familiarity with AI/LLM concepts (helpful but not required)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Querty-OS.git
   cd Querty-OS
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install development dependencies
make install-dev

# Or manually:
pip install -r requirements-dev.txt
pip install -e .
```

### 3. Install Pre-commit Hooks

```bash
make pre-commit

# Or manually:
pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Follow these guidelines:

- Write clear, concise commit messages
- Keep commits atomic and focused
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Run with coverage
make test-cov
```

### 4. Check Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Security check
make security-check
```

## Testing

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_<component>_<scenario>_<expected_result>`
- Use pytest fixtures for common setup
- Mark tests appropriately:
  ```python
  @pytest.mark.unit
  @pytest.mark.integration
  @pytest.mark.slow
  @pytest.mark.android
  ```

### Test Coverage

- Aim for >80% code coverage
- All new code should have tests
- Critical paths require comprehensive testing

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/ -m unit

# With coverage
pytest tests/ --cov=core --cov-report=html
```

## Code Quality

### Code Style

- **Line length**: Maximum 100 characters
- **Formatting**: Use `black` for code formatting
- **Import sorting**: Use `isort` with black profile
- **Docstrings**: Use Google-style docstrings

Example:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception occurs
    """
    pass
```

### Type Hints

- Use type hints for all function signatures
- Use `typing` module for complex types
- Example:
  ```python
  from typing import List, Dict, Optional

  def process_data(items: List[str], config: Dict[str, Any]) -> Optional[str]:
      pass
  ```

### Error Handling

- Use custom exceptions from `core.exceptions`
- Provide clear error messages
- Log errors appropriately
- Example:
  ```python
  from core.exceptions import AIServiceError

  try:
      result = process_llm_request()
  except Exception as e:
      logger.error(f"LLM processing failed: {e}")
      raise AIServiceError("Failed to process LLM request", details={"error": str(e)})
  ```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure relevant documentation is updated
2. **Add Tests**: Include tests for new features
3. **Run CI Checks**: Ensure all CI checks pass
4. **Update CHANGELOG**: Add entry to CHANGELOG.md
5. **Create PR**: Submit pull request with clear description

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
```

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Example:
```
feat(llm): add support for creative mode temperature adjustment

Implements dynamic temperature adjustment for creative mode based on
context and user preferences.

Fixes #123
```

## Priority System

Querty-OS follows a strict priority system for resource allocation:

**AI > Android > Linux > Windows**

### When Contributing

1. **AI Components** (Highest Priority)
   - LLM service
   - AI daemon
   - Input handlers
   - Always prioritize AI functionality

2. **Android Components** (Second Priority)
   - Native Android control
   - Android app integration
   - System services

3. **Linux Components** (Third Priority)
   - Chroot environment
   - Linux app support
   - System utilities

4. **Windows Components** (Lowest Priority)
   - Wine integration
   - Windows app support
   - Compatibility layers

### Resource Allocation

When implementing features:
- Ensure AI components get first access to resources
- Follow priority order for storage allocation
- Implement preemption correctly
- Test priority enforcement

### Testing Priority System

```python
from core.priority import SystemPriority, ResourcePriority

def test_priority_order():
    # AI should always have highest priority
    assert SystemPriority.AI > SystemPriority.ANDROID
    assert SystemPriority.ANDROID > SystemPriority.LINUX
    assert SystemPriority.LINUX > SystemPriority.WINDOWS
```

## Questions?

If you have questions:

1. Check existing documentation
2. Search existing issues
3. Create a new issue with the `question` label
4. Join our community discussions

## Thank You!

Your contributions make Querty-OS better for everyone. Thank you for taking the time to contribute!
