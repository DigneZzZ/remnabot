# Development startup script for Remnawave Bot (Windows)

Write-Host "🚀 Starting Remnawave Bot in development mode..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "📝 Please create .env file from .env.example:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.example .env" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path venv)) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements-dev.txt

# Export debug settings
$env:DEBUG = "True"
$env:LOG_LEVEL = "DEBUG"

# Start bot
Write-Host "✅ Starting bot..." -ForegroundColor Green
python -m src.main
