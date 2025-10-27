# 🤖 Telegram Message Summarizer Bot

[![Python](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Blue_Python_3.11%2B_Shield_Badge.svg/2560px-Blue_Python_3.11%2B_Shield_Badge.svg.png)
[![License](https://i.ytimg.com/vi/4cgpu9L2AE8/maxresdefault.jpg)
[![Telegram Bot API](https://i.ytimg.com/vi/6JulxW0koZ0/maxresdefault.jpg)

A smart Telegram bot that automatically summarizes conversations using AI in **both group chats and private/individual chats**. Simply mention the bot in a group chat or use the `/summarize` command, and it will provide a concise bullet-point summary of recent messages!

> **🎉 NEW:** The bot now works in both **group chats** and **private/individual chats**! Use `/summarize` in any conversation to get an instant summary.

## ✨ Features

- 🔍 **Smart Summarization**: Uses Anthropic's Claude models to create intelligent summaries
- 💬 **Dual Chat Support**: Works seamlessly in both group chats AND private/individual chats
- 📝 **Bullet Point Format**: Easy-to-read summaries with key highlights
- ⚡ **Real-time Processing**: Get summaries instantly when you need them
- 🗄️ **PostgreSQL Database Support**: Store unlimited message history (optional, with fallback to in-memory)
- 📅 **Custom Timeframe Filtering**: Summarize messages from specific time periods
  - Relative timeframes: "last 2 hours", "today", "yesterday"
  - Shorthand syntax: "60d", "2mo", "3w", "24h" ⭐ **NEW**
  - Absolute date ranges: "from 2024-01-15 to 2024-01-20", "on 2024-01-15"
- 💰 **Budget Protection & Cost Tracking**: Built-in monthly budget enforcement with automatic tracking
  - Set budget limits to prevent unexpected charges
  - Real-time usage monitoring with `/usage` command
  - Automatic alerts at 50%, 75%, and 90% of budget
  - Monthly auto-reset on the 1st of each month
- 🛡️ **Smart Safeguards** ⭐ **NEW**: Comprehensive protection against unexpected costs
  - **Hard Message Limits**: Maximum 1,000 messages per request
  - **Smart Sampling**: Intelligent message selection for large datasets
  - **Cost Estimation**: Pre-request cost warnings (warns if >$0.50)
  - **Database Checks**: Warnings for long timeframes without persistent storage
- 🔒 **Privacy Focused**: Only processes messages when explicitly requested
- 🌍 **24/7 Availability**: Runs continuously on cloud platforms
- 👥 **Multi-Chat Support**: Use the same bot across multiple groups and private conversations
- ⚙️ **Customizable**: Adjust message limits and time ranges with optional parameters

## 🎯 Use Cases

- **Catch up on missed conversations** when you've been away (both groups and private chats)
- **Review long discussions** to extract key points
- **Save time** by getting the gist without reading hundreds of messages
- **Meeting recaps** for team discussions in group chats
- **Community updates** in large groups
- **Personal chat summaries** for lengthy one-on-one conversations
- **Study group discussions** in both group and private settings

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telegram account
- Anthropic API key
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
   - `ANTHROPIC_API_KEY`
3. Deploy!

#### Deploy on Render

1. Fork this repository
2. Connect it to Render
3. Add environment variables
4. Deploy as a Background Worker

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed deployment guides.

## 📚 Usage

### Using in Group Chats

1. Add the bot to your Telegram group
2. Make the bot an admin (so it can read messages)
3. Start chatting!

**To get a summary in group chats:**

**Method 1: Mention the bot**
```
@YourBotUsername what did I miss?
```

**Method 2: Use the command**
```
/summarize
```
or
```
/summary
```

**Method 3: Use command with custom message count**
```
/summarize 50
```
This will summarize the last 50 messages instead of the default.

**Method 4: Use command with shorthand timeframes** ⭐ **NEW**
```
/summarize 24h
/summarize 60d
/summarize 2mo
/summarize 3w
```

**Method 5: Use command with natural language timeframes**
```
/summarize today
/summarize yesterday
/summarize last 2 hours
/summarize last 3 days
/summarize from 2024-01-15 to 2024-01-20
/summarize on 2024-01-15
```

**Method 6: Reply with mention**
Reply to any message and mention the bot.

---

### Using in Private/Individual Chats

1. Start a private chat with the bot
2. Send some messages in your conversation
3. Use the `/summarize` command to get a summary

**To get a summary in private chats:**

**Method 1: Use the command**
```
/summarize
```
or
```
/summary
```

**Method 2: Use command with custom message count**
```
/summarize 30
```
This will summarize the last 30 messages of your private conversation.

**Method 3: Use command with shorthand timeframes** ⭐ **NEW**
```
/summarize 24h
/summarize 7d
/summarize 2mo
```

**Method 4: Use command with natural language timeframes**
```
/summarize today
/summarize yesterday
/summarize last 2 hours
/summarize last 1 week
/summarize from 2024-10-01 to 2024-10-15
/summarize on 2024-10-15
```

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
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `DATABASE_URL` | No | - | PostgreSQL connection URL (optional, for persistent storage) |
| `CLAUDE_MODEL` | No | `claude-3-haiku-20240307` | Claude model to use (see options below) |
| `MESSAGE_LIMIT` | No | `75` | Maximum number of messages to summarize |
| `MAX_MESSAGE_AGE_HOURS` | No | `24` | Only summarize messages within this timeframe |
| `MONTHLY_BUDGET` | No | `10.0` | Monthly API budget limit in USD (default: $10) |
| `ADMIN_USER_ID` | No | - | Your Telegram user ID for budget notifications |

**Available Claude Models (in order of accessibility):**
- `claude-3-haiku-20240307` ⭐ **DEFAULT - Works for ALL API tiers** (fastest and most cost-effective)
- `claude-3-sonnet-20240229` (balanced performance - may require higher tier)
- `claude-3-opus-20240229` (highest quality - may require higher tier)
- `claude-3-5-sonnet-20240620` or `20241022` (latest Sonnet - requires specific API access)

**⚠️ IMPORTANT:** 
- **Haiku is the recommended model** as it works with all Anthropic API tiers and is the most cost-effective
- Only set the `CLAUDE_MODEL` environment variable if you want to override the default
- If you're getting 404 model errors, **DELETE** the `CLAUDE_MODEL` variable to use Haiku

### Database Setup (Optional but Recommended)

The bot supports PostgreSQL for persistent message storage, allowing you to:
- Store unlimited message history (not just last 100 messages)
- Use custom timeframe filtering effectively
- Retrieve summaries from any time period
- Maintain history across bot restarts

**Setting up Database:**

1. **On Railway (Automatic):**
   - Railway provides PostgreSQL automatically
   - Add a PostgreSQL service to your project
   - Railway will set the `DATABASE_URL` environment variable automatically
   - The bot will detect and use it on next deployment

2. **On Render (Automatic):**
   - Go to Dashboard → New → PostgreSQL
   - Create a PostgreSQL database
   - Copy the "Internal Database URL"
   - Add it as `DATABASE_URL` environment variable in your bot service
   - Render will handle the connection

3. **Custom PostgreSQL:**
   - Set `DATABASE_URL` in this format:
   ```
   postgresql://username:password@host:port/database
   ```

**Without Database:**
- Bot will use in-memory storage (last 100 messages only)
- Custom timeframe filtering will work but only for messages in memory
- History is lost on bot restart

### Budget Management & Cost Tracking 💰

The bot includes a comprehensive cost tracking system to help you monitor and control API spending:

**🎯 Features:**

1. **Automatic Cost Tracking**
   - Tracks every API call with precise token usage
   - Uses Claude 3 Haiku pricing:
     - Input tokens: $0.25 per million
     - Output tokens: $1.25 per million
   - Stores usage data persistently in `cost_data.json`

2. **Budget Enforcement**
   - Hard limit: $10/month by default (configurable)
   - Prevents API calls when budget is exceeded
   - Shows clear error messages with reset date
   - Automatically resets on the 1st of each month

3. **Admin Notifications**
   - Sends alerts at 50%, 75%, and 90% of budget
   - Includes detailed usage statistics
   - Shows remaining budget and days until reset

4. **Usage Commands**
   - `/usage` - Check current month's spending and budget status
   - `/resetusage` - Manually reset usage (admin only)

**📊 Setting Up Budget Tracking:**

1. **Set Monthly Budget (Optional):**
   ```
   MONTHLY_BUDGET=10.0
   ```
   Default is $10/month. Adjust based on your needs.

2. **Enable Admin Notifications (Highly Recommended):**
   
   To receive budget warnings, you need to set your Telegram user ID:
   
   **Finding Your User ID:**
   - Method 1: Use [@userinfobot](https://t.me/userinfobot) on Telegram
   - Method 2: Send any message to your bot and check the logs
   - Method 3: Use [@getidsbot](https://t.me/getidsbot)
   
   Then set it as an environment variable:
   ```
   ADMIN_USER_ID=123456789
   ```

3. **Deploy and Start Using:**
   - Cost tracking is automatic - no additional setup needed
   - Use `/usage` anytime to check your spending
   - You'll receive DMs when hitting 50%, 75%, and 90% of budget

**📈 Example Usage Output:**

```
📊 Monthly Budget Usage Report

Period: 2024-10
Status: 🟢 HEALTHY

💰 Budget:
• Spent: $2.4567
• Limit: $10.00
• Remaining: $7.5433
• Used: 24.6%

[████░░░░░░░░░░░░░░░░] 24.6%

🔢 Token Usage:
• Input: 98,234 tokens ($0.024559)
• Output: 45,678 tokens ($0.057098)
• Total: 143,912 tokens

📈 Activity:
• API requests: 156
• Avg cost/request: $0.015748

⏰ Budget resets in 8 day(s)
```

**🚨 Budget Limit Reached:**

When you hit the monthly limit, users will see:

```
🚫 Monthly Budget Limit Reached

Current spending: $10.0234
Monthly budget: $10.00
Budget resets in 5 day(s) (on the 1st of next month)

Please check back after the reset or contact the bot administrator.
```

**💡 Tips:**

- Start with the default $10/month budget and adjust as needed
- Set up `ADMIN_USER_ID` to receive proactive alerts
- Check `/usage` regularly to monitor spending
- Use `/resetusage` only if needed (usage auto-resets monthly)
- With Haiku model, $10 covers ~2,000-5,000 summaries per month

### Customization

You can customize the bot's behavior by editing `bot.py`:

- **Summary style**: Modify the prompt in `generate_summary()`
- **Response format**: Change the summary template
- **Message filtering**: Adjust what messages are included
- **Database settings**: Modify `database.py` for custom retention policies

## 🏗️ Architecture

```
┌─────────────┐
│   Telegram  │
│    Chat     │
└──────┬──────┘
       │ User mentions bot or uses /summarize
       ▼
┌─────────────┐
│  Bot API    │
│  (Python)   │
└──────┬──────┘
       │ Stores messages
       ▼
┌─────────────────────────┐
│  Storage Layer          │
│  ┌─────────────────┐   │
│  │   PostgreSQL    │   │ (Optional)
│  │    Database     │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │   In-Memory     │   │ (Fallback)
│  │     Cache       │   │
│  └─────────────────┘   │
└───────────┬─────────────┘
            │ Retrieves messages by count/timeframe
            ▼
┌─────────────────┐
│ Timeframe Parser│
│ + Formatter     │
└───────┬─────────┘
        │ Formats & sends to AI
        ▼
┌─────────────┐
│Anthropic API│
│  (Claude)   │
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

### Anthropic API
- **Claude 3 Haiku** ⭐ (DEFAULT): ~$0.0001-0.0005 per summary (most cost-effective!)
  - 100 summaries ≈ $0.01-0.05
  - 1000 summaries ≈ $0.10-0.50
  - 10,000 summaries ≈ $1-5
- **Claude 3 Sonnet**: ~$0.003-0.015 per summary (balanced)
- **Claude 3 Opus**: ~$0.015-0.075 per summary (highest quality)
- **Claude 3.5 Sonnet**: ~$0.003-0.015 per summary (latest, requires special access)

**Total Monthly Cost**: $0-5 for typical usage with Haiku (small-medium groups, ~500-1000 summaries/month)

### 🛡️ Built-in Budget Protection

The bot includes automatic cost tracking and budget enforcement:
- **Default Budget**: $10/month (configurable via `MONTHLY_BUDGET`)
- **Automatic Tracking**: Every API call is tracked with precise token usage
- **Hard Limit**: Bot stops making API calls when budget is exceeded
- **Proactive Alerts**: Get notifications at 50%, 75%, and 90% of budget
- **Monthly Reset**: Budget automatically resets on the 1st of each month
- **Usage Monitoring**: Use `/usage` command anytime to check spending

This ensures you never have surprise charges and stay within your planned budget!

## 🛡️ Smart Safeguards & Protection Features

The bot includes comprehensive safeguards to protect you from unexpected costs while ensuring reliable operation:

### 1. **Hard Message Limits**

To prevent overwhelming the API and your budget:

- **Maximum limit:** 1,000 messages per summary request
- **Automatic enforcement:** If you request a timeframe with more messages, smart sampling kicks in automatically
- **User notification:** You'll be informed when the limit is reached

**Example:**
```
/summarize 60d  # If this returns 5,000 messages
```

Response:
```
⚠️ Message Limit Exceeded

Found 5,000 messages but the maximum allowed is 1,000.

🤖 Smart Sampling will be used:
• I'll intelligently select 1,000 representative messages
• Messages will be evenly distributed across the timeframe
• Longer, more substantive messages will be prioritized
• The summary will still capture the key themes and discussions

Proceeding with smart sampling...
```

### 2. **Smart Sampling**

When message counts are high (>500), the bot uses intelligent sampling:

**How it works:**
- **Even Distribution:** Messages are sampled evenly across the entire timeframe
- **Engagement Priority:** Longer, more substantive messages are prioritized
- **Context Preservation:** The sampling maintains chronological flow and context
- **Automatic Application:** No user intervention needed

**Benefits:**
- Faster processing
- Lower API costs
- Better quality summaries (less noise)
- Captures representative discussion

**Example output:**
```
📊 Summarized 500 messages (intelligently sampled from 2,345 messages)
🔍 Smart Sampling Applied:
• Original: 2,345 messages
• Analyzed: 500 messages
• Sampling: 21.3% of messages
• Method: Evenly distributed across timeframe, prioritizing substantive messages
```

### 3. **Cost Estimation & Warnings**

Before processing expensive summaries, the bot calculates and warns you:

**Cost Warning Threshold:** $0.50 per request

**What you'll see:**
```
⚠️ High Cost Warning

This summary will be expensive:
• Estimated cost: $0.6234
• Estimated tokens: ~15,234
• Warning threshold: $0.50

📊 Processing 800 messages

⚡ Proceeding with summary generation...
```

**Features:**
- Pre-request cost estimation based on message count and content
- Automatic budget check before processing
- Request blocked if monthly budget exceeded
- Transparent cost reporting after each summary

### 4. **Database Requirement Checks**

For long timeframes without a database, you'll get a helpful warning:

**Example:**
```
/summarize 60d  # Without DATABASE_URL configured
```

Response:
```
⚠️ Database Not Configured

You're querying a timeframe of 60d, but the bot is running without a persistent database.

This means:
• Only messages from the last 24 hours are available
• Only the last 100 messages are kept in memory
• Message history is lost when the bot restarts

To access longer history:
1. Set up a PostgreSQL database (see README.md)
2. Add the DATABASE_URL environment variable
3. Redeploy the bot

I'll search the available messages, but results may be limited.
```

### 5. **Budget Tracking Integration**

All safeguards work together with the budget tracking system:

- **Pre-check:** Estimated cost checked against remaining budget
- **Hard stop:** Request blocked if it would exceed monthly limit
- **Cost tracking:** Actual costs tracked after each request
- **Admin alerts:** Notifications at 50%, 75%, and 90% thresholds

### Recommended Usage Patterns

**For $10/month budget (using Claude Haiku):**

✅ **Efficient Usage:**
- Use shorthand syntax: `/summarize 7d` instead of counting messages
- Let smart sampling handle large datasets automatically
- Check `/usage` regularly to monitor spending
- Use database storage for long-term history

⚠️ **What to avoid:**
- Repeatedly requesting very large timeframes without database
- Summarizing more than 500 messages per request when possible
- Ignoring budget warnings

**Cost Examples (with Haiku):**
- 50 messages: ~$0.0001-0.0003
- 100 messages: ~$0.0003-0.0008
- 500 messages: ~$0.002-0.005
- 1000 messages: ~$0.005-0.01

With $10/month, you can typically handle:
- **2,000-5,000 summaries** of ~100 messages each
- **500-1,000 summaries** of ~500 messages each
- **Mix of sizes:** Most common usage pattern

## 🔒 Privacy & Security

- **Optional database storage**: You control whether messages are stored persistently
  - **With DATABASE_URL**: Messages stored in PostgreSQL for extended history
  - **Without DATABASE_URL**: Only last 100 messages kept in memory (cleared on restart)
- **On-demand processing**: Only processes messages when explicitly requested (via mention or `/summarize` command)
- **Works in private chats**: The bot can summarize your private conversations while maintaining the same privacy standards
- **Anthropic data policy**: Review [Anthropic's privacy policy](https://www.anthropic.com/legal/privacy)
- **Secure credentials**: All tokens and API keys stored as environment variables
- **No sharing**: Your messages are only sent to Anthropic for summarization, never shared elsewhere

⚠️ **Important**: 
- Messages are sent to Anthropic's API for summarization. Consider this before using in sensitive conversations (both in groups and private chats).
- If you enable database storage, messages will be persisted in your PostgreSQL database. Ensure your database is properly secured.
- You can disable database storage by removing the `DATABASE_URL` environment variable.

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
├── database.py               # PostgreSQL database module
├── timeframe_parser.py       # Timeframe parsing module (with shorthand support)
├── cost_tracker.py           # Cost tracking and budget enforcement
├── smart_sampler.py          # Smart sampling for large message sets ⭐ NEW
├── cost_data.json            # Persistent cost tracking data (auto-generated)
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
| `/help` | Display help information with timeframe examples |
| `/summarize` or `/summary` | Get a summary of recent messages (works in both group and private chats) |
| `/summarize <number>` | Get a summary of the last \<number\> messages (e.g., `/summarize 50`) |
| `/summarize <timeframe>` | Get a summary for a specific timeframe (e.g., `/summarize today`) |
| `/usage` | Check current month's API usage and budget status |
| `/resetusage` | Manually reset usage statistics (admin only - requires ADMIN_USER_ID) |

**Supported Timeframes:**
- Shorthand: `24h`, `60d`, `2mo`, `3w` (h=hours, d=days, w=weeks, mo=months) ⭐ **NEW**
- Relative: `today`, `yesterday`, `last X hours`, `last X days`, `last X weeks`
- Absolute: `from YYYY-MM-DD to YYYY-MM-DD`, `on YYYY-MM-DD`

## 🐛 Troubleshooting

### Bot doesn't respond in group chats
- Verify bot privacy settings are disabled in BotFather (Settings → Group Privacy → Turn OFF)
- Check if bot is an admin in the group
- Review deployment logs for errors

### Bot doesn't respond in private chats
- Make sure you're using the `/summarize` or `/summary` command (mentions don't work in private chats)
- Verify the bot is running (check deployment status)
- Review deployment logs for errors

### "No messages available"
- Bot can only see messages after it was added to the group or started in private chat
- Wait for more conversation, then try again
- The bot needs at least a few messages to create a meaningful summary

### Anthropic API Errors - Complete Troubleshooting Guide

#### 🔍 Error: 404 Model Not Found

If you're seeing errors like `Error 404: model 'claude-3-5-sonnet-20241022' not found` or `Model not available`:

**What this means:** Your API key doesn't have access to the specific Claude model being used.

**✅ Solution (Follow in order):**

**Step 1: Delete the CLAUDE_MODEL environment variable (MOST COMMON FIX)**

The bot now defaults to **Haiku** (`claude-3-haiku-20240307`), which works for ALL API tiers.

- **Railway:**
  1. Go to your project → Variables tab
  2. Look for `CLAUDE_MODEL` variable
  3. If it exists, click the trash icon to DELETE it
  4. Bot will auto-redeploy with Haiku as default

- **Render:**
  1. Go to your service → Environment tab
  2. Look for `CLAUDE_MODEL` variable
  3. If it exists, delete it
  4. Click "Save Changes"

**Step 2: Verify the fix in deployment logs**

After redeployment, check logs for:
- ✅ Success: `✓ Using default Claude model: claude-3-haiku-20240307 (Haiku - works for all API tiers)`
- ❌ Still an issue: `⚠️ CLAUDE_MODEL environment variable is SET to:` (variable still exists)

**Step 3: Verify API key access in Anthropic Console**

1. Visit **[Anthropic Console](https://console.anthropic.com/)**
2. Log in to your account
3. Go to **Settings → API Keys**
   - Verify your API key is active
   - Check the creation date (keys don't expire but can be deleted)
4. Go to **Settings → Billing**
   - Confirm you have a valid payment method
   - Check your current balance and usage
   - Ensure you haven't exceeded spending limits
5. Go to **Settings → Organization**
   - Check your API tier/plan
   - Some models require higher tiers

**Step 4: Check which models are available to your account**

Unfortunately, Anthropic doesn't provide a direct UI to see available models, but you can:

1. **Check API tier:** Most new free accounts have access to Haiku
2. **Test via API Console:** Visit [Anthropic Workbench](https://console.anthropic.com/workbench) and try different models
3. **Model availability by tier:**
   - ✅ **All tiers:** `claude-3-haiku-20240307` (DEFAULT)
   - ⚠️ **Higher tiers may be needed for:** Sonnet and Opus variants
   - ⚠️ **Special access required:** Claude 3.5 Sonnet (20240620, 20241022)

**Step 5: Alternative - Try different models (if Haiku doesn't work)**

Set `CLAUDE_MODEL` environment variable to one of these (in order of likelihood to work):

```
claude-3-haiku-20240307     ← Try this first (DEFAULT)
claude-3-sonnet-20240229    ← Try this second
claude-3-opus-20240229      ← Try this third
```

#### 🔑 Error: 401 Unauthorized / Authentication Failed

**What this means:** There's an issue with your Anthropic API key.

**✅ Solutions:**

1. **Verify API key is correct:**
   - Go to [Anthropic Console → API Keys](https://console.anthropic.com/settings/keys)
   - Check if your key is listed and active
   - API keys start with `sk-ant-api03-`
   - If unsure, create a new API key

2. **Check environment variable:**
   - Go to deployment platform (Railway/Render)
   - Verify `ANTHROPIC_API_KEY` is set correctly
   - Check for extra spaces, quotes, or characters
   - Copy-paste directly from Anthropic Console

3. **Verify billing setup:**
   - Go to [Anthropic Console → Billing](https://console.anthropic.com/settings/billing)
   - Ensure valid payment method is added
   - Confirm you have available credits
   - Check if spending limits are set

#### ⏱️ Error: 429 Rate Limit / Quota Exceeded

**What this means:** You've hit API usage limits or run out of credits.

**✅ Solutions:**

1. **Wait and retry** - Rate limits reset quickly (usually within minutes)
2. **Check usage:** [Anthropic Console → Usage](https://console.anthropic.com/settings/usage)
3. **Add more credits** if balance is low
4. **Consider upgrading** API tier for higher limits
5. **Reduce bot usage** - Use longer MESSAGE_LIMIT intervals

#### 🔧 Error: 500/503 Service Error

**What this means:** Temporary issue with Anthropic's API service.

**✅ Solutions:**

1. **Wait 5-10 minutes** and try again
2. **Check status:** [Anthropic Status Page](https://status.anthropic.com/)
3. **Review Twitter:** [@AnthropicAI](https://twitter.com/AnthropicAI) for announcements
4. If persistent (>30 min), contact Anthropic support

### Quick Diagnosis Checklist

Run through this checklist to identify your issue:

- [ ] Check deployment logs for specific error codes
- [ ] Verify `CLAUDE_MODEL` environment variable is NOT set (let bot use Haiku default)
- [ ] Confirm `ANTHROPIC_API_KEY` is correct and active
- [ ] Check Anthropic billing has valid payment method
- [ ] Verify you have available API credits
- [ ] Ensure bot is using `claude-3-haiku-20240307` (see logs)
- [ ] Test API key in [Anthropic Workbench](https://console.anthropic.com/workbench)
- [ ] Check [Anthropic Status](https://status.anthropic.com/) for service issues

### Still Having Issues?

1. **Check deployment logs** - They contain detailed error information
2. **Review environment variables** - Ensure all are set correctly
3. **Test in Anthropic Console** - Verify your API key works there
4. **Contact Anthropic Support** - For API tier and model access questions
5. **See detailed setup guide** - [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

**⚠️ Key Reminder:** The bot defaults to **Haiku** which should work for ALL API tiers. Only set `CLAUDE_MODEL` if you specifically need a different model and have verified access.

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
- Monitor Anthropic usage on their dashboard
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
- [Anthropic](https://www.anthropic.com/) - Claude AI for intelligent summarization
- [Railway](https://railway.app/) - Easy cloud deployment
- [Render](https://render.com/) - Alternative cloud hosting

## 📧 Support

- **Setup Issues**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- **Bugs**: Open an issue on GitHub
- **Questions**: Check the FAQ in SETUP_INSTRUCTIONS.md

## 🗺️ Roadmap

Recent additions:
- [x] PostgreSQL database support for persistent storage
- [x] Custom timeframe filtering (relative and absolute dates)
- [x] Budget tracking and cost enforcement system
- [x] Shorthand timeframe syntax (60d, 2mo, 3w, 24h) ⭐ **NEW**
- [x] Hard message limits (max 1000 per request) ⭐ **NEW**
- [x] Smart sampling for large message sets ⭐ **NEW**
- [x] Cost estimation and warnings before processing ⭐ **NEW**
- [x] Database requirement checks for long timeframes ⭐ **NEW**

Future improvements planned:
- [ ] Support for multiple languages
- [ ] Custom summary templates
- [ ] Analytics dashboard
- [ ] Message sentiment analysis
- [ ] Export summaries to PDF
- [ ] Integration with other chat platforms
- [ ] Scheduled automatic summaries

## ⭐ Show Your Support

If you find this bot useful, please consider:
- Giving it a star on GitHub ⭐
- Sharing it with others who might benefit
- Contributing improvements
- Reporting bugs or suggesting features

---

**Made with ❤️ for the Telegram community**

*Happy Summarizing! 🚀*
