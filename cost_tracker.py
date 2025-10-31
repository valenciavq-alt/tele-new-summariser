"""
Cost Tracking and Budget Enforcement Module

This module tracks Claude API usage and enforces monthly budget limits.
It provides persistent cost tracking, budget warnings, and usage statistics.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks Claude API costs and enforces budget limits
    
    Pricing (Claude 3 Haiku as of implementation):
    - Input tokens: $0.25 per million tokens
    - Output tokens: $1.25 per million tokens
    """
    
    # Claude 3 Haiku pricing (per million tokens)
    INPUT_TOKEN_COST = 0.25 / 1_000_000  # $0.25 per 1M tokens
    OUTPUT_TOKEN_COST = 1.25 / 1_000_000  # $1.25 per 1M tokens
    
    # Warning thresholds (as percentage of budget)
    WARNING_THRESHOLDS = [50, 75, 90]
    
    def __init__(self, monthly_budget: Optional[float] = None, data_file: str = "cost_data.json"):
        """
        Initialize the cost tracker
        
        Args:
            monthly_budget: Monthly budget limit in USD (default: $10)
            data_file: Path to JSON file for persistent storage
        """
        self.monthly_budget = monthly_budget or float(os.getenv('MONTHLY_BUDGET', '10.0'))
        self.data_file = Path(data_file)
        self.data = self._load_data()
        self.warnings_sent = set()  # Track which warnings have been sent for current month
        
        # Auto-reset if new month
        self._check_and_reset_month()
        
        logger.info(f"Cost tracker initialized with ${self.monthly_budget:.2f} monthly budget")
    
    def _load_data(self) -> Dict:
        """Load cost data from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded existing cost data from {self.data_file}")
                    return data
            except Exception as e:
                logger.error(f"Error loading cost data: {e}")
                return self._create_default_data()
        else:
            logger.info("No existing cost data found, creating new data file")
            return self._create_default_data()
    
    def _create_default_data(self) -> Dict:
        """Create default data structure"""
        return {
            'current_month': datetime.now(timezone.utc).strftime('%Y-%m'),
            'total_cost': 0.0,
            'input_tokens': 0,
            'output_tokens': 0,
            'request_count': 0,
            'history': []
        }
    
    def _save_data(self):
        """Save cost data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            logger.debug(f"Saved cost data to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving cost data: {e}")
    
    def _check_and_reset_month(self):
        """Check if it's a new month and reset if necessary"""
        current_month = datetime.now(timezone.utc).strftime('%Y-%m')
        
        if self.data['current_month'] != current_month:
            logger.info(f"New month detected! Resetting usage from {self.data['current_month']} to {current_month}")
            
            # Archive current month to history
            self.data['history'].append({
                'month': self.data['current_month'],
                'total_cost': self.data['total_cost'],
                'input_tokens': self.data['input_tokens'],
                'output_tokens': self.data['output_tokens'],
                'request_count': self.data['request_count']
            })
            
            # Keep only last 12 months of history
            if len(self.data['history']) > 12:
                self.data['history'] = self.data['history'][-12:]
            
            # Reset current month data
            self.data['current_month'] = current_month
            self.data['total_cost'] = 0.0
            self.data['input_tokens'] = 0
            self.data['output_tokens'] = 0
            self.data['request_count'] = 0
            
            # Clear warnings sent for new month
            self.warnings_sent.clear()
            
            self._save_data()
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for given token usage
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Total cost in USD
        """
        input_cost = input_tokens * self.INPUT_TOKEN_COST
        output_cost = output_tokens * self.OUTPUT_TOKEN_COST
        total_cost = input_cost + output_cost
        
        return total_cost
    
    def can_make_request(self, estimated_tokens: int = 2000) -> Tuple[bool, Optional[str]]:
        """
        Check if a request can be made within budget
        
        Args:
            estimated_tokens: Estimated total tokens for request (default: 2000)
        
        Returns:
            Tuple of (can_proceed, error_message)
            - can_proceed: True if within budget, False otherwise
            - error_message: Error message if budget exceeded, None otherwise
        """
        # Auto-reset if new month
        self._check_and_reset_month()
        
        # Estimate cost (assume worst case: all output tokens)
        estimated_cost = estimated_tokens * self.OUTPUT_TOKEN_COST
        projected_total = self.data['total_cost'] + estimated_cost
        
        if projected_total > self.monthly_budget:
            # Budget exceeded
            remaining_days = self._days_until_reset()
            error_msg = (
                f"🚫 **Monthly Budget Limit Reached**\n\n"
                f"Current spending: ${self.data['total_cost']:.4f}\n"
                f"Monthly budget: ${self.monthly_budget:.2f}\n"
                f"Budget resets in {remaining_days} day(s) (on the 1st of next month)\n\n"
                f"Please check back after the reset or contact the bot administrator."
            )
            return False, error_msg
        
        return True, None
    
    def track_request(self, input_tokens: int, output_tokens: int) -> Dict:
        """
        Track a completed API request
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
        
        Returns:
            Dict with cost breakdown and budget status
        """
        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens)
        
        # Update data
        self.data['total_cost'] += cost
        self.data['input_tokens'] += input_tokens
        self.data['output_tokens'] += output_tokens
        self.data['request_count'] += 1
        
        # Save to disk
        self._save_data()
        
        # Calculate budget usage
        budget_used_pct = (self.data['total_cost'] / self.monthly_budget) * 100
        
        logger.info(
            f"Tracked request: {input_tokens} input + {output_tokens} output tokens, "
            f"cost: ${cost:.6f}, total: ${self.data['total_cost']:.4f} ({budget_used_pct:.1f}% of budget)"
        )
        
        return {
            'request_cost': cost,
            'total_cost': self.data['total_cost'],
            'budget_used_pct': budget_used_pct,
            'remaining_budget': self.monthly_budget - self.data['total_cost'],
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
    
    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics
        
        Returns:
            Dict with comprehensive usage statistics
        """
        # Auto-reset if new month
        self._check_and_reset_month()
        
        budget_used_pct = (self.data['total_cost'] / self.monthly_budget) * 100
        remaining_budget = self.monthly_budget - self.data['total_cost']
        
        return {
            'current_month': self.data['current_month'],
            'total_cost': self.data['total_cost'],
            'monthly_budget': self.monthly_budget,
            'budget_used_pct': budget_used_pct,
            'remaining_budget': remaining_budget,
            'input_tokens': self.data['input_tokens'],
            'output_tokens': self.data['output_tokens'],
            'total_tokens': self.data['input_tokens'] + self.data['output_tokens'],
            'request_count': self.data['request_count'],
            'days_until_reset': self._days_until_reset(),
            'budget_status': self._get_budget_status(budget_used_pct)
        }
    
    def _get_budget_status(self, budget_used_pct: float) -> str:
        """Get human-readable budget status"""
        if budget_used_pct >= 100:
            return "🔴 EXCEEDED"
        elif budget_used_pct >= 90:
            return "🟠 CRITICAL"
        elif budget_used_pct >= 75:
            return "🟡 HIGH"
        elif budget_used_pct >= 50:
            return "🟢 MODERATE"
        else:
            return "🟢 HEALTHY"
    
    def _days_until_reset(self) -> int:
        """Calculate days until the next month (reset date)"""
        now = datetime.now(timezone.utc)
        
        # Calculate first day of next month
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_month = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        days_remaining = (next_month - now).days
        return max(1, days_remaining)  # At least 1 day
    
    def check_warning_thresholds(self) -> Optional[Dict]:
        """
        Check if any warning thresholds have been crossed
        
        Returns:
            Warning dict if threshold crossed and not yet warned, None otherwise
        """
        budget_used_pct = (self.data['total_cost'] / self.monthly_budget) * 100
        
        # Check each threshold in descending order
        for threshold in sorted(self.WARNING_THRESHOLDS, reverse=True):
            if budget_used_pct >= threshold and threshold not in self.warnings_sent:
                # Mark this threshold as warned
                self.warnings_sent.add(threshold)
                
                stats = self.get_usage_stats()
                
                return {
                    'threshold': threshold,
                    'stats': stats,
                    'message': self._format_warning_message(threshold, stats)
                }
        
        return None
    
    def _format_warning_message(self, threshold: int, stats: Dict) -> str:
        """Format a warning message for admin notification"""
        msg = (
            f"⚠️ **Budget Alert: {threshold}% Threshold Reached**\n\n"
            f"📊 **Current Usage ({stats['current_month']}):**\n"
            f"• Total spent: ${stats['total_cost']:.4f}\n"
            f"• Budget used: {stats['budget_used_pct']:.1f}%\n"
            f"• Remaining: ${stats['remaining_budget']:.4f}\n"
            f"• Monthly limit: ${stats['monthly_budget']:.2f}\n\n"
            f"🔢 **Token Usage:**\n"
            f"• Input tokens: {stats['input_tokens']:,}\n"
            f"• Output tokens: {stats['output_tokens']:,}\n"
            f"• Total tokens: {stats['total_tokens']:,}\n"
            f"• API requests: {stats['request_count']}\n\n"
            f"⏰ **Budget resets in {stats['days_until_reset']} day(s)**\n\n"
            f"Status: {stats['budget_status']}"
        )
        
        return msg
    
    def reset_usage(self) -> Dict:
        """
        Manually reset usage (admin command)
        
        Returns:
            Dict with previous stats before reset
        """
        previous_stats = {
            'month': self.data['current_month'],
            'total_cost': self.data['total_cost'],
            'input_tokens': self.data['input_tokens'],
            'output_tokens': self.data['output_tokens'],
            'request_count': self.data['request_count']
        }
        
        # Add to history
        self.data['history'].append(previous_stats)
        
        # Keep only last 12 months
        if len(self.data['history']) > 12:
            self.data['history'] = self.data['history'][-12:]
        
        # Reset current data
        current_month = datetime.now(timezone.utc).strftime('%Y-%m')
        self.data['current_month'] = current_month
        self.data['total_cost'] = 0.0
        self.data['input_tokens'] = 0
        self.data['output_tokens'] = 0
        self.data['request_count'] = 0
        
        # Clear warnings
        self.warnings_sent.clear()
        
        self._save_data()
        
        logger.warning(f"Usage manually reset by admin. Previous usage: ${previous_stats['total_cost']:.4f}")
        
        return previous_stats
    
    def get_formatted_usage_message(self) -> str:
        """
        Get a formatted usage message for the /usage command
        
        Returns:
            Markdown-formatted usage statistics
        """
        stats = self.get_usage_stats()
        
        # Create progress bar
        progress_bar = self._create_progress_bar(stats['budget_used_pct'])
        
        msg = (
            f"📊 **Monthly Budget Usage Report**\n\n"
            f"**Period:** {stats['current_month']}\n"
            f"**Status:** {stats['budget_status']}\n\n"
            f"💰 **Budget:**\n"
            f"• Spent: ${stats['total_cost']:.4f}\n"
            f"• Limit: ${stats['monthly_budget']:.2f}\n"
            f"• Remaining: ${stats['remaining_budget']:.4f}\n"
            f"• Used: {stats['budget_used_pct']:.1f}%\n\n"
            f"{progress_bar}\n\n"
            f"🔢 **Token Usage:**\n"
            f"• Input: {stats['input_tokens']:,} tokens (${stats['input_tokens'] * self.INPUT_TOKEN_COST:.6f})\n"
            f"• Output: {stats['output_tokens']:,} tokens (${stats['output_tokens'] * self.OUTPUT_TOKEN_COST:.6f})\n"
            f"• Total: {stats['total_tokens']:,} tokens\n\n"
            f"📈 **Activity:**\n"
            f"• API requests: {stats['request_count']}\n"
            f"• Avg cost/request: ${(stats['total_cost'] / stats['request_count']):.6f}\n\n" if stats['request_count'] > 0 else ""
            f"⏰ **Budget resets in {stats['days_until_reset']} day(s)**"
        )
        
        return msg
    
    def _create_progress_bar(self, percentage: float, length: int = 20) -> str:
        """Create a text-based progress bar"""
        filled = int((percentage / 100) * length)
        filled = min(filled, length)  # Cap at length
        
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {percentage:.1f}%"


# Global cost tracker instance
cost_tracker: Optional[CostTracker] = None


def initialize_cost_tracker(monthly_budget: Optional[float] = None, data_file: str = "cost_data.json") -> CostTracker:
    """
    Initialize the global cost tracker instance
    
    Args:
        monthly_budget: Monthly budget limit in USD
        data_file: Path to JSON file for persistent storage
    
    Returns:
        Initialized CostTracker instance
    """
    global cost_tracker
    cost_tracker = CostTracker(monthly_budget=monthly_budget, data_file=data_file)
    return cost_tracker


def get_cost_tracker() -> Optional[CostTracker]:
    """
    Get the global cost tracker instance
    
    Returns:
        CostTracker instance or None if not initialized
    """
    return cost_tracker
