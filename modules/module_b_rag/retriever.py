"""
Retriever for RAG Knowledge Vault.
Performs semantic search and retrieval of relevant document chunks.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from modules.module_b_rag.vector_store import VectorStore
from modules.module_b_rag.embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)


class Retriever:
    """Handles semantic search and retrieval of document chunks."""
    
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store instance for data retrieval
            embedding_manager: Embedding manager for query embedding
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
    
    async def search(self, query: str, top_k: int = 3, threshold: float = 0.6, 
                    source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search for relevant document chunks.
        
        Args:
            query: Search query text
            top_k: Maximum number of results to return
            threshold: Similarity threshold (0.0 to 1.0)
            source_filter: Optional filter by document source
            
        Returns:
            List of relevant chunks with content, source, and similarity scores
            
        Raises:
            RuntimeError: If search fails
        """
        try:
            start_time = time.time()
            
            # Validate inputs
            if not query.strip():
                return []
            
            if top_k <= 0:
                top_k = 3
            
            if threshold < 0.0 or threshold > 1.0:
                threshold = 0.6
            
            # Generate query embedding
            query_embedding = await self.embedding_manager.generate_embedding(query)
            
            # Prepare metadata filter
            where_filter = None
            if source_filter:
                where_filter = {"source": source_filter}
            
            # Perform vector search
            search_results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=threshold,
                where=where_filter
            )
            
            # Post-process results
            processed_results = []
            for result in search_results:
                processed_result = {
                    "content": result["content"],
                    "source": result["source"],
                    "score": result["score"],
                    "metadata": result.get("metadata", {})
                }
                
                # Add relevance indicators
                processed_result["metadata"]["search_query"] = query
                processed_result["metadata"]["search_timestamp"] = time.time()
                
                processed_results.append(processed_result)
            
            search_time = time.time() - start_time
            
            logger.info(f"Search completed: '{query}' -> {len(processed_results)} results in {search_time:.3f}s")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def search_with_context(self, query: str, context: str, top_k: int = 3, 
                                 threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Perform contextual search by combining query with context.
        
        Args:
            query: Primary search query
            context: Additional context to enhance search
            top_k: Maximum number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of relevant chunks with enhanced relevance scoring
        """
        try:
            # Combine query and context for better search
            enhanced_query = f"{query} {context}".strip()
            
            # Perform standard search with enhanced query
            results = await self.search(
                query=enhanced_query,
                top_k=top_k * 2,  # Get more results for re-ranking
                threshold=threshold * 0.8  # Lower threshold for initial search
            )
            
            # Re-rank results based on relevance to original query
            if len(results) > top_k:
                # Generate embedding for original query
                query_embedding = await self.embedding_manager.generate_embedding(query)
                
                # Re-score results based on original query
                rescored_results = []
                for result in results:
                    content_embedding = await self.embedding_manager.generate_embedding(result["content"])
                    
                    # Calculate similarity to original query
                    similarity_results = await self.embedding_manager.similarity_search_embedding(
                        query_embedding, [content_embedding], threshold=0.0
                    )
                    
                    if similarity_results:
                        result["score"] = similarity_results[0]["score"]
                        result["metadata"]["context_enhanced"] = True
                        rescored_results.append(result)
                
                # Sort by new scores and limit results
                rescored_results.sort(key=lambda x: x["score"], reverse=True)
                results = rescored_results[:top_k]
            
            return results
            
        except Exception as e:
            logger.error(f"Contextual search failed: {e}")
            # Fallback to regular search
            return await self.search(query, top_k, threshold)
    
    async def search_by_source(self, query: str, source: str, top_k: int = 3, 
                              threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Search within a specific document source.
        
        Args:
            query: Search query
            source: Document source to search within
            top_k: Maximum number of results
            threshold: Similarity threshold
            
        Returns:
            List of relevant chunks from the specified source
        """
        return await self.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            source_filter=source
        )
    
    async def get_similar_chunks(self, reference_content: str, top_k: int = 5, 
                                threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a reference content.
        
        Args:
            reference_content: Reference text to find similar content for
            top_k: Maximum number of results
            threshold: Similarity threshold (higher for similarity search)
            
        Returns:
            List of similar chunks
        """
        try:
            # Use the reference content as the search query
            return await self.search(
                query=reference_content,
                top_k=top_k,
                threshold=threshold
            )
            
        except Exception as e:
            logger.error(f"Similar chunks search failed: {e}")
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the retrieval system.
        
        Returns:
            Dictionary with retrieval statistics
        """
        try:
            vector_stats = self.vector_store.get_statistics()
            embedding_info = self.embedding_manager.get_model_info()
            
            return {
                "vector_store": vector_stats,
                "embedding_model": embedding_info,
                "search_capabilities": {
                    "semantic_search": True,
                    "contextual_search": True,
                    "source_filtering": True,
                    "similarity_matching": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get search statistics: {e}")
            return {
                "error": str(e),
                "vector_store": {},
                "embedding_model": {},
                "search_capabilities": {}
            }
    
    async def validate_search_quality(self, test_queries: List[str], 
                                     expected_sources: List[str]) -> Dict[str, Any]:
        """
        Validate search quality with test queries.
        
        Args:
            test_queries: List of test queries
            expected_sources: List of expected source documents
            
        Returns:
            Dictionary with validation results
        """
        try:
            results = {
                "total_queries": len(test_queries),
                "successful_searches": 0,
                "average_results_per_query": 0,
                "sources_found": set(),
                "query_results": []
            }
            
            total_results = 0
            
            for query in test_queries:
                try:
                    search_results = await self.search(query, top_k=5, threshold=0.5)
                    
                    query_result = {
                        "query": query,
                        "results_count": len(search_results),
                        "sources": [r["source"] for r in search_results],
                        "avg_score": sum(r["score"] for r in search_results) / len(search_results) if search_results else 0
                    }
                    
                    results["query_results"].append(query_result)
                    
                    if search_results:
                        results["successful_searches"] += 1
                        total_results += len(search_results)
                        results["sources_found"].update(r["source"] for r in search_results)
                
                except Exception as e:
                    logger.error(f"Test query failed: {query} - {e}")
                    continue
            
            results["average_results_per_query"] = total_results / len(test_queries) if test_queries else 0
            results["sources_found"] = list(results["sources_found"])
            results["source_coverage"] = len(results["sources_found"]) / len(expected_sources) if expected_sources else 0
            
            return results
            
        except Exception as e:
            logger.error(f"Search quality validation failed: {e}")
            return {"error": str(e)}