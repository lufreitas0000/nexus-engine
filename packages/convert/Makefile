# Binary Paths
PYTHON = python3
PYTEST = $(PYTHON) -m pytest
MYPY   = $(PYTHON) -m mypy
PIP    = $(PYTHON) -m pip

# Package Resolution
PACKAGE_ROOT = app_spatial_compiler
SRC_DIR = $(PACKAGE_ROOT)/src
TESTS_DIR = $(PACKAGE_ROOT)/tests

.PHONY: all test lint install clean help

all: lint test

## test: Execute all TDD assertions over synthetic RAM manifolds
test:
	@echo "Running synthetic manifold assertions..."
	export PYTHONPATH=$$(pwd) && $(PYTEST) $(TESTS_DIR) -v

## lint: Execute strict static analysis on memory-contiguous structures
lint:
	@echo "Executing strict static analysis..."
	$(MYPY) -p $(PACKAGE_ROOT).src -p $(PACKAGE_ROOT).tests

## install: Synchronize dependencies from requirements.txt
install:
	$(PIP) install -r $(PACKAGE_ROOT)/requirements.txt

## clean: Remove __pycache__ and build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
