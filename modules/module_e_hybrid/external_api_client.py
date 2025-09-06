"""
External API Client for Module E: Hybrid Intelligence Gateway
Manages communication with external AI services like Grok.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ExternalResponse:
    """Response from external AI service."""
    success: bool
    response: str
    source: str
    confidence: float
    processing_time: float
    cached: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class ExternalAPIClient:
    """
    Client for external AI services with fallback handling.
    
    Supports multiple external AI providers with automatic
    fallback and response caching.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize external API client.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config or {}
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # API configurations
        self.grok_config = self.config.get('grok', {})
        self.openai_config = self.config.get('openai', {})
        self.anthropic_config = self.config.get('anthropic', {})
        
        # Default to mock mode if no real API keys
        self.mock_mode = not any([
            self.grok_config.get('api_key'),
            self.openai_config.get('api_key'),
            self.anthropic_config.get('api_key')
        ])
        
        if self.mock_mode:
            logger.info("External API client running in mock mode - no real API keys configured")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def check_internet_connectivity(self) -> bool:
        """
        Check if internet connection is available.
        
        Returns:
            True if internet is available, False otherwise
        """
        try:
            response = await self.client.get("https://httpbin.org/status/200", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Internet connectivity check failed: {e}")
            return False
    
    async def query_grok(self, query: str, context: Optional[str] = None) -> ExternalResponse:
        """
        Query Grok AI service.
        
        Args:
            query: Query to send to Grok
            context: Optional context to include
            
        Returns:
            ExternalResponse with Grok's response
        """
        start_time = datetime.now()
        
        if self.mock_mode:
            return await self._mock_grok_response(query, context, start_time)
        
        try:
            # Check if Grok API is configured
            if not self.grok_config.get('api_key'):
                return ExternalResponse(
                    success=False,
                    response="",
                    source="grok",
                    confidence=0.0,
                    processing_time=0.0,
                    error="Grok API key not configured"
                )
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.grok_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Build prompt with context
            full_prompt = query
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {query}"
            
            payload = {
                "model": self.grok_config.get('model', 'grok-beta'),
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful Linux system administrator assistant. Provide accurate, practical advice for Linux administration tasks."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                "max_tokens": self.grok_config.get('max_tokens', 1000),
                "temperature": self.grok_config.get('temperature', 0.7)
            }
            
            # Make API request
            grok_url = self.grok_config.get('api_url', 'https://api.x.ai/v1/chat/completions')
            response = await self.client.post(grok_url, headers=headers, json=payload)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response text
                response_text = ""
                if 'choices' in data and len(data['choices']) > 0:
                    response_text = data['choices'][0]['message']['content']
                
                # Calculate confidence based on response quality
                confidence = self._calculate_response_confidence(response_text)
                
                return ExternalResponse(
                    success=True,
                    response=response_text,
                    source="grok",
                    confidence=confidence,
                    processing_time=processing_time,
                    metadata={
                        "model": payload["model"],
                        "tokens_used": data.get('usage', {}).get('total_tokens', 0)
                    }
                )
            else:
                error_msg = f"Grok API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                return ExternalResponse(
                    success=False,
                    response="",
                    source="grok",
                    confidence=0.0,
                    processing_time=processing_time,
                    error=error_msg
                )
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Grok API request failed: {str(e)}"
            logger.error(error_msg)
            
            return ExternalResponse(
                success=False,
                response="",
                source="grok",
                confidence=0.0,
                processing_time=processing_time,
                error=error_msg
            )
    
    async def _mock_grok_response(self, query: str, context: Optional[str], start_time: datetime) -> ExternalResponse:
        """Generate mock Grok response for testing."""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        # Generate contextual mock response
        mock_responses = {
            "log": "To analyze system logs, use: `journalctl -xe` for recent errors, `journalctl -u service_name` for specific services, and `dmesg | tail` for kernel messages. Check `/var/log/syslog` for general system events.",
            "backup": "For backups, use rsync: `rsync -av --progress source/ destination/`. For automated backups, consider: `tar -czf backup_$(date +%Y%m%d).tar.gz /path/to/data`. Always test restore procedures.",
            "disk": "Check disk usage with: `df -h` for filesystem usage, `du -sh /*` for directory sizes, and `lsblk` for block devices. Use `ncdu` for interactive disk usage analysis.",
            "memory": "Monitor memory with: `free -h` for overview, `ps aux --sort=-%mem` for memory-hungry processes, and `vmstat 1 5` for memory statistics over time.",
            "process": "Manage processes with: `ps aux` for all processes, `top` or `htop` for real-time monitoring, `kill -9 PID` for force termination, and `systemctl` for service management."
        }
        
        # Find relevant mock response
        response_text = "I can help you with Linux administration tasks. "
        for keyword, response in mock_responses.items():
            if keyword in query.lower():
                response_text = response
                break
        else:
            response_text += "Please provide more specific details about your Linux administration needs."
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ExternalResponse(
            success=True,
            response=response_text,
            source="grok_mock",
            confidence=0.85,  # High confidence for mock responses
            processing_time=processing_time,
            metadata={"mock": True, "query_keywords": [k for k in mock_responses.keys() if k in query.lower()]}
        )
    
    async def query_openai(self, query: str, context: Optional[str] = None) -> ExternalResponse:
        """
        Query OpenAI API as fallback.
        
        Args:
            query: Query to send
            context: Optional context
            
        Returns:
            ExternalResponse with OpenAI's response
        """
        start_time = datetime.now()
        
        # For now, return mock response
        await asyncio.sleep(0.3)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ExternalResponse(
            success=False,
            response="",
            source="openai",
            confidence=0.0,
            processing_time=processing_time,
            error="OpenAI integration not implemented yet"
        )
    
    async def query_with_fallback(self, query: str, context: Optional[str] = None) -> ExternalResponse:
        """
        Query external APIs with automatic fallback.
        
        Args:
            query: Query to send
            context: Optional context
            
        Returns:
            ExternalResponse from the first successful API
        """
        # Try Grok first
        grok_response = await self.query_grok(query, context)
        if grok_response.success:
            return grok_response
        
        logger.warning("Grok query failed, trying fallback APIs")
        
        # Try OpenAI as fallback
        openai_response = await self.query_openai(query, context)
        if openai_response.success:
            return openai_response
        
        # All APIs failed
        return ExternalResponse(
            success=False,
            response="",
            source="fallback_failed",
            confidence=0.0,
            processing_time=0.0,
            error="All external APIs failed"
        )
    
    def _calculate_response_confidence(self, response: str) -> float:
        """
        Calculate confidence score for external API response.
        
        Args:
            response: Response text to analyze
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not response or len(response.strip()) < 10:
            return 0.1
        
        confidence = 0.5  # Base confidence
        
        # Length bonus (longer responses tend to be more detailed)
        if len(response) > 100:
            confidence += 0.1
        if len(response) > 300:
            confidence += 0.1
        
        # Technical content indicators
        technical_indicators = [
            'command', 'sudo', 'systemctl', 'journalctl', 'grep', 'awk', 'sed',
            '/var/log', '/etc/', 'chmod', 'chown', 'ps aux', 'df -h', 'free -h'
        ]
        
        technical_score = sum(1 for indicator in technical_indicators if indicator in response.lower())
        confidence += min(technical_score * 0.05, 0.2)  # Max 0.2 bonus
        
        # Uncertainty penalties
        uncertainty_words = ['maybe', 'might', 'possibly', 'not sure', 'unclear']
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        confidence -= uncertainty_count * 0.1
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))


# Global client instance
external_api_client = ExternalAPIClient()


async def query_external_api(query: str, context: Optional[str] = None) -> ExternalResponse:
    """Convenience function for external API queries."""
    return await external_api_client.query_with_fallback(query, context)