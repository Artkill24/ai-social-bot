# 🤖 Tech Curator AI

AI-powered system for automatically generating and publishing tech insights on social media.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Bluesky](https://img.shields.io/badge/Follow-@tech--curator--ai-blue)](https://bsky.app/profile/tech-curator-ai.bsky.social)

## 🌟 Features

- ✅ **Free AI Generation** - Uses Groq (Llama 3.1 70B) - completely free
- ✅ **Auto-posting** - Scheduled posts via GitHub Actions
- ✅ **Multi-platform** - Bluesky (LinkedIn coming soon)
- ✅ **Analytics** - SQLite database for tracking performance
- ✅ **Trending Topics** - Automatic detection from HackerNews, Reddit
- ✅ **Human Review** - All content can be reviewed before posting

## 🎯 What it Does

1. **Detects trending tech topics** from various sources
2. **Generates educational content** using AI
3. **Posts automatically** to Bluesky (and more platforms)
4. **Tracks performance** in local database

## 🛠️ Tech Stack

- **Python 3.11+**
- **Groq AI** (Llama 3.1 70B) - Free tier
- **Bluesky AT Protocol** - Open social network
- **SQLite** - Local analytics storage
- **GitHub Actions** - Free automation

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- Bluesky account
- Groq API key (free at console.groq.com)

### Installation
```bash
# Clone repository
git clone https://github.com/Artkill24/ai-social-bot.git
cd ai-social-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Add your credentials
```

### Configuration

Edit `.env` with your credentials:
```bash
GROQ_API_KEY=your_groq_key_here
BLUESKY_USERNAME=your-handle.bsky.social
BLUESKY_PASSWORD=your-app-password
```

**Get credentials:**
- Groq API Key: [console.groq.com](https://console.groq.com) (free)
- Bluesky account: [bsky.app](https://bsky.app)
- Bluesky App Password: Settings → Privacy → App Passwords

### Usage
```bash
# Run manually
python -m src.main

# Or use the wrapper
python run.py
```

## 📊 Project Structure
```
ai-social-bot/
├── src/
│   ├── content/
│   │   └── generator.py      # AI content generation
│   ├── platforms/
│   │   └── bluesky.py        # Bluesky integration
│   ├── utils/
│   │   └── database.py       # SQLite database
│   └── main.py               # Main entry point
├── data/
│   └── posts.db              # Analytics database
├── .github/
│   └── workflows/            # GitHub Actions (coming)
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md
```

## 💰 Cost Breakdown

**Monthly costs: $0-5** 🎉

- Groq AI: **FREE** (generous limits)
- Bluesky API: **FREE** (unlimited)
- GitHub Actions: **FREE** (2000 min/month)
- SQLite: **FREE**

Optional upgrades:
- Claude API: $3-40/month (better quality)
- LinkedIn API: Enterprise only

## 🌐 Follow the Bot

- **Bluesky**: [@tech-curator-ai.bsky.social](https://bsky.app/profile/tech-curator-ai.bsky.social)
- **GitHub**: [Artkill24/ai-social-bot](https://github.com/Artkill24/ai-social-bot)

## 📈 Roadmap

- [x] Basic content generation
- [x] Bluesky integration
- [x] Local database
- [ ] GitHub Actions automation
- [ ] LinkedIn integration
- [ ] Trending topics detection
- [ ] Analytics dashboard
- [ ] Web interface

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## ⚠️ Disclaimer

This is an automated bot. All content is AI-generated and human-reviewed. 
The bot clearly identifies itself as automated on its profile.

## 🙏 Acknowledgments

- **Groq** - For free AI inference
- **Bluesky** - For open social protocol
- **AT Protocol** - For decentralized social networking

---

Made with ❤️ in Italy 🇮🇹
