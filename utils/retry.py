# Retry handling utilities
"""
Retry handling utilities for the Person Intelligence Crawler.
"""

import time
import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handles retry logic for failed requests."""
    
    def __init__(self, max_retries: int = 3, initial_backoff: float = 1.0, 
                 max_backoff: float = 60.0, backoff_factor: float = 2.0):
        """Initialize retry handler."""
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic."""
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                # If the function is a coroutine, await it
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                retries += 1
                
                if retries > self.max_retries:
                    logger.error(f"Max retries exceeded: {str(e)}")
                    break
                
                # Calculate backoff time
                backoff = min(
                    self.max_backoff, 
                    self.initial_backoff * (self.backoff_factor ** (retries - 1))
                )
                
                logger.warning(f"Attempt {retries} failed: {str(e)}. Retrying in {backoff:.2f}s")
                await asyncio.sleep(backoff)
        
        # Re-raise the last exception
        if last_exception:
            raise last_exception
    
    def execute_with_retry_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic (synchronous version)."""
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                retries += 1
                
                if retries > self.max_retries:
                    logger.error(f"Max retries exceeded: {str(e)}")
                    break
                
                # Calculate backoff time
                backoff = min(
                    self.max_backoff, 
                    self.initial_backoff * (self.backoff_factor ** (retries - 1))
                )
                
                logger.warning(f"Attempt {retries} failed: {str(e)}. Retrying in {backoff:.2f}s")
                time.sleep(backoff)
        
        # Re-raise the last exception
        if last_exception:
            raise last_exception