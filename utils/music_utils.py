import asyncio
import discord
import youtube_dl
import random
import subprocess
import shutil
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
    """YouTube downloader utility class"""
    
    def __init__(self):
        # Browser user agents for better compatibility - updated with more recent versions
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        ]
        
        # Rotate user agent for each instance
        import random
        self.current_user_agent = random.choice(self.user_agents)
        
        self.ytdl_format_options = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
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
            'prefer_ffmpeg': False,  # Disable FFmpeg preference
            'postprocessors': [],  # No post-processing
            # Enhanced headers to avoid bot detection
            'http_headers': {
                'User-Agent': self.current_user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            },
            # Additional options for youtube-dl
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'allsubtitles': False,
            'listsubtitles': False,
            'subtitlesformat': 'best',
            'subtitleslangs': ['en'],
            'force_generic_extractor': False,
            'no_check_certificate': True,
            'prefer_insecure': False,
            'call_home': False,
            'sleep_interval': 0,
            'max_sleep_interval': 0,
            'sleep_interval_requests': 1,  # Add delay between requests
            'sleep_interval_subtitles': 1,
        }
        
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
            'options': '-vn -filter:a "volume=0.5"'
        }
        
        # Initialize with default options
        self.ytdl = youtube_dl.YoutubeDL(self.ytdl_format_options)
        self._setup_browser_cookies()
    
    def _setup_browser_cookies(self):
        """Setup enhanced YouTube access for youtube-dl"""
        print("Setting up YouTube access with youtube-dl...")
        
        # youtube-dl doesn't support the same parameter updates as yt-dlp
        # The configuration is set in the constructor and doesn't need runtime updates
        print("✅ YouTube access configured with youtube-dl")
    
    async def extract_info(self, url: str, download: bool = False) -> Optional[Dict[str, Any]]:
        """Extract information from YouTube URL with enhanced retry logic"""
        loop = asyncio.get_event_loop()
        
        # Try multiple times with different configurations
        for attempt in range(3):  # Reduced to 3 attempts for simplicity
            try:
                print(f"Extraction attempt {attempt + 1}/3 for: {url}")
                
                # Add delay between attempts to avoid rate limiting
                if attempt > 0:
                    await asyncio.sleep(2 + attempt)  # Progressive delay
                
                data = await loop.run_in_executor(
                    None, 
                    lambda: self.ytdl.extract_info(url, download=download)
                )
                
                if data is None:
                    print(f"No data returned from YouTube on attempt {attempt + 1}")
                    if attempt == 2:  # Last attempt
                        return None
                    continue
                
                print(f"Successfully extracted info on attempt {attempt + 1}")
                return data
                
            except Exception as e:
                error_msg = str(e)
                print(f"Attempt {attempt + 1} failed: {error_msg}")
                
                # Handle specific DNS and network errors
                if ("Name or service not known" in error_msg or 
                    "TransportError" in error_msg or 
                    "ConnectionError" in error_msg or
                    "timeout" in error_msg.lower()):
                    print(f"Network error detected on attempt {attempt + 1}")
                    if attempt < 2:  # Not the last attempt
                        print("Retrying due to network issue...")
                        await asyncio.sleep(3 + attempt)  # Longer delay for network issues
                        continue
                
                # Handle specific JSON parsing errors and player response errors
                if ("JSONDecodeError" in error_msg or "Expecting value" in error_msg or 
                    "Failed to extract any player response" in error_msg):
                    print(f"YouTube extraction error detected on attempt {attempt + 1}")
                    if attempt < 2:  # Not the last attempt
                        print("Retrying with different configuration...")
                        continue
                
                if attempt == 2:  # Last attempt
                    # Re-raise with better error message
                    if "Name or service not known" in error_msg:
                        raise Exception("Network connectivity issue. Please check your internet connection and try again.")
                    elif "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                        raise Exception("YouTube anti-bot protection detected. The search term may be too generic or YouTube is blocking requests.")
                    elif ("JSONDecodeError" in error_msg or "Expecting value" in error_msg or 
                          "Failed to extract any player response" in error_msg):
                        raise Exception("YouTube returned invalid data or blocked the request. This may be due to anti-bot protection or server issues.")
                    elif "Private video" in error_msg:
                        raise Exception("This video is private.")
                    elif "Video unavailable" in error_msg:
                        raise Exception("Video is not available.")
                    else:
                        raise Exception(f"Failed to extract video info after 3 attempts: {error_msg}")
        
        return None
    
    async def search_youtube(self, query: str) -> Optional[Dict[str, Any]]:
        """Search YouTube for a query or extract info from URL"""
        try:
            print(f"Searching YouTube for: {query}")  # Debug logging
            
            # Check if it's a URL
            if self._is_url(query):
                print(f"Detected URL: {query}")  # Debug logging
                # Direct URL - extract info directly
                info = await self.extract_info(query, download=False)
                
                # Handle None response
                if not info:
                    print("No info extracted from URL")
                    return None
                
                # Ensure we have the webpage_url for later refreshing
                if 'webpage_url' not in info:
                    info['webpage_url'] = query
                print(f"Extracted info for URL: {info.get('title', 'Unknown')} - {info.get('url', 'No URL')}")  # Debug logging
                return info
            else:
                print(f"Searching for query: {query}")  # Debug logging
                # Search query - use ytsearch
                info = await self.extract_info(f"ytsearch:{query}", download=False)
                
                # Handle None response or missing entries
                if not info:
                    print("No search info returned")
                    return None
                
                print(f"Search info received: {type(info)}")  # Debug logging
                print(f"Info keys: {list(info.keys()) if isinstance(info, dict) else 'Not a dict'}")  # Debug logging
                
                if 'entries' not in info or not info['entries'] or len(info['entries']) == 0:
                    print("No search results found in entries")
                    return None
                
                print(f"Total entries found: {len(info['entries'])}")  # Debug logging
                print(f"Entry types: {[type(entry) for entry in info['entries'][:5]]}")  # Debug logging first 5
                
                # Filter out None entries and find the first valid result
                valid_entries = [entry for entry in info['entries'] if entry is not None]
                
                print(f"Valid entries after filtering: {len(valid_entries)}")  # Debug logging
                
                if not valid_entries:
                    print("All search results are None - no valid entries found")
                    # Try to understand why all entries are None
                    none_count = sum(1 for entry in info['entries'] if entry is None)
                    print(f"Found {none_count} None entries out of {len(info['entries'])} total entries")
                    
                    # Check if this might be due to bot detection
                    if none_count == len(info['entries']):
                        print("All entries are None - likely bot detection. Trying fallback search...")
                        fallback_result = await self.fallback_search(query)
                        if fallback_result:
                            print("Fallback search succeeded!")
                            return fallback_result
                        else:
                            # If fallback also fails, it's likely bot detection
                            raise Exception("YouTube is blocking requests due to bot detection. Try using a different search term or wait a few minutes before trying again.")
                    
                    return None
                
                result = valid_entries[0]
                
                print(f"Selected result type: {type(result)}")  # Debug logging
                print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")  # Debug logging
                
                # Double-check the result is valid
                if not result or not result.get('id'):
                    print("First valid search result is missing required data")
                    print(f"Result has ID: {bool(result.get('id'))}")  # Debug logging
                    print(f"Result ID value: {result.get('id')}")  # Debug logging
                    return None
                
                # For search results, the webpage_url is the actual YouTube watch URL
                # The 'url' field contains the direct stream URL
                if 'webpage_url' not in result and 'id' in result:
                    # Construct the YouTube watch URL from the video ID
                    result['webpage_url'] = f"https://www.youtube.com/watch?v={result['id']}"
                print(f"Found search result: {result.get('title', 'Unknown')} - Stream URL: {result.get('url', 'No URL')}")  # Debug logging
                print(f"Original YouTube URL: {result.get('webpage_url', 'No webpage URL')}")  # Debug logging
                return result
                
        except Exception as e:
            error_msg = str(e)
            print(f"Search error: {error_msg}")  # Debug logging
            
            # Try fallback search for non-URL queries
            if not self._is_url(query):
                print("Trying fallback search method...")
                fallback_result = await self.fallback_search(query)
                if fallback_result:
                    print("Fallback search succeeded!")
                    return fallback_result
            
            # Handle specific YouTube errors
            if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                raise Exception("YouTube is blocking this request due to bot detection. Try using a different search term, wait a few minutes, or try a more specific query.")
            elif "Private video" in error_msg:
                raise Exception("This video is private and cannot be played.")
            elif "Video unavailable" in error_msg:
                raise Exception("This video is not available in your region.")
            elif "not iterable" in error_msg:
                raise Exception("YouTube search failed. Please try a different search term or URL.")
            else:
                raise Exception(f"Search failed: {error_msg}")
    
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
    
    async def fallback_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Enhanced fallback search method with multiple strategies to avoid bot detection"""
        print(f"Trying fallback search for: {query}")
        
        # Try multiple fallback strategies with different approaches
        fallback_strategies = [
            {
                'name': 'Mobile user agent',
                'options': {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch',
                    'ignoreerrors': True,
                    'sleep_interval_requests': 2,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                    }
                }
            },
            {
                'name': 'Minimal extraction with delays',
                'options': {
                    'format': 'worst',
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch',
                    'ignoreerrors': True,
                    'extractflat': True,
                    'sleep_interval_requests': 3,
                    'http_headers': {
                        'User-Agent': self.user_agents[1],
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                }
            },
            {
                'name': 'Firefox with extended headers',
                'options': {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch',
                    'ignoreerrors': True,
                    'sleep_interval_requests': 1,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                    }
                }
            },
            {
                'name': 'Generic search with minimal footprint',
                'options': {
                    'format': 'bestaudio',
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch1',  # Search for only 1 result
                    'ignoreerrors': True,
                    'extractflat': True,
                    'sleep_interval_requests': 4,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                        'Accept': '*/*',
                    }
                }
            }
        ]
        
        loop = asyncio.get_event_loop()
        
        for i, strategy in enumerate(fallback_strategies):
            try:
                print(f"Trying fallback strategy {i+1}/4: {strategy['name']}")
                
                # Add progressive delay between strategies
                if i > 0:
                    delay = 3 + (i * 2)  # 3, 5, 7, 9 seconds
                    print(f"Waiting {delay} seconds before next strategy...")
                    await asyncio.sleep(delay)
                
                fallback_ytdl = youtube_dl.YoutubeDL(strategy['options'])
                
                # Try searching with this strategy
                info = await loop.run_in_executor(
                    None,
                    lambda: fallback_ytdl.extract_info(f"ytsearch1:{query}", download=False)
                )
                
                if info and 'entries' in info and info['entries']:
                    # Filter out None entries
                    valid_entries = [entry for entry in info['entries'] if entry is not None]
                    
                    if valid_entries:
                        result = valid_entries[0]
                        if result and result.get('id'):
                            print(f"Fallback strategy '{strategy['name']}' succeeded!")
                            # Construct basic info
                            return {
                                'title': result.get('title', query),
                                'id': result['id'],
                                'webpage_url': f"https://www.youtube.com/watch?v={result['id']}",
                                'url': f"https://www.youtube.com/watch?v={result['id']}",  # Will be processed later
                                'duration': result.get('duration', 0),
                                'uploader': result.get('uploader', 'Unknown'),
                            }
                        else:
                            print(f"Fallback strategy '{strategy['name']}' returned invalid result")
                    else:
                        print(f"Fallback strategy '{strategy['name']}' returned no valid entries")
                else:
                    print(f"Fallback strategy '{strategy['name']}' returned no info or entries")
                
            except Exception as e:
                print(f"Fallback strategy '{strategy['name']}' failed: {e}")
                continue
        
        print("All fallback strategies failed")
        return None
    
    async def get_audio_source(self, url: str) -> discord.AudioSource:
        """Get audio source without FFmpeg using direct streaming"""
        print(f"Getting audio source for: {url}")  # Debug logging
        
        try:
            # Always extract fresh info to get the best audio stream
            if 'googlevideo.com' in url:
                # This is already a direct stream URL, but we need to check if it's expired
                import time
                from urllib.parse import urlparse, parse_qs
                
                try:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    
                    if 'expire' in query_params:
                        expire_time = int(query_params['expire'][0])
                        current_time = int(time.time())
                        
                        print(f"Stream URL expire time: {expire_time}, current time: {current_time}")
                        
                        if current_time >= expire_time:
                            print("Stream URL has expired")
                            raise Exception("Stream URL has expired, need to refresh from original YouTube URL")
                        else:
                            print("Stream URL is still valid, using direct streaming")
                            return self._create_direct_audio_source(url)
                    else:
                        print("No expire parameter, using direct streaming")
                        return self._create_direct_audio_source(url)
                except Exception as e:
                    print(f"Error checking URL expiration: {e}")
                    raise Exception("Stream URL has expired, need to refresh from original YouTube URL")
            else:
                # This is a YouTube watch URL, extract the best audio stream
                print(f"Extracting audio stream from YouTube URL: {url}")
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None, 
                    lambda: self.ytdl.extract_info(url, download=False)
                )
                
                if not info:
                    raise Exception("Could not extract audio info")
                
                # Get the best audio URL
                audio_url = info.get('url')
                if not audio_url:
                    raise Exception("No audio URL found")
                
                print(f"Extracted audio stream URL: {audio_url}")
                return self._create_direct_audio_source(audio_url)
                
        except Exception as e:
            raise Exception(f"Error creating audio source: {str(e)}")
    
    def _create_direct_audio_source(self, url: str) -> discord.AudioSource:
        """Create audio source using optimized streaming approach"""
        print(f"Creating optimized audio source")  # Debug logging
        
        try:
            # Check if this is a WebM Opus stream (best for Discord)
            if 'mime=audio%2Fwebm' in url and 'codecs=opus' in url:
                print("Detected WebM Opus stream - using optimized playback")
                # For WebM Opus, we can use minimal FFmpeg options
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                    'options': '-vn'  # No video, minimal processing for Opus
                }
            else:
                print("Using standard audio processing")
                # For other formats, use standard options
                ffmpeg_options = self.ffmpeg_options
            
            # Create the audio source
            return discord.FFmpegPCMAudio(url, before_options=ffmpeg_options['before_options'], options=ffmpeg_options['options'])
            
        except Exception as e:
            print(f"Error creating direct audio source: {e}")
            # Fallback to basic audio source
            return self._create_audio_source(url)
    
    def _create_audio_source(self, url: str) -> discord.AudioSource:
        """Create audio source with volume control"""
        print(f"Creating audio source with volume control")  # Debug logging
        
        try:
            # Create FFmpeg audio source
            source = discord.FFmpegPCMAudio(url, before_options=self.ffmpeg_options['before_options'], options=self.ffmpeg_options['options'])
            
            # Add volume control
            return discord.PCMVolumeTransformer(source, volume=0.5)
            
        except Exception as e:
            print(f"Error creating audio source: {e}")
            # Last resort - basic audio source without volume control
            return discord.FFmpegPCMAudio(url, before_options=self.ffmpeg_options['before_options'], options=self.ffmpeg_options['options']) 