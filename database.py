"""
Database module for PostgreSQL message storage

This module provides PostgreSQL database support for storing and retrieving
Telegram messages. It's optional - the bot will fall back to in-memory storage
if DATABASE_URL is not configured.
"""

import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import asyncio

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("asyncpg not installed - database features will be unavailable")

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv('DATABASE_URL')
        self.enabled = False
        
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        if not self.database_url:
            logger.info("DATABASE_URL not set - database features disabled")
            return False
            
        if not ASYNCPG_AVAILABLE:
            logger.warning("asyncpg not available - database features disabled")
            return False
        
        try:
            # Handle Railway/Render postgres:// URLs (need to convert to postgresql://)
            if self.database_url.startswith('postgres://'):
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            # Create tables
            await self._create_tables()
            
            self.enabled = True
            logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("Falling back to in-memory storage")
            self.enabled = False
            return False
    
    async def _create_tables(self):
        """Create the messages table if it doesn't exist"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    user_id BIGINT,
                    username TEXT,
                    text TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    date TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(chat_id, message_id)
                )
            """)
            
            # Create summaries table for tracking usage
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT,
                    message_count INT NOT NULL,
                    input_tokens INT,
                    output_tokens INT,
                    model TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes for better query performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id 
                ON messages(chat_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_date 
                ON messages(chat_id, date DESC)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_summaries_chat_id 
                ON summaries(chat_id)
            """)
            
            logger.info("Database tables created/verified")
    
    async def store_message(
        self,
        chat_id: int,
        message_id: int,
        user_id: Optional[int],
        username: str,
        text: str,
        timestamp: datetime
    ):
        """
        Store a message in the database
        
        Args:
            chat_id: Telegram chat ID
            message_id: Telegram message ID
            user_id: Telegram user ID
            username: Username or first name
            text: Message text
            timestamp: Message timestamp (timezone-aware)
        """
        if not self.enabled or not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO messages (chat_id, message_id, user_id, username, text, timestamp, date)
                    VALUES ($1, $2, $3, $4, $5, $6, $6)
                    ON CONFLICT (chat_id, message_id) DO UPDATE
                    SET text = EXCLUDED.text,
                        username = EXCLUDED.username,
                        timestamp = EXCLUDED.timestamp
                """, chat_id, message_id, user_id, username, text, timestamp)
                
        except Exception as e:
            logger.error(f"Error storing message in database: {e}")
    
    async def get_messages_by_count(
        self,
        chat_id: int,
        limit: int,
        max_age_hours: Optional[int] = None
    ) -> List[Dict]:
        """
        Get the most recent N messages from a chat
        
        Args:
            chat_id: Telegram chat ID
            limit: Maximum number of messages to retrieve
            max_age_hours: Optional maximum age of messages in hours
            
        Returns:
            List of message dictionaries
        """
        if not self.enabled or not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                if max_age_hours:
                    # Query with age filter
                    rows = await conn.fetch("""
                        SELECT message_id, user_id, username, text, timestamp, date
                        FROM messages
                        WHERE chat_id = $1
                          AND date > NOW() - INTERVAL '1 hour' * $2
                        ORDER BY date DESC
                        LIMIT $3
                    """, chat_id, max_age_hours, limit)
                else:
                    # Query without age filter
                    rows = await conn.fetch("""
                        SELECT message_id, user_id, username, text, timestamp, date
                        FROM messages
                        WHERE chat_id = $1
                        ORDER BY date DESC
                        LIMIT $2
                    """, chat_id, limit)
                
                # Convert to list of dicts and reverse to chronological order
                messages = [
                    {
                        'message_id': row['message_id'],
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'text': row['text'],
                        'timestamp': row['timestamp'].strftime('%H:%M:%S'),
                        'date': row['date']
                    }
                    for row in rows
                ]
                
                # Reverse to get chronological order (oldest first)
                return list(reversed(messages))
                
        except Exception as e:
            logger.error(f"Error retrieving messages from database: {e}")
            return []
    
    async def get_messages_by_timeframe(
        self,
        chat_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get messages within a specific timeframe
        
        Args:
            chat_id: Telegram chat ID
            start_time: Start of timeframe (timezone-aware)
            end_time: End of timeframe (timezone-aware), defaults to now
            
        Returns:
            List of message dictionaries
        """
        if not self.enabled or not self.pool:
            return []
        
        if end_time is None:
            end_time = datetime.now(timezone.utc)
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT message_id, user_id, username, text, timestamp, date
                    FROM messages
                    WHERE chat_id = $1
                      AND date >= $2
                      AND date <= $3
                    ORDER BY date ASC
                """, chat_id, start_time, end_time)
                
                messages = [
                    {
                        'message_id': row['message_id'],
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'text': row['text'],
                        'timestamp': row['timestamp'].strftime('%H:%M:%S'),
                        'date': row['date']
                    }
                    for row in rows
                ]
                
                return messages
                
        except Exception as e:
            logger.error(f"Error retrieving messages by timeframe from database: {e}")
            return []
    
    async def get_message_count(self, chat_id: int) -> int:
        """Get total message count for a chat"""
        if not self.enabled or not self.pool:
            return 0
        
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM messages
                    WHERE chat_id = $1
                """, chat_id)
                return count or 0
                
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0
    
    async def cleanup_old_messages(self, days: int = 30):
        """
        Clean up messages older than specified days
        
        Args:
            days: Number of days to keep messages (default: 30)
        """
        if not self.enabled or not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                deleted = await conn.execute("""
                    DELETE FROM messages
                    WHERE date < NOW() - INTERVAL '1 day' * $1
                """, days)
                logger.info(f"Cleaned up old messages: {deleted}")
                
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {e}")
    
    async def track_summary(
        self,
        chat_id: int,
        user_id: Optional[int],
        message_count: int,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        model: str = "claude-3-haiku-20240307"
    ):
        """
        Track a summary generation for usage statistics
        
        Args:
            chat_id: Telegram chat ID
            user_id: Telegram user ID who requested the summary
            message_count: Number of messages summarized
            input_tokens: Number of input tokens used (if available)
            output_tokens: Number of output tokens generated (if available)
            model: Claude model used
        """
        if not self.enabled or not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO summaries (chat_id, user_id, message_count, input_tokens, output_tokens, model)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, chat_id, user_id, message_count, input_tokens, output_tokens, model)
                
        except Exception as e:
            logger.error(f"Error tracking summary: {e}")
    
    async def get_usage_stats(self, chat_id: int) -> Dict:
        """
        Get usage statistics for a chat
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Dictionary with usage statistics
        """
        if not self.enabled or not self.pool:
            return {
                'total_messages': 0,
                'total_summaries': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'oldest_message': None,
                'newest_message': None,
                'database_enabled': False
            }
        
        try:
            async with self.pool.acquire() as conn:
                # Get message statistics
                message_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_messages,
                        MIN(date) as oldest_message,
                        MAX(date) as newest_message
                    FROM messages
                    WHERE chat_id = $1
                """, chat_id)
                
                # Get summary statistics
                summary_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_summaries,
                        COALESCE(SUM(input_tokens), 0) as total_input_tokens,
                        COALESCE(SUM(output_tokens), 0) as total_output_tokens,
                        COALESCE(SUM(message_count), 0) as messages_summarized
                    FROM summaries
                    WHERE chat_id = $1
                """, chat_id)
                
                return {
                    'total_messages': message_stats['total_messages'] or 0,
                    'total_summaries': summary_stats['total_summaries'] or 0,
                    'total_input_tokens': int(summary_stats['total_input_tokens'] or 0),
                    'total_output_tokens': int(summary_stats['total_output_tokens'] or 0),
                    'messages_summarized': int(summary_stats['messages_summarized'] or 0),
                    'oldest_message': message_stats['oldest_message'],
                    'newest_message': message_stats['newest_message'],
                    'database_enabled': True
                }
                
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {
                'total_messages': 0,
                'total_summaries': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'oldest_message': None,
                'newest_message': None,
                'database_enabled': False,
                'error': str(e)
            }
    
    async def get_global_usage_stats(self) -> Dict:
        """
        Get global usage statistics across all chats
        
        Returns:
            Dictionary with global usage statistics
        """
        if not self.enabled or not self.pool:
            return {
                'total_messages': 0,
                'total_summaries': 0,
                'total_chats': 0,
                'database_enabled': False
            }
        
        try:
            async with self.pool.acquire() as conn:
                # Get global message statistics
                message_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(DISTINCT chat_id) as total_chats
                    FROM messages
                """)
                
                # Get global summary statistics
                summary_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_summaries,
                        COALESCE(SUM(input_tokens), 0) as total_input_tokens,
                        COALESCE(SUM(output_tokens), 0) as total_output_tokens
                    FROM summaries
                """)
                
                return {
                    'total_messages': message_stats['total_messages'] or 0,
                    'total_chats': message_stats['total_chats'] or 0,
                    'total_summaries': summary_stats['total_summaries'] or 0,
                    'total_input_tokens': int(summary_stats['total_input_tokens'] or 0),
                    'total_output_tokens': int(summary_stats['total_output_tokens'] or 0),
                    'database_enabled': True
                }
                
        except Exception as e:
            logger.error(f"Error getting global usage stats: {e}")
            return {
                'total_messages': 0,
                'total_summaries': 0,
                'total_chats': 0,
                'database_enabled': False,
                'error': str(e)
            }
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = DatabaseManager()
