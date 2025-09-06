# Retriever Configuration

## BM25 + Embedding Hybrid Setup

### Embedding Model
- **Model**: `nomic-embed-text` (via Ollama)
- **Host**: localhost:11434
- **Dimensions**: 768
- **Normalization**: L2 normalized to unit length
- **Tokenizer**: Ollama internal (nomic-embed-text)

### Search Parameters
- **Default topK**: 3
- **Default threshold**: 0.6 (cosine similarity)
- **Batch size**: 10 (for bulk embedding)
- **Context search**: topK * 2 with threshold * 0.8

### Vector Store (ChromaDB)
```python
# Default configuration
collection_name = "linux_knowledge_vault"
distance_metric = "cosine"  # Cosine similarity for normalized embeddings
```

### Search Methods
1. **Standard Search**: `search(query, top_k=3, threshold=0.6)`
2. **Contextual Search**: `search_with_context(query, context, top_k=3)`
3. **Source-filtered Search**: `search_by_source(query, source, top_k=3)`
4. **Similarity Search**: `get_similar_chunks(reference_content, top_k=5, threshold=0.7)`

### Performance Settings
- **Health check**: Auto-pull model if not available
- **Batch processing**: 0.1s delay between batches
- **Fallback**: Zero vector for failed embeddings
- **Error handling**: Graceful degradation with logging

## Current Issues
- No BM25 implementation (pure embedding search)
- No reranker implemented
- Simple cosine similarity only
- No query rewriting