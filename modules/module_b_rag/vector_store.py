"""
Vector store for RAG Knowledge Vault.
Manages persistent storage and retrieval using ChromaDB.
"""

import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from modules.module_b_rag.chunk_processor import DocumentChunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, persist_directory: str, collection_name: str = "documents"):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document chunks for RAG system"}
            )
            
            logger.info(f"Initialized ChromaDB at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"Vector store initialization failed: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check if vector store is accessible.
        
        Returns:
            True if vector store is healthy
        """
        try:
            # Try to access the collection
            count = self.collection.count()
            logger.debug(f"Vector store health check: {count} documents")
            return True
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return False
    
    def add_chunk(self, chunk: DocumentChunk, embedding: List[float]) -> str:
        """
        Add a document chunk with its embedding to the store.
        
        Args:
            chunk: Document chunk to store
            embedding: Embedding vector for the chunk
            
        Returns:
            Unique ID for the stored chunk
            
        Raises:
            RuntimeError: If storage fails
        """
        try:
            # Generate unique ID if not provided
            chunk_id = chunk.chunk_id or str(uuid.uuid4())
            
            # Prepare metadata (ChromaDB requires string values)
            metadata = {
                "source": chunk.source,
                "chunk_index": str(chunk.metadata.get("chunk_index", 0)),
                "token_count": str(chunk.token_count),
                "content_length": str(len(chunk.content)),
                "file_type": chunk.metadata.get("file_type", "unknown")
            }
            
            # Add additional metadata as strings
            for key, value in chunk.metadata.items():
                if key not in metadata and value is not None:
                    metadata[f"meta_{key}"] = str(value)
            
            # Add to collection
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk.content],
                metadatas=[metadata]
            )
            
            logger.debug(f"Added chunk {chunk_id} to vector store")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Failed to add chunk to vector store: {e}")
            raise RuntimeError(f"Vector store add failed: {str(e)}")
    
    def add_chunks_batch(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> List[str]:
        """
        Add multiple chunks in batch for efficiency.
        
        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors
            
        Returns:
            List of chunk IDs
            
        Raises:
            RuntimeError: If batch storage fails
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")
            
            if not chunks:
                return []
            
            # Prepare batch data
            ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                chunk_id = chunk.chunk_id or str(uuid.uuid4())
                ids.append(chunk_id)
                documents.append(chunk.content)
                
                # Prepare metadata
                metadata = {
                    "source": chunk.source,
                    "chunk_index": str(chunk.metadata.get("chunk_index", 0)),
                    "token_count": str(chunk.token_count),
                    "content_length": str(len(chunk.content)),
                    "file_type": chunk.metadata.get("file_type", "unknown")
                }
                
                # Add additional metadata
                for key, value in chunk.metadata.items():
                    if key not in metadata and value is not None:
                        metadata[f"meta_{key}"] = str(value)
                
                metadatas.append(metadata)
            
            # Add batch to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store in batch")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add chunks batch to vector store: {e}")
            raise RuntimeError(f"Vector store batch add failed: {str(e)}")
    
    def search(self, query_embedding: List[float], top_k: int = 3, 
               threshold: float = 0.6, where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Similarity threshold (0.0 to 1.0)
            where: Optional metadata filter
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k * 2, 50),  # Get more results to filter by threshold
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Process results
            search_results = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                # For normalized embeddings: cosine_similarity = 1 - (L2_distance^2 / 2)
                # This gives values between 0 and 1, where 1 is perfect match
                similarity = max(0.0, 1.0 - (distance * distance / 2.0))
                
                logger.debug(f"Distance: {distance:.4f} -> Similarity: {similarity:.4f}")
                
                # Filter by threshold
                if similarity >= threshold:
                    # Convert metadata back to appropriate types
                    processed_metadata = {}
                    for key, value in metadata.items():
                        if key.startswith("meta_"):
                            processed_metadata[key[5:]] = value
                        elif key in ["chunk_index", "token_count", "content_length"]:
                            try:
                                processed_metadata[key] = int(value)
                            except (ValueError, TypeError):
                                processed_metadata[key] = value
                        else:
                            processed_metadata[key] = value
                    
                    search_results.append({
                        "content": doc,
                        "source": metadata.get("source", "unknown"),
                        "score": similarity,
                        "metadata": processed_metadata
                    })
            
            # Sort by similarity score (descending) and limit results
            search_results.sort(key=lambda x: x["score"], reverse=True)
            search_results = search_results[:top_k]
            
            logger.debug(f"Vector search returned {len(search_results)} results above threshold {threshold}")
            return search_results
            
        except Exception as e:
            logger.error(f"Vector store search failed: {e}")
            return []
    
    def delete_by_source(self, source: str) -> int:
        """
        Delete all chunks from a specific source.
        
        Args:
            source: Source identifier to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Find chunks from this source
            results = self.collection.get(
                where={"source": source},
                include=["metadatas"]
            )
            
            if not results['ids']:
                return 0
            
            # Delete the chunks
            self.collection.delete(ids=results['ids'])
            
            deleted_count = len(results['ids'])
            logger.info(f"Deleted {deleted_count} chunks from source '{source}'")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete chunks from source '{source}': {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        try:
            total_count = self.collection.count()
            
            # Get sample of metadata to analyze sources
            sample_results = self.collection.get(
                limit=min(1000, total_count),
                include=["metadatas"]
            )
            
            sources = set()
            file_types = set()
            
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    if 'source' in metadata:
                        sources.add(metadata['source'])
                    if 'file_type' in metadata:
                        file_types.add(metadata['file_type'])
            
            return {
                "collections": 1,
                "documents": total_count,
                "unique_sources": len(sources),
                "file_types": list(file_types),
                "storage_path": str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Failed to get vector store statistics: {e}")
            return {
                "collections": 0,
                "documents": 0,
                "unique_sources": 0,
                "file_types": [],
                "storage_path": str(self.persist_directory),
                "error": str(e)
            }
    
    def reset(self) -> bool:
        """
        Reset the vector store (delete all data).
        
        Returns:
            True if reset was successful
        """
        try:
            self.client.reset()
            
            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG system"}
            )
            
            logger.info("Vector store reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset vector store: {e}")
            return False