#!/usr/bin/env python3
"""
Reset ChromaDB and test Module B with normalized embeddings.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.module_b_rag.document_loader import DocumentLoader
from modules.module_b_rag.chunk_processor import ChunkProcessor
from modules.module_b_rag.embedding_manager import EmbeddingManager
from modules.module_b_rag.vector_store import VectorStore
from modules.module_b_rag.retriever import Retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_and_test():
    """Reset ChromaDB and test with normalized embeddings."""
    
    print("🔄 Resetting ChromaDB and testing with normalized embeddings")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing components...")
    document_loader = DocumentLoader()
    chunk_processor = ChunkProcessor()
    embedding_manager = EmbeddingManager()
    
    # Ensure data directory exists
    data_dir = Path("data/chromadb")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    vector_store = VectorStore(str(data_dir))
    retriever = Retriever(vector_store, embedding_manager)
    
    # Reset ChromaDB
    print("\n2. Resetting ChromaDB...")
    reset_success = vector_store.reset()
    print(f"   ✅ ChromaDB reset: {reset_success}")
    
    # Test embedding normalization
    print("\n3. Testing embedding normalization...")
    test_text = "Linux disk space can be checked with df -h command. This shows filesystem usage."
    embedding = await embedding_manager.generate_embedding(test_text)
    
    import numpy as np
    norm = np.linalg.norm(embedding)
    print(f"   📏 Embedding norm: {norm:.4f} (should be ~1.0)")
    print(f"   📊 Embedding range: [{min(embedding):.4f}, {max(embedding):.4f}]")
    
    # Add test document
    print("\n4. Adding test document with normalized embeddings...")
    import base64
    test_content = "Linux disk space can be checked with df -h command. This shows filesystem usage in human-readable format. Use df -h to see disk space usage."
    base64_content = base64.b64encode(test_content.encode()).decode()
    
    document = document_loader.load_from_base64(
        base64_content, 
        {"source": "test_normalized.txt", "type": "txt"}
    )
    
    chunks = chunk_processor.process_document(document)
    print(f"   📄 Created {len(chunks)} chunks")
    
    # Store with normalized embeddings
    for chunk in chunks:
        chunk_embedding = await embedding_manager.generate_embedding(chunk.content)
        chunk_id = vector_store.add_chunk(chunk, chunk_embedding)
        print(f"   ✅ Stored chunk: {chunk_id}")
    
    # Test search with various queries
    print("\n5. Testing search with normalized embeddings...")
    test_queries = [
        "How to check disk space?",
        "df -h command",
        "filesystem usage",
        "disk space usage",
        "show disk usage"
    ]
    
    for query in test_queries:
        print(f"\n   🔍 Query: '{query}'")
        
        # Test with different thresholds
        for threshold in [0.0, 0.3, 0.6, 0.8]:
            results = await retriever.search(
                query=query,
                top_k=3,
                threshold=threshold
            )
            
            print(f"      Threshold {threshold}: {len(results)} results")
            for i, result in enumerate(results):
                print(f"         {i+1}. Score: {result['score']:.4f} - '{result['content'][:50]}...'")
    
    # Test direct similarity calculation
    print("\n6. Testing direct similarity calculation...")
    query_embedding = await embedding_manager.generate_embedding("How to check disk space?")
    stored_embedding = await embedding_manager.generate_embedding(test_content)
    
    query_norm = np.linalg.norm(query_embedding)
    stored_norm = np.linalg.norm(stored_embedding)
    
    print(f"   📏 Query norm: {query_norm:.4f}")
    print(f"   📏 Stored norm: {stored_norm:.4f}")
    
    # Calculate cosine similarity
    dot_product = np.dot(query_embedding, stored_embedding)
    cosine_sim = dot_product / (query_norm * stored_norm)
    print(f"   🔢 Cosine similarity: {cosine_sim:.4f}")
    
    # Calculate L2 distance
    l2_distance = np.linalg.norm(np.array(query_embedding) - np.array(stored_embedding))
    print(f"   📐 L2 distance: {l2_distance:.4f}")
    
    # Calculate similarity from L2 distance (for normalized vectors)
    similarity_from_distance = max(0.0, 1.0 - (l2_distance * l2_distance / 2.0))
    print(f"   🎯 Similarity from L2: {similarity_from_distance:.4f}")
    
    print("\n" + "=" * 60)
    print("🎯 Reset and test completed!")

if __name__ == "__main__":
    asyncio.run(reset_and_test())