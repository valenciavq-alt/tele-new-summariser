"""
Smart Sampling Module

This module provides intelligent message sampling for large message sets.
It helps reduce API costs by selecting the most relevant messages while
preserving context and important information.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartSampler:
    """
    Intelligently samples messages from large sets while preserving context
    
    The sampler prioritizes:
    1. Even distribution across the timeframe
    2. Messages with more engagement (longer text, if reaction data available)
    3. Maintaining chronological flow
    """
    
    # Configuration
    HARD_MESSAGE_LIMIT = 1000  # Absolute maximum messages per request
    SAFE_PROCESSING_LIMIT = 500  # Recommended limit before suggesting sampling
    
    def __init__(self, hard_limit: int = HARD_MESSAGE_LIMIT):
        """
        Initialize the smart sampler
        
        Args:
            hard_limit: Maximum number of messages allowed (default: 1000)
        """
        self.hard_limit = hard_limit
    
    def check_message_count(self, message_count: int) -> Dict:
        """
        Check if message count requires action
        
        Args:
            message_count: Number of messages to be processed
            
        Returns:
            Dict with status and recommendation:
            {
                'status': 'ok' | 'suggest_sampling' | 'require_sampling',
                'message_count': int,
                'should_sample': bool,
                'recommended_sample_size': int,
                'warning_message': Optional[str]
            }
        """
        result = {
            'message_count': message_count,
            'should_sample': False,
            'recommended_sample_size': message_count,
            'warning_message': None
        }
        
        if message_count > self.hard_limit:
            # Exceeds hard limit - must sample
            result['status'] = 'require_sampling'
            result['should_sample'] = True
            result['recommended_sample_size'] = self.hard_limit
            result['warning_message'] = (
                f"⚠️ **Message Limit Exceeded**\n\n"
                f"Found **{message_count:,} messages** but the maximum allowed is **{self.hard_limit:,}**.\n\n"
                f"🤖 **Smart Sampling will be used:**\n"
                f"• I'll intelligently select {self.hard_limit:,} representative messages\n"
                f"• Messages will be evenly distributed across the timeframe\n"
                f"• Longer, more substantive messages will be prioritized\n"
                f"• The summary will still capture the key themes and discussions\n\n"
                f"Proceeding with smart sampling..."
            )
        elif message_count > self.SAFE_PROCESSING_LIMIT:
            # Suggest sampling for efficiency
            result['status'] = 'suggest_sampling'
            result['should_sample'] = True
            result['recommended_sample_size'] = self.SAFE_PROCESSING_LIMIT
            result['warning_message'] = (
                f"📊 **Large Message Set Detected**\n\n"
                f"Found **{message_count:,} messages** in this timeframe.\n\n"
                f"🤖 **Smart Sampling Enabled:**\n"
                f"• Using {self.SAFE_PROCESSING_LIMIT:,} representative messages\n"
                f"• This provides better summaries and faster processing\n"
                f"• Messages are evenly sampled across the timeframe\n\n"
                f"Processing..."
            )
        else:
            result['status'] = 'ok'
        
        return result
    
    def sample_messages(
        self,
        messages: List[Dict],
        target_size: int,
        prioritize_engagement: bool = True
    ) -> List[Dict]:
        """
        Intelligently sample messages to reduce to target size
        
        Strategy:
        1. Divide timeframe into equal segments
        2. Take messages evenly from each segment
        3. Within each segment, prioritize longer/more substantive messages
        
        Args:
            messages: List of message dictionaries (must be chronologically sorted)
            target_size: Target number of messages to sample
            prioritize_engagement: Whether to prioritize longer messages
            
        Returns:
            Sampled list of messages (chronologically sorted)
        """
        if len(messages) <= target_size:
            # No sampling needed
            return messages
        
        if target_size <= 0:
            logger.warning("Invalid target_size, returning empty list")
            return []
        
        logger.info(f"Smart sampling: {len(messages)} messages → {target_size} messages")
        
        # Calculate number of segments
        # Use segments equal to target_size for maximum distribution
        num_segments = min(target_size, len(messages))
        messages_per_segment = target_size // num_segments
        remaining_messages = target_size % num_segments
        
        # Divide messages into segments
        segment_size = len(messages) // num_segments
        sampled_messages = []
        
        for i in range(num_segments):
            # Calculate segment boundaries
            start_idx = i * segment_size
            if i == num_segments - 1:
                # Last segment takes all remaining messages
                end_idx = len(messages)
            else:
                end_idx = (i + 1) * segment_size
            
            segment = messages[start_idx:end_idx]
            
            # How many messages to take from this segment
            take_count = messages_per_segment
            if remaining_messages > 0:
                take_count += 1
                remaining_messages -= 1
            
            # Sample from this segment
            if prioritize_engagement:
                # Sort by message length (longer = more substantive)
                # Keep date field for final sorting
                segment_sorted = sorted(
                    segment,
                    key=lambda m: len(m.get('text', '')),
                    reverse=True
                )
                sampled_segment = segment_sorted[:take_count]
            else:
                # Just take evenly spaced messages from segment
                if len(segment) <= take_count:
                    sampled_segment = segment
                else:
                    step = len(segment) / take_count
                    sampled_segment = [
                        segment[int(j * step)]
                        for j in range(take_count)
                    ]
            
            sampled_messages.extend(sampled_segment)
        
        # Sort by date to maintain chronological order
        sampled_messages.sort(key=lambda m: m.get('date', datetime.min))
        
        logger.info(f"Smart sampling complete: selected {len(sampled_messages)} messages")
        
        return sampled_messages
    
    def get_sampling_explanation(self, original_count: int, sampled_count: int) -> str:
        """
        Generate user-friendly explanation of sampling
        
        Args:
            original_count: Original number of messages
            sampled_count: Number of messages after sampling
            
        Returns:
            Formatted explanation string
        """
        return (
            f"🔍 **Smart Sampling Applied:**\n"
            f"• Original: {original_count:,} messages\n"
            f"• Analyzed: {sampled_count:,} messages\n"
            f"• Sampling: {(sampled_count/original_count*100):.1f}% of messages\n"
            f"• Method: Evenly distributed across timeframe, prioritizing substantive messages\n"
        )


# Global sampler instance
_sampler: Optional[SmartSampler] = None


def get_smart_sampler(hard_limit: Optional[int] = None) -> SmartSampler:
    """
    Get or create the global smart sampler instance
    
    Args:
        hard_limit: Optional hard limit override
        
    Returns:
        SmartSampler instance
    """
    global _sampler
    
    if _sampler is None or (hard_limit and hard_limit != _sampler.hard_limit):
        _sampler = SmartSampler(hard_limit=hard_limit or SmartSampler.HARD_MESSAGE_LIMIT)
    
    return _sampler
