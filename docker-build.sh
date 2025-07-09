#!/bin/bash

# Banketnika Discord Bot - Docker Build Script
# This script helps you quickly set up and run the bot using Docker

set -e  # Exit on any error

echo "🐳 Banketnika Discord Bot - Docker Setup"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
        echo "🔧 Please edit .env file and add your Discord bot token:"
        echo "   DISCORD_TOKEN=your_bot_token_here"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ .env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs temp config
echo "✅ Directories created"

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build --no-cache

# Start the bot
echo "🚀 Starting Banketnika Discord Bot..."
docker-compose up -d

# Show status
echo ""
echo "✅ Bot is starting up!"
echo "📊 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f banketnika-bot"
echo "🛑 Stop bot: docker-compose down"
echo ""
echo "🎵 Happy botting! Made with ❤️ for the Bulgarian Discord community."

# Show logs for a few seconds
echo "📋 Showing initial logs (press Ctrl+C to exit):"
echo "=================================================="
docker-compose logs -f banketnika-bot 