#!/bin/bash

# Development startup script for Remnawave Bot

echo "🚀 Starting Remnawave Bot in development mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please create .env file from .env.example:"
    echo "   cp .env.example .env"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements-dev.txt

# Export debug settings
export DEBUG=True
export LOG_LEVEL=DEBUG

# Start bot
echo "✅ Starting bot..."
python -m src.main
