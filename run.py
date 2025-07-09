#!/usr/bin/env python3
"""
Startup script for Banketnika Discord Bot
Advanced Bulgarian Music Bot with Alternative Player Support

This script provides a user-friendly way to start the bot with:
- Dependency checking
- FFmpeg detection with fallback support
- Alternative player for better compatibility
- Proper error handling and user feedback
"""

import os
import sys
import subprocess

# Bot version info
BOT_VERSION = "2.0.0"
BOT_CODENAME = "Alternative Player Edition"

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import discord
        import yt_dlp
        import dotenv
        import aiohttp
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_bot_files():
    """Check if all bot files are present"""
    required_files = [
        'bot.py',
        'config.py',
        'cogs/music.py',
        'utils/music_utils.py',
        'utils/alternative_player.py',
        'utils/cleanup.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing bot files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All bot files are present!")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg is installed and ready!")
        print("   Using optimized alternative player for better performance")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg not found - using minimal fallback mode")
        print("   The bot will work with basic audio functionality")
        print("   For best performance, install FFmpeg:")
        print("     Windows: Download from https://ffmpeg.org/download.html")
        print("     Linux: sudo apt install ffmpeg")
        print("     macOS: brew install ffmpeg")
        return True  # Changed to True - bot can work without FFmpeg

def check_env_file():
    """Check if .env file exists and has BOT_TOKEN"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and add your bot token")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'BOT_TOKEN=' not in content or 'your_bot_token_here' in content:
            print("❌ BOT_TOKEN not configured in .env file!")
            print("Please add your Discord bot token to the .env file")
            return False
    
    print("✅ Configuration file is ready!")
    return True

def main():
    """Main startup function"""
    print("🎵 Starting Banketnika Discord Bot...")
    print(f"   Version {BOT_VERSION} - {BOT_CODENAME}")
    print("   Advanced Bulgarian Music Bot with Alternative Player")
    print("=" * 55)
    
    # Check all prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_bot_files():
        sys.exit(1)
    
    # FFmpeg check (non-blocking)
    ffmpeg_available = check_ffmpeg()
    
    if not check_env_file():
        sys.exit(1)
    
    print("=" * 55)
    if ffmpeg_available:
        print("🚀 All systems ready! Starting bot with full features...")
    else:
        print("🚀 Starting bot with alternative player (limited features)...")
    print("   Type Ctrl+C to stop the bot")
    print("=" * 55)
    
    # Import and run the bot
    try:
        from bot import main as bot_main
        import asyncio
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n")
        print("=" * 55)
        print("👋 Bot stopped by user. Довиждане!")
        print("   Thank you for using Banketnika Bot!")
        print("=" * 55)
    except ImportError as e:
        print(f"💥 Import error: {e}")
        print("   Make sure all files are in the correct location")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error starting bot: {e}")
        print("   Check your configuration and try again")
        sys.exit(1)

if __name__ == "__main__":
    main() 