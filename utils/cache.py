# Caching utilities
"""
Caching utilities for the Person Intelligence Crawler.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional

from config.base_config import CacheConfig

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of search results to avoid unnecessary repeat requests."""
    
    def __init__(self, config: CacheConfig):
        """Initialize cache manager with configuration."""
        self.config = config
        if not self.config.enabled:
            logger.info("Cache is disabled")
            return
            
        self.cache_dir = config.cache_dir
        self.ttl = config.ttl
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Cache initialized at {cache_dir} with TTL of {ttl} seconds")
        
    def _get_cache_key(self, query: str, source: str) -> str:
        """Generate a unique cache key based on the query and source."""
        combined = f"{query}:{source}".lower()
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, query: str, source: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached results if they exist and are not expired."""
        if not self.config.enabled:
            return None
            
        key = self._get_cache_key(query, source)
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if the cache is expired
            timestamp = data.get('_timestamp', 0)
            if time.time() - timestamp > self.ttl:
                logger.debug(f"Cache expired for {query} on {source}")
                return None
                
            logger.info(f"Cache hit for {query} on {source}")
            return data.get('results')
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, query: str, source: str, results: Dict[str, Any]) -> None:
        """Store results in the cache."""
        if not self.config.enabled:
            return
            
        key = self._get_cache_key(query, source)
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                '_timestamp': time.time(),
                'results': results
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
                
            logger.debug(f"Cached results for {query} on {source}")
        except Exception as e:
            logger.warning(f"Error writing to cache: {str(e)}")
            
     def cleanup_expired(self) -> int:
        """Remove expired cache entries. Returns count of removed entries."""
        if not self.config.enabled:
            return 0
            
        count = 0
        current_time = time.time()
        try:
            for file_name in os.listdir(self.cache_dir):
                if not file_name.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, file_name)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    timestamp = data.get('_timestamp', 0)
                    if current_time - timestamp > self.ttl:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logger.warning(f"Error cleaning up cache file {file_name}: {str(e)}")
            
            return count
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.config.enabled:
            return {"enabled": False}
            
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            size_bytes = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
            
            return {
                "enabled": True,
                "entries": len(files),
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "ttl_seconds": self.ttl,
                "cache_dir": self.cache_dir
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"enabled": True, "error": str(e)}