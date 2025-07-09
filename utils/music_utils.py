import asyncio
import discord
import yt_dlp
import random
from typing import Optional, Dict, Any
from config import Config

class MusicUtils:
    """Utility class for music-related operations"""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration from seconds to MM:SS or HH:MM:SS format"""
        if seconds < 3600:
            return f"{seconds // 60:02d}:{seconds % 60:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def get_random_banket_phrase() -> str:
        """Get a random Bulgarian banket phrase"""
        return random.choice(Config.BANKET_PHRASES)
    
    @staticmethod
    def create_music_embed(title: str, description: str = "", color: int = Config.COLOR_PRIMARY) -> discord.Embed:
        """Create a standardized music embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        embed.set_footer(text=f"{Config.BOT_NAME} • {MusicUtils.get_random_banket_phrase()}")
        return embed
    
    @staticmethod
    def create_now_playing_embed(song_info: Dict[str, Any]) -> discord.Embed:
        """Create a now playing embed"""
        embed = discord.Embed(
            title="🎵 Сега свири",
            description=f"**{song_info['title']}**",
            color=Config.COLOR_PRIMARY
        )
        
        if song_info.get('duration'):
            embed.add_field(
                name="⏱️ Продължителност",
                value=MusicUtils.format_duration(song_info['duration']),
                inline=True
            )
        
        if song_info.get('uploader'):
            embed.add_field(
                name="👤 Канал",
                value=song_info['uploader'],
                inline=True
            )
        
        if song_info.get('requester'):
            embed.add_field(
                name="🎯 Заявена от",
                value=song_info['requester'].mention,
                inline=True
            )
        
        if song_info.get('thumbnail'):
            embed.set_thumbnail(url=song_info['thumbnail'])
        
        embed.set_footer(text=f"{Config.BOT_NAME} • {MusicUtils.get_random_banket_phrase()}")
        return embed
    
    @staticmethod
    def create_queue_embed(queue_list: list, current_song: Optional[Dict] = None) -> discord.Embed:
        """Create a queue display embed"""
        embed = discord.Embed(
            title="🎼 Опашка за музика",
            color=Config.COLOR_PRIMARY
        )
        
        if current_song:
            embed.add_field(
                name="🎵 Сега свири",
                value=f"**{current_song['title']}**",
                inline=False
            )
        
        if queue_list:
            queue_text = ""
            for i, song in enumerate(queue_list[:10], 1):  # Show first 10 songs
                duration = MusicUtils.format_duration(song['duration']) if song.get('duration') else "N/A"
                queue_text += f"`{i}.` **{song['title']}** [{duration}]\n"
            
            if len(queue_list) > 10:
                queue_text += f"\n... и още {len(queue_list) - 10} песни"
            
            embed.add_field(
                name="📋 Следващи песни",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Следващи песни",
                value="Няма песни в опашката",
                inline=False
            )
        
        embed.set_footer(text=f"{Config.BOT_NAME} • Общо: {len(queue_list)} песни")
        return embed

class YouTubeDownloader:
    """YouTube downloader utility class"""
    
    def __init__(self):
        self.ytdl_format_options = {
            'format': 'bestaudio[ext=webm]/bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,  # Enable playlist support
            'nocheckcertificate': True,
            'ignoreerrors': True,  # Continue on errors in playlists
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'extractflat': False,
            'age_limit': 99,
            'geo_bypass': True,
            'cookiefile': None,
            'playlistend': 50,  # Limit playlist to first 50 songs
        }
        
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_format_options)
    
    async def extract_info(self, url: str, download: bool = False) -> Dict[str, Any]:
        """Extract information from YouTube URL"""
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None, 
                lambda: self.ytdl.extract_info(url, download=download)
            )
            if data is None:
                raise Exception("No data returned from YouTube")
            return data
        except Exception as e:
            raise Exception(f"Error extracting info: {str(e)}")
    
    async def search_youtube(self, query: str) -> Optional[Dict[str, Any]]:
        """Search YouTube for a query or extract info from URL"""
        try:
            # Check if it's a URL
            if self._is_url(query):
                # Direct URL - extract info directly
                info = await self.extract_info(query, download=False)
                return info
            else:
                # Search query - use ytsearch
                info = await self.extract_info(f"ytsearch:{query}", download=False)
                if info and 'entries' in info and len(info['entries']) > 0:
                    return info['entries'][0]
                return None
        except Exception as e:
            raise Exception(f"Search error: {str(e)}")
    
    def is_playlist(self, info: Dict[str, Any]) -> bool:
        """Check if the extracted info is a playlist"""
        return 'entries' in info and len(info.get('entries', [])) > 1
    
    def _is_url(self, query: str) -> bool:
        """Check if the query is a URL"""
        url_indicators = [
            'http://', 'https://', 'www.',
            'youtube.com', 'youtu.be', 'music.youtube.com',
            'soundcloud.com', 'spotify.com'
        ]
        return any(indicator in query.lower() for indicator in url_indicators)
    
    def get_audio_source(self, url: str) -> discord.FFmpegPCMAudio:
        """Get audio source for discord.py"""
        return discord.FFmpegPCMAudio(
            url,
            before_options=self.ffmpeg_options['before_options'],
            options=self.ffmpeg_options['options']
        ) 