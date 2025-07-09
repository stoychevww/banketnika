# 🐳 Docker Setup for Banketnika Bot

This document explains how to run the Banketnika Discord bot using Docker and Docker Compose.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- A Discord bot token (see main README for setup instructions)

## 🚀 Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repo-url>
   cd banketnika
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token and other settings
   ```

3. **Build and run the bot**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f banketnika-bot
   ```

## 🛠️ Available Commands

### Basic Operations
```bash
# Build and start the bot
docker-compose up -d

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# View logs
docker-compose logs -f banketnika-bot

# View bot status
docker-compose ps
```

### Development Commands
```bash
# Build without cache
docker-compose build --no-cache

# Run in development mode (with live logs)
docker-compose up

# Execute commands inside the container
docker-compose exec banketnika-bot bash

# View resource usage
docker stats banketnika-discord-bot
```

### Maintenance Commands
```bash
# Update the bot (rebuild with latest code)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Clean up unused Docker resources
docker system prune -a
```

## 📁 Directory Structure

```
banketnika/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Files to exclude from build
├── .env                    # Environment variables (create this)
├── logs/                   # Bot logs (auto-created)
├── temp/                   # Temporary files (auto-created)
└── ...                     # Rest of your bot code
```

## 🔧 Configuration

### Environment Variables (.env file)
```env
# Discord Bot Token (required)
DISCORD_TOKEN=your_bot_token_here

# Optional: Bot prefix (default: !)
BOT_PREFIX=!

# Optional: Debug mode
DEBUG=False

# Optional: Log level
LOG_LEVEL=INFO
```

### Resource Limits
The bot is configured with the following resource limits:
- **CPU**: 2.0 cores max, 0.5 cores reserved
- **Memory**: 1GB max, 256MB reserved

You can adjust these in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

## 📊 Monitoring

### Health Checks
The bot includes built-in health checks that run every 30 seconds:
```bash
# Check health status
docker-compose ps

# View detailed health info
docker inspect banketnika-discord-bot | grep -A 10 '"Health"'
```

### Logs
Logs are automatically managed with rotation:
- Maximum file size: 10MB
- Maximum files: 3
- Location: `./logs/` directory

### Persistent Data
The following directories are mounted as volumes:
- `./logs` - Bot logs
- `./temp` - Temporary audio files
- `./config` - Configuration files (read-only)

## 🔒 Security Features

- **Non-root user**: Bot runs as `botuser` (UID 1000)
- **Read-only config**: Configuration directory is mounted read-only
- **Isolated network**: Bot runs in its own Docker network
- **Resource limits**: CPU and memory usage is limited

## 🐛 Troubleshooting

### Common Issues

1. **Bot won't start**:
   ```bash
   # Check logs for errors
   docker-compose logs banketnika-bot
   
   # Verify environment variables
   docker-compose exec banketnika-bot env | grep DISCORD
   ```

2. **Permission errors**:
   ```bash
   # Fix directory permissions
   sudo chown -R 1000:1000 logs/ temp/
   ```

3. **Out of memory**:
   ```bash
   # Increase memory limit in docker-compose.yml
   # Or check memory usage
   docker stats banketnika-discord-bot
   ```

4. **FFmpeg not working**:
   ```bash
   # Test FFmpeg inside container
   docker-compose exec banketnika-bot ffmpeg -version
   ```

### Debugging Mode

To run the bot in debug mode:
```bash
# Add to your .env file
DEBUG=True

# Restart the bot
docker-compose restart
```

## 🔄 Updates

To update the bot:
1. Pull latest code changes
2. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## 📚 Advanced Usage

### Custom Dockerfile
If you need to customize the Docker image, edit the `Dockerfile`:
- Add additional system packages
- Install Python packages
- Modify the runtime environment

### Multiple Environments
You can run multiple instances:
```bash
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f banketnika-bot`
2. Verify your `.env` file has all required variables
3. Ensure Docker and Docker Compose are up to date
4. Check the main README for bot-specific troubleshooting

---

**Happy botting! 🎵** Made with ❤️ for the Bulgarian Discord community. 