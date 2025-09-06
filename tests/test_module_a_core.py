"""
Unit tests for Module A: Core Intelligence Engine
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent / "modules"))

from modules.module_a_core.main import app
from modules.module_a_core.ollama_client import OllamaClient, QueryProcessor
from modules.module_a_core.confidence import ConfidenceCalculator


class TestOllamaClient:
    """Test cases for OllamaClient."""
    
    @pytest.fixture
    def ollama_client(self):
        return OllamaClient(host="localhost", port=11434, model="llama3.1:8b")
    
    @pytest.mark.asyncio
    async def test_is_available_success(self, ollama_client):
        """Test successful availability check."""
        with patch.object(ollama_client.client, 'list') as mock_list:
            mock_list.return_value = {
                'models': [{'name': 'llama3.1:8b'}, {'name': 'other:model'}]
            }
            
            result = await ollama_client.is_available()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_is_available_model_not_found(self, ollama_client):
        """Test availability check when model is not available."""
        with patch.object(ollama_client.client, 'list') as mock_list:
            mock_list.return_value = {
                'models': [{'name': 'other:model'}]
            }
            
            result = await ollama_client.is_available()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_is_available_connection_error(self, ollama_client):
        """Test availability check with connection error."""
        with patch.object(ollama_client.client, 'list') as mock_list:
            mock_list.side_effect = Exception("Connection failed")
            
            result = await ollama_client.is_available()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, ollama_client):
        """Test successful response generation."""
        mock_response = {
            'response': 'Use df -h to check disk usage',
            'prompt_eval_count': 50,
            'eval_count': 20,
            'total_duration': 1500000000  # nanoseconds
        }
        
        with patch.object(ollama_client.client, 'generate') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await ollama_client.generate_response("How to check disk usage?")
            
            assert result['response'] == 'Use df -h to check disk usage'
            assert result['model_used'] == 'llama3.1:8b'
            assert 'prompt_tokens' in result
            assert 'response_tokens' in result
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, ollama_client):
        """Test response generation with context."""
        with patch.object(ollama_client.client, 'generate') as mock_generate:
            mock_generate.return_value = {'response': 'Test response'}
            
            await ollama_client.generate_response("Test query", "Test context")
            
            # Verify context was included in prompt
            call_args = mock_generate.call_args
            prompt = call_args[1]['prompt']
            assert 'Test context' in prompt
            assert 'Test query' in prompt
    
    def test_prepare_prompt_without_context(self, ollama_client):
        """Test prompt preparation without context."""
        prompt = ollama_client._prepare_prompt("How to check disk usage?")
        
        assert "Linux system administrator" in prompt
        assert "How to check disk usage?" in prompt
        assert "Context:" not in prompt
    
    def test_prepare_prompt_with_context(self, ollama_client):
        """Test prompt preparation with context."""
        prompt = ollama_client._prepare_prompt("Test query", "Test context")
        
        assert "Test query" in prompt
        assert "Test context" in prompt
        assert "Context:" in prompt


class TestQueryProcessor:
    """Test cases for QueryProcessor."""
    
    @pytest.fixture
    def processor(self):
        return QueryProcessor()
    
    def test_validate_query_valid(self, processor):
        """Test validation of valid queries."""
        assert processor.validate_query("How to check disk usage?") is True
        assert processor.validate_query("What is the ls command?") is True
    
    def test_validate_query_invalid(self, processor):
        """Test validation of invalid queries."""
        assert processor.validate_query("") is False
        assert processor.validate_query("ab") is False  # Too short
        assert processor.validate_query("a" * 2001) is False  # Too long
        assert processor.validate_query(None) is False
        assert processor.validate_query(123) is False
    
    def test_preprocess_query(self, processor):
        """Test query preprocessing."""
        # Test whitespace cleanup
        result = processor.preprocess_query("  How   to  check   disk  ")
        assert result == "How to check disk?"
        
        # Test punctuation addition
        result = processor.preprocess_query("What is ls command")
        assert result == "What is ls command?"
        
        # Test existing punctuation preservation
        result = processor.preprocess_query("How are you!")
        assert result == "How are you!"
    
    def test_extract_context_hints(self, processor):
        """Test context hint extraction."""
        # Test Linux keywords detection
        result = processor.extract_context_hints("How to use systemctl in Linux?")
        assert result is not None
        assert "linux" in result.lower()
        assert "systemctl" in result.lower()
        
        # Test no keywords
        result = processor.extract_context_hints("What is the weather today?")
        assert result is None


class TestConfidenceCalculator:
    """Test cases for ConfidenceCalculator."""
    
    @pytest.fixture
    def calculator(self):
        return ConfidenceCalculator()
    
    def test_calculate_confidence_high_quality(self, calculator):
        """Test confidence calculation for high-quality response."""
        response = """To check disk usage in Linux, use the 'df -h' command. 
        This will show you disk usage in human-readable format with sizes in KB, MB, GB.
        You can also use 'du -sh /path' to check specific directory usage."""
        
        confidence = calculator.calculate_confidence(response, "How to check disk usage?", 2.5)
        assert confidence > 0.6  # Should be reasonably confident
    
    def test_calculate_confidence_low_quality(self, calculator):
        """Test confidence calculation for low-quality response."""
        response = "Maybe try something. Not sure."
        
        confidence = calculator.calculate_confidence(response, "How to check disk usage?", 0.1)
        assert confidence < 0.5  # Should have low confidence
    
    def test_calculate_confidence_empty_response(self, calculator):
        """Test confidence calculation for empty response."""
        confidence = calculator.calculate_confidence("", "test query")
        assert confidence == 0.0
    
    def test_should_escalate(self, calculator):
        """Test escalation decision logic."""
        assert calculator.should_escalate(0.3, 0.5) is True
        assert calculator.should_escalate(0.7, 0.5) is False
        assert calculator.should_escalate(0.5, 0.5) is False  # Boundary case
    
    def test_length_score_calculation(self, calculator):
        """Test length-based scoring."""
        # Very short response
        short_score = calculator._calculate_length_score("Yes.")
        assert short_score < 0.5
        
        # Optimal length response
        optimal_response = "Use df -h to check disk usage. This shows human-readable format."
        optimal_score = calculator._calculate_length_score(optimal_response)
        assert optimal_score > 0.7
        
        # Very long response
        long_response = "a" * 1000
        long_score = calculator._calculate_length_score(long_response)
        assert long_score < optimal_score
    
    def test_uncertainty_score_calculation(self, calculator):
        """Test uncertainty-based scoring."""
        # Response with uncertainty
        uncertain_response = "I'm not sure, but maybe you could try something."
        uncertain_score = calculator._calculate_uncertainty_score(uncertain_response)
        
        # Response with confidence
        confident_response = "Definitely use df -h command. This always works."
        confident_score = calculator._calculate_uncertainty_score(confident_response)
        
        assert confident_score > uncertain_score


class TestAPIEndpoints:
    """Test cases for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        with patch('modules.module_a_core.main.ollama_client.is_available') as mock_available:
            mock_available.return_value = True
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["version"] == "1.0.0"
    
    def test_health_endpoint_ollama_unavailable(self, client):
        """Test health check when Ollama is unavailable."""
        with patch('modules.module_a_core.main.ollama_client.is_available') as mock_available:
            mock_available.return_value = False
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "degraded" in data["status"]
    
    def test_infer_endpoint_success(self, client):
        """Test successful inference request."""
        mock_generation_result = {
            'response': 'Use df -h to check disk usage',
            'model_used': 'llama3.1:8b',
            'prompt_tokens': 50,
            'response_tokens': 20,
            'total_duration': 1500000000
        }
        
        with patch('modules.module_a_core.main.ollama_client.is_available') as mock_available, \
             patch('modules.module_a_core.main.ollama_client.generate_response') as mock_generate:
            
            mock_available.return_value = True
            mock_generate.return_value = mock_generation_result
            
            response = client.post("/infer", json={
                "query": "How to check disk usage?",
                "context": "Linux administration"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Use df -h to check disk usage"
            assert "confidence" in data
            assert "status" in data
            assert "processing_time" in data
            assert data["model_used"] == "llama3.1:8b"
    
    def test_infer_endpoint_invalid_query(self, client):
        """Test inference with invalid query."""
        response = client.post("/infer", json={
            "query": "ab"  # Too short
        })
        
        assert response.status_code == 400
        assert "Invalid query" in response.json()["detail"]
    
    def test_infer_endpoint_ollama_unavailable(self, client):
        """Test inference when Ollama is unavailable."""
        with patch('modules.module_a_core.main.ollama_client.is_available') as mock_available:
            mock_available.return_value = False
            
            response = client.post("/infer", json={
                "query": "How to check disk usage?"
            })
            
            assert response.status_code == 503
            assert "LLM service unavailable" in response.json()["detail"]
    
    def test_status_endpoint(self, client):
        """Test status endpoint."""
        with patch('modules.module_a_core.main.ollama_client.is_available') as mock_available:
            mock_available.return_value = True
            
            response = client.get("/status")
            assert response.status_code == 200
            data = response.json()
            assert data["module"] == "Core Intelligence Engine"
            assert data["version"] == "1.0.0"
            assert data["status"] == "operational"
            assert "ollama" in data
            assert "endpoints" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])