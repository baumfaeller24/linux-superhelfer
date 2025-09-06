"""
Tests for Module B: RAG Knowledge Vault.
"""

import pytest
import asyncio
import base64
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Import modules to test
import sys
sys.path.append('modules')

from module_b_rag.document_loader import DocumentLoader, Document
from module_b_rag.chunk_processor import ChunkProcessor, DocumentChunk
from module_b_rag.embedding_manager import EmbeddingManager


class TestDocumentLoader:
    """Test document loading functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = DocumentLoader(max_file_size_mb=1)  # Small limit for testing
    
    def test_load_text_from_base64(self):
        """Test loading text document from base64."""
        text_content = "This is a test document with some content."
        base64_content = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
        
        metadata = {
            'source': 'test.txt',
            'type': 'txt'
        }
        
        document = self.loader.load_from_base64(base64_content, metadata)
        
        assert document.content == text_content
        assert document.source == 'test.txt'
        assert document.metadata['type'] == 'txt'
        assert document.size_bytes == len(text_content.encode('utf-8'))
    
    def test_load_invalid_base64(self):
        """Test handling of invalid base64 content."""
        invalid_base64 = "invalid_base64_content"
        metadata = {'source': 'test.txt', 'type': 'txt'}
        
        with pytest.raises(Exception):
            self.loader.load_from_base64(invalid_base64, metadata)
    
    def test_file_size_limit(self):
        """Test file size limit enforcement."""
        # Create content larger than limit (1MB)
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        base64_content = base64.b64encode(large_content.encode('utf-8')).decode('utf-8')
        
        metadata = {'source': 'large.txt', 'type': 'txt'}
        
        with pytest.raises(ValueError, match="File too large"):
            self.loader.load_from_base64(base64_content, metadata)
    
    def test_empty_content(self):
        """Test handling of empty content."""
        empty_content = ""
        base64_content = base64.b64encode(empty_content.encode('utf-8')).decode('utf-8')
        
        metadata = {'source': 'empty.txt', 'type': 'txt'}
        
        with pytest.raises(ValueError, match="no readable text"):
            self.loader.load_from_base64(base64_content, metadata)
    
    def test_validate_document(self):
        """Test document validation."""
        # Valid document
        valid_doc = Document(
            content="Valid content",
            source="test.txt",
            metadata={'type': 'txt'},
            size_bytes=100
        )
        assert self.loader.validate_document(valid_doc) is True
        
        # Invalid document (empty content)
        invalid_doc = Document(
            content="",
            source="test.txt",
            metadata={'type': 'txt'},
            size_bytes=0
        )
        assert self.loader.validate_document(invalid_doc) is False


class TestChunkProcessor:
    """Test document chunking functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ChunkProcessor(chunk_size=100, chunk_overlap=20)
    
    def test_process_document(self):
        """Test document processing into chunks."""
        content = "This is a test document. " * 50  # Create longer content
        document = Document(
            content=content,
            source="test.txt",
            metadata={'type': 'txt'},
            size_bytes=len(content)
        )
        
        chunks = self.processor.process_document(document)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.source == "test.txt" for chunk in chunks)
        assert all(chunk.token_count > 0 for chunk in chunks)
    
    def test_process_text(self):
        """Test processing raw text into chunks."""
        text = "This is a test text. " * 30
        chunks = self.processor.process_text(text, "test_source")
        
        assert len(chunks) > 0
        assert all(chunk.source == "test_source" for chunk in chunks)
    
    def test_chunk_validation(self):
        """Test chunk validation."""
        # Valid chunk
        valid_chunk = DocumentChunk(
            content="Valid chunk content with sufficient length",
            source="test.txt",
            chunk_id="test_001",
            metadata={'chunk_index': 0},
            token_count=10
        )
        assert self.processor._is_valid_chunk(valid_chunk) is True
        
        # Invalid chunk (too short)
        invalid_chunk = DocumentChunk(
            content="Short",
            source="test.txt",
            chunk_id="test_002",
            metadata={'chunk_index': 1},
            token_count=1
        )
        assert self.processor._is_valid_chunk(invalid_chunk) is False
    
    def test_get_chunk_statistics(self):
        """Test chunk statistics calculation."""
        chunks = [
            DocumentChunk("Content 1", "source1", "id1", {}, 10),
            DocumentChunk("Content 2", "source2", "id2", {}, 20),
            DocumentChunk("Content 3", "source1", "id3", {}, 15)
        ]
        
        stats = self.processor.get_chunk_statistics(chunks)
        
        assert stats['total_chunks'] == 3
        assert stats['total_tokens'] == 45
        assert stats['avg_tokens_per_chunk'] == 15.0
        assert stats['min_tokens'] == 10
        assert stats['max_tokens'] == 20
        assert len(stats['sources']) == 2


class TestEmbeddingManager:
    """Test embedding generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.embedding_manager = EmbeddingManager()
    
    @pytest.mark.asyncio
    async def test_health_check_mock(self):
        """Test health check with mocked Ollama."""
        with patch.object(self.embedding_manager.client, 'list') as mock_list:
            mock_list.return_value = {
                'models': [{'name': 'nomic-embed-text'}]
            }
            
            result = await self.embedding_manager.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_generate_embedding_mock(self):
        """Test embedding generation with mocked Ollama."""
        test_text = "This is a test text for embedding"
        mock_embedding = [0.1, 0.2, 0.3] * 256  # Mock 768-dim embedding
        
        with patch.object(self.embedding_manager.client, 'embeddings') as mock_embeddings:
            mock_embeddings.return_value = {'embedding': mock_embedding}
            
            # Mock health check
            self.embedding_manager._model_available = True
            
            result = await self.embedding_manager.generate_embedding(test_text)
            
            assert result == mock_embedding
            assert len(result) == 768
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text."""
        with pytest.raises(ValueError, match="empty text"):
            await self.embedding_manager.generate_embedding("")
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_mock(self):
        """Test batch embedding generation."""
        texts = ["Text 1", "Text 2", "Text 3"]
        mock_embedding = [0.1] * 768
        
        with patch.object(self.embedding_manager, 'generate_embedding') as mock_generate:
            mock_generate.return_value = mock_embedding
            
            results = await self.embedding_manager.generate_embeddings_batch(texts)
            
            assert len(results) == 3
            assert all(len(emb) == 768 for emb in results)
            assert mock_generate.call_count == 3
    
    def test_get_model_info(self):
        """Test model information retrieval."""
        info = self.embedding_manager.get_model_info()
        
        assert 'model' in info
        assert 'host' in info
        assert 'port' in info
        assert info['model'] == 'nomic-embed-text'


class TestIntegration:
    """Integration tests for Module B components."""
    
    @pytest.mark.asyncio
    async def test_document_to_chunks_to_embeddings(self):
        """Test complete pipeline from document to embeddings."""
        # Create test document
        loader = DocumentLoader()
        processor = ChunkProcessor(chunk_size=50)
        embedding_manager = EmbeddingManager()
        
        # Mock embedding generation
        mock_embedding = [0.1] * 768
        with patch.object(embedding_manager, 'generate_embedding') as mock_generate:
            mock_generate.return_value = mock_embedding
            embedding_manager._model_available = True
            
            # Load document
            text_content = "This is a test document. " * 20
            base64_content = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
            metadata = {'source': 'test.txt', 'type': 'txt'}
            
            document = loader.load_from_base64(base64_content, metadata)
            
            # Process into chunks
            chunks = processor.process_document(document)
            assert len(chunks) > 0
            
            # Generate embeddings
            embeddings = []
            for chunk in chunks:
                embedding = await embedding_manager.generate_embedding(chunk.content)
                embeddings.append(embedding)
            
            assert len(embeddings) == len(chunks)
            assert all(len(emb) == 768 for emb in embeddings)


# Fixtures for testing
@pytest.fixture
def sample_text_document():
    """Create a sample text document for testing."""
    content = """
    Linux System Administration Guide
    
    This document covers essential Linux administration tasks.
    
    Chapter 1: File System Management
    The Linux file system is hierarchical, starting from the root directory (/).
    Important directories include /etc for configuration files, /var for variable data,
    and /home for user directories.
    
    Chapter 2: Process Management
    Processes in Linux can be managed using commands like ps, top, and kill.
    The ps command shows running processes, while top provides real-time monitoring.
    
    Chapter 3: Network Configuration
    Network interfaces can be configured using tools like ifconfig or ip.
    The /etc/network/interfaces file contains network configuration on Debian systems.
    """
    
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')


@pytest.fixture
def sample_metadata():
    """Create sample metadata for testing."""
    return {
        'source': 'linux_admin_guide.txt',
        'type': 'txt',
        'author': 'Test Author',
        'category': 'documentation'
    }


def test_sample_fixtures(sample_text_document, sample_metadata):
    """Test that fixtures work correctly."""
    assert sample_text_document is not None
    assert sample_metadata['source'] == 'linux_admin_guide.txt'
    
    # Decode and check content
    decoded = base64.b64decode(sample_text_document).decode('utf-8')
    assert 'Linux System Administration' in decoded