# Adverse media configuration
"""
Configuration models for adverse media crawling.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class NewsSourceConfig(BaseModel):
    """Configuration for a news source."""
    name: str
    enabled: bool = True
    api_url: Optional[str] = None
    api_key_name: Optional[str] = None
    requires_auth: bool = False
    search_endpoint: Optional[str] = None
    web_search_template: Optional[str] = None
    timeout: int = Field(default=30, ge=5, le=120)  # seconds
    params_template: Optional[Dict[str, str]] = None  # Default query params
    response_format: Optional[str] = "json"  # Expected response format
    max_content_length: Optional[int] = 10000  # Character limit for content


class AdverseMediaConfig(BaseModel):
    """Configuration for adverse media searches."""
    sources: List[NewsSourceConfig] = Field(default_factory=list)
    timeframe_days: int = Field(default=365, ge=1, le=3650)  # Look back period
    max_results_per_source: int = Field(default=50, ge=1, le=200)
    sentiment_analysis: bool = True
    entity_recognition: bool = True
    language_codes: List[str] = Field(
        default_factory=lambda: ["en", "es", "fr", "de", "ru", "zh", "ar"]
    )
    
    @validator('sources', pre=True, each_item=False)
    def set_default_sources(cls, v):
        if v:
            return v
            
        # Default news sources
        return [
            NewsSourceConfig(
                name="google_news",
                web_search_template="https://news.google.com/search?q={query}",
                requires_auth=False
            ),
            NewsSourceConfig(
                name="bing_news",
                api_url="https://api.bing.microsoft.com/v7.0",
                search_endpoint="/news/search",
                requires_auth=True,
                api_key_name="bing_api_key"
            ),
            NewsSourceConfig(
                name="lexisnexis",
                api_url="https://api.lexisnexis.com",
                search_endpoint="/search/news",
                requires_auth=True,
                api_key_name="lexisnexis_api_key"
            ),
            NewsSourceConfig(
                name="factiva",
                api_url="https://api.dowjones.com/factiva/v1",
                search_endpoint="/search",
                requires_auth=True,
                api_key_name="factiva_api_key"
            )
        ]