"""
Data models for intelligence results.
"""

import json
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from models.base_models import RiskLevel, SourceType
from models.social_media_models import SocialMediaProfile
from models.pep_models import PEPRecord
from models.media_models import NewsArticle

class SearchResult(BaseModel):
    """Structured representation of a search result."""
    source: str
    source_type: SourceType
    url: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    verified: bool = False
    sentiment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string URL."""
        result = self.dict()
        if self.date:
            result['date'] = self.date.isoformat()
        return result


class PersonIntelligence(BaseModel):
    """Container for all gathered intelligence about a person."""
    name: str
    query_time: datetime = Field(default_factory=datetime.now)
    social_media_profiles: Dict[str, List[SocialMediaProfile]] = Field(default_factory=dict)
    pep_records: List[PEPRecord] = Field(default_factory=list)
    news_articles: List[NewsArticle] = Field(default_factory=list)
    summary: str = ""
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sources_checked: Set[str] = Field(default_factory=set)
    sources_successful: Set[str] = Field(default_factory=set)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the results to a dictionary."""
        result = {
            "name": self.name,
            "query_time": self.query_time.isoformat(),
            "social_media_profiles": {},
            "pep_records": [],
            "news_articles": [],
            "summary": self.summary,
            "risk_level": self.risk_level,
            "confidence_score": self.confidence_score,
            "sources_checked": list(self.sources_checked),
            "sources_successful": list(self.sources_successful),
            "errors": self.errors
        }
        
        # Convert social media profiles
        for platform, profiles in self.social_media_profiles.items():
            result["social_media_profiles"][platform] = [p.to_dict() for p in profiles]
        
        # Convert PEP records
        result["pep_records"] = [r.to_dict() for r in self.pep_records]
        
        # Convert news articles
        result["news_articles"] = [a.to_dict() for a in self.news_articles]
        
        return result
    
    def to_json(self) -> str:
        """Convert the results to a JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)
    
    def to_markdown(self) -> str:
        """Generate a markdown report of the findings."""
        md = f"# Intelligence Report: {self.name}\n\n"
        md += f"**Generated:** {self.query_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Risk Level:** {self.risk_level.value.upper()}\n"
        md += f"**Confidence Score:** {self.confidence_score:.2f}/1.0\n\n"
        
        md += f"## Summary\n\n{self.summary}\n\n"
        
        # Social Media Profiles
        if self.social_media_profiles:
            md += "## Social Media Presence\n\n"
            for platform, profiles in self.social_media_profiles.items():
                md += f"### {platform.title()}\n\n"
                for profile in profiles:
                    md += f"* **Username:** {profile.username}\n"
                    if profile.display_name:
                        md += f"* **Display Name:** {profile.display_name}\n"
                    if profile.url:
                        md += f"* **URL:** {profile.url}\n"
                    if profile.follower_count:
                        md += f"* **Followers:** {profile.follower_count:,}\n"
                    if profile.is_verified:
                        md += "* **Verified Account:** Yes\n"
                    if profile.bio:
                        md += f"* **Bio:** {profile.bio}\n"
                    md += "\n"
        
        # PEP Records
        if self.pep_records:
            md += "## Political Exposure & Sanctions\n\n"
            for record in self.pep_records:
                md += f"### {record.source}\n\n"
                md += f"* **Name:** {record.name}\n"
                if record.position:
                    md += f"* **Position:** {record.position}\n"
                if record.organization:
                    md += f"* **Organization:** {record.organization}\n"
                if record.country:
                    md += f"* **Country:** {record.country}\n"
                if record.sanctions:
                    md += "* **Sanctions:** " + ", ".join([s.get('name', 'Unknown') for s in record.sanctions]) + "\n"
                if record.watchlists:
                    md += "* **Watchlists:** " + ", ".join(record.watchlists) + "\n"
                if record.url:
                    md += f"* **Source URL:** {record.url}\n"
                md += "\n"
        
        # News Articles
        if self.news_articles:
            md += "## Media Coverage\n\n"
            for article in sorted(self.news_articles, key=lambda x: x.published_date if x.published_date else datetime.min, reverse=True):
                md += f"### {article.title}\n\n"
                md += f"* **Source:** {article.source}\n"
                if article.published_date:
                    md += f"* **Date:** {article.published_date.strftime('%Y-%m-%d')}\n"
                if article.authors:
                    md += f"* **Authors:** {', '.join(article.authors)}\n"
                if article.sentiment:
                    md += f"* **Sentiment:** {article.sentiment.value}\n"
                if article.summary:
                    md += f"* **Summary:** {article.summary}\n"
                md += f"* **URL:** {article.url}\n\n"
        
        # Sources and Errors
        md += "## Sources\n\n"
        md += f"* **Sources Checked:** {len(self.sources_checked)}\n"
        md += f"* **Successful Sources:** {len(self.sources_successful)}\n\n"
        
        if self.errors:
            md += "## Errors\n\n"
            for error in self.errors:
                md += f"* **{error.get('source', 'Unknown')}:** {error.get('message', 'Unknown error')}\n"
        
        return md