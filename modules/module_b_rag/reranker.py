"""
Reranker for RAG Knowledge Vault - Grok's Implementation.
Cross-encoder reranking using sentence-transformers.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import CrossEncoder
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Reranker will use fallback scoring.")


class Reranker:
    """Cross-encoder reranker for improving search result quality."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", score_cutoff: float = 0.3):
        """
        Initialize reranker with cross-encoder model.
        
        Args:
            model_name: HuggingFace model name for cross-encoder
            score_cutoff: Minimum score threshold for results
        """
        self.model_name = model_name
        self.score_cutoff = score_cutoff
        self.model = None
        self._model_loaded = False
        
        # Try to load model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = CrossEncoder(model_name)
                self._model_loaded = True
                logger.info(f"Reranker loaded: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load reranker model {model_name}: {e}")
                self._model_loaded = False
        else:
            logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
    
    async def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank search results using cross-encoder.
        
        Args:
            query: Search query
            candidates: List of candidate results with 'content' field
            top_k: Maximum number of results to return
            
        Returns:
            Reranked and filtered results
        """
        if not candidates:
            return []
        
        if not self._model_loaded:
            # Fallback to original scoring
            logger.debug("Reranker not available, using fallback scoring")
            return await self._fallback_rerank(query, candidates, top_k)
        
        try:
            start_time = time.time()
            
            # Prepare query-document pairs for cross-encoder
            pairs = []
            for candidate in candidates:
                content = candidate.get('content', '')
                if content.strip():
                    pairs.append([query, content])
            
            if not pairs:
                return []
            
            # Get cross-encoder scores
            scores = self.model.predict(pairs)
            
            # Combine scores with candidates
            scored_candidates = []
            for i, (candidate, score) in enumerate(zip(candidates, scores)):
                if score >= self.score_cutoff:
                    candidate_copy = candidate.copy()
                    candidate_copy['rerank_score'] = float(score)
                    candidate_copy['original_score'] = candidate.get('score', 0.0)
                    scored_candidates.append(candidate_copy)
            
            # Sort by rerank score (descending)
            scored_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Limit to top_k
            results = scored_candidates[:top_k]
            
            rerank_time = time.time() - start_time
            logger.info(f"Reranked {len(candidates)} → {len(results)} results in {rerank_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback to original scoring
            return await self._fallback_rerank(query, candidates, top_k)
    
    async def _fallback_rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """
        Fallback reranking using simple text similarity.
        """
        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            scored_candidates = []
            for candidate in candidates:
                content = candidate.get('content', '').lower()
                content_words = set(content.split())
                
                # Simple word overlap scoring
                overlap = len(query_words.intersection(content_words))
                total_words = len(query_words.union(content_words))
                
                if total_words > 0:
                    similarity = overlap / total_words
                else:
                    similarity = 0.0
                
                if similarity >= self.score_cutoff:
                    candidate_copy = candidate.copy()
                    candidate_copy['rerank_score'] = similarity
                    candidate_copy['original_score'] = candidate.get('score', 0.0)
                    scored_candidates.append(candidate_copy)
            
            # Sort by similarity score
            scored_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            return scored_candidates[:top_k]
            
        except Exception as e:
            logger.error(f"Fallback reranking failed: {e}")
            # Return original candidates with minimal processing
            return candidates[:top_k]
    
    async def rerank_with_context(self, query: str, context: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank with additional context.
        
        Args:
            query: Primary query
            context: Additional context
            candidates: Candidate results
            top_k: Maximum results
            
        Returns:
            Reranked results considering context
        """
        # Combine query and context for better reranking
        enhanced_query = f"{query} {context}".strip()
        return await self.rerank(enhanced_query, candidates, top_k)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranker model."""
        return {
            "model_name": self.model_name,
            "score_cutoff": self.score_cutoff,
            "model_loaded": self._model_loaded,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "fallback_mode": not self._model_loaded
        }
    
    async def validate_reranking(self, test_queries: List[str], test_documents: List[str]) -> Dict[str, Any]:
        """
        Validate reranking quality with test data.
        
        Args:
            test_queries: List of test queries
            test_documents: List of test documents
            
        Returns:
            Validation results
        """
        try:
            results = {
                "total_tests": len(test_queries),
                "successful_reranks": 0,
                "average_rerank_time": 0,
                "score_distribution": {"high": 0, "medium": 0, "low": 0},
                "test_results": []
            }
            
            total_time = 0
            
            for query in test_queries:
                try:
                    # Create mock candidates from test documents
                    candidates = [
                        {"content": doc, "score": 0.5, "source": f"test_doc_{i}"}
                        for i, doc in enumerate(test_documents)
                    ]
                    
                    start_time = time.time()
                    reranked = await self.rerank(query, candidates, top_k=5)
                    rerank_time = time.time() - start_time
                    
                    total_time += rerank_time
                    
                    if reranked:
                        results["successful_reranks"] += 1
                        
                        # Analyze score distribution
                        avg_score = sum(r.get('rerank_score', 0) for r in reranked) / len(reranked)
                        if avg_score >= 0.7:
                            results["score_distribution"]["high"] += 1
                        elif avg_score >= 0.4:
                            results["score_distribution"]["medium"] += 1
                        else:
                            results["score_distribution"]["low"] += 1
                    
                    results["test_results"].append({
                        "query": query,
                        "results_count": len(reranked),
                        "avg_score": sum(r.get('rerank_score', 0) for r in reranked) / len(reranked) if reranked else 0,
                        "rerank_time": rerank_time
                    })
                    
                except Exception as e:
                    logger.error(f"Validation test failed for query '{query}': {e}")
                    continue
            
            results["average_rerank_time"] = total_time / len(test_queries) if test_queries else 0
            
            return results
            
        except Exception as e:
            logger.error(f"Reranking validation failed: {e}")
            return {"error": str(e)}


# Convenience function for external use
async def rerank_results(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for reranking results."""
    reranker = Reranker()
    return await reranker.rerank(query, candidates, top_k)


if __name__ == "__main__":
    # Test the reranker
    async def test_reranker():
        reranker = Reranker()
        
        test_query = "Linux file permissions"
        test_candidates = [
            {"content": "chmod 755 sets read, write, execute for owner", "score": 0.8, "source": "doc1"},
            {"content": "Python file handling with open() function", "score": 0.7, "source": "doc2"},
            {"content": "Linux chmod command changes file permissions", "score": 0.6, "source": "doc3"},
            {"content": "Docker container networking configuration", "score": 0.5, "source": "doc4"}
        ]
        
        print(f"Query: {test_query}")
        print(f"Original candidates: {len(test_candidates)}")
        
        reranked = await reranker.rerank(test_query, test_candidates, top_k=3)
        
        print(f"Reranked results: {len(reranked)}")
        for i, result in enumerate(reranked, 1):
            print(f"{i}. Score: {result.get('rerank_score', 0):.3f} - {result['content'][:50]}...")
    
    # Run test
    asyncio.run(test_reranker())