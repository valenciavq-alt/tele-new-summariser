"""
Timeframe Parser Module

Parses natural language timeframe expressions into datetime ranges.
Supports both relative timeframes (e.g., "last 2 hours") and absolute dates.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TimeframeParser:
    """Parses natural language timeframe expressions"""
    
    # Regular expression patterns
    RELATIVE_PATTERN = re.compile(
        r'^last\s+(\d+)\s+(hour|hours|day|days|week|weeks)$',
        re.IGNORECASE
    )
    
    DATE_RANGE_PATTERN = re.compile(
        r'^from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})$',
        re.IGNORECASE
    )
    
    SINGLE_DATE_PATTERN = re.compile(
        r'^on\s+(\d{4}-\d{2}-\d{2})$',
        re.IGNORECASE
    )
    
    def __init__(self, timezone_offset: Optional[timedelta] = None):
        """
        Initialize timeframe parser
        
        Args:
            timezone_offset: Optional timezone offset from UTC
        """
        self.timezone_offset = timezone_offset or timedelta(0)
    
    def parse(self, text: str) -> Optional[Tuple[datetime, Optional[datetime]]]:
        """
        Parse a timeframe expression into start and end datetime
        
        Args:
            text: Natural language timeframe expression
            
        Returns:
            Tuple of (start_time, end_time) or None if parsing fails
            end_time can be None for open-ended ranges
        """
        text = text.strip().lower()
        
        # Try parsing "today"
        if text == 'today':
            return self._parse_today()
        
        # Try parsing "yesterday"
        if text == 'yesterday':
            return self._parse_yesterday()
        
        # Try parsing relative timeframes (e.g., "last 2 hours")
        relative_match = self.RELATIVE_PATTERN.match(text)
        if relative_match:
            return self._parse_relative(relative_match)
        
        # Try parsing date ranges (e.g., "from 2024-01-15 to 2024-01-20")
        range_match = self.DATE_RANGE_PATTERN.match(text)
        if range_match:
            return self._parse_date_range(range_match)
        
        # Try parsing single date (e.g., "on 2024-01-15")
        single_match = self.SINGLE_DATE_PATTERN.match(text)
        if single_match:
            return self._parse_single_date(single_match)
        
        # No match found
        return None
    
    def _parse_today(self) -> Tuple[datetime, datetime]:
        """Parse 'today' timeframe"""
        now = datetime.now(timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return (start_of_today, end_of_today)
    
    def _parse_yesterday(self) -> Tuple[datetime, datetime]:
        """Parse 'yesterday' timeframe"""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return (start_of_yesterday, end_of_yesterday)
    
    def _parse_relative(self, match: re.Match) -> Tuple[datetime, datetime]:
        """
        Parse relative timeframes like 'last 2 hours', 'last 3 days'
        
        Args:
            match: Regex match object
            
        Returns:
            Tuple of (start_time, end_time)
        """
        amount = int(match.group(1))
        unit = match.group(2).lower()
        
        now = datetime.now(timezone.utc)
        
        # Normalize unit to singular form
        if unit.endswith('s'):
            unit = unit[:-1]
        
        # Calculate timedelta based on unit
        if unit == 'hour':
            delta = timedelta(hours=amount)
        elif unit == 'day':
            delta = timedelta(days=amount)
        elif unit == 'week':
            delta = timedelta(weeks=amount)
        else:
            # Should not happen due to regex, but just in case
            delta = timedelta(hours=24)
        
        start_time = now - delta
        end_time = now
        
        return (start_time, end_time)
    
    def _parse_date_range(self, match: re.Match) -> Tuple[datetime, datetime]:
        """
        Parse date ranges like 'from 2024-01-15 to 2024-01-20'
        
        Args:
            match: Regex match object
            
        Returns:
            Tuple of (start_time, end_time)
        """
        start_date_str = match.group(1)
        end_date_str = match.group(2)
        
        try:
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Set to start of start_date and end of end_date
            start_time = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            end_time = end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
            )
            
            # Validate that start is before end
            if start_time > end_time:
                logger.warning(f"Invalid date range: start ({start_date_str}) is after end ({end_date_str})")
                return None
            
            return (start_time, end_time)
            
        except ValueError as e:
            logger.error(f"Error parsing date range: {e}")
            return None
    
    def _parse_single_date(self, match: re.Match) -> Tuple[datetime, datetime]:
        """
        Parse single date like 'on 2024-01-15'
        
        Args:
            match: Regex match object
            
        Returns:
            Tuple of (start_time, end_time) for the entire day
        """
        date_str = match.group(1)
        
        try:
            # Parse date
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Set to start and end of the day
            start_time = date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            end_time = date.replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
            )
            
            return (start_time, end_time)
            
        except ValueError as e:
            logger.error(f"Error parsing single date: {e}")
            return None
    
    @staticmethod
    def is_timeframe_query(text: str) -> bool:
        """
        Check if the text contains a timeframe expression
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to contain a timeframe expression
        """
        text = text.strip().lower()
        
        # Check for known patterns
        keywords = ['today', 'yesterday', 'last', 'from', 'to', 'on']
        
        # Quick check for date patterns
        if re.search(r'\d{4}-\d{2}-\d{2}', text):
            return True
        
        # Check for keywords
        for keyword in keywords:
            if keyword in text:
                return True
        
        return False
    
    @staticmethod
    def get_examples() -> list:
        """Get list of example timeframe expressions"""
        return [
            "today",
            "yesterday",
            "last 2 hours",
            "last 3 days",
            "last 1 week",
            "from 2024-01-15 to 2024-01-20",
            "on 2024-01-15"
        ]


# Convenience function for direct usage
def parse_timeframe(text: str) -> Optional[Tuple[datetime, Optional[datetime]]]:
    """
    Parse a timeframe expression
    
    Args:
        text: Natural language timeframe expression
        
    Returns:
        Tuple of (start_time, end_time) or None if parsing fails
    """
    parser = TimeframeParser()
    return parser.parse(text)
