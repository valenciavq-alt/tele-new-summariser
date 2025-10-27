"""
Telegram Message Summarizer Bot

This bot provides AI-generated summaries of recent messages in both
Telegram group chats and private/individual chats.

In group chats: mention the bot or use /summarize command
In private chats: use /summarize command
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import asyncio

from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Configuration
MESSAGE_LIMIT = int(os.getenv('MESSAGE_LIMIT', '75'))  # Number of messages to summarize
MAX_MESSAGE_AGE_HOURS = int(os.getenv('MAX_MESSAGE_AGE_HOURS', '24'))  # Only summarize recent messages


def get_bot_username():
    """Get the bot's username from environment variable"""
    return os.getenv('BOT_USERNAME', '').lower()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    welcome_message = """
👋 **Welcome to the Message Summarizer Bot!**

I can help summarize conversations in your group chats AND private chats!

**How to use me:**

**In Group Chats:**
1. Add me to your Telegram group
2. Give me permission to read messages
3. Mention me with @{} or use /summarize command
4. I'll summarize the recent messages in bullet points!

**In Private Chats:**
1. Send me messages in this private chat
2. Use the /summarize command
3. I'll summarize our recent conversation!

**Commands:**
/start - Show this welcome message
/help - Get help on how to use the bot
/summarize - Get a summary of recent messages (works in both group and private chats)

**Example:**
In groups: "@{} what did I miss?" or use /summarize
In private chats: Just type /summarize

Let's get started! 🚀
    """.format(
        get_bot_username() or "bot",
        get_bot_username() or "bot"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_message = """
🤖 **Message Summarizer Bot - Help**

**How it works:**
I can summarize recent messages in both group chats and private chats! I'll read the last {} messages and create a brief summary with key points.

**Ways to use:**

**In Group Chats:**
• Mention me: @{} 
• Use the command: /summarize
• Reply to any message and mention me

**In Private Chats:**
• Use the command: /summarize
• I'll summarize our recent conversation

**Tips:**
• I work in both group discussions and private chats
• I'll only summarize messages from the last {} hours
• The summary will be in bullet point format for easy reading

**Privacy:**
• In groups: I only process messages when explicitly mentioned or commanded
• In private: I only summarize when you use /summarize
• I don't store chat history permanently (only last {} messages in memory)
• All processing is done in real-time

Need more help? Contact the bot administrator.
    """.format(
        MESSAGE_LIMIT,
        get_bot_username() or "bot",
        MAX_MESSAGE_AGE_HOURS,
        MAX_STORED_MESSAGES
    )
    
    await update.message.reply_text(help_message, parse_mode='Markdown')


async def fetch_recent_messages(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    limit: int = MESSAGE_LIMIT
) -> List[dict]:
    """
    Fetch recent messages from the chat
    
    Args:
        context: Telegram context
        chat_id: Chat ID to fetch messages from
        limit: Maximum number of messages to fetch
    
    Returns:
        List of message dictionaries with text and metadata
    """
    messages = []
    message_count = 0
    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=MAX_MESSAGE_AGE_HOURS)
    
    try:
        # Note: Telegram API doesn't provide direct history access
        # We'll work with what's available in the bot's context
        # This is a limitation - bots can't access full message history
        # We'll document this clearly for users
        
        logger.info(f"Attempting to fetch up to {limit} recent messages from chat {chat_id}")
        
        # Return empty list with a note - actual implementation will use stored messages
        # In production, you might want to use a database to store recent messages
        return messages
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []


def format_messages_for_summary(messages: List[dict]) -> str:
    """
    Format messages into a string for the AI to summarize
    
    Args:
        messages: List of message dictionaries
    
    Returns:
        Formatted string of messages
    """
    if not messages:
        return "No messages available to summarize."
    
    formatted = []
    for msg in messages:
        timestamp = msg.get('timestamp', 'Unknown time')
        username = msg.get('username', 'Unknown user')
        text = msg.get('text', '')
        
        if text:
            formatted.append(f"[{timestamp}] {username}: {text}")
    
    return "\n".join(formatted)


async def generate_summary(messages_text: str) -> str:
    """
    Generate a summary using Claude API (Anthropic)
    
    Args:
        messages_text: Formatted string of messages to summarize
    
    Returns:
        AI-generated summary in bullet point format
    """
    # Determine which model to use
    # IMPORTANT: Use claude-3-haiku-20240307 as the default (most basic and universally available)
    # Haiku is the fastest, most cost-effective model and should work for ALL API tiers
    # Only set CLAUDE_MODEL environment variable if you want to override this default
    model_name = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
    
    try:
        if not messages_text or messages_text == "No messages available to summarize.":
            return "⚠️ No recent messages available to summarize. I can only summarize messages that I've seen since being added to the group."
        
        # Create the prompt for Claude
        prompt = f"""You are a helpful assistant that summarizes Telegram group chat conversations.

Please analyze the following chat messages and create a concise summary in bullet point format.

Focus on:
- Main topics discussed
- Key decisions or conclusions
- Important questions or concerns
- Action items or tasks mentioned
- Notable announcements

Chat messages:
{messages_text}

Please provide a brief summary in bullet points (maximum 8 points). Start with "📝 Summary:"
"""
        
        # Call Claude API
        # Available Claude models (in order of accessibility):
        # - claude-3-haiku-20240307: Fastest, most cost-effective, AVAILABLE TO ALL API TIERS (DEFAULT)
        # - claude-3-sonnet-20240229: Balanced performance and speed
        # - claude-3-opus-20240229: Most capable (may require higher API tier)
        # - claude-3-5-sonnet-20240620 / 20241022: Latest Sonnet (requires specific API access)
        # 
        # To change the model, set the CLAUDE_MODEL environment variable:
        # export CLAUDE_MODEL='claude-3-sonnet-20240229'
        logger.info(f"Using Claude model: {model_name}")
        
        response = anthropic_client.messages.create(
            model=model_name,
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        summary = response.content[0].text.strip()
        return summary
        
    except Exception as e:
        error_msg = f"Error generating summary with model '{model_name}': {e}"
        logger.error(error_msg)
        
        # Provide detailed error information to help with debugging
        error_str = str(e).lower()
        detailed_error = "❌ **Sorry, I encountered an error while generating the summary.**\n\n"
        
        # Distinguish between different error types
        if "404" in str(e) or "not found" in error_str or "not_found" in error_str:
            detailed_error += "🔍 **Error Type: Model Not Found (404)**\n\n"
            detailed_error += f"**Model attempted:** `{model_name}`\n"
            detailed_error += f"**Error details:** {str(e)}\n\n"
            detailed_error += "**This means:** Your API key doesn't have access to this specific Claude model.\n\n"
            detailed_error += "**✅ Recommended Solutions:**\n\n"
            detailed_error += "1. **Check if CLAUDE_MODEL environment variable is set:**\n"
            detailed_error += "   • Go to your deployment platform (Railway/Render)\n"
            detailed_error += "   • Look in Environment Variables section\n"
            detailed_error += "   • If `CLAUDE_MODEL` exists, DELETE it to use the default (Haiku)\n"
            detailed_error += "   • Haiku (`claude-3-haiku-20240307`) should work for all API tiers\n\n"
            detailed_error += "2. **Verify model availability in Anthropic Console:**\n"
            detailed_error += "   • Visit: https://console.anthropic.com/\n"
            detailed_error += "   • Check which models are available to your account\n"
            detailed_error += "   • Ensure you have sufficient API credits\n\n"
            detailed_error += "3. **Try alternative models (set CLAUDE_MODEL to one of these):**\n"
            detailed_error += "   • `claude-3-haiku-20240307` (Recommended - works for all tiers)\n"
            detailed_error += "   • `claude-3-sonnet-20240229` (Mid-tier)\n"
            detailed_error += "   • `claude-3-opus-20240229` (May require higher tier)\n\n"
            detailed_error += "📖 See README.md for detailed troubleshooting guide.\n"
            
        elif "401" in str(e) or "unauthorized" in error_str or "authentication" in error_str:
            detailed_error += "🔑 **Error Type: Authentication Failed (401)**\n\n"
            detailed_error += f"**Error details:** {str(e)}\n\n"
            detailed_error += "**This means:** There's an issue with your Anthropic API key.\n\n"
            detailed_error += "**✅ Solutions:**\n\n"
            detailed_error += "1. **Verify your API key is correct:**\n"
            detailed_error += "   • Go to https://console.anthropic.com/settings/keys\n"
            detailed_error += "   • Check if your API key is active\n"
            detailed_error += "   • If needed, create a new API key\n\n"
            detailed_error += "2. **Check environment variable:**\n"
            detailed_error += "   • Go to your deployment platform\n"
            detailed_error += "   • Verify `ANTHROPIC_API_KEY` is set correctly\n"
            detailed_error += "   • Make sure there are no extra spaces or characters\n\n"
            detailed_error += "3. **Verify billing:**\n"
            detailed_error += "   • Check https://console.anthropic.com/settings/billing\n"
            detailed_error += "   • Ensure you have a valid payment method\n"
            detailed_error += "   • Confirm you have available credits\n"
            
        elif "429" in str(e) or "rate" in error_str or "quota" in error_str:
            detailed_error += "⏱️ **Error Type: Rate Limit or Quota Exceeded (429)**\n\n"
            detailed_error += f"**Error details:** {str(e)}\n\n"
            detailed_error += "**This means:** You've hit API rate limits or run out of credits.\n\n"
            detailed_error += "**✅ Solutions:**\n\n"
            detailed_error += "1. **Wait a moment and try again** (rate limits reset quickly)\n"
            detailed_error += "2. **Check your usage:** https://console.anthropic.com/settings/billing\n"
            detailed_error += "3. **Add more credits** if your balance is low\n"
            detailed_error += "4. **Consider upgrading** your API tier for higher limits\n"
            
        elif "500" in str(e) or "503" in str(e) or "internal" in error_str:
            detailed_error += "🔧 **Error Type: API Service Error (500/503)**\n\n"
            detailed_error += f"**Error details:** {str(e)}\n\n"
            detailed_error += "**This means:** There's a temporary issue with Anthropic's service.\n\n"
            detailed_error += "**✅ Solutions:**\n\n"
            detailed_error += "1. **Wait a few minutes and try again**\n"
            detailed_error += "2. **Check Anthropic status:** https://status.anthropic.com/\n"
            detailed_error += "3. **If issue persists, contact Anthropic support**\n"
            
        else:
            # Generic error
            detailed_error += "❓ **Error Type: Unknown**\n\n"
            detailed_error += f"**Model:** `{model_name}`\n"
            detailed_error += f"**Error details:** {str(e)}\n\n"
            detailed_error += "**✅ General troubleshooting:**\n\n"
            detailed_error += "1. Check deployment logs for more details\n"
            detailed_error += "2. Verify all environment variables are set correctly\n"
            detailed_error += "3. Confirm Anthropic API is operational: https://status.anthropic.com/\n"
            detailed_error += "4. Try redeploying your bot\n"
        
        return detailed_error


# Store recent messages in memory (in production, use a database)
chat_message_store = {}
MAX_STORED_MESSAGES = 100


async def store_message(update: Update):
    """Store messages in memory for later summarization"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    
    # Initialize storage for this chat if not exists
    if chat_id not in chat_message_store:
        chat_message_store[chat_id] = []
    
    # Store message data
    message_data = {
        'text': update.message.text,
        'username': update.message.from_user.username or update.message.from_user.first_name or "Unknown",
        'timestamp': update.message.date.strftime('%H:%M:%S'),
        'date': update.message.date
    }
    
    chat_message_store[chat_id].append(message_data)
    
    # Keep only the last MAX_STORED_MESSAGES
    if len(chat_message_store[chat_id]) > MAX_STORED_MESSAGES:
        chat_message_store[chat_id] = chat_message_store[chat_id][-MAX_STORED_MESSAGES:]


async def get_stored_messages(chat_id: int, limit: int = MESSAGE_LIMIT) -> List[dict]:
    """Retrieve stored messages for a chat"""
    if chat_id not in chat_message_store:
        return []
    
    messages = chat_message_store[chat_id]
    
    # Filter by age - use timezone-aware datetime (UTC)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=MAX_MESSAGE_AGE_HOURS)
    recent_messages = [
        msg for msg in messages
        if msg.get('date') and msg['date'] > cutoff_time
    ]
    
    # Return the last 'limit' messages
    return recent_messages[-limit:]


async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when the bot is mentioned in a message"""
    # Store this message first
    await store_message(update)
    
    # Reuse the summary request handler
    await handle_summary_request(update, context, MESSAGE_LIMIT)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /summary and /summarize commands with optional number parameter"""
    # Store this message
    await store_message(update)
    
    # Check if a custom message limit was provided
    custom_limit = MESSAGE_LIMIT
    if context.args and len(context.args) > 0:
        try:
            custom_limit = int(context.args[0])
            # Enforce reasonable limits
            if custom_limit < 1:
                custom_limit = 1
            elif custom_limit > MAX_STORED_MESSAGES:
                custom_limit = MAX_STORED_MESSAGES
        except ValueError:
            # If the argument is not a valid number, use default
            pass
    
    # Use custom handler logic with custom limit
    await handle_summary_request(update, context, custom_limit)


async def handle_summary_request(update: Update, context: ContextTypes.DEFAULT_TYPE, message_limit: int = MESSAGE_LIMIT):
    """Handle summary request with custom message limit"""
    try:
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        # Bot now works in both group chats and private chats
        # No chat type restriction needed
        
        # Send a "working on it" message
        status_message = await update.message.reply_text("🤔 Let me read through the recent messages and create a summary for you...")
        
        # Get stored messages with custom limit
        messages = await get_stored_messages(chat_id, message_limit)
        
        logger.info(f"Found {len(messages)} messages to summarize for chat {chat_id}")
        
        if not messages:
            await status_message.edit_text(
                "⚠️ I don't have enough message history to create a summary yet.\n\n"
                "I can only see messages sent after I was added to this group. "
                "Once there's more conversation, mention me again and I'll create a summary! 📝"
            )
            return
        
        # Format messages
        messages_text = format_messages_for_summary(messages)
        
        # Generate summary
        summary = await generate_summary(messages_text)
        
        # Send the summary
        response = f"{summary}\n\n📊 Summarized {len(messages)} messages from the last {MAX_MESSAGE_AGE_HOURS} hours."
        
        await status_message.edit_text(response)
        
    except Exception as e:
        logger.error(f"Error handling summary request: {e}")
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease try again later."
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages to store them"""
    await store_message(update)


def main():
    """Start the bot"""
    # Get configuration from environment variables
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY not found in environment variables!")
        raise ValueError("ANTHROPIC_API_KEY is required")
    
    # Create the Application
    application = Application.builder().token(telegram_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("summarize", summary_command))  # Also support /summarize
    
    # Register handler for mentions (when bot is tagged)
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Entity("mention") | filters.Entity("text_mention"),
        handle_mention
    ))
    
    # Register handler to store all text messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    ))
    
    # Log startup
    logger.info("Bot is starting...")
    logger.info(f"Message limit: {MESSAGE_LIMIT}")
    logger.info(f"Max message age: {MAX_MESSAGE_AGE_HOURS} hours")
    
    # Log Claude model configuration
    configured_model = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
    if os.getenv('CLAUDE_MODEL'):
        logger.warning(f"⚠️ CLAUDE_MODEL environment variable is SET to: {configured_model}")
        logger.warning("   This will override the default model (Haiku) in the code!")
        logger.warning("   If you're experiencing 404 errors, DELETE this environment variable!")
    else:
        logger.info(f"✓ Using default Claude model: {configured_model} (Haiku - works for all API tiers)")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
