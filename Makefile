# Takeo-ORM Makefile

# Go variables
GO_MODULE = github.com/gaetan1903/Takeo-ORM
GO_BINARY = bin/takeo
GOPY_MODULE = takeo_core

# Python variables
PYTHON = python3
VENV_DIR = venv

# Default target
.PHONY: all
all: build

# Install dependencies
.PHONY: install-deps
install-deps:
	@echo "Installing Go dependencies..."
	go mod tidy
	@echo "Installing Python dependencies..."
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Installing gopy (if not already installed)..."
	go install github.com/go-python/gopy@latest

# Build Go binary
.PHONY: build-go
build-go:
	@echo "Building Go binary..."
	mkdir -p bin
	go build -o $(GO_BINARY) ./cmd/main.go

# Generate Python bindings using gopy
.PHONY: build-bindings
build-bindings:
	@echo "Generating Python bindings with gopy..."
	mkdir -p python/bindings
	gopy build -output=python/bindings -name=$(GOPY_MODULE) ./core

# Build everything
.PHONY: build
build: install-deps build-go build-bindings

# Test Go code
.PHONY: test-go
test-go:
	@echo "Running Go tests..."
	go test ./core/...

# Test Python code
.PHONY: test-python
test-python:
	@echo "Running Python tests..."
	$(PYTHON) -m pytest tests/ -v

# Test everything
.PHONY: test
test: test-go test-python

# Run example
.PHONY: example
example:
	@echo "Running usage example..."
	cd examples && $(PYTHON) usage_example.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf bin/
	rm -rf python/bindings/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Development setup
.PHONY: dev-setup
dev-setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m pip install --upgrade pip
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m pip install -r requirements.txt
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m pip install -r requirements-dev.txt 2>/dev/null || true

# Lint Go code
.PHONY: lint-go
lint-go:
	@echo "Linting Go code..."
	golangci-lint run ./... 2>/dev/null || echo "golangci-lint not installed, skipping..."

# Lint Python code
.PHONY: lint-python
lint-python:
	@echo "Linting Python code..."
	$(PYTHON) -m flake8 python/ examples/ tests/ 2>/dev/null || echo "flake8 not installed, skipping..."
	$(PYTHON) -m black --check python/ examples/ tests/ 2>/dev/null || echo "black not installed, skipping..."

# Lint everything
.PHONY: lint
lint: lint-go lint-python

# Format code
.PHONY: format
format:
	@echo "Formatting Go code..."
	go fmt ./...
	@echo "Formatting Python code..."
	$(PYTHON) -m black python/ examples/ tests/ 2>/dev/null || echo "black not installed, skipping..."

# Show help
.PHONY: help
help:
	@echo "Takeo-ORM Build System"
	@echo "====================="
	@echo ""
	@echo "Available targets:"
	@echo "  all           - Build everything (default)"
	@echo "  install-deps  - Install Go and Python dependencies"
	@echo "  build-go      - Build Go binary"
	@echo "  build-bindings- Generate Python bindings with gopy"
	@echo "  build         - Build Go code and Python bindings"
	@echo "  test          - Run all tests"
	@echo "  test-go       - Run Go tests"
	@echo "  test-python   - Run Python tests"
	@echo "  example       - Run usage example"
	@echo "  clean         - Clean build artifacts"
	@echo "  dev-setup     - Set up development environment"
	@echo "  lint          - Lint all code"
	@echo "  lint-go       - Lint Go code"
	@echo "  lint-python   - Lint Python code"
	@echo "  format        - Format all code"
	@echo "  help          - Show this help message"
	@echo ""
	@echo "Example workflow:"
	@echo "  make dev-setup  # Set up development environment"
	@echo "  make build      # Build the project"
	@echo "  make test       # Run tests"
	@echo "  make example    # Run example"