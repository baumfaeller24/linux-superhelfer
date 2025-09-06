"""
Web Enhancement Client for Module A
Automatically enhances knowledge base when needed
"""

import asyncio
import aiohttp
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class WebEnhancer:
    def __init__(self, web_scraper_url: str = "http://localhost:8005"):
        self.web_scraper_url = web_scraper_url
        self.enhancement_threshold = 0.5  # Confidence threshold for enhancement
        
    async def should_enhance_knowledge(self, query: str, confidence: float, sources: list) -> bool:
        """Determine if knowledge base should be enhanced for this query"""
        
        # Enhance if confidence is low and we have few sources
        if confidence < self.enhancement_threshold and len(sources) < 2:
            return True
            
        # Enhance if no sources found
        if not sources:
            return True
            
        return False
    
    async def enhance_knowledge_for_query(self, query: str) -> Optional[Dict]:
        """Automatically enhance knowledge base for a specific query"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.web_scraper_url}/auto_enhance_query",
                    params={"query": query}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Knowledge enhancement result: {result}")
                        return result
                    else:
                        logger.warning(f"Enhancement failed with status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Web enhancement failed: {e}")
            return None
    
    async def search_and_learn(self, query: str, max_sources: int = 3) -> Optional[Dict]:
        """Trigger web search and learning for a query"""
        try:
            payload = {
                "query": query,
                "max_sources": max_sources,
                "source_types": ["wiki", "stackoverflow"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.web_scraper_url}/search_and_learn",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Web learning completed: {result['sources_uploaded']} sources added")
                        return result
                    else:
                        logger.warning(f"Web learning failed with status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Web learning failed: {e}")
            return None