"""
Tools for LangGraph agents in the Person Intelligence Crawler.
"""

import re
import logging
from typing import List, Dict, Any, Callable, Optional, Tuple
from datetime import datetime

from models.base_models import RiskLevel

logger = logging.getLogger(__name__)

class SearchStrategyTools:
    """Tools for search strategy generation."""
    
    @staticmethod
    def extract_platforms(text: str) -> List[str]:
        """Extract recommended platforms from search strategy text."""
        # Simple extraction using common platform names
        platforms = []
        common_platforms = [
            "twitter", "linkedin", "facebook", "instagram", 
            "tiktok", "youtube", "reddit", "github"
        ]
        
        for platform in common_platforms:
            if platform.lower() in text.lower():
                platforms.append(platform)
                
        return platforms or common_platforms[:3]  # Default to top 3 if none found
    
    @staticmethod
    def extract_search_terms(text: str) -> List[str]:
        """Extract recommended search terms from search strategy text."""
        # Look for sections about search terms
        search_term_section = re.search(
            r'(?:search terms|queries|keywords)[:\s]+([^#]+)',
            text, re.IGNORECASE
        )
        
        if search_term_section:
            # Extract terms from the section
            terms_text = search_term_section.group(1).strip()
            # Split by common separators and clean up
            terms = re.split(r'[,;\n•-]', terms_text)
            # Remove empty terms and strip whitespace
            terms = [term.strip().strip('"\'') for term in terms if term.strip()]
            
            if terms:
                return terms
                
        # Default: return the name as a search term
        return []
    
    @staticmethod
    def extract_name_variations(text: str) -> List[str]:
        """Extract name variations from search strategy text."""
        # Look for sections about name variations
        variation_section = re.search(
            r'(?:name variations|alternative spellings|aliases)[:\s]+([^#]+)',
            text, re.IGNORECASE
        )
        
        if variation_section:
            # Extract variations from the section
            variations_text = variation_section.group(1).strip()
            # Split by common separators and clean up
            variations = re.split(r'[,;\n•-]', variations_text)
            # Remove empty variations and strip whitespace
            variations = [var.strip().strip('"\'') for var in variations if var.strip()]
            
            if variations:
                return variations
                
        return []
    
    @staticmethod
    def extract_regions(text: str) -> List[str]:
        """Extract relevant geographical regions from search strategy text."""
        # Look for sections about regions
        region_section = re.search(
            r'(?:regions|geographical|countries|locations)[:\s]+([^#]+)',
            text, re.IGNORECASE
        )
        
        if region_section:
            # Extract regions from the section
            regions_text = region_section.group(1).strip()
            # Split by common separators and clean up
            regions = re.split(r'[,;\n•-]', regions_text)
            # Remove empty regions and strip whitespace
            regions = [region.strip().strip('"\'') for region in regions if region.strip()]