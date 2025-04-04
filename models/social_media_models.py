# Social media data models
"""
Data models for social media information.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class SocialMediaProfile(BaseModel):
    """Structured representation of a social media profile."""
    platform: str
    username: str
    url: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    is_verified: bool = False
    profile_image_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    joined_date: Optional[datetime] = None
    last_active_date: Optional[datetime] = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    posts: List[Dict[str, Any]] = Field(default_factory=list)
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string URLs."""
        result = self.dict()
        if self.url:
            result['url'] = str(self.url)
        if self.profile_image_url:
            result['profile_image_url'] = str(self.profile_image_url)
        if self.joined_date:
            result['joined_date'] = self.joined_date.isoformat()
        if self.last_active_date:
            result['last_active_date'] = self.last_active_date.isoformat()
        return result