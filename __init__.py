# Package initialization
"""
Person Intelligence Crawler

A production-ready framework that combines Firecrawl with LLM-based agents
to gather comprehensive information about individuals across the internet.
"""

__version__ = "1.0.0"

from coordinator import PersonIntelCrawler
from models.intelligence_models import PersonIntelligence
from models.base_models import RiskLevel, SourceType, Sentiment

__all__ = [
    "PersonIntelCrawler",
    "PersonIntelligence",
    "RiskLevel",
    "SourceType",
    "Sentiment"
]