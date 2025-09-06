"""
Knowledge client for Module A to communicate with Module B (RAG Knowledge Vault).
Handles context retrieval and integration for enhanced AI responses.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContextSnippet:
    """Context snippet from knowledge base."""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


class KnowledgeClient:
    """Client for communicating with Module B RAG Knowledge Vault."""
    
    def __init__(self, base_url: str = "http://localhost:8002", timeout: float = 5.0):
        """
        Initialize knowledge client.
        
        Args:
            base_url: Base URL for Module B API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = None
        self._available = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def health_check(self) -> bool:
        """
        Check if Module B is available.
        
        Returns:
            True if Module B is healthy and available
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                is_healthy = data.get("status") == "ok"
                self._available = is_healthy
                logger.debug(f"Module B health check: {is_healthy}")
                return is_healthy
            else:
                logger.warning(f"Module B health check failed: HTTP {response.status_code}")
                self._available = False
                return False
                
        except Exception as e:
            logger.warning(f"Module B health check failed: {e}")
            self._available = False
            return False
    
    async def search_context(self, query: str, top_k: int = 3, threshold: float = 0.6) -> List[ContextSnippet]:
        """
        Search for relevant context in the knowledge base.
        
        Args:
            query: Search query
            top_k: Maximum number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant context snippets
        """
        try:
            # Check availability first
            if self._available is None:
                await self.health_check()
            
            if not self._available:
                logger.info("Module B not available, skipping context search")
                return []
            
            client = await self._get_client()
            
            # Prepare search request
            search_data = {
                "query": query,
                "top_k": top_k,
                "threshold": threshold
            }
            
            logger.debug(f"Searching context for query: '{query}' (top_k={top_k}, threshold={threshold})")
            
            # Make search request
            response = await client.post(
                f"{self.base_url}/search",
                json=search_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                snippets = []
                
                for snippet_data in data.get("snippets", []):
                    snippet = ContextSnippet(
                        content=snippet_data["content"],
                        source=snippet_data["source"],
                        score=snippet_data["score"],
                        metadata=snippet_data.get("metadata", {})
                    )
                    snippets.append(snippet)
                
                logger.info(f"Retrieved {len(snippets)} context snippets for query '{query}'")
                return snippets
                
            else:
                logger.error(f"Context search failed: HTTP {response.status_code} - {response.text}")
                return []
                
        except asyncio.TimeoutError:
            logger.warning(f"Context search timed out for query '{query}'")
            self._available = False
            return []
        except Exception as e:
            logger.error(f"Context search failed for query '{query}': {e}")
            self._available = False
            return []
    
    def format_context_for_prompt(self, snippets: List[ContextSnippet], max_length: int = 2000) -> str:
        """
        Format context snippets for inclusion in AI prompts.
        
        Args:
            snippets: List of context snippets
            max_length: Maximum total length of formatted context
            
        Returns:
            Formatted context string for prompt inclusion
        """
        if not snippets:
            return ""
        
        context_parts = []
        current_length = 0
        
        # Sort by relevance score (highest first)
        sorted_snippets = sorted(snippets, key=lambda x: x.score, reverse=True)
        
        for snippet in sorted_snippets:
            # Format snippet with source attribution
            snippet_text = f"[Source: {snippet.source}] {snippet.content}"
            
            # Check if adding this snippet would exceed max length
            if current_length + len(snippet_text) + 10 > max_length:  # +10 for separators
                break
            
            context_parts.append(snippet_text)
            current_length += len(snippet_text) + 10
        
        if context_parts:
            formatted_context = "\n\n".join(context_parts)
            logger.debug(f"Formatted context: {len(formatted_context)} chars from {len(context_parts)} snippets")
            return formatted_context
        else:
            return ""
    
    def get_context_sources(self, snippets: List[ContextSnippet]) -> List[str]:
        """
        Extract unique source names from context snippets.
        
        Args:
            snippets: List of context snippets
            
        Returns:
            List of unique source names
        """
        sources = list(set(snippet.source for snippet in snippets))
        return sorted(sources)
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get client status information.
        
        Returns:
            Dictionary with client status
        """
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "available": self._available,
            "client_active": self._client is not None
        }


class ContextIntegrator:
    """Integrates context into AI prompts for enhanced responses."""
    
    def __init__(self, knowledge_client: KnowledgeClient):
        """
        Initialize context integrator.
        
        Args:
            knowledge_client: Knowledge client for context retrieval
        """
        self.knowledge_client = knowledge_client
    
    async def enhance_query_with_context(self, query: str, context_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance a query with relevant context from the knowledge base.
        
        Args:
            query: Original user query
            context_config: Optional configuration for context search
            
        Returns:
            Dictionary with enhanced query, context, and metadata
        """
        # Default context configuration
        config = {
            "top_k": 3,
            "threshold": 0.6,
            "max_context_length": 2000,
            "enable_context": True
        }
        
        if context_config:
            config.update(context_config)
        
        result = {
            "original_query": query,
            "enhanced_query": query,
            "context": "",
            "context_snippets": [],
            "sources": [],
            "context_used": False
        }
        
        # Skip context if disabled
        if not config.get("enable_context", True):
            logger.debug("Context enhancement disabled")
            return result
        
        try:
            # Search for relevant context
            snippets = await self.knowledge_client.search_context(
                query=query,
                top_k=config["top_k"],
                threshold=config["threshold"]
            )
            
            if snippets:
                # Format context for prompt
                context_text = self.knowledge_client.format_context_for_prompt(
                    snippets, 
                    max_length=config["max_context_length"]
                )
                
                if context_text:
                    # Create enhanced query with context
                    enhanced_query = self._create_context_enhanced_prompt(query, context_text)
                    
                    result.update({
                        "enhanced_query": enhanced_query,
                        "context": context_text,
                        "context_snippets": snippets,
                        "sources": self.knowledge_client.get_context_sources(snippets),
                        "context_used": True
                    })
                    
                    logger.info(f"Enhanced query with {len(snippets)} context snippets from {len(result['sources'])} sources")
                else:
                    logger.debug("No context formatted (empty after processing)")
            else:
                logger.debug("No relevant context found for query")
                
        except Exception as e:
            logger.error(f"Context enhancement failed: {e}")
            # Return original query on error
        
        return result
    
    def _create_context_enhanced_prompt(self, query: str, context: str) -> str:
        """
        Create an enhanced prompt that includes context.
        
        Args:
            query: Original user query
            context: Formatted context from knowledge base
            
        Returns:
            Enhanced prompt with context
        """
        enhanced_prompt = f"""You are a helpful Linux system administrator assistant. Use the following relevant documentation to provide accurate and detailed responses.

RELEVANT DOCUMENTATION:
{context}

USER QUERY: {query}

Please provide a comprehensive response based on the documentation above. If the documentation doesn't fully cover the query, supplement with your general knowledge but clearly indicate what comes from the provided documentation versus general knowledge."""

        return enhanced_prompt
    
    def extract_response_attribution(self, response_text: str, sources: List[str]) -> Dict[str, Any]:
        """
        Extract attribution information from AI response.
        
        Args:
            response_text: AI-generated response text
            sources: List of source documents used for context
            
        Returns:
            Dictionary with response and attribution information
        """
        return {
            "response": response_text,
            "sources_used": sources,
            "has_context": len(sources) > 0,
            "attribution_note": f"Response enhanced with information from: {', '.join(sources)}" if sources else None
        }