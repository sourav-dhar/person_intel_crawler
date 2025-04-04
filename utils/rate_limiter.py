# Rate limiting utilities
"""
Rate limiting utilities for the Person Intelligence Crawler.
"""

import time
import logging
from typing import Dict, List

from config.base_config import RateLimitConfig

logger = logging.getLogger(__name__)

class RateLimiter:
    """Manages rate limiting across different sources."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize rate limiter with configuration."""
        self.requests_per_period = config.requests_per_period
        self.period = config.period_seconds  # in seconds
        self.request_timestamps: Dict[str, List[float]] = {}
        
    def check_and_update(self, source: str) -> bool:
        """
        Check if we can make a request to the source and update the counter.
        Returns True if request is allowed, False if rate limit is exceeded.
        """
        current_time = time.time()
        
        # Initialize if first request for this source
        if source not in self.request_timestamps:
            self.request_timestamps[source] = []
        
        # Remove timestamps older than the rate limit period
        self.request_timestamps[source] = [
            ts for ts in self.request_timestamps[source]
            if current_time - ts <= self.period
        ]
        
        # Check if we've exceeded the rate limit
        if len(self.request_timestamps[source]) >= self.requests_per_period:
            logger.warning(f"Rate limit exceeded for {source}")
            return False
        
        # Add current timestamp and allow the request
        self.request_timestamps[source].append(current_time)
        return True
    
    def wait_if_needed(self, source: str) -> None:
        """Wait until a request can be made if rate limited."""
        while not self.check_and_update(source):
            sleep_time = 1
            logger.info(f"Rate limited for {source}, waiting {sleep_time}s")
            time.sleep(sleep_time)