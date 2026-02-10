# Makefile for Querty-OS
.PHONY: help install install-dev test lint format clean run docs

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
PYLINT := $(PYTHON) -m pylint
BANDIT := $(PYTHON) -m bandit

help:
	@echo "Querty-OS Development Commands"
	@echo "==============================="
	@echo "install          - Install production dependencies"
	@echo "install-dev      - Install development dependencies"
	@echo "test             - Run all tests"
	@echo "test-unit        - Run unit tests only"
	@echo "test-integration - Run integration tests only"
	@echo "test-cov         - Run tests with coverage report"
	@echo "lint             - Run all linters"
	@echo "format           - Format code with black and isort"
	@echo "format-check     - Check code formatting without changes"
	@echo "type-check       - Run type checking with mypy"
	@echo "security-check   - Run security checks with bandit"
	@echo "clean            - Remove build artifacts and cache"
	@echo "run              - Run the AI daemon"
	@echo "docs             - Generate documentation"
	@echo "pre-commit       - Install pre-commit hooks"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

test:
	$(PYTEST) tests/ -v

test-unit:
	$(PYTEST) tests/ -v -m unit

test-integration:
	$(PYTEST) tests/ -v -m integration

test-cov:
	$(PYTEST) tests/ -v --cov=core --cov-report=html --cov-report=term

lint:
	@echo "Running flake8..."
	$(FLAKE8) core/ tests/
	@echo "Running pylint..."
	$(PYLINT) core/
	@echo "Running mypy..."
	$(MYPY) core/
	@echo "All linting passed!"

format:
	@echo "Running black..."
	$(BLACK) core/ tests/
	@echo "Running isort..."
	$(ISORT) core/ tests/
	@echo "Code formatted!"

format-check:
	@echo "Checking black formatting..."
	$(BLACK) --check core/ tests/
	@echo "Checking isort formatting..."
	$(ISORT) --check-only core/ tests/

type-check:
	$(MYPY) core/

security-check:
	$(BANDIT) -r core/ -f screen

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"

run:
	$(PYTHON) core/ai-daemon/daemon.py

docs:
	@echo "Generating documentation..."
	cd docs && make html
	@echo "Documentation generated in docs/_build/html/"

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed!"

ci: format-check lint type-check security-check test
	@echo "All CI checks passed!"
