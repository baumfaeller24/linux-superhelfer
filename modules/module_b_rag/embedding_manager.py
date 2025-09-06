"""
Embedding manager for RAG Knowledge Vault.
Generates normalized embeddings using nomic-embed-text via Ollama.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
import ollama
from ollama import AsyncClient
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation using Ollama with nomic-embed-text model."""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "nomic-embed-text"):
        """
        Initialize embedding manager.
        
        Args:
            host: Ollama server host
            port: Ollama server port
            model: Embedding model name
        """
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.client = AsyncClient(host=self.base_url)
        self._model_available = None
    
    async def health_check(self) -> bool:
        """
        Check if embedding service is available.
        
        Returns:
            True if service is available and model is loaded
        """
        try:
            # Check if Ollama is running
            models = await self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            # Check if our embedding model is available
            model_available = any(self.model in model_name for model_name in available_models)
            
            if not model_available:
                logger.warning(f"Embedding model '{self.model}' not found. Available models: {available_models}")
                # Try to pull the model
                try:
                    logger.info(f"Attempting to pull model '{self.model}'...")
                    await self.client.pull(self.model)
                    model_available = True
                    logger.info(f"Successfully pulled model '{self.model}'")
                except Exception as pull_error:
                    logger.error(f"Failed to pull model '{self.model}': {pull_error}")
            
            self._model_available = model_available
            return model_available
            
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            self._model_available = False
            return False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate normalized embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Normalized embedding vector as list of floats
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        try:
            if not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
            
            # Check service availability
            if self._model_available is None:
                await self.health_check()
            
            if not self._model_available:
                raise RuntimeError("Embedding service not available")
            
            # Generate embedding using Ollama
            response = await self.client.embeddings(
                model=self.model,
                prompt=text
            )
            
            embedding = response['embedding']
            
            if not embedding or not isinstance(embedding, list):
                raise RuntimeError("Invalid embedding response from Ollama")
            
            # Normalize embedding to unit length for better similarity calculation
            normalized_embedding = self._normalize_embedding(embedding)
            
            logger.debug(f"Generated normalized embedding for text ({len(text)} chars): {len(normalized_embedding)} dimensions")
            return normalized_embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed for text '{text[:50]}...': {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
    
    async def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
            
        Raises:
            RuntimeError: If batch processing fails
        """
        try:
            if not texts:
                return []
            
            embeddings = []
            
            # Process in batches to avoid overwhelming the service
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = []
                
                for text in batch:
                    try:
                        embedding = await self.generate_embedding(text)
                        batch_embeddings.append(embedding)
                    except Exception as e:
                        logger.error(f"Failed to embed text in batch: {e}")
                        # Use zero vector as fallback
                        batch_embeddings.append([0.0] * 768)  # Assuming 768-dim embeddings
                
                embeddings.extend(batch_embeddings)
                
                # Small delay between batches to be nice to the service
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(embeddings)} embeddings in batches")
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}")
    
    async def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings from this model.
        
        Returns:
            Embedding dimension
        """
        try:
            # Generate a test embedding to determine dimension
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding)
            
        except Exception as e:
            logger.error(f"Failed to determine embedding dimension: {e}")
            # Return default dimension for nomic-embed-text
            return 768
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize embedding vector to unit length.
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            Normalized embedding vector
        """
        try:
            import numpy as np
            
            # Convert to numpy array
            vec = np.array(embedding, dtype=np.float32)
            
            # Calculate L2 norm
            norm = np.linalg.norm(vec)
            
            # Avoid division by zero
            if norm == 0:
                logger.warning("Zero-norm embedding detected, returning original")
                return embedding
            
            # Normalize to unit length
            normalized_vec = vec / norm
            
            # Convert back to list
            normalized_embedding = normalized_vec.tolist()
            
            logger.debug(f"Normalized embedding: norm {norm:.4f} -> 1.0")
            return normalized_embedding
            
        except Exception as e:
            logger.error(f"Embedding normalization failed: {e}")
            # Return original embedding as fallback
            return embedding
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "available": self._model_available,
            "normalized": True
        }
    
    async def similarity_search_embedding(self, query_embedding: List[float], 
                                        candidate_embeddings: List[List[float]], 
                                        threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Perform similarity search using embeddings.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            threshold: Similarity threshold
            
        Returns:
            List of similarity results with scores and indices
        """
        try:
            import numpy as np
            
            if not query_embedding or not candidate_embeddings:
                return []
            
            # Convert to numpy arrays for efficient computation
            query_vec = np.array(query_embedding)
            candidate_vecs = np.array(candidate_embeddings)
            
            # Normalize vectors
            query_norm = query_vec / np.linalg.norm(query_vec)
            candidate_norms = candidate_vecs / np.linalg.norm(candidate_vecs, axis=1, keepdims=True)
            
            # Compute cosine similarities
            similarities = np.dot(candidate_norms, query_norm)
            
            # Filter by threshold and sort
            results = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    results.append({
                        'index': i,
                        'score': float(similarity)
                    })
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []