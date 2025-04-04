# Proxy management utilities
"""
Proxy management utilities for the Person Intelligence Crawler.
"""

import time
import logging
from typing import Optional
from urllib.parse import urlparse

from config.base_config import ProxyConfig

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxy selection and rotation."""
    
    def __init__(self, config: ProxyConfig):
        """Initialize proxy manager with configuration."""
        self.config = config
        self.last_rotation = time.time()
        self.current_proxy = None
        
        if config.enabled:
            self.current_proxy = self._format_proxy_url()
            logger.info(f"Proxy enabled: {self.current_proxy}")
    
    def _format_proxy_url(self) -> Optional[str]:
        """Format the proxy URL with authentication if needed."""
        if not self.config.enabled or not self.config.url:
            return None
            
        proxy_url = self.config.url
        
        # Add authentication if provided
        if self.config.username and self.config.password:
            parsed = urlparse(proxy_url)
            auth_url = f"{parsed.scheme}://{self.config.username}:{self.config.password}@{parsed.netloc}{parsed.path}"
            return auth_url
            
        return proxy_url
    
    def get_proxy(self) -> Optional[str]:
        """Get the current proxy URL, rotating if needed."""
        if not self.config.enabled:
            return None
            
        # Check if rotation is needed
        if (self.config.rotation_enabled and self.config.rotation_interval and 
            time.time() - self.last_rotation > self.config.rotation_interval):
            # In a real implementation, this would select from a pool of proxies
            # For now, just reset the timer
            self.last_rotation = time.time()
            logger.info("Proxy rotation triggered")
            
        return self.current_proxy