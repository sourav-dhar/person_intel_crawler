# Enums and base models
"""
Base data models for the Person Intelligence Crawler.
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import Any

class Sentiment(str, Enum):
    """Enumeration of sentiment values."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class SourceType(str, Enum):
    """Type of information source."""
    SOCIAL_MEDIA = "social_media"
    PEP_DATABASE = "pep_database"
    ADVERSE_MEDIA = "adverse_media"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk level assessment."""
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseCrawler(ABC):
    """Base class for all crawlers."""
    
    @abstractmethod
    async def search(self, name: str) -> Any:
        """Search for information about a person."""
        pass
    
    @abstractmethod
    def get_source_type(self) -> SourceType:
        """Get the type of source this crawler handles."""
        pass