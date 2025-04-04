# Text analysis utilities
"""
Text analysis utilities for the Person Intelligence Crawler.
"""

import logging
from typing import List, Dict, Any, Optional

# NLP libraries
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy

from models.base_models import Sentiment

logger = logging.getLogger(__name__)

# Initialize NLP resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK resources: {e}")

# Load spaCy model for entity recognition
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.warning(f"Failed to load spaCy model: {e}. Entity recognition will be limited.")
    nlp = None


class TextAnalyzer:
    """Handles text analysis operations like sentiment analysis and entity recognition."""
    
    def __init__(self):
        """Initialize text analyzer with required models."""
        self.sentiment_analyzer = SentimentIntensityAnalyzer() if 'vader_lexicon' in nltk.data.path else None
        self.nlp = nlp  # spaCy model loaded at module level
    
    def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text."""
        if not text or not self.sentiment_analyzer:
            return Sentiment.NEUTRAL
            
        scores = self.sentiment_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            return Sentiment.POSITIVE
        elif compound <= -0.05:
            if compound <= -0.5:
                return Sentiment.VERY_NEGATIVE
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        if not text or not self.nlp:
            return []
            
        try:
            doc = self.nlp(text[:100000])  # Limit text length to avoid memory issues
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
                
            return entities
        except Exception as e:
            logger.warning(f"Entity extraction error: {e}")
            return []
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text."""
        if not text or not self.nlp:
            return []
            
        try:
            doc = self.nlp(text[:100000])  # Limit text length
            
            # Filter for nouns and proper nouns, exclude stopwords
            keywords = [token.lemma_ for token in doc 
                       if token.pos_ in ('NOUN', 'PROPN') 
                       and not token.is_stop 
                       and len(token.text) > 1]
            
            # Count occurrences and return top N
            keyword_counts = {}
            for keyword in keywords:
                if keyword in keyword_counts:
                    keyword_counts[keyword] += 1
                else:
                    keyword_counts[keyword] = 1
                    
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            return [k for k, _ in sorted_keywords[:top_n]]
            
        except Exception as e:
            logger.warning(f"Keyword extraction error: {e}")
            return []
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate the similarity between two names."""
        if not name1 or not name2:
            return 0.0
            
        # Simple Jaccard similarity implementation
        # More sophisticated name matching could be used
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        
        intersection = len(name1_parts.intersection(name2_parts))
        union = len(name1_parts.union(name2_parts))
        
        return intersection / union if union > 0 else 0.0
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Create a short summary of a longer text."""
        if not text:
            return ""
            
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= max_sentences:
                return text
                
            # For a simple extractive summary, just return the first few sentences
            # A more sophisticated approach would use text ranking algorithms
            return " ".join(sentences[:max_sentences])
            
        except Exception as e:
            logger.warning(f"Text summarization error: {e}")
            return text[:200] + "..." if len(text) > 200 else text