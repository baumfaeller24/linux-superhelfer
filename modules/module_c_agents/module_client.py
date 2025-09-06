"""
Module client for Module C: Proactive Agents.
Handles communication with Module A (Core Intelligence) and Module B (RAG Knowledge Vault).
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModuleResponse:
    """Response from module communication."""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0.0


class ModuleClient:
    """Client for communicating with other modules."""
    
    def __init__(self, module_a_url: str = "http://localhost:8001", 
                 module_b_url: str = "http://localhost:8002", timeout: float = 10.0):
        """Initialize module client."""
        self.module_a_url = module_a_url.rstrip('/')
        self.module_b_url = module_b_url.rstrip('/')
        self.timeout = timeout
        self._client = None
        self._module_a_available = None
        self._module_b_available = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def check_module_a_health(self) -> bool:
        """Check if Module A is available."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.module_a_url}/health")
            is_healthy = response.status_code == 200 and response.json().get("status") == "ok"
            self._module_a_available = is_healthy
            return is_healthy
        except Exception as e:
            logger.warning(f"Module A health check failed: {e}")
            self._module_a_available = False
            return False
    
    async def check_module_b_health(self) -> bool:
        """Check if Module B is available."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.module_b_url}/health")
            is_healthy = response.status_code == 200 and response.json().get("status") == "ok"
            self._module_b_available = is_healthy
            return is_healthy
        except Exception as e:
            logger.warning(f"Module B health check failed: {e}")
            self._module_b_available = False
            return False
    
    async def enhance_task_with_ai(self, task_description: str, task_parameters: Dict[str, Any]) -> ModuleResponse:
        """Enhance task execution with AI assistance."""
        import time
        start_time = time.time()
        
        try:
            if self._module_a_available is None:
                await self.check_module_a_health()
            
            if not self._module_a_available:
                return ModuleResponse(
                    success=False,
                    data={},
                    error="Module A not available",
                    processing_time=time.time() - start_time
                )
            
            # Create enhanced query for AI
            query_parts = [f"Help me with this Linux administration task: {task_description}"]
            
            if task_parameters:
                query_parts.append("Parameters:")
                for key, value in task_parameters.items():
                    query_parts.append(f"- {key}: {value}")
            
            query_parts.append("Please provide specific commands and best practices.")
            enhanced_query = "\n".join(query_parts)
            
            client = await self._get_client()
            response = await client.post(
                f"{self.module_a_url}/infer_with_context",
                json={
                    "query": enhanced_query,
                    "top_k": 5,
                    "threshold": 0.5
                }
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return ModuleResponse(
                    success=True,
                    data=data,
                    processing_time=processing_time
                )
            else:
                return ModuleResponse(
                    success=False,
                    data={},
                    error=f"AI enhancement failed: HTTP {response.status_code}",
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return ModuleResponse(
                success=False,
                data={},
                error=f"AI enhancement failed: {str(e)}",
                processing_time=processing_time
            )
    
    async def get_module_status(self) -> Dict[str, Any]:
        """Get status of both modules."""
        module_a_health = await self.check_module_a_health()
        module_b_health = await self.check_module_b_health()
        
        return {
            "module_a": {
                "available": module_a_health,
                "url": self.module_a_url
            },
            "module_b": {
                "available": module_b_health,
                "url": self.module_b_url
            },
            "integration_status": "operational" if (module_a_health and module_b_health) else "degraded"
        }