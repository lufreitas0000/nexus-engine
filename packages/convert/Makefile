# Binary Paths
PYTHON = python3
PYTEST = $(PYTHON) -m pytest
MYPY   = $(PYTHON) -m mypy
PIP    = $(PYTHON) -m pip

# Package Resolution
PACKAGE_ROOT = .
APP_MODULES = app_orchestrator app_spatial_compiler app_structurizer app_vision_encoder

.PHONY: all test lint install clean help

all: lint test

## test: Execute all TDD assertions
test:
	@echo "Running tests..."
	export PYTHONPATH=$$(pwd) && $(PYTEST) -n auto tests $(APP_MODULES) -v

## lint: Execute strict static analysis
lint:
	@echo "Executing strict static analysis..."
	$(MYPY) $(APP_MODULES) cli.py

## install: Synchronize dependencies
install:
	$(PIP) install -r requirements.txt

## clean: Remove __pycache__ and build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache

.PHONY: docker-build-cpu docker-build-cuda docker-up docker-down docker-test

docker-build-cpu:
	docker build -f docker/Dockerfile.cpu -t semantic-pdf-splitter:cpu-latest .

docker-build-cuda:
	docker build -f docker/Dockerfile.cuda -t semantic-pdf-splitter:cuda-latest .

docker-up:
	docker compose up -d

docker-down:
	docker compose down --volumes --remove-orphans

docker-test: docker-build-cpu
	docker run --rm semantic-pdf-splitter:cpu-latest pytest /app/tests/

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
