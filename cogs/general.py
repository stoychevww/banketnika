import discord
from discord.ext import commands
import random
import time
from config import Config
from utils.music_utils import MusicUtils

class General(commands.Cog):
    """General commands for Banketnika Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.command(name='help', aliases=['помощ', 'команди'])
    async def help_command(self, ctx, command_name: str = None):
        """Show help information"""
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name)
            if command:
                embed = MusicUtils.create_music_embed(
                    f"📖 Помощ за {command.name}",
                    f"**Описание:** {command.help or 'Няма описание'}\n"
                    f"**Използване:** `{Config.BOT_PREFIX}{command.name} {command.signature}`\n"
                    f"**Алтернативи:** {', '.join(command.aliases) if command.aliases else 'Няма'}"
                )
            else:
                embed = MusicUtils.create_music_embed(
                    "❌ Команда не е намерена",
                    f"Командата `{command_name}` не съществува",
                    Config.COLOR_ERROR
                )
        else:
            # Show general help
            embed = discord.Embed(
                title="🎵 Banketnika - Помощ",
                description=f"Добре дошли в {Config.BOT_NAME}! Ето всички команди:",
                color=Config.COLOR_PRIMARY
            )
            
            # Music commands
            music_commands = [
                f"`{Config.BOT_PREFIX}play <песен>` - Пусни песен",
                f"`{Config.BOT_PREFIX}pause` - Пауза",
                f"`{Config.BOT_PREFIX}resume` - Продължи",
                f"`{Config.BOT_PREFIX}skip` - Прескочи",
                f"`{Config.BOT_PREFIX}stop` - Спри",
                f"`{Config.BOT_PREFIX}queue` - Покажи опашката",
                f"`{Config.BOT_PREFIX}nowplaying` - Текуща песен",
                f"`{Config.BOT_PREFIX}shuffle` - Разбъркай опашката",
                f"`{Config.BOT_PREFIX}clear` - Изчисти опашката",
                f"`{Config.BOT_PREFIX}repeat` - Повтори песента",
                f"`{Config.BOT_PREFIX}disconnect` - Напусни канала"
            ]
            
            embed.add_field(
                name="🎶 Музикални команди",
                value="\n".join(music_commands),
                inline=False
            )
            
            # Special commands
            special_commands = [
                f"`{Config.BOT_PREFIX}banket` - Банкет режим!",
                f"`{Config.BOT_PREFIX}nazdrave` - Наздраве!",
                f"`{Config.BOT_PREFIX}info` - Информация за бота"
            ]
            
            embed.add_field(
                name="🎉 Специални команди",
                value="\n".join(special_commands),
                inline=False
            )
            
            embed.add_field(
                name="🔗 Полезни връзки",
                value="• Използвай български или английски команди\n"
                      "• Добави бота в твоя сървър\n"
                      "• Поддръжка: GitHub Issues",
                inline=False
            )
            
            embed.set_footer(text=f"{Config.BOT_NAME} • {MusicUtils.get_random_banket_phrase()}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='info', aliases=['информация', 'about'])
    async def info(self, ctx):
        """Show bot information"""
        uptime = int(time.time() - self.start_time)
        uptime_str = MusicUtils.format_duration(uptime)
        
        embed = discord.Embed(
            title=f"🎵 {Config.BOT_NAME}",
            description=Config.BOT_DESCRIPTION,
            color=Config.COLOR_PRIMARY
        )
        
        embed.add_field(
            name="📊 Статистики",
            value=f"**Сървъри:** {len(self.bot.guilds)}\n"
                  f"**Потребители:** {len(self.bot.users)}\n"
                  f"**Време онлайн:** {uptime_str}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Технически детайли",
            value=f"**Версия:** {Config.BOT_VERSION}\n"
                  f"**Discord.py:** {discord.__version__}\n"
                  f"**Префикс:** `{Config.BOT_PREFIX}`",
            inline=True
        )
        
        embed.add_field(
            name="🇧🇬 За българската култура",
            value="Банкетът е традиционна българска празнична трапеза, "
                  "където музиката играе централна роля. Този бот носи "
                  "духа на българския банкет във вашия Discord сървър!",
            inline=False
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Направен с ❤️ за българската общност • {MusicUtils.get_random_banket_phrase()}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='nazdrave', aliases=['наздраве', 'cheers'])
    async def nazdrave(self, ctx):
        """Nazdrave command - Bulgarian cheers!"""
        cheers_messages = [
            "🍻 Наздраве! За добро здраве и весели банкети!",
            "🥂 Наздраве! Да живеем дълго и щастливо!",
            "🍷 Наздраве! За приятелството и музиката!",
            "🎉 Наздраве! За всички хубави моменти!",
            "🍺 Наздраве! Да се веселим като хората!",
            "🥳 Наздраве! За любовта и радостта!"
        ]
        
        message = random.choice(cheers_messages)
        
        embed = MusicUtils.create_music_embed(
            "🎊 Наздраве!",
            message,
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Show bot latency"""
        latency = round(self.bot.latency * 1000)
        
        embed = MusicUtils.create_music_embed(
            "🏓 Pong!",
            f"Латентност: {latency}ms"
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='invite', aliases=['покани'])
    async def invite(self, ctx):
        """Get bot invite link"""
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(
                connect=True,
                speak=True,
                use_voice_activation=True,
                send_messages=True,
                embed_links=True,
                read_message_history=True,
                add_reactions=True
            )
        )
        
        embed = MusicUtils.create_music_embed(
            "🔗 Покани Banketnika",
            f"Искаш да добавиш {Config.BOT_NAME} в твоя сървър?\n"
            f"[Кликни тук за покана]({invite_url})",
            Config.COLOR_SUCCESS
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event when bot is ready"""
        print(f"{Config.BOT_NAME} is ready!")
        print(f"Connected to {len(self.bot.guilds)} servers")
        print(f"Serving {len(self.bot.users)} users")
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"музика | {Config.BOT_PREFIX}help"
        )
        await self.bot.change_presence(activity=activity)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Event when bot joins a guild"""
        print(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Try to send welcome message
        if guild.system_channel:
            embed = MusicUtils.create_music_embed(
                f"🎉 Здравейте от {Config.BOT_NAME}!",
                f"Благодаря, че ме поканихте в **{guild.name}**!\n\n"
                f"Използвайте `{Config.BOT_PREFIX}help` за да видите всички команди.\n"
                f"Започнете с `{Config.BOT_PREFIX}play <песен>` за да пуснете музика!\n\n"
                f"{MusicUtils.get_random_banket_phrase()}",
                Config.COLOR_SUCCESS
            )
            
            try:
                await guild.system_channel.send(embed=embed)
            except:
                pass  # Ignore if can't send message

async def setup(bot):
    await bot.add_cog(General(bot)) 