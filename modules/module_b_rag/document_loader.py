"""
Document loader for RAG Knowledge Vault.
Handles PDF and TXT file loading with validation and metadata extraction.
"""

import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import PyPDF2
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document data structure."""
    content: str
    source: str
    metadata: Dict[str, Any]
    size_bytes: int


class DocumentLoader:
    """Loads and validates documents from various sources."""
    
    def __init__(self, max_file_size_mb: int = 30):
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.supported_extensions = {'.pdf', '.txt'}
    
    def load_from_base64(self, base64_content: str, metadata: Dict[str, Any]) -> Document:
        """
        Load document from base64 encoded content.
        
        Args:
            base64_content: Base64 encoded file content
            metadata: File metadata including source and type
            
        Returns:
            Document object with extracted content
            
        Raises:
            ValueError: If file format is unsupported or content is invalid
            RuntimeError: If file processing fails
        """
        try:
            # Decode base64 content
            file_bytes = base64.b64decode(base64_content)
            
            # Check file size
            if len(file_bytes) > self.max_file_size_bytes:
                raise ValueError(f"File too large: {len(file_bytes)} bytes (max: {self.max_file_size_bytes})")
            
            # Determine file type from metadata or content
            file_type = metadata.get('type', '').lower()
            source = metadata.get('source', 'unknown')
            
            # Extract content based on file type
            if file_type == 'pdf' or self._is_pdf(file_bytes):
                content = self._extract_pdf_content(file_bytes)
            elif file_type == 'txt' or self._is_text(file_bytes):
                content = self._extract_text_content(file_bytes)
            else:
                raise ValueError(f"Unsupported file format: {file_type}")
            
            # Validate extracted content
            if not content.strip():
                raise ValueError("Document contains no readable text")
            
            # Create document object
            document = Document(
                content=content,
                source=source,
                metadata={
                    **metadata,
                    'file_type': file_type,
                    'content_length': len(content),
                    'size_bytes': len(file_bytes)
                },
                size_bytes=len(file_bytes)
            )
            
            logger.info(f"Loaded document: {source} ({len(content)} chars, {len(file_bytes)} bytes)")
            return document
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise RuntimeError(f"Document loading failed: {str(e)}")
    
    def load_from_file(self, file_path: Path) -> Document:
        """
        Load document from file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Document object with extracted content
        """
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        # Convert to base64 and use existing loader
        base64_content = base64.b64encode(file_bytes).decode('utf-8')
        
        metadata = {
            'source': str(file_path.name),
            'type': file_path.suffix.lower().lstrip('.'),
            'file_path': str(file_path)
        }
        
        return self.load_from_base64(base64_content, metadata)
    
    def _is_pdf(self, file_bytes: bytes) -> bool:
        """Check if file bytes represent a PDF."""
        return file_bytes.startswith(b'%PDF-')
    
    def _is_text(self, file_bytes: bytes) -> bool:
        """Check if file bytes represent text content."""
        try:
            file_bytes.decode('utf-8')
            return True
        except UnicodeDecodeError:
            try:
                file_bytes.decode('latin-1')
                return True
            except UnicodeDecodeError:
                return False
    
    def _extract_pdf_content(self, file_bytes: bytes) -> str:
        """Extract text content from PDF bytes."""
        try:
            pdf_file = BytesIO(file_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            content_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        content_parts.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not content_parts:
                raise ValueError("No text could be extracted from PDF")
            
            return '\n\n'.join(content_parts)
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Invalid PDF file: {str(e)}")
    
    def _extract_text_content(self, file_bytes: bytes) -> str:
        """Extract content from text file bytes."""
        try:
            # Try UTF-8 first
            try:
                return file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1
                return file_bytes.decode('latin-1')
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise ValueError(f"Invalid text file: {str(e)}")
    
    def validate_document(self, document: Document) -> bool:
        """
        Validate document content and metadata.
        
        Args:
            document: Document to validate
            
        Returns:
            True if document is valid
        """
        try:
            # Check content
            if not document.content or not document.content.strip():
                return False
            
            # Check size limits
            if document.size_bytes > self.max_file_size_bytes:
                return False
            
            # Check metadata
            if not document.source:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            return False