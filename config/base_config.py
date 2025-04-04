# Base configuration classes
"""
Base configuration models for the Person Intelligence Crawler.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, root_validator

class CacheConfig(BaseModel):
    """Configuration for caching."""
    enabled: bool = True
    ttl: int = Field(default=86400, ge=60, le=2592000)  # seconds (default 24h, max 30 days)
    cache_dir: str = ".cache"


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""
    requests_per_period: int = Field(default=100, ge=1, le=10000)
    period_seconds: int = Field(default=60, ge=1, le=3600)


class ProxyConfig(BaseModel):
    """Configuration for proxy usage."""
    enabled: bool = False
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rotation_enabled: bool = False
    rotation_interval: Optional[int] = None  # seconds


class CrawlerConfig(BaseModel):
    """Main configuration for the crawler.
    
    This is imported by the main coordinator and includes
    configurations for all components.
    """
    # Component configs are imported in coordinator.py to avoid circular imports
    
    # General crawler settings
    max_concurrent_requests: int = Field(default=10, ge=1, le=100)
    request_delay: float = Field(default=0.5, ge=0.1, le=10.0)  # seconds between requests
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    user_agent: str = "PersonIntelCrawler/1.0"
    output_format: str = "json"  # or "html", "text", "markdown"
    retries: int = Field(default=3, ge=0, le=10)
    timeout: int = Field(default=60, ge=5, le=300)  # Overall timeout per search in seconds
    
    # API keys
    api_keys: Dict[str, str] = Field(default_factory=dict)
    
    # Proxy configuration
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    
    # Threading
    thread_pool_size: int = Field(default=20, ge=1, le=100)
    
    @root_validator
    def check_api_keys(cls, values):
        """Check that required API keys are present."""
        # This is a placeholder that will be overridden in the coordinator
        # when all configs are loaded
        return values
    
    # Add URL validation for proxy
    @validator('url')
    def validate_proxy_url(cls, v):
        if v:
            try:
                result = urlparse(v)
                if not all([result.scheme, result.netloc]):
                    raise ValueError("Proxy URL must have scheme and host")
            except Exception:
                raise ValueError("Invalid proxy URL format")
        return v

    # Add directory existence check for cache
    @validator('cache_dir')
    def validate_cache_dir(cls, v):
        if not os.path.exists(v):
            try:
                os.makedirs(v, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create cache directory: {str(e)}")
        return v