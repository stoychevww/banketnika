import discord
from discord.ext import commands
import asyncio
import random
from typing import Optional, Dict, Any, List
from collections import deque
from config import Config
from utils.music_utils import MusicUtils, YouTubeDownloader
from utils.cleanup import CleanupManager
from utils.alternative_player import SimpleAudioPlayer

class MusicPlayer:
    """Music player class to handle queue and playback"""
    
    def __init__(self, bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.queue = deque()
        self.current_song = None
        self.voice_client = None
        self.volume = Config.DEFAULT_VOLUME
        self.is_playing = False
        self.is_paused = False
        self.repeat_mode = False
        self.shuffle_mode = False
        self.downloader = YouTubeDownloader()
        self.alternative_player = SimpleAudioPlayer()
        
    async def add_to_queue(self, song_info: Dict[str, Any]):
        """Add a song to the queue"""
        if len(self.queue) >= Config.MAX_QUEUE_SIZE:
            raise Exception(f"Опашката е пълна! Максимум {Config.MAX_QUEUE_SIZE} песни.")
        
        self.queue.append(song_info)
    
    async def play_next(self):
        """Play the next song in queue"""
        print(f"play_next called - Queue length: {len(self.queue)}, Is playing: {self.is_playing}, Repeat mode: {self.repeat_mode}")  # Debug logging
        
        if not self.queue and not self.repeat_mode:
            print("No songs in queue and repeat mode off - stopping playback")  # Debug logging
            self.current_song = None
            self.is_playing = False
            return
        
        if self.repeat_mode and self.current_song:
            next_song = self.current_song
            print(f"Repeat mode: Playing current song again - {next_song['title']}")  # Debug logging
        else:
            if self.shuffle_mode and len(self.queue) > 1:
                # Shuffle the queue
                queue_list = list(self.queue)
                random.shuffle(queue_list)
                self.queue = deque(queue_list)
                print("Shuffled queue")  # Debug logging
            
            next_song = self.queue.popleft()
            self.current_song = next_song
            print(f"Playing next song from queue: {next_song['title']} - {next_song['url']}")  # Debug logging
        
        try:
            print(f"Getting audio source for: {next_song['url']}")  # Debug logging
            
            # Try to get audio source using alternative player
            try:
                audio_source = await self.alternative_player.create_source(next_song['url'])
            except Exception as e:
                if "expired" in str(e).lower() or "403" in str(e) or "forbidden" in str(e).lower():
                    print(f"Stream URL expired, refreshing from original URL: {next_song.get('original_url', next_song['url'])}")
                    # Get fresh stream URL from original YouTube URL
                    fresh_info = await self.downloader.search_youtube(next_song.get('original_url', next_song['url']))
                    if fresh_info:
                        # Update the song data with fresh URL
                        next_song['url'] = fresh_info['url']
                        self.current_song = next_song  # Update current song with fresh URL
                        print(f"Got fresh stream URL: {fresh_info['url']}")
                        # Use the fresh stream URL with alternative player
                        audio_source = await self.alternative_player.create_source(fresh_info['url'])
                    else:
                        raise Exception("Could not refresh expired stream URL")
                else:
                    raise e
            
            print(f"Audio source created successfully")  # Debug logging
            
            # Play the audio
            if self.voice_client and self.voice_client.is_connected():
                print("Voice client connected, starting playback")  # Debug logging
                def after_playing(error):
                    if error:
                        print(f"Player error: {error}")
                    else:
                        print("Song finished playing")  # Debug logging
                    # Schedule the next song
                    CleanupManager.safe_schedule_coroutine(self.play_next(), self.bot.loop)
                
                self.voice_client.play(audio_source, after=after_playing)
                self.is_playing = True
                self.is_paused = False
                self._retry_count = 0  # Reset retry counter on successful playback
                print("Playback started successfully")  # Debug logging
            else:
                print("Voice client not connected, cannot play audio")
                self.is_playing = False
            
        except Exception as e:
            print(f"Error playing song: {e}")
            
            # Handle specific FFmpeg errors
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['ffmpeg', 'connection', 'network', 'timeout']):
                print("Network or FFmpeg error detected, waiting before retry")
                await asyncio.sleep(2)  # Wait 2 seconds before retry
            
            # Try to play next song after error, but limit retries
            if not hasattr(self, '_retry_count'):
                self._retry_count = 0
            
            if self._retry_count < 3:  # Max 3 retries
                self._retry_count += 1
                print(f"Retrying playback (attempt {self._retry_count}/3)")
                try:
                    await self.play_next()
                except Exception as next_error:
                    print(f"Error in play_next after error: {next_error}")
                    self.is_playing = False
            else:
                print("Max retries reached, stopping playback")
                self._retry_count = 0
                self.is_playing = False
    
    def pause(self):
        """Pause the current song"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
    
    def resume(self):
        """Resume the current song"""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
    
    def stop(self):
        """Stop the current song"""
        if self.voice_client:
            self.voice_client.stop()
            self.is_playing = False
            self.is_paused = False
        # Clean up alternative player resources
        self.alternative_player.cleanup()
    
    def skip(self):
        """Skip the current song"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
    
    def clear_queue(self):
        """Clear the queue"""
        self.queue.clear()
    
    def shuffle_queue(self):
        """Shuffle the queue"""
        if len(self.queue) > 1:
            queue_list = list(self.queue)
            random.shuffle(queue_list)
            self.queue = deque(queue_list)
            return True
        return False

class Music(commands.Cog):
    """Advanced Music Cog for Banketnika Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.downloader = YouTubeDownloader()
        
        # Check if FFmpeg is properly installed
        if not MusicUtils.check_ffmpeg():
            print("⚠️  WARNING: FFmpeg is not properly installed or configured!")
            print("Using alternative audio player with minimal FFmpeg requirements.")
        else:
            print("✅ FFmpeg is properly installed - using optimized alternative player")
    
    def get_player(self, guild_id: int) -> MusicPlayer:
        """Get or create a music player for the guild"""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(self.bot, guild_id)
        return self.players[guild_id]
    
    async def ensure_voice_connection(self, ctx) -> bool:
        """Ensure bot is connected to voice channel"""
        if not ctx.author.voice:
            embed = MusicUtils.create_music_embed(
                "❌ Грешка",
                "Трябва да сте в гласов канал за да използвате музикални команди!",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return False
        
        channel = ctx.author.voice.channel
        player = self.get_player(ctx.guild.id)
        
        if not player.voice_client:
            try:
                player.voice_client = await channel.connect()
            except Exception as e:
                embed = MusicUtils.create_music_embed(
                    "❌ Грешка",
                    f"Не мога да се свържа с гласовия канал: {str(e)}",
                    Config.COLOR_ERROR
                )
                await ctx.send(embed=embed)
                return False
        
        return True
    
    @commands.command(name='play', aliases=['p', 'свири', 'пусни'])
    async def play(self, ctx, *, query: str):
        """Play a song or add it to queue"""
        if not await self.ensure_voice_connection(ctx):
            return
        
        player = self.get_player(ctx.guild.id)
        
        # Show searching message
        searching_embed = MusicUtils.create_music_embed(
            "🔍 Търсене...",
            f"Търся: **{query}**",
            Config.COLOR_WARNING
        )
        search_msg = await ctx.send(embed=searching_embed)
        
        try:
            # Search for the song or extract URL info
            song_info = await self.downloader.search_youtube(query)
            
            if not song_info:
                embed = MusicUtils.create_music_embed(
                    "❌ Не намерих",
                    f"Не мога да намеря песен за: **{query}**\n"
                    f"Моля проверете дали URL-то е валидно или опитайте с друга заявка.",
                    Config.COLOR_ERROR
                )
                await search_msg.edit(embed=embed)
                return
            
            # Check if it's a playlist
            if self.downloader.is_playlist(song_info):
                await self._handle_playlist(ctx, song_info, search_msg, player)
                return
            
            # Single song handling
            await self._handle_single_song(ctx, song_info, search_msg, player)
        
        except Exception as e:
            print(f"Error in play command: {str(e)}")  # Debug logging
            error_msg = str(e)
            
            # Provide specific error messages for common issues
            if "No video found" in error_msg:
                error_msg = "Не намерих видео с това URL или заявка"
            elif "Private video" in error_msg:
                error_msg = "Видеото е частно и не може да бъде възпроизведено"
            elif "Video unavailable" in error_msg:
                error_msg = "Видеото не е налично в тази страна"
            elif "age-restricted" in error_msg:
                error_msg = "Видеото е с възрастови ограничения"
            
            embed = MusicUtils.create_music_embed(
                "❌ Грешка",
                f"Възникна грешка: {error_msg}",
                Config.COLOR_ERROR
            )
            await search_msg.edit(embed=embed)
    
    @commands.command(name='pause', aliases=['пауза'])
    async def pause(self, ctx):
        """Pause the current song"""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            embed = MusicUtils.create_music_embed(
                "❌ Няма музика",
                "В момента не свири музика",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return
        
        player.pause()
        embed = MusicUtils.create_music_embed(
            "⏸️ Пауза",
            "Музиката е паузирана",
            Config.COLOR_WARNING
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='resume', aliases=['продължи'])
    async def resume(self, ctx):
        """Resume the current song"""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_paused:
            embed = MusicUtils.create_music_embed(
                "❌ Не е паузирана",
                "Музиката не е паузирана",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return
        
        player.resume()
        embed = MusicUtils.create_music_embed(
            "▶️ Продължаване",
            "Музиката продължава",
            Config.COLOR_SUCCESS
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='skip', aliases=['прескочи', 'next'])
    async def skip(self, ctx):
        """Skip the current song"""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            embed = MusicUtils.create_music_embed(
                "❌ Няма музика",
                "В момента не свири музика",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return
        
        player.skip()
        embed = MusicUtils.create_music_embed(
            "⏭️ Прескочена",
            "Песента беше прескочена",
            Config.COLOR_SUCCESS
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stop', aliases=['спри'])
    async def stop(self, ctx):
        """Stop the music and clear queue"""
        player = self.get_player(ctx.guild.id)
        
        player.stop()
        player.clear_queue()
        
        embed = MusicUtils.create_music_embed(
            "⏹️ Спряна",
            "Музиката е спряна и опашката е изчистена",
            Config.COLOR_SUCCESS
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='queue', aliases=['q', 'опашка'])
    async def queue(self, ctx):
        """Show the current queue"""
        player = self.get_player(ctx.guild.id)
        
        embed = MusicUtils.create_queue_embed(list(player.queue), player.current_song)
        await ctx.send(embed=embed)
    
    @commands.command(name='nowplaying', aliases=['np', 'сега'])
    async def nowplaying(self, ctx):
        """Show currently playing song"""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            embed = MusicUtils.create_music_embed(
                "❌ Няма музика",
                "В момента не свири музика",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return
        
        embed = MusicUtils.create_now_playing_embed(player.current_song)
        await ctx.send(embed=embed)
    
    @commands.command(name='shuffle', aliases=['разбъркай'])
    async def shuffle(self, ctx):
        """Shuffle the queue"""
        player = self.get_player(ctx.guild.id)
        
        if player.shuffle_queue():
            embed = MusicUtils.create_music_embed(
                "🔀 Разбъркана",
                "Опашката беше разбъркана",
                Config.COLOR_SUCCESS
            )
        else:
            embed = MusicUtils.create_music_embed(
                "❌ Няма какво да се разбърка",
                "Опашката е празна или има само една песен",
                Config.COLOR_ERROR
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear', aliases=['изчисти'])
    async def clear(self, ctx):
        """Clear the queue"""
        player = self.get_player(ctx.guild.id)
        
        if not player.queue:
            embed = MusicUtils.create_music_embed(
                "❌ Празна опашка",
                "Опашката вече е празна",
                Config.COLOR_ERROR
            )
        else:
            player.clear_queue()
            embed = MusicUtils.create_music_embed(
                "🗑️ Изчистена",
                "Опашката беше изчистена",
                Config.COLOR_SUCCESS
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='repeat', aliases=['повтори'])
    async def repeat(self, ctx):
        """Toggle repeat mode"""
        player = self.get_player(ctx.guild.id)
        
        player.repeat_mode = not player.repeat_mode
        
        if player.repeat_mode:
            embed = MusicUtils.create_music_embed(
                "🔁 Повторение включено",
                "Текущата песен ще се повтаря",
                Config.COLOR_SUCCESS
            )
        else:
            embed = MusicUtils.create_music_embed(
                "🔁 Повторение изключено",
                "Текущата песен няма да се повтаря",
                Config.COLOR_WARNING
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='disconnect', aliases=['dc', 'напусни'])
    async def disconnect(self, ctx):
        """Disconnect from voice channel"""
        player = self.get_player(ctx.guild.id)
        
        if player.voice_client:
            # Use cleanup manager for safe disconnection
            await CleanupManager.cleanup_music_player(player)
            
            embed = MusicUtils.create_music_embed(
                "👋 Довиждане",
                "Напуснах гласовия канал",
                Config.COLOR_SUCCESS
            )
        else:
            embed = MusicUtils.create_music_embed(
                "❌ Не съм свързан",
                "Не съм свързан с гласов канал",
                Config.COLOR_ERROR
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='banket', aliases=['банкет'])
    async def banket(self, ctx):
        """Special banket command - play random Bulgarian folk music"""
        bulgarian_songs = [
            "Калинка",
            "Тих бял Дунав",
            "Малка мома",
            "Дилмано Дилберо",
            "Българско хоро",
            "Мила родино",
            "Дунавско хоро"
        ]
        
        random_song = random.choice(bulgarian_songs)
        
        embed = MusicUtils.create_music_embed(
            "🎉 Банкет режим!",
            f"Пускам българска народна музика: **{random_song}**\n{MusicUtils.get_random_banket_phrase()}",
            Config.COLOR_SECONDARY
        )
        await ctx.send(embed=embed)
        
        # Try to play the song
        await self.play(ctx, query=random_song)
    
    @commands.command(name='playlist', aliases=['pl', 'плейлист'])
    async def playlist(self, ctx, *, url: str):
        """Add a playlist to the queue"""
        if not await self.ensure_voice_connection(ctx):
            return
        
        # Check if it's a URL
        if not self.downloader._is_url(url):
            embed = MusicUtils.create_music_embed(
                "❌ Невалидно URL",
                "Моля предоставете валидно URL на плейлист",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return
        
        player = self.get_player(ctx.guild.id)
        
        # Show loading message
        loading_embed = MusicUtils.create_music_embed(
            "🔄 Зареждане на плейлист...",
            f"Зареждам плейлист от: **{url}**",
            Config.COLOR_WARNING
        )
        loading_msg = await ctx.send(embed=loading_embed)
        
        try:
            # Extract playlist info
            playlist_info = await self.downloader.search_youtube(url)
            
            if not playlist_info:
                embed = MusicUtils.create_music_embed(
                    "❌ Не мога да заредя плейлиста",
                    "Моля проверете дали URL-то е валидно",
                    Config.COLOR_ERROR
                )
                await loading_msg.edit(embed=embed)
                return
            
            # Handle the playlist
            await self._handle_playlist(ctx, playlist_info, loading_msg, player)
            
        except Exception as e:
            print(f"Error loading playlist: {str(e)}")
            embed = MusicUtils.create_music_embed(
                "❌ Грешка при зареждане",
                f"Възникна грешка при зареждане на плейлиста: {str(e)}",
                Config.COLOR_ERROR
            )
            await loading_msg.edit(embed=embed)
    
    async def _handle_single_song(self, ctx, song_info, search_msg, player):
        """Handle adding a single song to the queue"""
        print(f"_handle_single_song called for: {song_info.get('title', 'Unknown')}")  # Debug logging
        
        # Check song length
        if song_info.get('duration', 0) > Config.MAX_SONG_LENGTH:
            embed = MusicUtils.create_music_embed(
                "❌ Песента е твърде дълга",
                f"Максимална дължина: {Config.MAX_SONG_LENGTH // 60} минути",
                Config.COLOR_ERROR
            )
            await search_msg.edit(embed=embed)
            return
        
        # Prepare song info
        song_data = {
            'title': song_info['title'],
            'url': song_info['url'],
            'original_url': song_info.get('webpage_url', song_info['url']),  # Store original YouTube URL
            'duration': song_info.get('duration', 0),
            'uploader': song_info.get('uploader', 'Unknown'),
            'thumbnail': song_info.get('thumbnail'),
            'requester': ctx.author
        }
        
        print(f"Adding song to queue: {song_data['title']}")  # Debug logging
        
        # Add to queue
        await player.add_to_queue(song_data)
        
        # If not currently playing, start playing
        if not player.is_playing:
            print("Player not playing, starting playback")  # Debug logging
            try:
                await player.play_next()
                print("play_next completed successfully")  # Debug logging
                
                # Check if playback actually started
                if player.is_playing:
                    print("Playback started, updating message with now playing")  # Debug logging
                    embed = MusicUtils.create_now_playing_embed(song_data)
                    await search_msg.edit(embed=embed)
                else:
                    print("Playback failed to start")  # Debug logging
                    embed = MusicUtils.create_music_embed(
                        "❌ Грешка при възпроизвеждане",
                        f"Не мога да пусна песента: **{song_data['title']}**",
                        Config.COLOR_ERROR
                    )
                    await search_msg.edit(embed=embed)
            except Exception as e:
                print(f"Error in play_next: {e}")  # Debug logging
                embed = MusicUtils.create_music_embed(
                    "❌ Грешка при възпроизвеждане",
                    f"Възникна грешка при пускане на песента: {str(e)}",
                    Config.COLOR_ERROR
                )
                await search_msg.edit(embed=embed)
        else:
            print("Player already playing, adding to queue")  # Debug logging
            # Song added to queue
            embed = MusicUtils.create_music_embed(
                "✅ Добавена в опашката",
                f"**{song_data['title']}**\nПозиция в опашката: {len(player.queue)}",
                Config.COLOR_SUCCESS
            )
            await search_msg.edit(embed=embed)
    
    async def _handle_playlist(self, ctx, playlist_info, search_msg, player):
        """Handle adding a playlist to the queue"""
        entries = playlist_info.get('entries', [])
        playlist_title = playlist_info.get('title', 'Неизвестен плейлист')
        
        if not entries:
            embed = MusicUtils.create_music_embed(
                "❌ Празен плейлист",
                "Плейлистът е празен или не може да бъде зареден",
                Config.COLOR_ERROR
            )
            await search_msg.edit(embed=embed)
            return
        
        # Filter out songs that are too long and prepare song data
        valid_songs = []
        skipped_songs = 0
        
        for entry in entries:
            if entry.get('duration', 0) > Config.MAX_SONG_LENGTH:
                skipped_songs += 1
                continue
            
            song_data = {
                'title': entry['title'],
                'url': entry['url'],
                'original_url': entry.get('webpage_url', entry['url']),  # Store original YouTube URL
                'duration': entry.get('duration', 0),
                'uploader': entry.get('uploader', 'Unknown'),
                'thumbnail': entry.get('thumbnail'),
                'requester': ctx.author
            }
            valid_songs.append(song_data)
        
        # Check if we have valid songs
        if not valid_songs:
            embed = MusicUtils.create_music_embed(
                "❌ Няма валидни песни",
                "Всички песни в плейлиста са твърде дълги или недостъпни",
                Config.COLOR_ERROR
            )
            await search_msg.edit(embed=embed)
            return
        
        # Check if adding all songs would exceed queue limit
        if len(player.queue) + len(valid_songs) > Config.MAX_QUEUE_SIZE:
            max_songs = Config.MAX_QUEUE_SIZE - len(player.queue)
            valid_songs = valid_songs[:max_songs]
            
            embed = MusicUtils.create_music_embed(
                "⚠️ Плейлист съкратен",
                f"Плейлистът е съкратен до {max_songs} песни поради ограничения на опашката",
                Config.COLOR_WARNING
            )
            await search_msg.edit(embed=embed)
            await asyncio.sleep(3)  # Show warning for 3 seconds
        
        # Add all valid songs to queue
        for song_data in valid_songs:
            await player.add_to_queue(song_data)
        
        # Create playlist added embed
        embed = MusicUtils.create_music_embed(
            "📋 Плейлист добавен",
            f"**{playlist_title}**\n"
            f"✅ Добавени: {len(valid_songs)} песни\n"
            f"⏭️ Прескочени: {skipped_songs} песни (твърде дълги)\n"
            f"🎵 Позиция в опашката: {len(player.queue) - len(valid_songs) + 1}-{len(player.queue)}",
            Config.COLOR_SUCCESS
        )
        await search_msg.edit(embed=embed)
        
        # If not currently playing, start playing
        if not player.is_playing:
            await player.play_next()

async def setup(bot):
    await bot.add_cog(Music(bot)) 