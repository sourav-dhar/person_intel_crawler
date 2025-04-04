# PEP data models
"""
Data models for PEP (Politically Exposed Person) information.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from models.base_models import RiskLevel

class PEPRecord(BaseModel):
    """Structured representation of a PEP (Politically Exposed Person) record."""
    source: str
    name: str
    url: Optional[HttpUrl] = None
    position: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    sanctions: List[Dict[str, Any]] = Field(default_factory=list)
    watchlists: List[str] = Field(default_factory=list)
    related_entities: List[Dict[str, Any]] = Field(default_factory=list)
    risk_level: Optional[RiskLevel] = None
    last_updated: Optional[datetime] = None
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string URL."""
        result = self.dict()
        if self.url:
            result['url'] = str(self.url)
        if self.start_date:
            result['start_date'] = self.start_date.isoformat()
        if self.end_date:
            result['end_date'] = self.end_date.isoformat()
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
        return result