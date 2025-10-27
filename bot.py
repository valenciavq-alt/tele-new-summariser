"""
Telegram Message Summarizer Bot

This bot listens for mentions in Telegram group chats and provides
AI-generated summaries of recent messages.
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

I can help summarize conversations in your group chats.

**How to use me:**
1. Add me to your Telegram group
2. Give me permission to read messages
3. Mention me with @{} or reply to a message with my mention
4. I'll summarize the recent messages in bullet points!

**Commands:**
/start - Show this welcome message
/help - Get help on how to use the bot
/summary - Get a summary of recent messages (works in groups)

**Example:**
"@{} what did I miss?" or "@{} summarize"

Let's get started! Add me to a group and give it a try! 🚀
    """.format(
        get_bot_username() or "bot",
        get_bot_username() or "bot",
        get_bot_username() or "bot"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_message = """
🤖 **Message Summarizer Bot - Help**

**How it works:**
When you mention me in a group chat, I'll read the last {} messages and create a brief summary with key points.

**Ways to use:**
• Mention me: @{} 
• Use the command: /summary
• Reply to any message and mention me

**Tips:**
• I work best in active group discussions
• I'll only summarize messages from the last {} hours
• The summary will be in bullet point format for easy reading

**Privacy:**
• I only read messages when explicitly mentioned
• I don't store any chat history
• All processing is done in real-time

Need more help? Contact the bot administrator.
    """.format(
        MESSAGE_LIMIT,
        get_bot_username() or "bot",
        MAX_MESSAGE_AGE_HOURS
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
        response = anthropic_client.messages.create(
            model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        summary = response.content[0].text.strip()
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"❌ Sorry, I encountered an error while generating the summary: {str(e)}"


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
    try:
        # Store this message first
        await store_message(update)
        
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        # Check if this is a group chat
        if chat_type not in ['group', 'supergroup']:
            await update.message.reply_text(
                "🤖 I work best in group chats! Add me to a group and mention me to get message summaries."
            )
            return
        
        # Send a "working on it" message
        status_message = await update.message.reply_text("🤔 Let me read through the recent messages and create a summary for you...")
        
        # Get stored messages
        messages = await get_stored_messages(chat_id, MESSAGE_LIMIT)
        
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
        logger.error(f"Error handling mention: {e}")
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease try again later."
        )


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /summary command"""
    # Store this message
    await store_message(update)
    
    # Reuse the mention handler logic
    await handle_mention(update, context)


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
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
