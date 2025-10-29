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
from typing import List, Optional, Dict
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

# Import database and timeframe parser modules
from database import db_manager
from timeframe_parser import TimeframeParser, parse_timeframe

# Import cost tracker module
from cost_tracker import initialize_cost_tracker, get_cost_tracker

# Import smart sampler module
from smart_sampler import get_smart_sampler

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

# Admin configuration for cost tracking notifications
# Set ADMIN_USER_ID in environment to receive budget warnings
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')  # Your Telegram user ID


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
/usage - Check current API usage and budget status

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
    
    # Check if database is enabled to provide accurate info
    storage_info = "PostgreSQL database" if db_manager.enabled else f"last {MAX_STORED_MESSAGES} messages in memory"
    
    help_message = """
🤖 **Message Summarizer Bot - Help**

**How it works:**
I can summarize messages in both group chats and private chats using AI!

**Basic Usage:**

**In Group Chats:**
• Mention me: @{} 
• Use the command: `/summarize`
• Reply to any message and mention me

**In Private Chats:**
• Use the command: `/summarize`
• I'll summarize our recent conversation

**Advanced Features - Custom Timeframes:**

You can now specify custom timeframes for summaries!

**Examples:**
• `/summarize` - Default (last {} messages)
• `/summarize 50` - Summarize last 50 messages

**Shorthand Syntax (NEW):** ⭐
• `/summarize 24h` - Last 24 hours
• `/summarize 60d` - Last 60 days
• `/summarize 2mo` - Last 2 months
• `/summarize 3w` - Last 3 weeks

**Natural Language:**
• `/summarize today` - Today's messages
• `/summarize yesterday` - Yesterday's messages
• `/summarize last 2 hours` - Last 2 hours
• `/summarize last 3 days` - Last 3 days
• `/summarize last 1 week` - Last week
• `/summarize from 2024-01-15 to 2024-01-20` - Specific date range
• `/summarize on 2024-01-15` - Specific day

**Smart Features:**
• **Hard Limits:** Max 1000 messages per request
• **Smart Sampling:** Auto-sampling for large timeframes
• **Cost Warnings:** Alerts before expensive operations
• **Budget Protection:** Monthly spending limits

**Storage:**
• Messages are stored in: {}
• Summaries are in bullet point format for easy reading

**Privacy:**
• In groups: I only process messages when explicitly mentioned or commanded
• In private: I only summarize when you use /summarize
• All summaries are processed in real-time with Claude AI

**Budget & Usage:**
• Use `/usage` to check current API usage and budget
• The bot has a monthly budget limit to control costs
• Budget automatically resets on the 1st of each month

Need more help? Contact the bot administrator.
    """.format(
        get_bot_username() or "bot",
        MESSAGE_LIMIT,
        storage_info
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


def estimate_api_cost(message_count: int, messages_text: Optional[str] = None) -> Dict:
    """
    Estimate the API cost for processing messages
    
    Args:
        message_count: Number of messages to be processed
        messages_text: Optional formatted messages text for precise estimation
    
    Returns:
        Dict with cost estimation details:
        {
            'estimated_input_tokens': int,
            'estimated_output_tokens': int,
            'estimated_cost': float,
            'warning_threshold_exceeded': bool
        }
    """
    # Token estimation (conservative estimates)
    # Average message: ~50 tokens, plus prompt overhead (~200 tokens)
    # Output: typically 100-500 tokens depending on message count
    
    if messages_text:
        # More precise estimation based on actual text
        # Rough approximation: 1 token ≈ 4 characters
        estimated_input_tokens = len(messages_text) // 4 + 300  # +300 for prompt
    else:
        # Rough estimation based on message count
        estimated_input_tokens = (message_count * 50) + 300
    
    # Output tokens scale with input but are typically smaller
    estimated_output_tokens = min(500, max(100, message_count // 2))
    
    # Calculate cost using Claude Haiku pricing
    INPUT_TOKEN_COST = 0.25 / 1_000_000  # $0.25 per 1M tokens
    OUTPUT_TOKEN_COST = 1.25 / 1_000_000  # $1.25 per 1M tokens
    
    estimated_cost = (
        (estimated_input_tokens * INPUT_TOKEN_COST) +
        (estimated_output_tokens * OUTPUT_TOKEN_COST)
    )
    
    # Warning threshold: $0.50
    WARNING_THRESHOLD = 0.50
    
    return {
        'estimated_input_tokens': estimated_input_tokens,
        'estimated_output_tokens': estimated_output_tokens,
        'estimated_cost': estimated_cost,
        'warning_threshold_exceeded': estimated_cost > WARNING_THRESHOLD,
        'warning_threshold': WARNING_THRESHOLD
    }


def check_database_availability_for_timeframe(
    timeframe_str: Optional[str],
    start_time: Optional[datetime]
) -> Optional[str]:
    """
    Check if database is needed for the requested timeframe
    
    Args:
        timeframe_str: Human-readable timeframe description
        start_time: Start time of the timeframe
    
    Returns:
        Warning message if database is needed but not available, None otherwise
    """
    if start_time is None:
        # Count-based query, no issue
        return None
    
    if db_manager.enabled:
        # Database is available, no issue
        return None
    
    # Calculate timeframe length
    now = datetime.now(timezone.utc)
    timeframe_length = (now - start_time).total_seconds() / 3600  # in hours
    
    # If timeframe is longer than MAX_MESSAGE_AGE_HOURS, warn user
    if timeframe_length > MAX_MESSAGE_AGE_HOURS:
        warning = (
            f"⚠️ **Database Not Configured**\n\n"
            f"You're querying a timeframe of **{timeframe_str}**, but the bot is running "
            f"without a persistent database.\n\n"
            f"**This means:**\n"
            f"• Only messages from the last **{MAX_MESSAGE_AGE_HOURS} hours** are available\n"
            f"• Only the last **{MAX_STORED_MESSAGES} messages** are kept in memory\n"
            f"• Message history is lost when the bot restarts\n\n"
            f"**To access longer history:**\n"
            f"1. Set up a PostgreSQL database (see README.md)\n"
            f"2. Add the `DATABASE_URL` environment variable\n"
            f"3. Redeploy the bot\n\n"
            f"I'll search the available messages, but results may be limited."
        )
        return warning
    
    return None


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


async def generate_summary(messages_text: str, context: ContextTypes.DEFAULT_TYPE = None) -> str:
    """
    Generate a summary using Claude API (Anthropic)
    
    Args:
        messages_text: Formatted string of messages to summarize
        context: Telegram context for sending admin notifications (optional)
    
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
        
        # Check budget before making API call
        tracker = get_cost_tracker()
        if tracker:
            can_proceed, error_msg = tracker.can_make_request(estimated_tokens=2000)
            if not can_proceed:
                logger.warning("Budget limit reached, blocking API request")
                return error_msg
        
        # Create the prompt for Claude
        prompt = f"""Hey! Can you summarize these messages for me? Give me the highlights in a casual, easy-to-read way with bullet points.

⚠️ CRITICAL RULES - READ CAREFULLY:
• ONLY use information that's ACTUALLY in the messages below
• DO NOT make up names, events, details, or anything else
• DO NOT invent conversations or assume things that weren't said
• DO NOT add creative interpretations or fill in gaps
• If someone's name appears in the messages, use it. If not, don't make one up.
• If there's nothing really significant to summarize, just say so - don't force it

Give me:
• The key points and highlights
• Who said what (if relevant)
• Any important decisions, plans, or questions
• Anything funny or noteworthy that actually happened

Format: Use bullet points to make it scannable and easy to read.

Tone: Keep it friendly and conversational, like you're texting a friend to catch them up. But remember - only tell me what ACTUALLY happened in these messages!

Messages:
{messages_text}

Remember: If the messages are just random small talk with nothing important, it's totally fine to say "Just some casual chat, nothing major!" Don't fabricate significance that isn't there."""
        
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
        
        # Track the cost after successful API call
        if tracker:
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            cost_info = tracker.track_request(input_tokens, output_tokens)
            logger.info(f"Cost tracked: ${cost_info['request_cost']:.6f} (Total: ${cost_info['total_cost']:.4f}, {cost_info['budget_used_pct']:.1f}% of budget)")
            
            # Check if we've crossed any warning thresholds
            warning = tracker.check_warning_thresholds()
            if warning and context and ADMIN_USER_ID:
                try:
                    # Send warning to admin
                    await context.bot.send_message(
                        chat_id=int(ADMIN_USER_ID),
                        text=warning['message'],
                        parse_mode='Markdown'
                    )
                    logger.info(f"Sent {warning['threshold']}% budget warning to admin")
                except Exception as e:
                    logger.error(f"Failed to send budget warning to admin: {e}")
        
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
    """Store messages in memory and/or database for later summarization"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    user_id = update.message.from_user.id if update.message.from_user else None
    username = update.message.from_user.username or update.message.from_user.first_name or "Unknown"
    text = update.message.text
    timestamp = update.message.date
    
    # Store in database if available
    if db_manager.enabled:
        await db_manager.store_message(
            chat_id=chat_id,
            message_id=message_id,
            user_id=user_id,
            username=username,
            text=text,
            timestamp=timestamp
        )
    
    # Also store in memory as fallback/cache
    # Initialize storage for this chat if not exists
    if chat_id not in chat_message_store:
        chat_message_store[chat_id] = []
    
    # Store message data
    message_data = {
        'message_id': message_id,
        'user_id': user_id,
        'text': text,
        'username': username,
        'timestamp': timestamp.strftime('%H:%M:%S'),
        'date': timestamp
    }
    
    chat_message_store[chat_id].append(message_data)
    
    # Keep only the last MAX_STORED_MESSAGES in memory
    if len(chat_message_store[chat_id]) > MAX_STORED_MESSAGES:
        chat_message_store[chat_id] = chat_message_store[chat_id][-MAX_STORED_MESSAGES:]


async def get_stored_messages(
    chat_id: int,
    limit: int = MESSAGE_LIMIT,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[dict]:
    """
    Retrieve stored messages for a chat
    
    Args:
        chat_id: Telegram chat ID
        limit: Maximum number of messages to retrieve (used when start_time is None)
        start_time: Optional start time for timeframe filtering
        end_time: Optional end time for timeframe filtering
    
    Returns:
        List of message dictionaries
    """
    # If timeframe is specified, use database (if available) or filter in-memory
    if start_time is not None:
        # Try database first
        if db_manager.enabled:
            return await db_manager.get_messages_by_timeframe(
                chat_id=chat_id,
                start_time=start_time,
                end_time=end_time
            )
        
        # Fall back to in-memory with timeframe filter
        if chat_id not in chat_message_store:
            return []
        
        messages = chat_message_store[chat_id]
        end_time = end_time or datetime.now(timezone.utc)
        
        # Filter by timeframe
        filtered_messages = [
            msg for msg in messages
            if msg.get('date') and start_time <= msg['date'] <= end_time
        ]
        
        return filtered_messages
    
    # Otherwise, use count-based retrieval
    # Try database first
    if db_manager.enabled:
        return await db_manager.get_messages_by_count(
            chat_id=chat_id,
            limit=limit,
            max_age_hours=MAX_MESSAGE_AGE_HOURS
        )
    
    # Fall back to in-memory storage
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
    """Handle the /summary and /summarize commands with optional parameters"""
    # Store this message
    await store_message(update)
    
    # Parse arguments
    start_time = None
    end_time = None
    custom_limit = MESSAGE_LIMIT
    timeframe_str = None
    
    if context.args and len(context.args) > 0:
        # Join all arguments to handle multi-word timeframes
        args_text = ' '.join(context.args)
        
        # Try parsing as a number first (backward compatibility)
        if len(context.args) == 1:
            try:
                custom_limit = int(context.args[0])
                # Enforce reasonable limits
                if custom_limit < 1:
                    custom_limit = 1
                elif custom_limit > MAX_STORED_MESSAGES:
                    custom_limit = MAX_STORED_MESSAGES
            except ValueError:
                # Not a number, try parsing as timeframe
                parser = TimeframeParser()
                timeframe_result = parser.parse(args_text)
                
                if timeframe_result:
                    start_time, end_time = timeframe_result
                    timeframe_str = args_text
                else:
                    # Invalid timeframe format
                    await update.message.reply_text(
                        "❌ Invalid timeframe format.\n\n"
                        "**Valid formats:**\n"
                        "• `/summarize 50` - Last 50 messages\n"
                        "• `/summarize 24h` - Last 24 hours (shorthand)\n"
                        "• `/summarize 60d` - Last 60 days (shorthand)\n"
                        "• `/summarize 2mo` - Last 2 months (shorthand)\n"
                        "• `/summarize today`\n"
                        "• `/summarize yesterday`\n"
                        "• `/summarize last 2 hours`\n"
                        "• `/summarize last 3 days`\n"
                        "• `/summarize from 2024-01-15 to 2024-01-20`\n"
                        "• `/summarize on 2024-01-15`",
                        parse_mode='Markdown'
                    )
                    return
        else:
            # Multiple arguments - must be a timeframe
            parser = TimeframeParser()
            timeframe_result = parser.parse(args_text)
            
            if timeframe_result:
                start_time, end_time = timeframe_result
                timeframe_str = args_text
            else:
                # Invalid timeframe format
                await update.message.reply_text(
                    "❌ Invalid timeframe format.\n\n"
                    "**Valid formats:**\n"
                    "• `/summarize 50` - Last 50 messages\n"
                    "• `/summarize 24h` - Last 24 hours (shorthand)\n"
                    "• `/summarize 60d` - Last 60 days (shorthand)\n"
                    "• `/summarize 2mo` - Last 2 months (shorthand)\n"
                    "• `/summarize today`\n"
                    "• `/summarize yesterday`\n"
                    "• `/summarize last 2 hours`\n"
                    "• `/summarize last 3 days`\n"
                    "• `/summarize from 2024-01-15 to 2024-01-20`\n"
                    "• `/summarize on 2024-01-15`",
                    parse_mode='Markdown'
                )
                return
    
    # Use custom handler logic with parsed parameters
    await handle_summary_request(
        update, 
        context, 
        message_limit=custom_limit,
        start_time=start_time,
        end_time=end_time,
        timeframe_str=timeframe_str
    )


async def handle_summary_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_limit: int = MESSAGE_LIMIT,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    timeframe_str: Optional[str] = None
):
    """
    Handle summary request with custom parameters
    
    This function now includes:
    - Database requirement checks for long timeframes
    - Hard message limits with smart sampling
    - Cost estimation and warnings
    - User confirmation for expensive operations
    
    Args:
        update: Telegram update object
        context: Telegram context
        message_limit: Number of messages to summarize (when timeframe not specified)
        start_time: Optional start time for timeframe filtering
        end_time: Optional end time for timeframe filtering
        timeframe_str: Optional human-readable timeframe description
    """
    try:
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        # Bot now works in both group chats and private chats
        # No chat type restriction needed
        
        # STEP 1: Check database availability for timeframe queries
        db_warning = check_database_availability_for_timeframe(timeframe_str, start_time)
        if db_warning:
            # Send warning but continue processing
            await update.message.reply_text(db_warning, parse_mode='Markdown')
            # Brief pause for user to read
            await asyncio.sleep(2)
        
        # Send a "working on it" message
        status_message = await update.message.reply_text("🤔 Let me read through the recent messages and create a summary for you...")
        
        # STEP 2: Get stored messages with custom limit or timeframe
        if start_time is not None:
            # Timeframe-based retrieval
            messages = await get_stored_messages(
                chat_id=chat_id,
                start_time=start_time,
                end_time=end_time
            )
        else:
            # Count-based retrieval
            messages = await get_stored_messages(chat_id, message_limit)
        
        logger.info(f"Found {len(messages)} messages to summarize for chat {chat_id}")
        
        if not messages:
            if start_time is not None:
                await status_message.edit_text(
                    f"⚠️ No messages found for the timeframe: **{timeframe_str}**\n\n"
                    "Try a different timeframe or check if I was active during that period.",
                    parse_mode='Markdown'
                )
            else:
                await status_message.edit_text(
                    "⚠️ I don't have enough message history to create a summary yet.\n\n"
                    "I can only see messages sent after I was added to this group. "
                    "Once there's more conversation, mention me again and I'll create a summary! 📝"
                )
            return
        
        # STEP 3: Check message count and apply smart sampling if needed
        sampler = get_smart_sampler()
        check_result = sampler.check_message_count(len(messages))
        
        original_message_count = len(messages)
        sampling_applied = False
        
        if check_result['should_sample']:
            # Inform user about sampling
            if check_result['warning_message']:
                await status_message.edit_text(check_result['warning_message'], parse_mode='Markdown')
                await asyncio.sleep(2)  # Let user read the message
            
            # Apply smart sampling
            messages = sampler.sample_messages(
                messages,
                check_result['recommended_sample_size']
            )
            sampling_applied = True
            logger.info(f"Smart sampling applied: {original_message_count} → {len(messages)} messages")
        
        # STEP 4: Format messages for API
        messages_text = format_messages_for_summary(messages)
        
        # STEP 5: Estimate cost and warn if expensive
        cost_estimate = estimate_api_cost(len(messages), messages_text)
        
        if cost_estimate['warning_threshold_exceeded']:
            # Warn user about high cost
            warning_msg = (
                f"⚠️ **High Cost Warning**\n\n"
                f"This summary will be expensive:\n"
                f"• Estimated cost: **${cost_estimate['estimated_cost']:.4f}**\n"
                f"• Estimated tokens: ~{cost_estimate['estimated_input_tokens'] + cost_estimate['estimated_output_tokens']:,}\n"
                f"• Warning threshold: ${cost_estimate['warning_threshold']:.2f}\n\n"
                f"📊 Processing {len(messages):,} messages"
            )
            if sampling_applied:
                warning_msg += f" (sampled from {original_message_count:,})"
            warning_msg += "\n\n⚡ Proceeding with summary generation..."
            
            await status_message.edit_text(warning_msg, parse_mode='Markdown')
            await asyncio.sleep(2)
            
            # Check budget before proceeding
            tracker = get_cost_tracker()
            if tracker:
                can_proceed, budget_error = tracker.can_make_request(
                    estimated_tokens=cost_estimate['estimated_input_tokens'] + cost_estimate['estimated_output_tokens']
                )
                if not can_proceed:
                    await status_message.edit_text(budget_error, parse_mode='Markdown')
                    return
        
        # Update status
        await status_message.edit_text("🤖 Generating AI summary...", parse_mode='Markdown')
        
        # STEP 6: Generate summary (pass context for admin notifications)
        summary = await generate_summary(messages_text, context)
        
        # STEP 7: Prepare response with appropriate context
        response_parts = [summary]
        
        # Add statistics
        stats_line = f"\n\n📊 Summarized **{len(messages):,} messages**"
        if sampling_applied:
            stats_line += f" (intelligently sampled from **{original_message_count:,} messages**)"
        
        if start_time is not None:
            # Format the dates nicely
            start_str = start_time.strftime('%Y-%m-%d %H:%M UTC')
            end_str = end_time.strftime('%Y-%m-%d %H:%M UTC') if end_time else 'now'
            stats_line += f" from **{timeframe_str}**\n⏰ ({start_str} to {end_str})"
        else:
            stats_line += f" from the last {MAX_MESSAGE_AGE_HOURS} hours"
        
        response_parts.append(stats_line)
        
        # Add cost info if significant
        if cost_estimate['estimated_cost'] > 0.01:  # More than 1 cent
            response_parts.append(f"\n💰 Estimated cost: ${cost_estimate['estimated_cost']:.4f}")
        
        response = "".join(response_parts)
        
        await status_message.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error handling summary request: {e}")
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease try again later."
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages to store them"""
    await store_message(update)


async def usage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /usage command - show current month's spending"""
    try:
        tracker = get_cost_tracker()
        if not tracker:
            await update.message.reply_text(
                "❌ Cost tracking is not enabled.",
                parse_mode='Markdown'
            )
            return
        
        # Get formatted usage message
        usage_msg = tracker.get_formatted_usage_message()
        
        await update.message.reply_text(usage_msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error handling /usage command: {e}")
        await update.message.reply_text(
            f"❌ Error retrieving usage statistics: {str(e)}"
        )


async def resetusage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /resetusage command - manually reset usage (admin only)"""
    try:
        # Check if user is admin
        user_id = update.effective_user.id
        
        if not ADMIN_USER_ID:
            await update.message.reply_text(
                "❌ Admin user not configured. Set ADMIN_USER_ID environment variable.",
                parse_mode='Markdown'
            )
            return
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text(
                "🚫 Unauthorized. This command is only available to the bot administrator.",
                parse_mode='Markdown'
            )
            logger.warning(f"Unauthorized /resetusage attempt by user {user_id}")
            return
        
        tracker = get_cost_tracker()
        if not tracker:
            await update.message.reply_text(
                "❌ Cost tracking is not enabled.",
                parse_mode='Markdown'
            )
            return
        
        # Reset usage
        previous_stats = tracker.reset_usage()
        
        msg = (
            f"✅ **Usage Reset Complete**\n\n"
            f"**Previous Month Statistics:**\n"
            f"• Period: {previous_stats['month']}\n"
            f"• Total cost: ${previous_stats['total_cost']:.4f}\n"
            f"• Input tokens: {previous_stats['input_tokens']:,}\n"
            f"• Output tokens: {previous_stats['output_tokens']:,}\n"
            f"• Requests: {previous_stats['request_count']}\n\n"
            f"**Current Month:**\n"
            f"• All counters have been reset to zero\n"
            f"• Fresh budget of ${tracker.monthly_budget:.2f} available"
        )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        logger.info(f"Usage manually reset by admin (user {user_id})")
        
    except Exception as e:
        logger.error(f"Error handling /resetusage command: {e}")
        await update.message.reply_text(
            f"❌ Error resetting usage: {str(e)}"
        )


async def initialize_database():
    """Initialize database connection on startup"""
    await db_manager.initialize()


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
    
    # Initialize database
    logger.info("Initializing database connection...")
    asyncio.get_event_loop().run_until_complete(initialize_database())
    
    if db_manager.enabled:
        logger.info("✅ Database enabled - messages will be stored in PostgreSQL")
    else:
        logger.info("ℹ️ Database not configured - using in-memory storage (last 100 messages)")
    
    # Initialize cost tracker
    logger.info("Initializing cost tracking system...")
    monthly_budget = float(os.getenv('MONTHLY_BUDGET', '10.0'))
    initialize_cost_tracker(monthly_budget=monthly_budget)
    logger.info(f"✅ Cost tracking enabled with ${monthly_budget:.2f} monthly budget")
    
    if ADMIN_USER_ID:
        logger.info(f"✅ Admin notifications enabled for user ID: {ADMIN_USER_ID}")
    else:
        logger.warning("⚠️ ADMIN_USER_ID not set - budget warnings will not be sent")
    
    # Create the Application
    application = Application.builder().token(telegram_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("summarize", summary_command))  # Also support /summarize
    application.add_handler(CommandHandler("usage", usage_command))
    application.add_handler(CommandHandler("resetusage", resetusage_command))
    
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
