import discord
from discord.ext import commands
import asyncio
import random
from typing import Optional, Dict, Any, List
from collections import deque
from config import Config
from utils.music_utils import MusicUtils, YouTubeDownloader

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
        
    async def add_to_queue(self, song_info: Dict[str, Any]):
        """Add a song to the queue"""
        if len(self.queue) >= Config.MAX_QUEUE_SIZE:
            raise Exception(f"Опашката е пълна! Максимум {Config.MAX_QUEUE_SIZE} песни.")
        
        self.queue.append(song_info)
    
    async def play_next(self):
        """Play the next song in queue"""
        if not self.queue and not self.repeat_mode:
            self.current_song = None
            self.is_playing = False
            return
        
        if self.repeat_mode and self.current_song:
            next_song = self.current_song
        else:
            if self.shuffle_mode and len(self.queue) > 1:
                # Shuffle the queue
                queue_list = list(self.queue)
                random.shuffle(queue_list)
                self.queue = deque(queue_list)
            
            next_song = self.queue.popleft()
            self.current_song = next_song
        
        try:
            # Get the audio source
            audio_source = self.downloader.get_audio_source(next_song['url'])
            
            # Play the audio
            if self.voice_client:
                self.voice_client.play(
                    audio_source,
                    after=lambda e: self.bot.loop.create_task(self.play_next()) if not e else print(f"Player error: {e}")
                )
            
            self.is_playing = True
            self.is_paused = False
            
        except Exception as e:
            print(f"Error playing song: {e}")
            await self.play_next()
    
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
            # Search for the song
            song_info = await self.downloader.search_youtube(query)
            
            if not song_info:
                embed = MusicUtils.create_music_embed(
                    "❌ Не намерих",
                    f"Не мога да намеря песен за: **{query}**",
                    Config.COLOR_ERROR
                )
                await search_msg.edit(embed=embed)
                return
            
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
                'duration': song_info.get('duration', 0),
                'uploader': song_info.get('uploader', 'Unknown'),
                'thumbnail': song_info.get('thumbnail'),
                'requester': ctx.author
            }
            
            # Add to queue
            await player.add_to_queue(song_data)
            
            # If not currently playing, start playing
            if not player.is_playing:
                await player.play_next()
                embed = MusicUtils.create_now_playing_embed(song_data)
                await search_msg.edit(embed=embed)
            else:
                # Song added to queue
                embed = MusicUtils.create_music_embed(
                    "✅ Добавена в опашката",
                    f"**{song_data['title']}**\nПозиция в опашката: {len(player.queue)}",
                    Config.COLOR_SUCCESS
                )
                await search_msg.edit(embed=embed)
        
        except Exception as e:
            embed = MusicUtils.create_music_embed(
                "❌ Грешка",
                f"Възникна грешка: {str(e)}",
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
            player.voice_client.stop()
            player.voice_client = None
            player.stop()
            player.clear_queue()
            
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

async def setup(bot):
    await bot.add_cog(Music(bot)) 