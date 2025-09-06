"""
Cache Manager for Module E: Hybrid Intelligence Gateway
Manages caching of external API responses in Module B.
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from external_api_client import ExternalResponse

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching of external API responses.
    
    Integrates with Module B (RAG) to store and retrieve
    cached responses from external AI services.
    """
    
    def __init__(self, module_b_url: str = "http://localhost:8002"):
        """
        Initialize cache manager.
        
        Args:
            module_b_url: URL for Module B (RAG) API
        """
        self.module_b_url = module_b_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache_collection = "external_api_cache"
        
        # Cache settings
        self.default_ttl = timedelta(hours=24)  # 24 hour default TTL
        self.max_cache_size = 1000  # Maximum cached responses
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def _generate_cache_key(self, query: str, context: Optional[str] = None) -> str:
        """
        Generate cache key for query and context.
        
        Args:
            query: Original query
            context: Optional context
            
        Returns:
            Cache key string
        """
        # Normalize query and context
        normalized_query = query.strip().lower()
        normalized_context = context.strip().lower() if context else ""
        
        # Create hash of normalized content
        content = f"{normalized_query}|{normalized_context}"
        cache_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return f"ext_cache_{cache_key}"
    
    async def check_module_b_health(self) -> bool:
        """
        Check if Module B is available for caching.
        
        Returns:
            True if Module B is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.module_b_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Module B health check failed: {e}")
            return False
    
    async def get_cached_response(self, query: str, context: Optional[str] = None) -> Optional[ExternalResponse]:
        """
        Retrieve cached response for query.
        
        Args:
            query: Original query
            context: Optional context
            
        Returns:
            Cached ExternalResponse if found, None otherwise
        """
        try:
            cache_key = self._generate_cache_key(query, context)
            
            # Search for cached response in Module B
            search_payload = {
                "query": f"cache_key:{cache_key}",
                "top_k": 1,
                "threshold": 0.9  # High threshold for exact matches
            }
            
            response = await self.client.post(
                f"{self.module_b_url}/search",
                json=search_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                snippets = data.get('snippets', [])
                
                if snippets:
                    # Parse cached response
                    cached_content = snippets[0]['content']
                    
                    try:
                        # Extract JSON from cached content
                        if 'CACHED_RESPONSE:' in cached_content:
                            json_str = cached_content.split('CACHED_RESPONSE:')[1].strip()
                            cached_data = json.loads(json_str)
                            
                            # Check if cache is still valid
                            cached_time = datetime.fromisoformat(cached_data['timestamp'])
                            if datetime.now() - cached_time < self.default_ttl:
                                
                                # Reconstruct ExternalResponse
                                cached_response = ExternalResponse(
                                    success=cached_data['success'],
                                    response=cached_data['response'],
                                    source=cached_data['source'],
                                    confidence=cached_data['confidence'],
                                    processing_time=cached_data['processing_time'],
                                    cached=True,
                                    error=cached_data.get('error'),
                                    metadata=cached_data.get('metadata', {})
                                )
                                
                                logger.info(f"Cache hit for query: {query[:50]}...")
                                return cached_response
                            else:
                                logger.info(f"Cache expired for query: {query[:50]}...")
                        
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.warning(f"Failed to parse cached response: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def store_response(self, query: str, response: ExternalResponse, context: Optional[str] = None) -> bool:
        """
        Store external API response in cache.
        
        Args:
            query: Original query
            response: ExternalResponse to cache
            context: Optional context
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(query, context)
            
            # Prepare cache document
            cache_data = {
                "cache_key": cache_key,
                "query": query,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "success": response.success,
                "response": response.response,
                "source": response.source,
                "confidence": response.confidence,
                "processing_time": response.processing_time,
                "error": response.error,
                "metadata": response.metadata or {}
            }
            
            # Create document content for Module B
            document_content = f"""External API Cache Entry
Cache Key: {cache_key}
Query: {query}
Context: {context or 'None'}
Source: {response.source}
Confidence: {response.confidence}
Timestamp: {cache_data['timestamp']}

Response:
{response.response}

CACHED_RESPONSE: {json.dumps(cache_data)}
"""
            
            # Upload to Module B
            upload_payload = {
                "content": document_content,
                "metadata": {
                    "source": "external_api_cache",
                    "type": "cache_entry",
                    "cache_key": cache_key,
                    "query_hash": hashlib.sha256(query.encode()).hexdigest()[:8],
                    "timestamp": cache_data['timestamp']
                }
            }
            
            response = await self.client.post(
                f"{self.module_b_url}/upload_content",
                json=upload_payload
            )
            
            if response.status_code == 200:
                logger.info(f"Cached response for query: {query[:50]}...")
                return True
            else:
                logger.error(f"Failed to cache response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
            return False
    
    async def clear_expired_cache(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        try:
            # Search for all cache entries
            search_payload = {
                "query": "External API Cache Entry",
                "top_k": self.max_cache_size,
                "threshold": 0.5
            }
            
            response = await self.client.post(
                f"{self.module_b_url}/search",
                json=search_payload
            )
            
            if response.status_code != 200:
                return 0
            
            data = response.json()
            snippets = data.get('snippets', [])
            
            expired_count = 0
            cutoff_time = datetime.now() - self.default_ttl
            
            for snippet in snippets:
                try:
                    content = snippet['content']
                    if 'CACHED_RESPONSE:' in content:
                        json_str = content.split('CACHED_RESPONSE:')[1].strip()
                        cached_data = json.loads(json_str)
                        
                        cached_time = datetime.fromisoformat(cached_data['timestamp'])
                        if cached_time < cutoff_time:
                            # This entry is expired
                            expired_count += 1
                            # Note: Actual deletion would require Module B delete API
                            
                except Exception as e:
                    logger.warning(f"Failed to check cache entry expiration: {e}")
                    continue
            
            logger.info(f"Found {expired_count} expired cache entries")
            return expired_count
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return 0
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache usage statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # Search for all cache entries
            search_payload = {
                "query": "External API Cache Entry",
                "top_k": self.max_cache_size,
                "threshold": 0.5
            }
            
            response = await self.client.post(
                f"{self.module_b_url}/search",
                json=search_payload
            )
            
            if response.status_code != 200:
                return {"error": "Failed to retrieve cache statistics"}
            
            data = response.json()
            snippets = data.get('snippets', [])
            
            stats = {
                "total_entries": len(snippets),
                "valid_entries": 0,
                "expired_entries": 0,
                "sources": {},
                "oldest_entry": None,
                "newest_entry": None
            }
            
            cutoff_time = datetime.now() - self.default_ttl
            entry_times = []
            
            for snippet in snippets:
                try:
                    content = snippet['content']
                    if 'CACHED_RESPONSE:' in content:
                        json_str = content.split('CACHED_RESPONSE:')[1].strip()
                        cached_data = json.loads(json_str)
                        
                        cached_time = datetime.fromisoformat(cached_data['timestamp'])
                        entry_times.append(cached_time)
                        
                        source = cached_data.get('source', 'unknown')
                        stats['sources'][source] = stats['sources'].get(source, 0) + 1
                        
                        if cached_time >= cutoff_time:
                            stats['valid_entries'] += 1
                        else:
                            stats['expired_entries'] += 1
                            
                except Exception as e:
                    logger.warning(f"Failed to parse cache entry for stats: {e}")
                    continue
            
            if entry_times:
                stats['oldest_entry'] = min(entry_times).isoformat()
                stats['newest_entry'] = max(entry_times).isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {"error": str(e)}


# Global cache manager instance
cache_manager = CacheManager()


async def get_cached_response(query: str, context: Optional[str] = None) -> Optional[ExternalResponse]:
    """Convenience function for cache retrieval."""
    return await cache_manager.get_cached_response(query, context)


async def store_response(query: str, response: ExternalResponse, context: Optional[str] = None) -> bool:
    """Convenience function for cache storage."""
    return await cache_manager.store_response(query, response, context)