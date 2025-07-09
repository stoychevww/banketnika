#!/usr/bin/env python3
"""
Banketnika - Advanced Bulgarian Discord Music Bot
A professional music bot that brings the spirit of Bulgarian banket culture to Discord servers.
"""

import discord
from discord.ext import commands
import asyncio
import logging
import sys
import os
from config import Config
from utils.music_utils import MusicUtils
from utils.cleanup import CleanupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('banketnika.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class Banketnika(commands.Bot):
    """Main bot class for Banketnika"""
    
    def __init__(self):
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            description=Config.BOT_DESCRIPTION,
            intents=intents,
            help_command=None  # We'll use custom help command
        )
        
        self.initial_extensions = [
            'cogs.music',
            'cogs.general',
            'cogs.banket'
        ]
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info(f"Starting {Config.BOT_NAME} v{Config.BOT_VERSION}")
        
        # Load extensions
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Serving {len(self.users)} users")
        
        # Print ASCII art
        print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║    ██████╗  █████╗ ███╗   ██╗██╗  ██╗███████╗████████╗███╗   ██╗██╗██╗  ██╗ █████╗  ║
║    ██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝██╔════╝╚══██╔══╝████╗  ██║██║██║ ██╔╝██╔══██╗ ║
║    ██████╔╝███████║██╔██╗ ██║█████╔╝ █████╗     ██║   ██╔██╗ ██║██║█████╔╝ ███████║ ║
║    ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ ██╔══╝     ██║   ██║╚██╗██║██║██╔═██╗ ██╔══██║ ║
║    ██████╔╝██║  ██║██║ ╚████║██║  ██╗███████╗   ██║   ██║ ╚████║██║██║  ██╗██║  ██║ ║
║    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ║
║                                                                                      ║
║                        🎵 Advanced Bulgarian Discord Music Bot 🎵                   ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """)
        
        print(f"🎉 {Config.BOT_NAME} is ready to bring the banket spirit to Discord!")
        print(f"📊 Connected to {len(self.guilds)} servers with {len(self.users)} users")
        print(f"🎵 Use {Config.BOT_PREFIX}help to see all commands")
        print(f"🇧🇬 {MusicUtils.get_random_banket_phrase()}")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            embed = MusicUtils.create_music_embed(
                "❌ Неизвестна команда",
                f"Командата `{ctx.message.content.split()[0]}` не съществува.\n"
                f"Използвайте `{Config.BOT_PREFIX}help` за да видите всички команди.",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = MusicUtils.create_music_embed(
                "❌ Липсва аргумент",
                f"Командата изисква допълнителни аргументи.\n"
                f"Използвайте `{Config.BOT_PREFIX}help {ctx.command.name}` за повече информация.",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = MusicUtils.create_music_embed(
                "⏰ Командата е в cooldown",
                f"Моля изчакайте {error.retry_after:.1f} секунди преди да използвате отново тази команда.",
                Config.COLOR_WARNING
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = MusicUtils.create_music_embed(
                "❌ Липсват права",
                f"Нямам необходимите права за изпълнение на тази команда.\n"
                f"Необходими права: {', '.join(error.missing_permissions)}",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingPermissions):
            embed = MusicUtils.create_music_embed(
                "❌ Недостатъчни права",
                f"Нямате необходимите права за изпълнение на тази команда.\n"
                f"Необходими права: {', '.join(error.missing_permissions)}",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
        
        else:
            # Log unexpected errors
            logger.error(f"Unexpected error in command {ctx.command}: {error}")
            
            embed = MusicUtils.create_music_embed(
                "❌ Неочаквана грешка",
                f"Възникна неочаквана грешка при изпълнение на командата.\n"
                f"Моля опитайте отново по-късно.",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""
        # Auto-disconnect if bot is alone in voice channel
        if member == self.user:
            return
        
        # Check if bot is in a voice channel
        voice_client = member.guild.voice_client
        if not voice_client:
            return
        
        # Check if bot is alone in the channel
        if len(voice_client.channel.members) == 1:  # Only the bot
            logger.info(f"Bot is alone in voice channel {voice_client.channel.name}, disconnecting...")
            
            # Clean up using cleanup manager
            music_cog = self.get_cog('Music')
            if music_cog and hasattr(music_cog, 'players'):
                players = getattr(music_cog, 'players', {})
                if member.guild.id in players:
                    player = players[member.guild.id]
                    await CleanupManager.cleanup_music_player(player)
    
    async def close(self):
        """Properly close the bot and clean up resources"""
        logger.info("Shutting down bot...")
        
        # Clean up all music players using cleanup manager
        music_cog = self.get_cog('Music')
        if music_cog:
            await CleanupManager.cleanup_all_players(music_cog)
        
        # Close the bot connection
        await super().close()

async def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Create and run bot
        bot = Banketnika()
        if Config.BOT_TOKEN:
            await bot.start(Config.BOT_TOKEN)
        else:
            raise ValueError("BOT_TOKEN is not set")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure BOT_TOKEN is set correctly.")
        sys.exit(1)
    
    except discord.LoginFailure:
        logger.error("Invalid bot token")
        print("❌ Invalid bot token! Please check your BOT_TOKEN in the .env file.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
        print("\n👋 Банкетника се изключва... Довиждане!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"💥 Fatal error: {e}")
        sys.exit(1) 