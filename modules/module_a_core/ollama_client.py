"""
Ollama client for Core Intelligence Engine.
Handles connection management and query processing with Llama 3.1 8B model.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import ollama
from ollama import AsyncClient
from shared.models import Query, Response


logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama API with connection management and error handling."""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama3.1:8b"):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.client = AsyncClient(host=self.base_url)
        
    async def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            # Add timeout protection
            models = await asyncio.wait_for(self.client.list(), timeout=5.0)
            # Check if our model is available
            available_models = [model['name'] for model in models['models']]
            
            # Log available models for debugging
            logger.debug(f"Available models: {available_models}")
            logger.debug(f"Looking for model: {self.model}")
            
            # Check exact match and partial matches (for tags)
            model_available = (
                self.model in available_models or
                any(self.model.startswith(model.split(':')[0]) for model in available_models) or
                any(model.startswith(self.model.split(':')[0]) for model in available_models)
            )
            
            if not model_available:
                logger.warning(f"Model {self.model} not found in available models: {available_models}")
            
            return model_available
        except asyncio.TimeoutError:
            logger.error("Ollama availability check timed out")
            return False
        except Exception as e:
            logger.error(f"Ollama availability check failed: {e}")
            return False
    
    async def generate_response(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate response using Ollama with Llama 3.1 8B model.
        
        Args:
            query: User query string
            context: Optional context information
            
        Returns:
            Dict with response, confidence, and metadata
        """
        try:
            # Prepare prompt with context if provided
            prompt = self._prepare_prompt(query, context)
            
            # Generate response using Ollama with timeout protection
            response = await asyncio.wait_for(
                self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 1000,
                    }
                ),
                timeout=300.0  # 5 minutes timeout for heavy models
            )
            
            response_text = response['response'].strip()
            
            return {
                'response': response_text,
                'model_used': self.model,
                'prompt_tokens': response.get('prompt_eval_count', 0),
                'response_tokens': response.get('eval_count', 0),
                'total_duration': response.get('total_duration', 0),
            }
            
        except asyncio.TimeoutError:
            logger.error("Ollama generation timed out")
            raise RuntimeError("LLM generation timed out - please try again")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"LLM generation failed: {str(e)}")
    
    def _prepare_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Prepare prompt with system instructions and context."""
        system_prompt = """You are a helpful Linux system administrator assistant. 
Provide clear, accurate, and practical answers to Linux administration questions.
Focus on commonly used commands and best practices.
If you're not certain about something, indicate your uncertainty."""
        
        if context:
            prompt = f"{system_prompt}\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
        else:
            prompt = f"{system_prompt}\n\nQuestion: {query}\n\nAnswer:"
            
        return prompt


class QueryProcessor:
    """Processes and validates user queries before sending to Ollama."""
    
    def __init__(self):
        self.max_query_length = 2000
        self.min_query_length = 3
    
    def validate_query(self, query: str) -> bool:
        """Validate query format and content."""
        if not query or not isinstance(query, str):
            return False
            
        query = query.strip()
        
        if len(query) < self.min_query_length:
            return False
            
        if len(query) > self.max_query_length:
            return False
            
        return True
    
    def preprocess_query(self, query: str) -> str:
        """Clean and preprocess query text."""
        # Basic cleaning
        query = query.strip()
        
        # Remove excessive whitespace
        query = ' '.join(query.split())
        
        # Ensure query ends with appropriate punctuation
        if not query.endswith(('?', '.', '!')):
            query += '?'
            
        return query
    
    def extract_context_hints(self, query: str) -> Optional[str]:
        """Extract context hints from query for better processing."""
        linux_keywords = [
            'linux', 'ubuntu', 'debian', 'centos', 'rhel', 'fedora',
            'bash', 'shell', 'command', 'terminal', 'cli',
            'systemd', 'systemctl', 'service', 'daemon',
            'file', 'directory', 'permission', 'chmod', 'chown',
            'network', 'firewall', 'iptables', 'ssh',
            'log', 'syslog', 'journal', 'monitoring'
        ]
        
        query_lower = query.lower()
        found_keywords = [kw for kw in linux_keywords if kw in query_lower]
        
        if found_keywords:
            return f"Linux administration context detected: {', '.join(found_keywords[:3])}"
        
        return None