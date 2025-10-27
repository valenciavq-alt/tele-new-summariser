# 🤖 Telegram Message Summarizer Bot

[![Python](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Blue_Python_3.11%2B_Shield_Badge.svg/2560px-Blue_Python_3.11%2B_Shield_Badge.svg.png)
[![License](https://i.ytimg.com/vi/4cgpu9L2AE8/maxresdefault.jpg)
[![Telegram Bot API](https://i.ytimg.com/vi/6JulxW0koZ0/maxresdefault.jpg)

A smart Telegram bot that automatically summarizes group chat conversations using AI. Simply mention the bot in any group chat, and it will provide a concise bullet-point summary of recent messages!

## ✨ Features

- 🔍 **Smart Summarization**: Uses OpenAI's GPT models to create intelligent summaries
- 💬 **Group Chat Support**: Works seamlessly in any Telegram group
- 📝 **Bullet Point Format**: Easy-to-read summaries with key highlights
- ⚡ **Real-time Processing**: Get summaries instantly when you need them
- 🔒 **Privacy Focused**: Only processes messages when explicitly mentioned
- 🌍 **24/7 Availability**: Runs continuously on cloud platforms
- 👥 **Multi-Group Support**: Use the same bot across multiple groups
- ⚙️ **Customizable**: Adjust message limits and time ranges

## 🎯 Use Cases

- **Catch up on missed conversations** when you've been away
- **Review long discussions** to extract key points
- **Save time** by getting the gist without reading hundreds of messages
- **Meeting recaps** for team discussions
- **Community updates** in large groups

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telegram account
- OpenAI API key
- GitHub account (for deployment)
- Railway or Render account (free tier available)

### Installation

1. **Clone or download this repository**

2. **Follow the complete setup guide**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed, step-by-step instructions written for non-technical users.

### Quick Deploy

#### Deploy on Railway (Recommended)

[![Deploy on Railway](https://i.ytimg.com/vi/nIG9U7IXHHs/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLAbv213ZF9YFvw2SoBY3wSyz8Utlg)

1. Click the button above
2. Add your environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `BOT_USERNAME`
   - `OPENAI_API_KEY`
3. Deploy!

#### Deploy on Render

1. Fork this repository
2. Connect it to Render
3. Add environment variables
4. Deploy as a Background Worker

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed deployment guides.

## 📚 Usage

### Adding the Bot to a Group

1. Add the bot to your Telegram group
2. Make the bot an admin (so it can read messages)
3. Start chatting!

### Getting a Summary

There are multiple ways to trigger a summary:

**Method 1: Mention the bot**
```
@YourBotUsername what did I miss?
```

**Method 2: Use the command**
```
/summary
```

**Method 3: Reply with mention**
Reply to any message and mention the bot.

### Example Output

```
📝 Summary:
• Project deadline extended to next Friday
• Sarah will lead the design review meeting
• New feature deployment scheduled for Monday
• Bug fix for login issue is in progress
• Team lunch planned for Thursday at noon

📊 Summarized 48 messages from the last 24 hours.
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Your Telegram bot token from BotFather |
| `BOT_USERNAME` | Yes | - | Your bot's username (without @) |
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-3.5-turbo` | OpenAI model to use (`gpt-3.5-turbo` or `gpt-4`) |
| `MESSAGE_LIMIT` | No | `75` | Maximum number of messages to summarize |
| `MAX_MESSAGE_AGE_HOURS` | No | `24` | Only summarize messages within this timeframe |

### Customization

You can customize the bot's behavior by editing `bot.py`:

- **Summary style**: Modify the prompt in `generate_summary()`
- **Response format**: Change the summary template
- **Message filtering**: Adjust what messages are included

## 🏗️ Architecture

```
┌─────────────┐
│   Telegram  │
│    Group    │
└──────┬──────┘
       │ User mentions bot
       ▼
┌─────────────┐
│  Bot API    │
│  (Python)   │
└──────┬──────┘
       │ Fetches recent messages
       ▼
┌─────────────┐
│  Message    │
│   Store     │
└──────┬──────┘
       │ Formats & sends to AI
       ▼
┌─────────────┐
│  OpenAI API │
│  (GPT-3.5)  │
└──────┬──────┘
       │ Returns summary
       ▼
┌─────────────┐
│   Telegram  │
│   Response  │
└─────────────┘
```

## 💰 Cost Estimate

### Hosting
- **Railway**: Free tier includes $5 credit/month (sufficient for most users)
- **Render**: Free tier includes 750 hours/month (24/7 operation)

### OpenAI API
- **GPT-3.5-turbo**: ~$0.002-0.005 per summary
  - 100 summaries ≈ $0.20-0.50
  - 1000 summaries ≈ $2-5
- **GPT-4**: ~$0.03-0.06 per summary (higher quality, more expensive)

**Total Monthly Cost**: $0-10 for typical usage (small-medium groups)

## 🔒 Privacy & Security

- **No persistent storage**: Messages are not stored in a database
- **In-memory only**: Last 100 messages kept in memory for quick access
- **On-demand processing**: Only processes messages when explicitly mentioned
- **OpenAI data policy**: Review [OpenAI's data usage policy](https://openai.com/policies/api-data-usage-policies)
- **Secure credentials**: All tokens and API keys stored as environment variables

⚠️ **Important**: Messages are sent to OpenAI's API for summarization. Consider this before using in sensitive conversations.

## 🛠️ Development

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-summarizer-bot.git
cd telegram-summarizer-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run the bot:
```bash
python bot.py
```

### Project Structure

```
telegram-summarizer-bot/
├── bot.py                    # Main bot application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── Procfile                 # Railway/Heroku deployment
├── railway.json             # Railway configuration
├── render.yaml              # Render configuration
├── runtime.txt              # Python version specification
├── README.md                # This file
└── SETUP_INSTRUCTIONS.md    # Detailed setup guide
```

## 📝 Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message and instructions |
| `/help` | Display help information |
| `/summary` | Get a summary of recent messages |

## 🐛 Troubleshooting

### Bot doesn't respond
- Verify bot privacy settings are disabled in BotFather
- Check if bot is an admin in the group
- Review deployment logs for errors

### "No messages available"
- Bot can only see messages after it was added to the group
- Wait for more conversation, then try again

### OpenAI errors
- Check your API key is valid
- Verify you have credits in your OpenAI account
- Check rate limits haven't been exceeded

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed troubleshooting.

## 🔄 Updates & Maintenance

### Updating the Bot

1. Make changes to your code
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update bot features"
git push
```
3. Railway/Render will automatically redeploy

### Monitoring

- Check deployment logs regularly
- Monitor OpenAI usage on their dashboard
- Track Railway/Render usage to stay within free tier

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [OpenAI](https://openai.com/) - AI-powered summarization
- [Railway](https://railway.app/) - Easy cloud deployment
- [Render](https://render.com/) - Alternative cloud hosting

## 📧 Support

- **Setup Issues**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- **Bugs**: Open an issue on GitHub
- **Questions**: Check the FAQ in SETUP_INSTRUCTIONS.md

## 🗺️ Roadmap

Future improvements planned:

- [ ] Support for multiple languages
- [ ] Custom summary templates
- [ ] Analytics dashboard
- [ ] Message sentiment analysis
- [ ] Export summaries to PDF
- [ ] Integration with other chat platforms
- [ ] Database support for better message history

## ⭐ Show Your Support

If you find this bot useful, please consider:
- Giving it a star on GitHub ⭐
- Sharing it with others who might benefit
- Contributing improvements
- Reporting bugs or suggesting features

---

**Made with ❤️ for the Telegram community**

*Happy Summarizing! 🚀*
