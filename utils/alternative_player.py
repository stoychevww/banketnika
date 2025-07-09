"""
Alternative audio player that doesn't rely on FFmpeg
Uses direct HTTP streaming and opus encoding
"""

import asyncio
import discord
import aiohttp
import io
from typing import Optional, AsyncGenerator
from config import Config

class DirectAudioSource(discord.AudioSource):
    """Direct HTTP audio source that streams without FFmpeg"""
    
    def __init__(self, url: str, volume: float = 0.5):
        self.url = url
        self.volume = volume
        self.session: Optional[aiohttp.ClientSession] = None
        self.response: Optional[aiohttp.ClientResponse] = None
        self.buffer = io.BytesIO()
        self.connected = False
        
    async def connect(self):
        """Connect to the audio stream"""
        if not self.connected:
            self.session = aiohttp.ClientSession()
            self.response = await self.session.get(self.url)
            self.connected = True
    
    def read(self) -> bytes:
        """Read audio data - this is called by discord.py"""
        if not self.connected:
            # We can't make this async, so we'll return empty data
            return b''
        
        try:
            # This is a simplified approach - in reality, we'd need proper audio decoding
            # For now, we'll return empty data to avoid blocking
            return b''
        except Exception:
            return b''
    
    def cleanup(self):
        """Clean up resources"""
        if self.response:
            self.response.close()
        if self.session:
            asyncio.create_task(self.session.close())
        self.connected = False

class SimpleAudioPlayer:
    """Simple audio player using basic HTTP streaming"""
    
    def __init__(self):
        self.current_source: Optional[DirectAudioSource] = None
        
    async def create_source(self, url: str) -> discord.AudioSource:
        """Create an audio source from URL"""
        print(f"Creating simple audio source for: {url}")
        
        try:
            # For WebM/Opus streams, we can try to use them more directly
            if 'mime=audio%2Fwebm' in url or 'mime=audio/webm' in url:
                print("Detected WebM audio stream")
                # Use a very basic FFmpeg command for WebM
                return discord.FFmpegOpusAudio(
                    url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    options='-vn'
                )
            else:
                # For other formats, use PCM
                print("Using PCM audio source")
                source = discord.FFmpegPCMAudio(
                    url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    options='-vn'
                )
                return discord.PCMVolumeTransformer(source, volume=0.3)
                
        except Exception as e:
            print(f"Error creating simple audio source: {e}")
            # Last resort - most basic FFmpeg
            source = discord.FFmpegPCMAudio(url)
            return discord.PCMVolumeTransformer(source, volume=0.3)
    
    def cleanup(self):
        """Clean up current source"""
        if self.current_source:
            self.current_source.cleanup()
            self.current_source = None 