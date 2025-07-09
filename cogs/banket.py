import discord
from discord.ext import commands
import random
import asyncio
from config import Config
from utils.music_utils import MusicUtils

class BanketCog(commands.Cog):
    """Special Bulgarian Banket Features"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Traditional Bulgarian folk songs
        self.bulgarian_folk_songs = [
            "Калинка",
            "Тих бял Дунав",
            "Малка мома",
            "Дилмано Дилберо",
            "Българско хоро",
            "Мила родино",
            "Дунавско хоро",
            "Ой, Марийке",
            "Излел е Делю хайдутин",
            "Радка пита млада невеста",
            "Севдалинка",
            "Хоро на Нестинарките",
            "Белите рози",
            "Тракийско хоро",
            "Шопско хоро",
            "Българче",
            "Дунавска лястовица",
            "Седнало е Джоре дос",
            "Полегнала е Тодора",
            "Кога си тръгнах от Пирина"
        ]
        
        # Traditional Bulgarian toasts
        self.bulgarian_toasts = [
            "Наздраве! За здраве и щастие!",
            "Наздраве! За дългия живот!",
            "Наздраве! За приятелството!",
            "Наздраве! За любовта!",
            "Наздраве! За семейството!",
            "Наздраве! За България!",
            "Наздраве! За хубавите моменти!",
            "Наздраве! За успехите!",
            "Наздраве! За мечтите!",
            "Наздраве! За младостта!"
        ]
        
        # Bulgarian banket expressions
        self.banket_expressions = [
            "Да се веселим като хората!",
            "Банкет като хората!",
            "Весело и здраво!",
            "Да живеем дълго и щастливо!",
            "Музиката е душата на банкета!",
            "За здраве и радост!",
            "Да пеем и да играем!",
            "Банкетът продължава!",
            "Хубаво настроение на всички!",
            "Да се радваме на живота!"
        ]
        
        # Famous Bulgarian musicians/bands
        self.bulgarian_artists = [
            "Валя Балканска",
            "Гуна Иванова",
            "Стефан Димитров",
            "Бисер Киров",
            "Филип Кутев",
            "Мистерия",
            "Слави Трифонов",
            "Лили Иванова",
            "Камелия",
            "Азис",
            "Преслава",
            "Андреа",
            "Цветелина Янева",
            "Емилия",
            "Глория",
            "Софи Маринова"
        ]
    
    @commands.command(name='folksong', aliases=['народна'])
    async def folksong(self, ctx):
        """Play a random Bulgarian folk song"""
        song = random.choice(self.bulgarian_folk_songs)
        
        embed = MusicUtils.create_music_embed(
            "🎵 Българска народна песен",
            f"Пускам: **{song}**\n\n{random.choice(self.banket_expressions)}",
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
        
        # Try to play the song
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            await music_cog.play(ctx, query=f"{song} българска народна песен")
    
    @commands.command(name='toast', aliases=['тост'])
    async def toast(self, ctx, *, message: str = None):
        """Make a Bulgarian toast"""
        if message:
            toast_message = f"🥂 {message}\n\n{random.choice(self.bulgarian_toasts)}"
        else:
            toast_message = random.choice(self.bulgarian_toasts)
        
        embed = MusicUtils.create_music_embed(
            "🍻 Българска здравица",
            toast_message,
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
        
        # Add reactions
        await ctx.message.add_reaction("🍻")
        await ctx.message.add_reaction("🥂")
        await ctx.message.add_reaction("🎉")
    
    @commands.command(name='horo', aliases=['хоро'])
    async def horo(self, ctx):
        """Start a horo (Bulgarian circle dance) session"""
        horo_songs = [
            "Дунавско хоро",
            "Тракийско хоро", 
            "Шопско хоро",
            "Българско хоро",
            "Хоро на Нестинарките",
            "Пайдушко хоро",
            "Елено моме",
            "Ръченица"
        ]
        
        song = random.choice(horo_songs)
        
        embed = MusicUtils.create_music_embed(
            "💃 Време за хоро!",
            f"Пускам: **{song}**\n\n"
            f"🕺 Хванете се за ръце и започваме хоро!\n"
            f"💃 Дясна нога напред, лява нога встрани!\n"
            f"🎶 {random.choice(self.banket_expressions)}",
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
        
        # Add dance reactions
        await ctx.message.add_reaction("💃")
        await ctx.message.add_reaction("🕺")
        await ctx.message.add_reaction("🎶")
        
        # Try to play the horo
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            await music_cog.play(ctx, query=f"{song} българско хоро")
    
    @commands.command(name='artist', aliases=['изпълнител'])
    async def artist(self, ctx, *, artist_name: str = None):
        """Play songs from a Bulgarian artist"""
        if not artist_name:
            artist_name = random.choice(self.bulgarian_artists)
        
        embed = MusicUtils.create_music_embed(
            "🎤 Български изпълнител",
            f"Търся песни от: **{artist_name}**\n\n"
            f"🇧🇬 Подкрепяме българската музика!\n"
            f"{random.choice(self.banket_expressions)}",
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
        
        # Try to play artist's songs
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            await music_cog.play(ctx, query=f"{artist_name} български песни")
    
    @commands.command(name='banketmix', aliases=['банкетмикс'])
    async def banket_mix(self, ctx):
        """Create a banket mix with multiple Bulgarian songs"""
        if not await self._ensure_voice_connection(ctx):
            return
        
        # Select 5 random songs for the mix
        selected_songs = random.sample(self.bulgarian_folk_songs, min(5, len(self.bulgarian_folk_songs)))
        
        embed = MusicUtils.create_music_embed(
            "🎉 Банкет микс!",
            f"Добавям {len(selected_songs)} български песни в опашката:\n\n" +
            "\n".join([f"🎵 {song}" for song in selected_songs]) +
            f"\n\n{random.choice(self.banket_expressions)}",
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
        
        # Add all songs to queue
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            for song in selected_songs:
                try:
                    await music_cog.play(ctx, query=f"{song} българска народна песен")
                    await asyncio.sleep(1)  # Small delay between requests
                except Exception as e:
                    print(f"Error adding song {song}: {e}")
    
    @commands.command(name='tradition', aliases=['традиция'])
    async def tradition(self, ctx):
        """Share Bulgarian banket traditions"""
        traditions = [
            {
                "title": "🍞 Чупене на хляба",
                "description": "Домакинът чупи хляба и го дава на гостите като символ на гостоприемство."
            },
            {
                "title": "🍷 Първата чаша",
                "description": "Първата чаша винце се пие за здравето на домакините."
            },
            {
                "title": "🎵 Песните на банкета",
                "description": "Народните песни се пеят всички заедно, създавайки единство."
            },
            {
                "title": "💃 Хорото",
                "description": "Българското хоро се играе в кръг, символизирайки единството."
            },
            {
                "title": "🥂 Здравиците",
                "description": "Здравиците се казват с уважение и искреност за всички присъстващи."
            },
            {
                "title": "🎶 Музиката",
                "description": "Музиката е сърцето на банкета - без нея няма истински празник."
            }
        ]
        
        tradition = random.choice(traditions)
        
        embed = MusicUtils.create_music_embed(
            "🇧🇬 Българска традиция",
            f"**{tradition['title']}**\n\n{tradition['description']}\n\n"
            f"*{random.choice(self.banket_expressions)}*",
            Config.COLOR_SECONDARY
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='cheers', aliases=['чукане'])
    async def cheers(self, ctx):
        """Interactive cheers command"""
        embed = MusicUtils.create_music_embed(
            "🥂 Време за здравица!",
            "Кой иска да чукне с мен?\n\n"
            "Реагирайте с 🍻 за да се присъедините!",
            Config.COLOR_SECONDARY
        )
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("🍻")
        
        # Wait for reactions
        def check(reaction, user):
            return reaction.message.id == message.id and str(reaction.emoji) == "🍻" and not user.bot
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # Update embed with cheers
            new_embed = MusicUtils.create_music_embed(
                "🍻 Наздраве!",
                f"{user.mention} чукна с мен!\n\n"
                f"{random.choice(self.bulgarian_toasts)}\n\n"
                f"*{random.choice(self.banket_expressions)}*",
                Config.COLOR_SUCCESS
            )
            
            await message.edit(embed=new_embed)
            
        except asyncio.TimeoutError:
            timeout_embed = MusicUtils.create_music_embed(
                "😔 Няма чукане",
                "Никой не иска да чукне... Но пак наздраве! 🍻",
                Config.COLOR_WARNING
            )
            await message.edit(embed=timeout_embed)
    
    async def _ensure_voice_connection(self, ctx) -> bool:
        """Ensure bot is connected to voice channel"""
        if not ctx.author.voice:
            embed = MusicUtils.create_music_embed(
                "❌ Грешка",
                "Трябва да сте в гласов канал за да използвате тази команда!",
                Config.COLOR_ERROR
            )
            await ctx.send(embed=embed)
            return False
        return True
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for banket-related messages"""
        if message.author.bot:
            return
        
        # Respond to banket-related keywords
        banket_keywords = ['банкет', 'banket', 'наздраве', 'nazdrave', 'хоро', 'horo']
        
        content = message.content.lower()
        for keyword in banket_keywords:
            if keyword in content and not content.startswith(Config.BOT_PREFIX):
                # Random chance to respond (20%)
                if random.random() < 0.2:
                    response = random.choice(self.banket_expressions)
                    await message.add_reaction("🍻")
                    await message.channel.send(f"🎉 {response}")
                break

async def setup(bot):
    await bot.add_cog(BanketCog(bot)) 