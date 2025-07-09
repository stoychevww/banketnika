import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Banketnika Discord Bot"""
    
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Music settings
    MAX_QUEUE_SIZE = 100
    MAX_SONG_LENGTH = 3600  # 1 hour in seconds
    DEFAULT_VOLUME = 0.5  # 50%
    MAX_VOLUME = 100  # Maximum volume percentage
    
    # Bot settings
    BOT_NAME = "Banketnika"
    BOT_DESCRIPTION = "Advanced Bulgarian Music Bot for Discord - Bringing the banket spirit to your server!"
    BOT_VERSION = "1.0.0"
    
    # Colors for embeds (Bulgarian flag colors)
    COLOR_PRIMARY = 0x00966E  # Green
    COLOR_SECONDARY = 0xD62612  # Red
    COLOR_SUCCESS = 0x00FF00
    COLOR_ERROR = 0xFF0000
    COLOR_WARNING = 0xFFFF00
    
    # Bulgarian banket phrases
    BANKET_PHRASES = [
        "Наздраве! 🍻",
        "Да живее българската музика! 🎵",
        "За здраве и щастие! 🥂",
        "Банкет като хората! 🎉",
        "Имаме богата банкетна култура! 🎶",
        "Живо и здраво! 🎊"
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required! Please set it in your .env file")
        
        return True 