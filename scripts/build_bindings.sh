#!/bin/bash
# Build script for generating Python bindings from Go code

set -e

echo "🔨 Building Takeo-ORM Python Bindings"
echo "======================================"

# Create output directory
mkdir -p python/bindings

# Clean previous builds
rm -rf python/bindings/*

echo "📦 Generating Python bindings with gopy..."

# Generate Python bindings
# Note: This requires gopy to be installed: go install github.com/go-python/gopy@latest
gopy build -output=python/bindings -name=takeo_core ./core

if [ $? -eq 0 ]; then
    echo "✅ Python bindings generated successfully!"
    echo "📁 Bindings available in: python/bindings/"
    
    # List generated files
    echo "📋 Generated files:"
    ls -la python/bindings/
else
    echo "❌ Failed to generate Python bindings"
    echo "💡 Make sure gopy is installed: go install github.com/go-python/gopy@latest"
    exit 1
fi

echo ""
echo "🚀 Next steps:"
echo "1. Install the generated package: pip install -e python/bindings/"
echo "2. Test the integration: python examples/usage_example.py"