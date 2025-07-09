import asyncio
import discord
import yt_dlp
import random
import subprocess
import shutil
import json
import time
import os
from typing import Optional, Dict, Any
from config import Config

class MusicUtils:
    """Utility class for music-related operations"""
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if FFmpeg is properly installed"""
        try:
            # Check if ffmpeg is in PATH
            if shutil.which('ffmpeg') is None:
                print("FFmpeg not found in PATH")
                return False
            
            # Try to run ffmpeg to check if it works
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                print("FFmpeg is properly installed")
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error checking FFmpeg: {e}")
            return False
    
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
    def create_music_buttons() -> discord.ui.View:
        """Create Discord buttons for music controls"""
        view = discord.ui.View(timeout=300)  # 5 minutes timeout
        
        # Play/Pause button
        play_pause_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            emoji="⏯️",
            label="Play/Pause",
            custom_id="music_play_pause"
        )
        
        # Skip button
        skip_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="⏭️",
            label="Skip",
            custom_id="music_skip"
        )
        
        # Stop button
        stop_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            emoji="⏹️",
            label="Stop",
            custom_id="music_stop"
        )
        
        # Queue button
        queue_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            label="Queue",
            custom_id="music_queue"
        )
        
        # Shuffle button
        shuffle_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="🔀",
            label="Shuffle",
            custom_id="music_shuffle"
        )
        
        view.add_item(play_pause_button)
        view.add_item(skip_button)
        view.add_item(stop_button)
        view.add_item(queue_button)
        view.add_item(shuffle_button)
        
        return view

    @staticmethod
    def create_now_playing_embed(song_info: Dict[str, Any]) -> discord.Embed:
        """Create a now playing embed with enhanced information"""
        embed = discord.Embed(
            title="🎵 Сега свири",
            description=f"**{song_info['title']}**",
            color=Config.COLOR_SUCCESS
        )
        
        # Add song information
        duration = MusicUtils.format_duration(song_info['duration']) if song_info.get('duration') else "Live"
        embed.add_field(name="⏱️ Продължителност", value=duration, inline=True)
        embed.add_field(name="👤 Канал", value=song_info.get('uploader', 'Unknown'), inline=True)
        embed.add_field(name="🎧 Заявена от", value=song_info['requester'].mention, inline=True)
        
        # Add thumbnail if available
        if song_info.get('thumbnail'):
            embed.set_thumbnail(url=song_info['thumbnail'])
        
        # Add progress bar (placeholder for now)
        embed.add_field(name="⏳ Прогрес", value="▬▬▬▬▬▬▬▬▬▬ 0%", inline=False)
        
        embed.set_footer(text=f"{Config.BOT_NAME} • Банкет режим активен! 🎉")
        return embed

    @staticmethod
    def create_queue_embed(queue_list: list, current_song: Optional[Dict] = None, page: int = 1, per_page: int = 10) -> discord.Embed:
        """Create a queue display embed with pagination"""
        embed = discord.Embed(
            title="🎼 Опашка за музика",
            color=Config.COLOR_PRIMARY
        )
        
        if current_song:
            duration = MusicUtils.format_duration(current_song['duration']) if current_song.get('duration') else "Live"
            embed.add_field(
                name="🎵 Сега свири",
                value=f"**{current_song['title']}** [{duration}]\n👤 {current_song.get('uploader', 'Unknown')}",
                inline=False
            )
        
        if queue_list:
            total_pages = (len(queue_list) + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_queue = queue_list[start_idx:end_idx]
            
            queue_text = ""
            for i, song in enumerate(page_queue, start_idx + 1):
                duration = MusicUtils.format_duration(song['duration']) if song.get('duration') else "Live"
                queue_text += f"`{i}.` **{song['title']}** [{duration}]\n"
                queue_text += f"    👤 {song.get('uploader', 'Unknown')} • 🎧 {song['requester'].display_name}\n"
            
            embed.add_field(
                name=f"📋 Следващи песни (Страница {page}/{total_pages})",
                value=queue_text,
                inline=False
            )
            
            # Add queue statistics
            total_duration = sum(song.get('duration', 0) for song in queue_list)
            embed.add_field(
                name="📊 Статистики",
                value=f"🎵 Общо песни: {len(queue_list)}\n⏱️ Общо време: {MusicUtils.format_duration(total_duration)}",
                inline=True
            )
        else:
            embed.add_field(
                name="📋 Следващи песни",
                value="Няма песни в опашката\nИзползвайте `!play <песен>` за да добавите песен",
                inline=False
            )
        
        embed.set_footer(text=f"{Config.BOT_NAME} • Използвайте бутоните за контрол")
        return embed

class YouTubeDownloader:
    """Enhanced YouTube downloader using yt-dlp with better bot detection evasion"""
    
    def __init__(self):
        # Enhanced user agents - more recent and diverse
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
        ]
        
        # Rotate user agent
        self.current_user_agent = random.choice(self.user_agents)
        
        # Base options for yt-dlp
        self.base_options = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': True,
            'age_limit': 99,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'prefer_ffmpeg': False,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'extractor_retries': 3,
            'file_access_retries': 3,
            'playlistend': 50,
            'source_address': '0.0.0.0'
        }
        
        # Enhanced headers
        self.headers = {
            'User-Agent': self.current_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Create yt-dlp instance
        self.ytdl = self._create_ytdl_instance()
        
        # Cookie jar for session persistence
        self.cookie_jar = {}
    
    def _create_ytdl_instance(self, additional_options: Optional[Dict] = None):
        """Create a new yt-dlp instance with current options"""
        options = self.base_options.copy()
        
        # Add headers
        options['http_headers'] = self.headers.copy()
        
        # Add any additional options
        if additional_options:
            options.update(additional_options)
        
        return yt_dlp.YoutubeDL(options)
    
    def _rotate_user_agent(self):
        """Rotate to a new user agent"""
        self.current_user_agent = random.choice(self.user_agents)
        self.headers['User-Agent'] = self.current_user_agent
    
    async def extract_info(self, url: str, download: bool = False) -> Optional[Dict[str, Any]]:
        """Extract information from YouTube URL with enhanced retry logic"""
        loop = asyncio.get_event_loop()
        
        # Try multiple extraction strategies
        strategies = [
            {'name': 'Standard', 'options': {}},
            {'name': 'No geo-bypass', 'options': {'geo_bypass': False}},
            {'name': 'Force generic', 'options': {'force_generic_extractor': True}},
            {'name': 'Different user agent', 'options': {'http_headers': {**self.headers, 'User-Agent': random.choice(self.user_agents)}}},
            {'name': 'Mobile user agent', 'options': {'http_headers': {**self.headers, 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'}}},
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                print(f"Extraction strategy {i+1}/{len(strategies)}: {strategy['name']}")
                
                # Create new ytdl instance with strategy options
                ytdl = self._create_ytdl_instance(strategy['options'])
                
                # Add delay between attempts
                if i > 0:
                    delay = 2 + (i * 2)  # Progressive delay
                    print(f"Waiting {delay} seconds before next attempt...")
                    await asyncio.sleep(delay)
                
                # Extract info
                data = await loop.run_in_executor(
                    None,
                    lambda: ytdl.extract_info(url, download=download)
                )
                
                if data:
                    print(f"✅ Strategy '{strategy['name']}' succeeded!")
                    return data
                else:
                    print(f"❌ Strategy '{strategy['name']}' returned no data")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Strategy '{strategy['name']}' failed: {error_msg}")
                
                # Check for specific errors
                if "Sign in to confirm" in error_msg:
                    print("Bot detection triggered, trying next strategy...")
                    continue
                elif "Private video" in error_msg:
                    raise Exception("This video is private and cannot be accessed.")
                elif "Video unavailable" in error_msg:
                    raise Exception("Video is not available.")
                elif "Premieres in" in error_msg:
                    raise Exception("This video is a premiere that hasn't started yet.")
                elif "This live event will begin in" in error_msg:
                    raise Exception("This is a scheduled live stream that hasn't started yet.")
                
                # Continue to next strategy
                continue
        
        # If all strategies failed
        raise Exception("All extraction strategies failed. YouTube may be temporarily blocking requests.")
    
    async def search_youtube(self, query: str) -> Optional[Dict[str, Any]]:
        """Search YouTube with enhanced bot detection evasion"""
        try:
            print(f"🔍 Searching for: {query}")
            
            # Check if it's a direct URL
            if self._is_url(query):
                print("📺 Direct URL detected, extracting info...")
                return await self.extract_info(query)
            
            # For search queries, try multiple search strategies
            search_strategies = [
                f"ytsearch1:{query}",
                f"ytsearch2:{query}",
                f"ytsearch3:{query}",
                f"ytsearch:{query}",
            ]
            
            for strategy in search_strategies:
                try:
                    print(f"🔍 Trying search strategy: {strategy}")
                    
                    # Use extract_info for search
                    search_result = await self.extract_info(strategy)
                    
                    if not search_result:
                        continue
                    
                    # Handle search results
                    if 'entries' in search_result:
                        entries = search_result['entries']
                        if entries:
                            # Filter out None entries
                            valid_entries = [e for e in entries if e is not None]
                            if valid_entries:
                                result = valid_entries[0]
                                print(f"✅ Found: {result.get('title', 'Unknown')}")
                                return result
                    
                    # Handle direct result (sometimes search returns direct result)
                    elif search_result.get('title'):
                        print(f"✅ Direct result: {search_result.get('title')}")
                        return search_result
                    
                except Exception as e:
                    print(f"❌ Search strategy failed: {e}")
                    continue
            
            # If all search strategies failed, try alternative search
            return await self._alternative_search(query)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Search failed: {error_msg}")
            
            # Try alternative search as last resort
            try:
                return await self._alternative_search(query)
            except:
                pass
            
            # Provide user-friendly error messages
            if "Sign in to confirm" in error_msg:
                raise Exception("YouTube is currently blocking bot requests. Please try again in a few minutes or use a more specific search term.")
            elif "Private video" in error_msg:
                raise Exception("This video is private and cannot be played.")
            elif "Video unavailable" in error_msg:
                raise Exception("Video is not available in your region.")
            else:
                raise Exception(f"Search failed: {error_msg}")
    
    async def _alternative_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Alternative search method using different approach"""
        print(f"🔄 Trying alternative search for: {query}")
        
        # Try with different extractors and options
        alt_strategies = [
            {
                'name': 'YouTube Music',
                'query': f"https://music.youtube.com/search?q={query.replace(' ', '+')}"
            },
            {
                'name': 'Direct YouTube search',
                'query': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            }
        ]
        
        for strategy in alt_strategies:
            try:
                print(f"🔍 Alternative strategy: {strategy['name']}")
                
                # Create special options for alternative search
                alt_options = {
                    'default_search': None,
                    'force_generic_extractor': True,
                    'playlist_items': '1',
                    'extract_flat': False
                }
                
                ytdl = self._create_ytdl_instance(alt_options)
                
                # Try to extract
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ytdl.extract_info(strategy['query'], download=False)
                )
                
                if result:
                    print(f"✅ Alternative search succeeded with {strategy['name']}")
                    return result
                    
            except Exception as e:
                print(f"❌ Alternative strategy '{strategy['name']}' failed: {e}")
                continue
        
        print("❌ All alternative search strategies failed")
        return None
    
    def _is_url(self, query: str) -> bool:
        """Check if the query is a URL"""
        url_indicators = [
            'http://', 'https://', 'www.',
            'youtube.com', 'youtu.be', 'music.youtube.com',
            'soundcloud.com', 'spotify.com'
        ]
        return any(indicator in query.lower() for indicator in url_indicators)
    
    def is_playlist(self, info: Dict[str, Any]) -> bool:
        """Check if the extracted info is a playlist"""
        return 'entries' in info and len(info.get('entries', [])) > 1
    
    async def get_audio_source(self, url: str) -> discord.AudioSource:
        """Get audio source with enhanced stream URL handling"""
        print(f"🎵 Creating audio source for: {url}")
        
        try:
            # Check if this is already a direct stream URL
            if 'googlevideo.com' in url:
                print("🎯 Direct stream URL detected")
                return self._create_audio_source(url)
            
            # Extract fresh stream URL
            print("🔄 Extracting fresh stream URL...")
            info = await self.extract_info(url)
            
            if not info:
                raise Exception("Could not extract stream information")
            
            stream_url = info.get('url')
            if not stream_url:
                raise Exception("No stream URL found")
            
            print(f"✅ Got stream URL: {stream_url[:100]}...")
            return self._create_audio_source(stream_url)
            
        except Exception as e:
            raise Exception(f"Failed to create audio source: {str(e)}")
    
    def _create_audio_source(self, url: str) -> discord.AudioSource:
        """Create audio source with optimized settings"""
        print("🎵 Creating Discord audio source...")
        
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
            'options': '-vn -filter:a "volume=0.5"'
        }
        
        try:
            # Create audio source with volume control
            source = discord.FFmpegPCMAudio(
                url, 
                before_options=ffmpeg_options['before_options'],
                options=ffmpeg_options['options']
            )
            
            return discord.PCMVolumeTransformer(source, volume=0.5)
            
        except Exception as e:
            print(f"❌ Error creating audio source: {e}")
            # Fallback to basic audio source
            return discord.FFmpegPCMAudio(url) 