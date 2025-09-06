# Module B: RAG Knowledge Vault

Document processing and semantic search using ChromaDB and embeddings for the Linux Superhelfer system.

## Overview

Module B provides a complete RAG (Retrieval-Augmented Generation) knowledge vault that processes documents, generates embeddings, and enables semantic search. It serves as the knowledge base for the Linux Superhelfer system, storing and retrieving relevant information to enhance AI responses.

## Features

### Document Processing
- **Multi-format Support**: PDF and TXT file processing
- **Size Validation**: Maximum 30MB total, 5 files per upload
- **Content Extraction**: Robust text extraction with error handling
- **Metadata Management**: Rich metadata tracking for documents

### Text Chunking
- **Smart Segmentation**: 500-token chunks with 50-token overlap
- **Hierarchical Splitting**: Preserves document structure (paragraphs, sentences)
- **Token Estimation**: Approximate token counting for chunk sizing

### Embedding Generation
- **Local Embeddings**: Uses nomic-embed-text via Ollama
- **Batch Processing**: Efficient batch embedding generation
- **Health Monitoring**: Automatic model availability checking

### Vector Storage
- **Persistent Storage**: ChromaDB with local persistence
- **Metadata Filtering**: Search by source, type, or custom metadata
- **Batch Operations**: Efficient bulk storage and retrieval

### Semantic Search
- **Similarity Search**: Cosine similarity with configurable threshold
- **Contextual Search**: Enhanced search with context integration
- **Source Filtering**: Search within specific documents
- **Top-K Results**: Configurable result count with relevance ranking

## API Endpoints

### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

### Document Upload
```http
POST /upload
Content-Type: application/json

{
  "files": ["base64_encoded_content"],
  "metadata": {
    "source": "linux_manual.pdf",
    "type": "pdf",
    "category": "documentation"
  }
}
```
**Response:**
```json
{
  "status": "uploaded",
  "processed_files": 1,
  "total_chunks": 25,
  "message": "Successfully processed 1 files into 25 chunks"
}
```

### Semantic Search
```http
POST /search
Content-Type: application/json

{
  "query": "How to check disk space in Linux?",
  "top_k": 3,
  "threshold": 0.6
}
```
**Response:**
```json
{
  "snippets": [
    {
      "content": "Use the df command to check disk space...",
      "source": "linux_manual.pdf",
      "score": 0.85,
      "metadata": {
        "chunk_index": 5,
        "file_type": "pdf"
      }
    }
  ],
  "query": "How to check disk space in Linux?",
  "total_results": 1,
  "processing_time": 0.234
}
```

### Status Information
```http
GET /status
```
**Response:**
```json
{
  "module": "RAG Knowledge Vault",
  "version": "1.0.0",
  "status": "operational",
  "components": {
    "vector_store": {
      "available": true,
      "collections": 1,
      "total_documents": 150
    },
    "embedding_service": {
      "available": true,
      "model": "nomic-embed-text"
    }
  }
}
```

## Configuration

- **Port**: 8002
- **Embedding Model**: nomic-embed-text (via Ollama)
- **Chunk Size**: 500 tokens with 50-token overlap
- **Search Threshold**: 0.6 (configurable)
- **File Limits**: 5 files per upload, 30MB total
- **Storage**: Local ChromaDB persistence in `data/chromadb/`

## Installation & Usage

### Prerequisites
```bash
# Ensure Ollama is running with embedding model
ollama pull nomic-embed-text
ollama serve
```

### Development Setup
```bash
cd modules/module_b_rag

# Install dependencies (if not already installed)
pip install chromadb langchain langchain-text-splitters pypdf2

# Start the module
PYTHONPATH=../.. python main.py
```

### Docker Setup
```bash
# From project root
docker-compose up module-b-rag
```

### Testing
```bash
# Run tests
pytest tests/test_module_b_rag.py -v

# Test upload
curl -X POST http://localhost:8002/upload \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["'$(base64 -w 0 sample.txt)'"],
    "metadata": {"source": "sample.txt", "type": "txt"}
  }'

# Test search
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Linux commands",
    "top_k": 3,
    "threshold": 0.6
  }'
```

## Architecture

```
Module B (RAG Knowledge Vault)
├── DocumentLoader
│   ├── PDF text extraction (PyPDF2)
│   ├── TXT file processing
│   └── Base64 content handling
├── ChunkProcessor
│   ├── Recursive text splitting
│   ├── Token estimation
│   └── Metadata preservation
├── EmbeddingManager
│   ├── Ollama integration
│   ├── nomic-embed-text model
│   └── Batch processing
├── VectorStore
│   ├── ChromaDB persistence
│   ├── Metadata filtering
│   └── Similarity search
└── Retriever
    ├── Semantic search
    ├── Contextual enhancement
    └── Result ranking
```

## Integration with Other Modules

### Module A (Core Intelligence)
Module A can query Module B for relevant context:
```python
import requests

# Search for relevant context
response = requests.post("http://localhost:8002/search", json={
    "query": user_query,
    "top_k": 3,
    "threshold": 0.6
})

context = " ".join([snippet["content"] for snippet in response.json()["snippets"]])
```

### Module C (Proactive Agents)
Agents can search for task-specific documentation:
```python
# Search for backup-related documentation
response = requests.post("http://localhost:8002/search", json={
    "query": "Linux backup procedures",
    "top_k": 5,
    "threshold": 0.7
})
```

## Troubleshooting

### ChromaDB Issues
```bash
# Check data directory permissions
ls -la data/chromadb/
chmod -R 755 data/chromadb/

# Reset ChromaDB if corrupted
rm -rf data/chromadb/
# Restart module to recreate
```

### Ollama Connection Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull embedding model if missing
ollama pull nomic-embed-text

# Check Ollama logs
journalctl -u ollama -f
```

### Upload Errors
- **File too large**: Check file size limits (30MB total)
- **Invalid base64**: Ensure proper base64 encoding
- **Unsupported format**: Only PDF and TXT files supported
- **Empty content**: Files must contain readable text

### Search Issues
- **No results**: Lower threshold or check if documents are indexed
- **Slow search**: Check ChromaDB performance and embedding service
- **Poor relevance**: Adjust threshold or improve query phrasing

## Performance Optimization

### Hardware Recommendations
- **GPU**: NVIDIA RTX 5090 (32GB VRAM) for fast embeddings
- **RAM**: 16GB+ for large document collections
- **Storage**: SSD for ChromaDB persistence

### Configuration Tuning
```python
# Adjust chunk size for your use case
chunk_processor = ChunkProcessor(
    chunk_size=750,  # Larger chunks for technical docs
    chunk_overlap=75  # More overlap for better context
)

# Tune search parameters
search_results = await retriever.search(
    query=query,
    top_k=5,  # More results for better context
    threshold=0.5  # Lower threshold for broader search
)
```

## Development Notes

- **Token Estimation**: Uses 4 chars/token approximation
- **Embedding Dimension**: 768 for nomic-embed-text
- **Similarity Metric**: Cosine similarity via ChromaDB
- **Persistence**: Automatic ChromaDB persistence to disk
- **Error Handling**: Comprehensive error handling with fallbacks

## Recent Fixes & Updates

### ✅ Search Functionality Restored (2025-01-09)
**Issue**: Search returned empty results due to unnormalized embeddings causing incorrect similarity calculations

**Root Cause**: 
- nomic-embed-text generates unnormalized embeddings (L2 norm ~20)
- ChromaDB L2 distances were extremely high (>300)
- Similarity calculation formula was incorrect for unnormalized vectors

**Solution Applied**:
- **Embedding Normalization**: All embeddings now normalized to unit length (L2 norm = 1.0)
- **Fixed Similarity Formula**: Corrected ChromaDB L2 distance to cosine similarity conversion
- **Database Reset**: ChromaDB reset to remove old unnormalized embeddings

**Performance Results**:
- ✅ Search scores: 0.80-0.92 for relevant queries
- ✅ Processing time: 0.01-0.03 seconds  
- ✅ Multi-document ranking works correctly
- ✅ All threshold levels (0.0, 0.3, 0.6, 0.8) function properly

**Verification**:
```bash
# Test search with high-quality results
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How to check disk space?", "threshold": 0.6}'

# Expected: Similarity scores >0.8 for relevant content
```

**Technical Details**:
- Embedding normalization: `embedding / np.linalg.norm(embedding)`
- Similarity formula: `max(0.0, 1.0 - (distance² / 2.0))` for normalized vectors
- Benefits: Consistent similarity scores, better ranking, faster search

## Future Enhancements

- Support for additional file formats (DOCX, HTML, Markdown)
- Advanced chunking strategies (semantic chunking)
- Query expansion and rewriting
- Caching layer for frequent searches
- Multi-language support
- Document versioning and updates