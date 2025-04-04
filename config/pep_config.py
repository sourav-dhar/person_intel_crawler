# PEP database configuration
"""
Configuration models for PEP (Politically Exposed Person) database crawling.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class PEPSourceConfig(BaseModel):
    """Configuration for a PEP (Politically Exposed Person) data source."""
    name: str
    enabled: bool = True
    api_url: Optional[str] = None
    api_key_name: Optional[str] = None
    requires_auth: bool = False
    search_endpoint: Optional[str] = None
    timeout: int = Field(default=20, ge=5, le=120)  # seconds
    api_key_format: Optional[str] = "Bearer {key}"  # Format string for auth
    rate_limit_rpm: Optional[int] = None  # Rate limits if known
    
    @validator('api_url')
    def validate_api_url(cls, v, values):
        if values.get('requires_auth') and not values.get('api_key_name'):
            raise ValueError("API key name must be provided for authenticated APIs")
        return v


class PEPDatabaseConfig(BaseModel):
    """Configuration for PEP (Politically Exposed Person) database searches."""
    sources: List[PEPSourceConfig] = Field(default_factory=list)
    require_exact_match: bool = False
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    
    @validator('sources', pre=True, each_item=False)
    def set_default_sources(cls, v):
        if v:
            return v
            
        # Default PEP sources
        return [
            PEPSourceConfig(
                name="opensanctions",
                api_url="https://api.opensanctions.org",
                search_endpoint="/search/person",
                requires_auth=True
            ),
            PEPSourceConfig(
                name="worldcheck",
                api_url="https://api.refinitiv.com/worldcheck/v1",
                search_endpoint="/person/search",
                requires_auth=True
            ),
            PEPSourceConfig(
                name="dowjones",
                api_url="https://api.dowjones.com/riskandcompliance/v1",
                search_endpoint="/persons",
                requires_auth=True
            ),
            PEPSourceConfig(
                name="ofac",
                api_url="https://sanctionssearch.ofac.treas.gov/api",
                search_endpoint="/search",
                requires_auth=False
            ),
            PEPSourceConfig(
                name="un_sanctions",
                api_url="https://api.un.org/sanctions",
                search_endpoint="/consolidated/search",
                requires_auth=False
            ),
            PEPSourceConfig(
                name="eu_sanctions",
                api_url="https://webgate.ec.europa.eu/fsd/fsf/api",
                search_endpoint="/persons/search",
                requires_auth=False
            )
        ]