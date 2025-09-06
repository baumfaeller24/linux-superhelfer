#!/usr/bin/env python3
"""
Debug script for Module B RAG search functionality.
Tests each component individually to identify the search issue.
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

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def debug_module_b():
    """Debug Module B components step by step."""
    
    print("🔍 Module B Debug Session")
    print("=" * 50)
    
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
    
    # Test 1: Embedding Manager
    print("\n2. Testing Embedding Manager...")
    try:
        health = await embedding_manager.health_check()
        print(f"   ✅ Health check: {health}")
        
        if health:
            test_text = "Linux disk space can be checked with df -h command"
            embedding = await embedding_manager.generate_embedding(test_text)
            print(f"   ✅ Generated embedding: {len(embedding)} dimensions")
            print(f"   📊 First 5 values: {embedding[:5]}")
            print(f"   📊 Embedding range: [{min(embedding):.4f}, {max(embedding):.4f}]")
        else:
            print("   ❌ Embedding service not available")
            return
    except Exception as e:
        print(f"   ❌ Embedding test failed: {e}")
        return
    
    # Test 2: Document Processing
    print("\n3. Testing Document Processing...")
    try:
        import base64
        test_content = "Linux disk space can be checked with df -h command. This shows filesystem usage."
        base64_content = base64.b64encode(test_content.encode()).decode()
        
        document = document_loader.load_from_base64(
            base64_content, 
            {"source": "test.txt", "type": "txt"}
        )
        print(f"   ✅ Document loaded: {len(document.content)} chars")
        
        chunks = chunk_processor.process_document(document)
        print(f"   ✅ Document chunked: {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"   📄 Chunk {i}: {len(chunk.content)} chars, {chunk.token_count} tokens")
            print(f"      Content preview: {chunk.content[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Document processing failed: {e}")
        return
    
    # Test 3: Vector Store Operations
    print("\n4. Testing Vector Store...")
    try:
        # Check current state
        stats = vector_store.get_statistics()
        print(f"   📊 Current stats: {stats}")
        
        # Add test chunk with embedding
        test_chunk = chunks[0]  # Use first chunk from above
        test_embedding = await embedding_manager.generate_embedding(test_chunk.content)
        
        chunk_id = vector_store.add_chunk(test_chunk, test_embedding)
        print(f"   ✅ Added chunk: {chunk_id}")
        
        # Verify storage
        new_stats = vector_store.get_statistics()
        print(f"   📊 Updated stats: {new_stats}")
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        return
    
    # Test 4: Direct ChromaDB Query
    print("\n5. Testing Direct ChromaDB Query...")
    try:
        collection = vector_store.collection
        
        # Get all documents
        all_docs = collection.get(include=["documents", "metadatas", "embeddings"])
        print(f"   📊 Total documents in ChromaDB: {len(all_docs['ids'])}")
        
        if all_docs['ids']:
            print(f"   📄 First document ID: {all_docs['ids'][0]}")
            print(f"   📄 First document content: {all_docs['documents'][0][:100]}...")
            print(f"   📄 First document metadata: {all_docs['metadatas'][0]}")
            
            if all_docs['embeddings']:
                embedding_dim = len(all_docs['embeddings'][0])
                print(f"   🔢 Embedding dimension: {embedding_dim}")
                print(f"   🔢 Embedding sample: {all_docs['embeddings'][0][:5]}")
        
    except Exception as e:
        print(f"   ❌ Direct ChromaDB query failed: {e}")
        return
    
    # Test 5: Manual Similarity Search
    print("\n6. Testing Manual Similarity Search...")
    try:
        query_text = "How to check disk space?"
        query_embedding = await embedding_manager.generate_embedding(query_text)
        print(f"   🔍 Query: '{query_text}'")
        print(f"   🔢 Query embedding: {len(query_embedding)} dimensions")
        
        # Test with different thresholds
        thresholds = [0.0, 0.3, 0.6, 0.9]
        
        for threshold in thresholds:
            results = vector_store.search(
                query_embedding=query_embedding,
                top_k=5,
                threshold=threshold
            )
            print(f"   📊 Threshold {threshold}: {len(results)} results")
            
            for i, result in enumerate(results):
                print(f"      Result {i+1}: score={result['score']:.4f}, content='{result['content'][:50]}...'")
        
    except Exception as e:
        print(f"   ❌ Manual similarity search failed: {e}")
        return
    
    # Test 6: ChromaDB Raw Query
    print("\n7. Testing ChromaDB Raw Query...")
    try:
        # Direct ChromaDB query with embedding
        raw_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"   📊 Raw ChromaDB results: {len(raw_results['documents'][0]) if raw_results['documents'] else 0}")
        
        if raw_results['documents'] and raw_results['documents'][0]:
            for i, (doc, distance) in enumerate(zip(raw_results['documents'][0], raw_results['distances'][0])):
                # Calculate similarity from distance (for normalized embeddings)
                similarity = max(0.0, 1.0 - (distance * distance / 2.0))
                print(f"      Raw result {i+1}: distance={distance:.4f}, similarity={similarity:.4f}")
                print(f"         Content: '{doc[:50]}...'")
        
    except Exception as e:
        print(f"   ❌ ChromaDB raw query failed: {e}")
        return
    
    # Test 6.5: Check embedding normalization
    print("\n7.5. Testing Embedding Normalization...")
    try:
        import numpy as np
        
        # Check if embeddings are normalized
        query_norm = np.linalg.norm(query_embedding)
        print(f"   📏 Query embedding norm: {query_norm:.4f} (should be ~1.0 for normalized)")
        
        # Get stored embedding and check its norm
        if all_docs['embeddings']:
            stored_embedding = all_docs['embeddings'][0]
            stored_norm = np.linalg.norm(stored_embedding)
            print(f"   📏 Stored embedding norm: {stored_norm:.4f} (should be ~1.0 for normalized)")
            
            # Calculate cosine similarity manually
            dot_product = np.dot(query_embedding, stored_embedding)
            cosine_sim = dot_product / (query_norm * stored_norm)
            print(f"   🔢 Manual cosine similarity: {cosine_sim:.4f}")
        
    except Exception as e:
        print(f"   ❌ Embedding normalization test failed: {e}")
    
    # Test 7: Retriever Search
    print("\n8. Testing Retriever Search...")
    try:
        search_results = await retriever.search(
            query="How to check disk space?",
            top_k=3,
            threshold=0.0  # Very low threshold to see any results
        )
        
        print(f"   📊 Retriever results: {len(search_results)}")
        
        for i, result in enumerate(search_results):
            print(f"      Result {i+1}: score={result['score']:.4f}")
            print(f"         Source: {result['source']}")
            print(f"         Content: '{result['content'][:100]}...'")
        
    except Exception as e:
        print(f"   ❌ Retriever search failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎯 Debug session completed!")

if __name__ == "__main__":
    asyncio.run(debug_module_b())