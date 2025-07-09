import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class CleanupManager:
    """Manages cleanup operations for the bot"""
    
    @staticmethod
    async def cleanup_voice_client(voice_client) -> None:
        """Safely cleanup a voice client"""
        if not voice_client:
            return
        
        try:
            if voice_client.is_playing():
                voice_client.stop()
        except Exception as e:
            logger.error(f"Error stopping voice client: {e}")
        
        try:
            if voice_client.is_connected():
                await voice_client.disconnect(force=True)
        except Exception as e:
            logger.error(f"Error disconnecting voice client: {e}")
    
    @staticmethod
    async def cleanup_music_player(player) -> None:
        """Safely cleanup a music player"""
        if not player:
            return
        
        try:
            player.stop()
            player.clear_queue()
            
            if player.voice_client:
                await CleanupManager.cleanup_voice_client(player.voice_client)
                player.voice_client = None
                
        except Exception as e:
            logger.error(f"Error cleaning up music player: {e}")
    
    @staticmethod
    async def cleanup_all_players(music_cog) -> None:
        """Cleanup all music players in a music cog"""
        if not music_cog or not hasattr(music_cog, 'players'):
            return
        
        for guild_id, player in music_cog.players.items():
            try:
                await CleanupManager.cleanup_music_player(player)
                logger.info(f"Cleaned up player for guild {guild_id}")
            except Exception as e:
                logger.error(f"Error cleaning up player for guild {guild_id}: {e}")
        
        # Clear the players dict
        music_cog.players.clear()
    
    @staticmethod
    def safe_schedule_coroutine(coro, loop):
        """Safely schedule a coroutine in an event loop"""
        try:
            if loop and not loop.is_closed():
                return asyncio.run_coroutine_threadsafe(coro, loop)
        except Exception as e:
            logger.error(f"Error scheduling coroutine: {e}")
        return None 