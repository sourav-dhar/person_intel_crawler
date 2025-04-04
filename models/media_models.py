# Media data models
"""
Data models for adverse media information.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from models.base_models import Sentiment

class NewsArticle(BaseModel):
    """Structured representation of a news article."""
    source: str
    title: str
    url: HttpUrl
    published_date: Optional[datetime] = None
    authors: List[str] = Field(default_factory=list)
    content: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string URL."""
        result = self.dict()
        result['url'] = str(self.url)
        if self.published_date:
            result['published_date'] = self.published_date.isoformat()
        return result