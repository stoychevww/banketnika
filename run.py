#!/usr/bin/env python3
"""
Simple startup script for Banketnika Discord Bot
This script provides a user-friendly way to start the bot with proper error handling.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import discord
        import yt_dlp
        import dotenv
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg is installed!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found!")
        print("Please install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False

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
    print("=" * 50)
    
    # Check all prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_ffmpeg():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    print("=" * 50)
    print("🚀 All checks passed! Starting bot...")
    print("=" * 50)
    
    # Import and run the bot
    try:
        from bot import main as bot_main
        import asyncio
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user. Довиждане!")
    except Exception as e:
        print(f"💥 Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 