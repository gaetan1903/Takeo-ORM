#!/bin/bash
# Takeo-ORM Build Script for Unix systems (Linux/macOS)

set -e  # Exit on any error

CLEAN=false
HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean|-c)
            CLEAN=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ "$HELP" = true ]; then
    echo "Takeo-ORM Unix Build Script"
    echo ""
    echo "Usage:"
    echo "  ./build.sh           - Build the project"
    echo "  ./build.sh --clean   - Clean and rebuild"
    echo "  ./build.sh --help    - Show this help"
    exit 0
fi

echo "Building Takeo-ORM for $(uname -s)..."

# Check prerequisites
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed or not in PATH"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

echo "Go: $(go version)"
echo "Python: $(python3 --version)"

# Clean if requested
if [ "$CLEAN" = true ]; then
    echo "Cleaning previous builds..."
    rm -rf python/bindings
    rm -rf bin
fi

# Check if make is available
if command -v make &> /dev/null; then
    echo "Using make for build..."
    make install-deps
    make build-go  
    make build-bindings
else
    echo "Make not found, using direct commands..."
    
    # Install dependencies
    echo "Installing dependencies..."
    go mod tidy
    python3 -m pip install -r requirements.txt
    python3 -m pip install pybindgen
    
    echo "Installing gopy..."
    go get github.com/go-python/gopy@latest
    go install github.com/go-python/gopy
    go install golang.org/x/tools/cmd/goimports@latest
    
    # Build Go binary
    echo "Building Go binary..."
    mkdir -p bin
    go build -o bin/takeo ./cmd/main.go
    
    # Generate Python bindings
    echo "Generating Python bindings..."
    mkdir -p python/bindings
    gopy build -output=python/bindings -name=takeo_core ./core
fi

echo "Build completed successfully!"
echo ""
echo "You can now run:"
echo "  python3 example.py"