import discord
from discord.ext import commands
from typing import Optional, Dict, Any
from utils.music_utils import MusicUtils
from config import Config

class MusicButtonHandler(discord.ui.View):
    """Handle Discord button interactions for music controls"""
    
    def __init__(self, bot, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.bot = bot
    
    def get_player(self, guild_id: int):
        """Get the music player for the guild"""
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            return music_cog.get_player(guild_id)
        return None
    
    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        emoji="⏯️",
        label="Play/Pause",
        custom_id="music_play_pause"
    )
    async def play_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle play/pause button"""
        await interaction.response.defer()
        
        if not interaction.guild_id:
            await interaction.followup.send("❌ Тази команда работи само в сървър", ephemeral=True)
            return
        
        player = self.get_player(interaction.guild_id)
        if not player:
            await interaction.followup.send("❌ Няма активен плейър", ephemeral=True)
            return
        
        if not player.is_playing:
            embed = MusicUtils.create_music_embed(
                "❌ Няма музика",
                "В момента не свири музика",
                Config.COLOR_ERROR
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if player.is_paused:
            player.resume()
            embed = MusicUtils.create_music_embed(
                "▶️ Продължаване",
                "Музиката продължава",
                Config.COLOR_SUCCESS
            )
        else:
            player.pause()
            embed = MusicUtils.create_music_embed(
                "⏸️ Пауза",
                "Музиката е паузирана",
                Config.COLOR_WARNING
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        style=discord.ButtonStyle.secondary,
        emoji="⏭️",
        label="Skip",
        custom_id="music_skip"
    )
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle skip button"""
        await interaction.response.defer()
        
        if not interaction.guild_id:
            await interaction.followup.send("❌ Тази команда работи само в сървър", ephemeral=True)
            return
        
        player = self.get_player(interaction.guild_id)
        if not player:
            await interaction.followup.send("❌ Няма активен плейър", ephemeral=True)
            return
        
        if not player.is_playing:
            embed = MusicUtils.create_music_embed(
                "❌ Няма музика",
                "В момента не свири музика",
                Config.COLOR_ERROR
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        player.skip()
        embed = MusicUtils.create_music_embed(
            "⏭️ Прескочена",
            "Песента беше прескочена",
            Config.COLOR_SUCCESS
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        style=discord.ButtonStyle.danger,
        emoji="⏹️",
        label="Stop",
        custom_id="music_stop"
    )
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle stop button"""
        await interaction.response.defer()
        
        if not interaction.guild_id:
            await interaction.followup.send("❌ Тази команда работи само в сървър", ephemeral=True)
            return
        
        player = self.get_player(interaction.guild_id)
        if not player:
            await interaction.followup.send("❌ Няма активен плейър", ephemeral=True)
            return
        
        player.stop()
        player.clear_queue()
        
        embed = MusicUtils.create_music_embed(
            "⏹️ Спряна",
            "Музиката е спряна и опашката е изчистена",
            Config.COLOR_SUCCESS
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        style=discord.ButtonStyle.secondary,
        emoji="📋",
        label="Queue",
        custom_id="music_queue"
    )
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle queue button"""
        await interaction.response.defer()
        
        if not interaction.guild_id:
            await interaction.followup.send("❌ Тази команда работи само в сървър", ephemeral=True)
            return
        
        player = self.get_player(interaction.guild_id)
        if not player:
            await interaction.followup.send("❌ Няма активен плейър", ephemeral=True)
            return
        
        embed = MusicUtils.create_queue_embed(list(player.queue), player.current_song)
        view = MusicButtonHandler(self.bot)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(
        style=discord.ButtonStyle.secondary,
        emoji="🔀",
        label="Shuffle",
        custom_id="music_shuffle"
    )
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle shuffle button"""
        await interaction.response.defer()
        
        if not interaction.guild_id:
            await interaction.followup.send("❌ Тази команда работи само в сървър", ephemeral=True)
            return
        
        player = self.get_player(interaction.guild_id)
        if not player:
            await interaction.followup.send("❌ Няма активен плейър", ephemeral=True)
            return
        
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
        
        await interaction.followup.send(embed=embed, ephemeral=True) 