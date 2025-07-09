import asyncio
import discord
import yt_dlp
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
        # Browser user agents for better compatibility
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
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
            # Cookie-based anti-bot protection will be set up in _setup_browser_cookies()
            'http_headers': {
                'User-Agent': self.user_agents[0]  # Use latest Chrome user agent
            },
            # Additional YouTube-specific options
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash'],
                    'player_skip': ['configs'],
                }
            },
        }
        
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
            'options': '-vn -filter:a "volume=0.5"'
        }
        
        # Initialize with default options
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_format_options)
        self._setup_browser_cookies()
    
    def _setup_browser_cookies(self):
        """Setup enhanced YouTube access without relying on browser cookies"""
        print("Setting up enhanced YouTube access...")
        
        # Skip cookie loading due to common DPAPI issues on Windows
        # Instead use the most effective header-based approach
        print("⚠️  Skipping browser cookies due to compatibility issues")
        print("Using advanced header-based approach for YouTube access")
        
        # Remove any cookie settings
        self.ytdl_format_options.pop('cookiesfrombrowser', None)
        
        # Enhanced headers that mimic a real browser session
        self.ytdl_format_options['http_headers'].update({
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
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        
        # Advanced YouTube-specific workarounds
        self.ytdl_format_options['extractor_args']['youtube'].update({
            'player_client': ['web', 'android', 'ios'],
            'skip': ['hls', 'dash'],
            'player_skip': ['configs'],
        })
        
        # Additional anti-detection measures
        self.ytdl_format_options.update({
            'sleep_interval': 1,  # Add delays between requests
            'max_sleep_interval': 3,
            'sleep_interval_subtitles': 1,
        })
        
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_format_options)
        print("✅ Enhanced YouTube access configured successfully")
    
    async def extract_info(self, url: str, download: bool = False) -> Optional[Dict[str, Any]]:
        """Extract information from YouTube URL with retry logic"""
        loop = asyncio.get_event_loop()
        
        # Try multiple times with different configurations
        for attempt in range(3):
            try:
                print(f"Extraction attempt {attempt + 1}/3 for: {url}")
                
                # For each attempt, try with slightly different options
                if attempt == 1:
                    # Second attempt: different user agent + more aggressive bypass
                    self.ytdl.params.update({
                        'http_headers': {
                            'User-Agent': self.user_agents[1]  # Firefox user agent
                        },
                        'extractor_args': {
                            'youtube': {
                                'skip': ['hls', 'dash', 'translated_subs'],
                                'player_skip': ['configs', 'webpage', 'js'],
                            }
                        }
                    })
                elif attempt == 2:
                    # Third attempt: Safari user agent + minimal extraction
                    self.ytdl.params.update({
                        'format': 'worst',
                        'http_headers': {
                            'User-Agent': self.user_agents[2]  # Safari user agent
                        },
                        'extractor_args': {'youtube': {'skip': ['hls', 'dash']}},
                    })
                
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
                
                if attempt == 2:  # Last attempt
                    # Re-raise with better error message
                    if "Sign in to confirm" in error_msg:
                        raise Exception("YouTube anti-bot protection detected. Try a different video or search term.")
                    elif "Private video" in error_msg:
                        raise Exception("This video is private.")
                    elif "Video unavailable" in error_msg:
                        raise Exception("Video is not available.")
                    else:
                        raise Exception(f"Failed to extract video info: {error_msg}")
                
                # Wait before retry
                await asyncio.sleep(1)
        
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
                
                if 'entries' not in info or not info['entries'] or len(info['entries']) == 0:
                    print("No search results found in entries")
                    return None
                
                result = info['entries'][0]
                
                # Handle None result
                if not result:
                    print("First search result is None")
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
                raise Exception("YouTube is blocking this request. The video may be age-restricted or require authentication.")
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
        """Fallback search method when main search fails"""
        try:
            print(f"Trying fallback search for: {query}")
            
            # Create a new ytdl instance with minimal options + cookies
            fallback_options = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch',
                'ignoreerrors': True,
                'extractflat': True,  # Minimal extraction
                'http_headers': {
                    'User-Agent': self.user_agents[0],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                }
            }
            
            # Don't use cookies in fallback - use enhanced headers only
            
            fallback_ytdl = yt_dlp.YoutubeDL(fallback_options)
            
            # Try searching with minimal extraction
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                lambda: fallback_ytdl.extract_info(f"ytsearch1:{query}", download=False)
            )
            
            if info and 'entries' in info and info['entries']:
                result = info['entries'][0]
                if result and 'id' in result:
                    # Construct basic info
                    return {
                        'title': result.get('title', query),
                        'id': result['id'],
                        'webpage_url': f"https://www.youtube.com/watch?v={result['id']}",
                        'url': f"https://www.youtube.com/watch?v={result['id']}",  # Will be processed later
                        'duration': result.get('duration', 0),
                        'uploader': result.get('uploader', 'Unknown'),
                    }
            
            return None
            
        except Exception as e:
            print(f"Fallback search also failed: {e}")
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
            if 'mime=audio%2Fwebm' in url or 'mime=audio/webm' in url:
                print("Using FFmpegOpusAudio for WebM stream")
                # WebM Opus is natively supported by Discord, less processing needed
                return discord.FFmpegOpusAudio(
                    url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                    options='-vn'
                )
            else:
                print("Using minimal FFmpeg PCM for compatibility")
                # Use minimal FFmpeg options for maximum compatibility
                source = discord.FFmpegPCMAudio(
                    url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                    options='-vn -ar 48000 -ac 2'  # Discord-compatible sample rate and channels
                )
                return discord.PCMVolumeTransformer(source, volume=0.4)
                
        except Exception as e:
            print(f"Error creating optimized audio source: {e}")
            # Ultimate fallback - most basic FFmpeg possible
            print("Using basic FFmpeg as last resort")
            try:
                source = discord.FFmpegPCMAudio(url, options='-vn')
                return discord.PCMVolumeTransformer(source, volume=0.4)
            except Exception as fallback_error:
                print(f"Even basic FFmpeg failed: {fallback_error}")
                # This means FFmpeg is completely broken
                raise Exception("FFmpeg is not working properly. Please check your FFmpeg installation.")
    
    def _create_audio_source(self, url: str) -> discord.AudioSource:
        """Create FFmpeg audio source with robust options and volume control"""
        # Enhanced FFmpeg options for better stability
        before_options = (
            '-reconnect 1 '
            '-reconnect_streamed 1 '
            '-reconnect_delay_max 5 '
            '-nostdin '
            '-user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"'
        )
        
        options = (
            '-vn '
            '-b:a 128k '
            '-bufsize 1024k '
            '-maxrate 128k '
            '-avoid_negative_ts make_zero '
            '-fflags +genpts'
        )
        
        print(f"Creating FFmpeg audio source with enhanced options")  # Debug logging
        
        try:
            # Create basic FFmpeg source
            ffmpeg_source = discord.FFmpegPCMAudio(
                url,
                before_options=before_options,
                options=options
            )
            
            # Wrap with volume transformer for better audio control
            return discord.PCMVolumeTransformer(ffmpeg_source, volume=0.5)
            
        except Exception as e:
            print(f"Error creating enhanced FFmpeg audio source: {e}")  # Debug logging
            # Fallback to basic options if enhanced options fail
            print("Trying fallback FFmpeg options")  # Debug logging
            try:
                fallback_source = discord.FFmpegPCMAudio(
                    url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                    options='-vn'
                )
                return discord.PCMVolumeTransformer(fallback_source, volume=0.5)
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")  # Debug logging
                # Last resort - minimal options
                minimal_source = discord.FFmpegPCMAudio(url, options='-vn')
                return discord.PCMVolumeTransformer(minimal_source, volume=0.5) 