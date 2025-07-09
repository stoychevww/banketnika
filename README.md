# 🎵 Banketnika - Advanced Bulgarian Discord Music Bot

**Banketnika** is a professional Discord music bot that brings the spirit of Bulgarian "banket" culture to your Discord server. Built with love for the Bulgarian community, this bot offers advanced music features while celebrating our rich cultural heritage.

## 🇧🇬 About Bulgarian Banket Culture

The "banket" (банкет) is a traditional Bulgarian celebratory feast where music plays a central role. It's a time when families and friends gather to share food, stories, and most importantly, music. Banketnika brings this warm, communal spirit to your Discord server, making every music session feel like a true Bulgarian celebration.

## ✨ Features

### 🎶 Advanced Music Playback
- **High-quality audio streaming** from YouTube
- **Queue management** with up to 100 songs
- **Seamless playback** with automatic song progression
- **Multiple audio sources** supported
- **Smart error handling** for uninterrupted experience

### 🎵 Music Controls
- **Play/Pause/Stop** - Full playback control
- **Skip songs** - Move to next track instantly  
- **Repeat mode** - Loop your favorite songs
- **Shuffle queue** - Randomize your playlist
- **Volume control** - Perfect audio levels
- **Now playing** - See current track info

### 🇧🇬 Bulgarian Cultural Features
- **Bilingual support** - Commands in Bulgarian and English
- **Cultural phrases** - Authentic Bulgarian expressions
- **Banket mode** - Special Bulgarian folk music selection
- **Nazdrave command** - Traditional Bulgarian toasts
- **Bulgarian flag colors** - Authentic visual design

### 🔧 Professional Features
- **Multi-server support** - Works across all your servers
- **Auto-disconnect** - Leaves when alone in voice channels
- **Error handling** - Graceful error management
- **Logging system** - Comprehensive activity logs
- **Permission management** - Secure command execution

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed on your system
- Discord Bot Token
- Basic knowledge of Discord bot setup

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/banketnika.git
   cd banketnika
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup FFmpeg**
   
   **Windows:**
   - Download FFmpeg from https://ffmpeg.org/download.html
   - Add FFmpeg to your system PATH
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```

4. **Configure the bot**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your bot token:
   ```env
   BOT_TOKEN=your_discord_bot_token_here
   BOT_PREFIX=!
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

### Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token and paste it in your `.env` file
5. Go to "OAuth2" → "URL Generator"
6. Select scopes: `bot`, `applications.commands`
7. Select permissions: `Connect`, `Speak`, `Use Voice Activity`, `Send Messages`, `Embed Links`, `Read Message History`, `Add Reactions`
8. Use the generated URL to invite the bot to your server

## 🎵 Commands

### Music Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `!play <song>` | `!p`, `!свири`, `!пусни` | Play a song or add to queue |
| `!pause` | `!пауза` | Pause current song |
| `!resume` | `!продължи` | Resume paused song |
| `!skip` | `!прескочи`, `!next` | Skip current song |
| `!stop` | `!спри` | Stop music and clear queue |
| `!queue` | `!q`, `!опашка` | Show current queue |
| `!nowplaying` | `!np`, `!сега` | Show currently playing song |
| `!shuffle` | `!разбъркай` | Shuffle the queue |
| `!clear` | `!изчисти` | Clear the queue |
| `!repeat` | `!повтори` | Toggle repeat mode |
| `!disconnect` | `!dc`, `!напусни` | Disconnect from voice channel |

### Special Bulgarian Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `!banket` | `!банкет` | Play random Bulgarian folk music |
| `!nazdrave` | `!наздраве`, `!cheers` | Bulgarian toast/cheers |
| `!help` | `!помощ`, `!команди` | Show help information |
| `!info` | `!информация`, `!about` | Bot information |
| `!invite` | `!покани` | Get bot invite link |

## 🎭 Example Usage

```
# Play a song
!play Despacito

# Use Bulgarian commands
!свири Калинка
!пауза
!продължи

# Special banket mode
!banket
# Bot will play random Bulgarian folk music

# Traditional Bulgarian toast
!nazdrave
# Bot responds with traditional Bulgarian cheers
```

## 📁 Project Structure

```
banketnika/
├── bot.py                 # Main bot file
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── cogs/
│   ├── music.py         # Music functionality
│   └── general.py       # General commands
└── utils/
    └── music_utils.py   # Music utility functions
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | Yes | - | Discord bot token |
| `BOT_PREFIX` | No | `!` | Command prefix |
| `MAX_QUEUE_SIZE` | No | `100` | Maximum songs in queue |
| `MAX_SONG_LENGTH` | No | `600` | Maximum song length (seconds) |
| `DEFAULT_VOLUME` | No | `0.5` | Default audio volume |

### Advanced Configuration

You can modify `config.py` to customize:
- Bot colors and themes
- Bulgarian phrases and messages
- Audio quality settings
- Logging preferences

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check if bot has proper permissions
- Verify bot token is correct
- Ensure bot is online and in your server

**Audio quality issues:**
- Install/update FFmpeg
- Check your internet connection
- Verify Discord voice permissions

**Bot leaves voice channel:**
- This is normal behavior when alone
- Bot auto-disconnects to save resources
- Rejoin voice channel to continue

**Commands in Bulgarian don't work:**
- Ensure proper Unicode support
- Check your Discord client language settings
- Try English alternatives

### Getting Help

1. Check the console output for error messages
2. Review the `banketnika.log` file
3. Ensure all dependencies are installed
4. Verify Discord permissions are correct

## 🤝 Contributing

We welcome contributions from the Bulgarian community and beyond! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Areas for Contribution
- Additional Bulgarian folk songs in banket mode
- More cultural phrases and expressions
- Performance optimizations
- Additional music sources
- Translation improvements
- Bug fixes and testing

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bulgarian folk music tradition** - Inspiration for this project
- **Discord.py community** - Excellent library and support
- **YouTube-dl contributors** - Audio extraction capabilities
- **Bulgarian Discord communities** - Testing and feedback

## 🎉 Support the Project

If you enjoy Banketnika, please:
- ⭐ Star this repository
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 🇧🇬 Share with Bulgarian Discord communities
- 🤝 Contribute code or translations

---

**Наздраве! 🍻** - Made with ❤️ for the Bulgarian community

*Banketnika - Bringing the spirit of Bulgarian banket culture to Discord servers worldwide!* 