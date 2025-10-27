# 🤖 Telegram Message Summarizer Bot - Complete Setup Guide

Welcome! This guide will help you set up your own Telegram bot that summarizes group chat messages. **No coding knowledge required!** Just follow these steps carefully.

---

## 📋 Table of Contents

1. [What You'll Need](#what-youll-need)
2. [Step 1: Create Your Telegram Bot](#step-1-create-your-telegram-bot)
3. [Step 2: Get Your Anthropic API Key](#step-2-get-your-anthropic-api-key)
4. [Step 3: Upload Your Bot Code to GitHub](#step-3-upload-your-bot-code-to-github)
5. [Step 4: Deploy Your Bot (Choose One)](#step-4-deploy-your-bot)
   - [Option A: Deploy on Railway (Recommended)](#option-a-deploy-on-railway-recommended)
   - [Option B: Deploy on Render](#option-b-deploy-on-render)
6. [Step 5: Add Your Bot to a Telegram Group](#step-5-add-your-bot-to-a-telegram-group)
7. [Step 6: Use Your Bot](#step-6-use-your-bot)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions](#frequently-asked-questions)

---

## What You'll Need

Before starting, make sure you have:

- ✅ A Telegram account
- ✅ A GitHub account (free - sign up at [github.com](https://github.com))
- ✅ An Anthropic account (you'll need to add payment details, but costs are very low - typically $0.01-0.05 per summary)
- ✅ About 30-45 minutes of time
- ✅ This bot code (you already have it!)

**Cost Estimate:**
- Telegram Bot: **FREE** ✨
- GitHub: **FREE** ✨
- Railway/Render: **FREE** tier available (sufficient for most users) ✨
- Anthropic API: Pay-as-you-go (approximately $0.003-0.015 per summary with Claude 3.5 Sonnet)

---

## Step 1: Create Your Telegram Bot

### 1.1 Open Telegram and Find BotFather

1. Open the Telegram app on your phone or computer
2. In the search bar at the top, type: **@BotFather**
3. Click on the official BotFather (it has a blue verification checkmark ✓)
4. Click **START** at the bottom

### 1.2 Create Your New Bot

1. Send this message to BotFather: `/newbot`

2. BotFather will ask you to choose a **name** for your bot
   - Example: "My Message Summarizer"
   - Type your chosen name and send it

3. BotFather will ask you to choose a **username** for your bot
   - Must end with "bot" (e.g., "MySummarizerBot" or "message_summary_bot")
   - Must be unique (not already taken)
   - Example: `my_summarizer_bot`
   - Type your chosen username and send it

4. **SUCCESS!** 🎉 BotFather will send you a message containing your **Bot Token**
   - It looks like this: `6234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`
   - **IMPORTANT:** Keep this token secret! Anyone with this token can control your bot

### 1.3 Save Your Bot Token

1. **Copy the entire token** (it's a long string of numbers, letters, and symbols)
2. Save it in a safe place - you'll need it soon
   - Example: Create a text file on your computer called "bot-credentials.txt"
   - Paste the token there

### 1.4 Configure Your Bot Settings (Optional but Recommended)

Send these commands to BotFather to set up your bot:

1. Set a description (what users see when they first start your bot):
   ```
   /setdescription
   ```
   - Choose your bot from the list
   - Send: "I can summarize group chat messages! Just mention me to get a summary."

2. Set a profile picture (optional):
   ```
   /setuserpic
   ```
   - Choose your bot
   - Upload an image

3. Enable Group Privacy OFF (so bot can read messages):
   ```
   /setprivacy
   ```
   - Choose your bot
   - Click **Disable**
   - This allows the bot to see all messages in group chats

**✅ Step 1 Complete!** You now have:
- Your Bot Token (saved safely)
- Your Bot Username (remember it!)

---

## Step 2: Get Your Anthropic API Key

Anthropic provides the Claude AI that creates the summaries. You'll need an API key.

### 2.1 Create an Anthropic Account

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Click **Sign up** and create your account
3. Verify your email address
4. Log in to your account

### 2.2 Add Payment Information

1. After logging in, you'll see a message about adding payment details
2. Click on your profile icon or settings (top right corner)
3. Go to **Billing** → **Payment methods**
4. Click **Add payment method**
5. Enter your credit/debit card information

**💰 Important Notes About Costs:**
- Anthropic charges pay-as-you-go (you only pay for what you use)
- Claude 3.5 Sonnet costs approximately $0.003-0.015 per summary
- Example: 100 summaries = approximately $0.30-1.50
- You can set spending limits in the Billing section
- Recommended: Set a limit of $5-10/month to start

### 2.3 Get Your API Key

1. Click on your profile icon or settings (top right)
2. Select **API Keys**
3. Click **+ Create Key**
4. Give it a name (e.g., "Telegram Bot")
5. Click **Create Key**
6. **IMPORTANT:** Copy the key immediately - you won't be able to see it again!
   - It looks like: `sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890...`
7. Save it in your "bot-credentials.txt" file

**✅ Step 2 Complete!** You now have:
- Anthropic account
- API Key (saved safely)
- Payment method added

---

## Step 3: Upload Your Bot Code to GitHub

GitHub will store your bot code and connect it to the hosting service.

### 3.1 Create a GitHub Account (if you don't have one)

1. Go to [https://github.com](https://github.com)
2. Click **Sign up**
3. Follow the steps to create your account
4. Verify your email

### 3.2 Create a New Repository

1. Log in to GitHub
2. Click the **+** icon in the top right corner
3. Select **New repository**
4. Fill in the details:
   - **Repository name:** `telegram-summarizer-bot` (or any name you like)
   - **Description:** "A bot that summarizes Telegram group messages"
   - **Public or Private:** Choose **Public** (free) or **Private** (if you prefer)
   - **DO NOT** check "Add a README file" (we already have one)
5. Click **Create repository**

### 3.3 Upload Your Bot Files

#### Option A: Using GitHub Web Interface (Easiest)

1. You should see a page that says "Quick setup"
2. Click on **uploading an existing file**
3. Drag and drop ALL these files from your computer:
   - `bot.py`
   - `requirements.txt`
   - `.env.example`
   - `Procfile`
   - `railway.json`
   - `render.yaml`
   - `runtime.txt`
   - `README.md`
   - `SETUP_INSTRUCTIONS.md` (this file!)
4. Scroll down and click **Commit changes**

#### Option B: Using Git Command Line (For Advanced Users)

If you're comfortable with the command line:

```bash
cd telegram_summarizer_bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-summarizer-bot.git
git push -u origin main
```

**✅ Step 3 Complete!** Your code is now on GitHub!

---

## Step 4: Deploy Your Bot

Now let's make your bot run 24/7 in the cloud! Choose **ONE** of these options:

---

## Option A: Deploy on Railway (Recommended)

Railway is beginner-friendly and offers a generous free tier.

### 4.1 Create a Railway Account

1. Go to [https://railway.app](https://railway.app)
2. Click **Login** (top right)
3. Click **Sign in with GitHub**
4. Authorize Railway to access your GitHub account

### 4.2 Create a New Project

1. Click **New Project** (or **+ New**)
2. Select **Deploy from GitHub repo**
3. Choose your `telegram-summarizer-bot` repository
4. Railway will start setting up your project

### 4.3 Add Environment Variables

This is where you'll add your Bot Token and Anthropic API Key!

1. Click on your deployed service
2. Go to the **Variables** tab
3. Click **+ New Variable** for each of these:

   **Variable 1:**
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: [Paste your bot token from Step 1]

   **Variable 2:**
   - Key: `BOT_USERNAME`
   - Value: [Your bot username WITHOUT the @ symbol]
   - Example: If your bot is @MySummarizerBot, enter: MySummarizerBot

   **Variable 3:**
   - Key: `ANTHROPIC_API_KEY`
   - Value: [Paste your Anthropic API key from Step 2]

   **Variable 4 (Optional):**
   - Key: `CLAUDE_MODEL`
   - Value: `claude-3-5-sonnet-20241022`

   **Variable 5 (Optional):**
   - Key: `MESSAGE_LIMIT`
   - Value: `75`

   **Variable 6 (Optional):**
   - Key: `MAX_MESSAGE_AGE_HOURS`
   - Value: `24`

4. The bot will automatically restart with the new variables

### 4.4 Verify Deployment

1. Go to the **Deployments** tab
2. You should see a deployment with status "SUCCESS" and "ACTIVE"
3. Click on **View Logs** to see your bot starting up
4. Look for a message like: "Bot is starting..."

### 4.5 Monitor Usage (Stay Within Free Tier)

Railway free tier includes:
- $5 of free credits per month
- Shared resources

To check your usage:
1. Go to your project dashboard
2. Click on **Usage** (bottom left)
3. Monitor your monthly usage

**✅ Railway Deployment Complete!** Your bot is now running 24/7! 🎉

Skip to [Step 5](#step-5-add-your-bot-to-a-telegram-group)

---

## Option B: Deploy on Render

Render is another great free hosting option.

### 4.1 Create a Render Account

1. Go to [https://render.com](https://render.com)
2. Click **Get Started**
3. Sign up with GitHub (click **GitHub** button)
4. Authorize Render to access your GitHub account

### 4.2 Create a New Web Service

1. Click **New +** (top right)
2. Select **Background Worker**
3. Click **Connect** next to your GitHub account
4. Find and click **Connect** on your `telegram-summarizer-bot` repository

### 4.3 Configure Your Service

Fill in these settings:

1. **Name:** `telegram-summarizer-bot` (or any name)
2. **Region:** Choose the closest region to you
3. **Branch:** `main`
4. **Runtime:** `Python 3`
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `python bot.py`
7. **Instance Type:** Select **Free**

### 4.4 Add Environment Variables

Scroll down to the **Environment Variables** section:

1. Click **Add Environment Variable** for each of these:

   **Variable 1:**
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: [Paste your bot token from Step 1]

   **Variable 2:**
   - Key: `BOT_USERNAME`
   - Value: [Your bot username WITHOUT the @ symbol]

   **Variable 3:**
   - Key: `ANTHROPIC_API_KEY`
   - Value: [Paste your Anthropic API key from Step 2]

   **Variable 4:**
   - Key: `CLAUDE_MODEL`
   - Value: `claude-3-5-sonnet-20241022`

   **Variable 5:**
   - Key: `MESSAGE_LIMIT`
   - Value: `75`

   **Variable 6:**
   - Key: `MAX_MESSAGE_AGE_HOURS`
   - Value: `24`

2. Click **Create Background Worker** at the bottom

### 4.5 Verify Deployment

1. Wait for deployment to complete (usually 2-5 minutes)
2. You should see "Deploy succeeded" with a green checkmark
3. Click on **Logs** tab to see your bot running
4. Look for: "Bot is starting..."

### 4.6 Monitor Free Tier Usage

Render free tier includes:
- 750 hours per month (enough for 24/7 operation!)
- Shared resources

The service will automatically sleep after 15 minutes of inactivity, but will wake up when someone uses the bot.

**✅ Render Deployment Complete!** Your bot is now running! 🎉

---

## Step 5: Add Your Bot to a Telegram Group

Now let's add your bot to a group so it can start summarizing messages!

### 5.1 Open Your Group Chat

1. Open Telegram
2. Go to the group where you want to add the bot
3. **Note:** You must be an admin of the group to add bots

### 5.2 Add the Bot

1. Click on the **group name** at the top
2. Click **Add Members** (or **Invite to Group**)
3. Search for your bot's username (e.g., @MySummarizerBot)
4. Select your bot
5. Click **Add** or **Invite**

### 5.3 Make the Bot an Admin (Important!)

For the bot to read messages, it needs to be an admin:

1. In the group settings, go to **Administrators**
2. Click **Add Admin**
3. Select your bot
4. **Uncheck** all permissions except:
   - ✅ Read Messages (this should be enabled by default)
5. Click **Done** or **Save**

### 5.4 Test the Bot

1. Send a regular message in the group: "Hello everyone!"
2. Send a few more messages to build up history
3. Now mention your bot: "@YourBotUsername summarize" or just "@YourBotUsername"
4. The bot should respond with a summary!

**✅ Step 5 Complete!** Your bot is now in your group!

---

## Step 6: Use Your Bot

### How to Get a Summary

There are **three ways** to use your bot:

#### Method 1: Mention the Bot
Type `@YourBotUsername` anywhere in a message:
```
@MySummarizerBot what did I miss?
```

#### Method 2: Use the /summary Command
Just type:
```
/summary
```

#### Method 3: Reply to a Message
Reply to any message in the group and mention the bot:
```
@MySummarizerBot summarize from here
```

### What the Bot Does

1. ✅ Reads the last 75 messages (or whatever you set in MESSAGE_LIMIT)
2. ✅ Only includes messages from the last 24 hours (or whatever you set)
3. ✅ Sends them to OpenAI for AI-powered summarization
4. ✅ Returns a clean, bullet-point summary
5. ✅ Tells you how many messages were summarized

### Example Summary

```
📝 Summary:
• Meeting scheduled for Friday at 3 PM
• John will prepare the presentation slides
• Budget approval still pending from management
• Sarah shared the Q3 sales report link
• Team agreed to use the new project management tool
• Next review meeting in two weeks

📊 Summarized 45 messages from the last 24 hours.
```

### Bot Commands

- `/start` - Get welcome message and instructions
- `/help` - Show help information
- `/summary` - Get a summary of recent messages

**✅ You're all done!** Your bot is fully operational! 🚀

---

## Troubleshooting

### Problem: Bot doesn't respond when mentioned

**Possible Solutions:**

1. **Check if bot is online:**
   - Go to your Railway/Render dashboard
   - Check the logs for errors
   - Make sure the deployment status is "ACTIVE"

2. **Verify bot privacy settings:**
   - Go to @BotFather on Telegram
   - Send: `/setprivacy`
   - Select your bot
   - Make sure it's set to **DISABLED**

3. **Check if bot is an admin:**
   - Go to group settings → Administrators
   - Your bot should be listed there

4. **Verify environment variables:**
   - Check Railway/Render dashboard
   - Make sure all variables are set correctly
   - No extra spaces in the values

### Problem: Bot says "No messages available to summarize"

**Cause:** The bot can only see messages sent AFTER it was added to the group.

**Solution:** 
- Wait for more messages to be sent in the group
- Have a short conversation (10-20 messages)
- Try mentioning the bot again

### Problem: "Error generating summary" message

**Possible Causes:**

1. **Anthropic API Key Issue:**
   - Check if your API key is correct
   - Verify you have credits/payment method on Anthropic
   - Check Anthropic usage limits

2. **Check Anthropic Account:**
   - Log in to [console.anthropic.com](https://console.anthropic.com)
   - Go to Billing → Usage
   - Make sure you have available credits
   - Check if your API key is active

3. **API Rate Limits:**
   - If many people use the bot at once, Anthropic might rate-limit you
   - Wait a few minutes and try again

### Problem: Bot stopped working after a few days

**Possible Causes:**

1. **Free tier limits reached (Railway):**
   - Check your Railway usage dashboard
   - You may need to upgrade or wait for next month

2. **Service went to sleep (Render):**
   - Free tier services sleep after inactivity
   - Just mention the bot again - it will wake up

3. **Anthropic credits depleted:**
   - Add more credits to your Anthropic account

### Problem: "TELEGRAM_BOT_TOKEN not found" error in logs

**Solution:**
- Go to your deployment dashboard (Railway/Render)
- Check Environment Variables section
- Make sure `TELEGRAM_BOT_TOKEN` is set correctly
- Redeploy the service

### How to View Logs

**On Railway:**
1. Go to your project dashboard
2. Click on your service
3. Click **Deployments**
4. Click **View Logs**

**On Render:**
1. Go to your dashboard
2. Click on your service
3. Click the **Logs** tab

### Still Having Issues?

1. Check the logs first - they usually show what's wrong
2. Verify all environment variables are set correctly
3. Make sure your Anthropic account has available credits
4. Restart the service on Railway/Render
5. Check that your bot has admin privileges in the group

---

## Frequently Asked Questions

### How much does it cost to run this bot?

**Hosting:** Free (Railway/Render free tiers)
**Anthropic API:** Approximately $0.003-0.015 per summary
- 100 summaries ≈ $0.30-1.50
- 1000 summaries ≈ $3-15

### Can I use this bot in multiple groups?

Yes! Your bot can be added to as many groups as you want. Each group's messages are kept separate.

### How many messages can the bot summarize?

By default, it summarizes the last 75 messages from the past 24 hours. You can change this by modifying the environment variables:
- `MESSAGE_LIMIT`: Number of messages (default: 75)
- `MAX_MESSAGE_AGE_HOURS`: Time range in hours (default: 24)

### Is my chat data private?

- Your messages are sent to Anthropic's API for summarization
- Anthropic's data policy: [https://www.anthropic.com/legal/privacy](https://www.anthropic.com/legal/privacy)
- The bot doesn't store messages permanently (only keeps last 100 in memory)
- For sensitive conversations, consider this before using

### Can I change the bot's summarization style?

Yes! Edit the `bot.py` file and modify the prompt in the `generate_summary()` function. For example:
- Change "maximum 8 points" to "maximum 5 points" for shorter summaries
- Add "use formal language" or "use casual language"
- Specify different focus areas

### How do I update my bot after making changes?

1. Make changes to your code locally
2. Upload updated files to GitHub:
   - Go to your repository on GitHub
   - Click on the file you want to update
   - Click the pencil icon (Edit)
   - Make your changes
   - Click **Commit changes**
3. Railway/Render will automatically detect changes and redeploy

### Can I use different Claude models?

Yes! Just change the `CLAUDE_MODEL` environment variable. Options include:
- `claude-3-5-sonnet-20241022` (default, best balance of speed and quality)
- `claude-3-opus-20240229` (highest quality, more expensive)
- `claude-3-sonnet-20240229` (faster, more economical)
Note: Claude 3.5 Sonnet is usually the best choice for most use cases

### How do I stop the bot?

**Temporarily:**
- Railway: Click on your service → Settings → Pause service
- Render: Click on your service → Settings → Suspend

**Permanently:**
- Delete the service from Railway/Render dashboard
- Delete the bot using @BotFather: `/deletebot`

### Can other people use my bot?

Yes! Anyone can:
- Add your bot to their groups (if they have the bot username)
- Use the bot in groups where it's already added

The bot works for all group members - no special permissions needed to use it!

### What if I lose my bot token?

Unfortunately, tokens can't be recovered. But you can generate a new one:
1. Go to @BotFather
2. Send: `/token`
3. Select your bot
4. You'll get a new token
5. Update the environment variable in Railway/Render

**Note:** The old token will stop working.

---

## Need More Help?

- Check the logs in your Railway/Render dashboard
- Review the Troubleshooting section above
- Check Anthropic status: [https://status.anthropic.com](https://status.anthropic.com)
- Check Telegram Bot API status: [https://telegram.org](https://telegram.org)

---

## Congratulations! 🎉

You've successfully set up your Telegram Message Summarizer Bot! 

Your bot is now:
- ✅ Running 24/7 in the cloud
- ✅ Ready to summarize messages in any group
- ✅ Accessible to all group members
- ✅ Powered by AI for intelligent summaries

Enjoy using your bot! 🚀

---

**Pro Tips:**
- Set a monthly spending limit on Anthropic to control costs
- Monitor your Railway/Render usage to stay within free tier
- Keep your tokens and API keys secure - never share them!
- Read your deployment logs regularly to catch issues early

---

*Last updated: October 2025*
