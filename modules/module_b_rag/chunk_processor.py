"""
Chunk processor for RAG Knowledge Vault.
Splits documents into 500-token chunks using langchain text splitters.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from modules.module_b_rag.document_loader import Document

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Document chunk data structure."""
    content: str
    source: str
    chunk_id: str
    metadata: Dict[str, Any]
    token_count: int


class ChunkProcessor:
    """Processes documents into manageable chunks for embedding."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunk processor.
        
        Args:
            chunk_size: Target size for each chunk in tokens (approximate)
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        # Using character-based splitting with approximation: 1 token ≈ 4 characters
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 4,  # Approximate token-to-character conversion
            chunk_overlap=chunk_overlap * 4,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamation endings
                "? ",    # Question endings
                "; ",    # Semicolon breaks
                ", ",    # Comma breaks
                " ",     # Word breaks
                ""       # Character breaks (fallback)
            ]
        )
    
    def process_document(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into chunks.
        
        Args:
            document: Document to process
            
        Returns:
            List of DocumentChunk objects
            
        Raises:
            RuntimeError: If chunking fails
        """
        try:
            # Split document content
            text_chunks = self.text_splitter.split_text(document.content)
            
            if not text_chunks:
                raise RuntimeError("Document could not be split into chunks")
            
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                # Skip empty chunks
                if not chunk_text.strip():
                    continue
                
                # Estimate token count (rough approximation)
                token_count = self._estimate_token_count(chunk_text)
                
                # Create chunk ID
                chunk_id = f"{document.source}_{i:04d}"
                
                # Create chunk metadata
                chunk_metadata = {
                    **document.metadata,
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'chunk_id': chunk_id,
                    'original_document_size': document.size_bytes
                }
                
                chunk = DocumentChunk(
                    content=chunk_text.strip(),
                    source=document.source,
                    chunk_id=chunk_id,
                    metadata=chunk_metadata,
                    token_count=token_count
                )
                
                chunks.append(chunk)
            
            logger.info(f"Split document '{document.source}' into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process document '{document.source}': {e}")
            raise RuntimeError(f"Chunk processing failed: {str(e)}")
    
    def process_text(self, text: str, source: str = "text_input") -> List[DocumentChunk]:
        """
        Process raw text into chunks.
        
        Args:
            text: Raw text to process
            source: Source identifier for the text
            
        Returns:
            List of DocumentChunk objects
        """
        # Create a temporary document object
        document = Document(
            content=text,
            source=source,
            metadata={'type': 'text', 'source': source},
            size_bytes=len(text.encode('utf-8'))
        )
        
        return self.process_document(document)
    
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough approximation based on character count.
        More accurate tokenization would require the actual tokenizer.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple heuristic: average 4 characters per token
        # This is approximate and varies by language and content type
        char_count = len(text)
        estimated_tokens = max(1, char_count // 4)
        
        return estimated_tokens
    
    def validate_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Validate and filter chunks.
        
        Args:
            chunks: List of chunks to validate
            
        Returns:
            List of valid chunks
        """
        valid_chunks = []
        
        for chunk in chunks:
            if self._is_valid_chunk(chunk):
                valid_chunks.append(chunk)
            else:
                logger.warning(f"Skipping invalid chunk: {chunk.chunk_id}")
        
        return valid_chunks
    
    def _is_valid_chunk(self, chunk: DocumentChunk) -> bool:
        """
        Check if chunk is valid for processing.
        
        Args:
            chunk: Chunk to validate
            
        Returns:
            True if chunk is valid
        """
        try:
            # Check content
            if not chunk.content or not chunk.content.strip():
                return False
            
            # Check minimum content length (at least 10 characters)
            if len(chunk.content.strip()) < 10:
                return False
            
            # Check token count is reasonable
            if chunk.token_count < 1 or chunk.token_count > self.chunk_size * 2:
                return False
            
            # Check required metadata
            if not chunk.source or not chunk.chunk_id:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Chunk validation failed: {e}")
            return False
    
    def get_chunk_statistics(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Get statistics about processed chunks.
        
        Args:
            chunks: List of chunks to analyze
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_tokens': 0,
                'avg_tokens_per_chunk': 0,
                'min_tokens': 0,
                'max_tokens': 0
            }
        
        token_counts = [chunk.token_count for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'sources': list(set(chunk.source for chunk in chunks))
        }