# Takeo-ORM Build Script for Windows
# This script builds the project on Windows without requiring make

param(
    [switch]$Clean = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Takeo-ORM Windows Build Script"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\build.ps1          - Build the project"
    Write-Host "  .\build.ps1 -Clean   - Clean and rebuild"
    Write-Host "  .\build.ps1 -Help    - Show this help"
    exit 0
}

Write-Host "Building Takeo-ORM for Windows..." -ForegroundColor Green

# Check prerequisites
$goVersion = go version 2>$null
if (-not $goVersion) {
    Write-Host "Error: Go is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Go: $goVersion" -ForegroundColor Blue
Write-Host "Python: $pythonVersion" -ForegroundColor Blue

# Clean if requested
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path "python\bindings") {
        Remove-Item -Recurse -Force "python\bindings"
    }
    if (Test-Path "bin") {
        Remove-Item -Recurse -Force "bin"
    }
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
go mod tidy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m pip install pybindgen
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Installing gopy..." -ForegroundColor Yellow
go get github.com/go-python/gopy@latest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

go install github.com/go-python/gopy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

go install golang.org/x/tools/cmd/goimports@latest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Build Go binary
Write-Host "Building Go binary..." -ForegroundColor Yellow
if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}
go build -o "bin\takeo.exe" ".\cmd\main.go"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Generate Python bindings
Write-Host "Generating Python bindings..." -ForegroundColor Yellow
if (-not (Test-Path "python\bindings")) {
    New-Item -ItemType Directory -Path "python\bindings" -Force | Out-Null
}

gopy build -output=python\bindings -name=takeo_core .\core
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run:" -ForegroundColor Blue
Write-Host "  python usage_example.py"