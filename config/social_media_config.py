# Social media configuration
"""
Configuration models for social media crawling.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class PlatformConfig(BaseModel):
    """Configuration for a social media platform."""
    name: str
    enabled: bool = True
    search_url_template: str
    profile_url_template: Optional[str] = None
    search_depth: int = Field(default=2, ge=1, le=5)
    extract_connections: bool = True
    extract_posts: bool = True
    max_posts: int = Field(default=50, ge=1, le=200)


class SocialMediaConfig(BaseModel):
    """Configuration for social media sources to search."""
    platforms: List[PlatformConfig] = Field(default_factory=list)
    timeout_per_platform: int = Field(default=30, ge=5, le=120)  # seconds
    connection_depth: int = Field(default=1, ge=0, le=3)
    
    @validator('platforms', pre=True, each_item=False)
    def set_default_platforms(cls, v):
        if v:
            return v
        
        # Default platform configurations
        return [
            PlatformConfig(
                name="twitter",
                search_url_template="https://twitter.com/search?q={query}&f=user",
                profile_url_template="https://twitter.com/{username}"
            ),
            PlatformConfig(
                name="linkedin",
                search_url_template="https://www.linkedin.com/search/results/people/?keywords={query}",
                profile_url_template="https://www.linkedin.com/in/{username}"
            ),
            PlatformConfig(
                name="facebook",
                search_url_template="https://www.facebook.com/search/people/?q={query}",
                profile_url_template="https://www.facebook.com/{username}"
            ),
            PlatformConfig(
                name="instagram",
                search_url_template="https://www.instagram.com/{query}/",
                profile_url_template="https://www.instagram.com/{username}"
            ),
            PlatformConfig(
                name="tiktok",
                search_url_template="https://www.tiktok.com/search?q={query}",
                profile_url_template="https://www.tiktok.com/@{username}"
            ),
            PlatformConfig(
                name="youtube",
                search_url_template="https://www.youtube.com/results?search_query={query}&sp=EgIQAg%253D%253D",
                profile_url_template="https://www.youtube.com/@{username}"
            ),
            PlatformConfig(
                name="reddit",
                search_url_template="https://www.reddit.com/search/?q={query}&type=user",
                profile_url_template="https://www.reddit.com/user/{username}"
            ),
            PlatformConfig(
                name="github",
                search_url_template="https://github.com/search?q={query}&type=users",
                profile_url_template="https://github.com/{username}"
            )
        ]
        
    @validator('search_url_template', 'profile_url_template')
    def validate_url_templates(cls, v):
        if v and '{query}' not in v and '{username}' not in v:
            raise ValueError("URL template must contain at least one placeholder: {query} or {username}")
        return v