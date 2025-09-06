"""
Module B: RAG Knowledge Vault
Document processing, embedding generation, and semantic search using ChromaDB.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from shared.models import HealthStatus
from modules.module_b_rag.document_loader import DocumentLoader
from modules.module_b_rag.chunk_processor import ChunkProcessor
from modules.module_b_rag.embedding_manager import EmbeddingManager
from modules.module_b_rag.vector_store import VectorStore
from modules.module_b_rag.retriever import Retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Knowledge Vault", 
    version="1.0.0",
    description="Document processing and semantic search using ChromaDB"
)

# Initialize data directories
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
CHROMADB_DIR = DATA_DIR / "chromadb"

for dir_path in [DATA_DIR, UPLOADS_DIR, PROCESSED_DIR, CHROMADB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Initialize components
document_loader = DocumentLoader()
chunk_processor = ChunkProcessor()
embedding_manager = EmbeddingManager()
vector_store = VectorStore(str(CHROMADB_DIR))
retriever = Retriever(vector_store, embedding_manager)


class UploadRequest(BaseModel):
    """Request model for document upload."""
    files: List[str] = Field(..., description="Base64 encoded file contents")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata")


class UploadResponse(BaseModel):
    """Response model for document upload."""
    status: str = Field(..., description="Upload status")
    processed_files: int = Field(..., description="Number of files processed")
    total_chunks: int = Field(..., description="Total chunks created")
    message: str = Field(..., description="Status message")


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=3, description="Number of results to return")
    threshold: float = Field(default=0.6, description="Similarity threshold")


class SearchSnippet(BaseModel):
    """Individual search result snippet."""
    content: str = Field(..., description="Snippet content")
    source: str = Field(..., description="Source document")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for semantic search."""
    snippets: List[SearchSnippet] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results")
    processing_time: float = Field(..., description="Search processing time")


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint with component status."""
    try:
        # Check if ChromaDB is accessible
        vector_store_status = vector_store.health_check()
        
        # Check if Ollama embedding service is available
        embedding_status = await embedding_manager.health_check()
        
        if vector_store_status and embedding_status:
            return HealthStatus(status="ok", version="1.0.0")
        elif vector_store_status or embedding_status:
            return HealthStatus(status="degraded", version="1.0.0")
        else:
            return HealthStatus(status="error", version="1.0.0")
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(status="error", version="1.0.0")


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(request: UploadRequest):
    """
    Upload and process documents for indexing.
    
    Args:
        request: UploadRequest with base64 encoded files and metadata
        
    Returns:
        UploadResponse with processing status and statistics
        
    Raises:
        HTTPException: If file processing fails or limits are exceeded
    """
    try:
        if len(request.files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 files allowed per upload"
            )
        
        processed_files = 0
        total_chunks = 0
        
        for i, file_content in enumerate(request.files):
            try:
                # Extract metadata for this file
                file_metadata = request.metadata.copy()
                file_metadata.update({
                    "file_index": i,
                    "upload_timestamp": str(Path().cwd())
                })
                
                # Load and validate document
                document = document_loader.load_from_base64(
                    file_content, 
                    file_metadata
                )
                
                # Process into chunks
                chunks = chunk_processor.process_document(document)
                
                # Generate embeddings and store
                for chunk in chunks:
                    embedding = await embedding_manager.generate_embedding(chunk.content)
                    vector_store.add_chunk(chunk, embedding)
                
                processed_files += 1
                total_chunks += len(chunks)
                
                logger.info(f"Processed file {i+1}: {len(chunks)} chunks created")
                
            except Exception as e:
                logger.error(f"Failed to process file {i+1}: {e}")
                continue
        
        if processed_files == 0:
            raise HTTPException(
                status_code=400,
                detail="No files could be processed successfully"
            )
        
        return UploadResponse(
            status="uploaded",
            processed_files=processed_files,
            total_chunks=total_chunks,
            message=f"Successfully processed {processed_files} files into {total_chunks} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search documents using semantic similarity.
    
    Args:
        request: SearchRequest with query and search parameters
        
    Returns:
        SearchResponse with relevant document snippets
        
    Raises:
        HTTPException: If search fails or query is invalid
    """
    import time
    start_time = time.time()
    
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        if len(request.query) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Query too long (max 1000 characters)"
            )
        
        # Perform semantic search
        results = await retriever.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        processing_time = time.time() - start_time
        
        # Convert results to response format
        snippets = [
            SearchSnippet(
                content=result["content"],
                source=result["source"],
                score=result["score"],
                metadata=result.get("metadata", {})
            )
            for result in results
        ]
        
        logger.info(f"Search completed: {len(snippets)} results in {processing_time:.3f}s")
        
        return SearchResponse(
            snippets=snippets,
            query=request.query,
            total_results=len(snippets),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """Get detailed module status information."""
    try:
        vector_store_status = vector_store.health_check()
        embedding_status = await embedding_manager.health_check()
        
        # Get collection statistics
        stats = vector_store.get_statistics()
        
        return {
            "module": "RAG Knowledge Vault",
            "version": "1.0.0",
            "status": "operational" if (vector_store_status and embedding_status) else "degraded",
            "components": {
                "vector_store": {
                    "available": vector_store_status,
                    "path": str(CHROMADB_DIR),
                    "collections": stats.get("collections", 0),
                    "total_documents": stats.get("documents", 0)
                },
                "embedding_service": {
                    "available": embedding_status,
                    "model": "nomic-embed-text"
                }
            },
            "endpoints": ["/health", "/upload", "/search", "/status"],
            "limits": {
                "max_files_per_upload": 5,
                "max_total_size_mb": 30,
                "chunk_size_tokens": 500,
                "search_threshold": 0.6
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "module": "RAG Knowledge Vault",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)