"""
Module Orchestrator for Module F
Handles request routing and communication with all backend modules.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from config_manager import config_manager
import time


@dataclass
class QueryResponse:
    """Response from module query."""
    success: bool
    data: Dict[str, Any]
    module: str
    processing_time: float
    error: Optional[str] = None


class ModuleOrchestrator:
    """Orchestrates requests across all backend modules."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=180.0)  # 3 minutes for 70B model
        self.config = config_manager
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health status of all modules."""
        results = {}
        
        for module_key, module_config in self.config.get_enabled_modules().items():
            url = self.config.get_module_url(module_key)
            if url:
                try:
                    response = await self.client.get(f"{url}/health", timeout=30.0)
                    results[module_key] = response.status_code == 200
                except Exception as e:
                    print(f"Health check failed for {module_key}: {e}")
                    results[module_key] = False
            else:
                results[module_key] = False
        
        return results
    
    async def query_core_intelligence(self, query: str) -> QueryResponse:
        """Query Module A: Core Intelligence Engine."""
        start_time = time.time()
        
        try:
            url = self.config.get_module_url('core')
            if not url:
                return QueryResponse(
                    success=False,
                    data={},
                    module='core',
                    processing_time=0,
                    error="Module A not configured"
                )
            
            response = await self.client.post(
                f"{url}/infer",
                json={"query": query, "enable_context_search": True}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                return QueryResponse(
                    success=True,
                    data=response.json(),
                    module='core',
                    processing_time=processing_time
                )
            else:
                return QueryResponse(
                    success=False,
                    data={},
                    module='core',
                    processing_time=processing_time,
                    error=f"HTTP {response.status_code}"
                )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                data={},
                module='core',
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def execute_proactive_task(self, task_type: str, params: Dict[str, Any]) -> QueryResponse:
        """Execute task via Module C: Proactive Agents."""
        start_time = time.time()
        
        try:
            url = self.config.get_module_url('agents')
            if not url:
                return QueryResponse(
                    success=False,
                    data={},
                    module='agents',
                    processing_time=0,
                    error="Module C not configured"
                )
            
            response = await self.client.post(
                f"{url}/execute_task",
                json={"task_type": task_type, "params": params}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                return QueryResponse(
                    success=True,
                    data=response.json(),
                    module='agents',
                    processing_time=processing_time
                )
            else:
                return QueryResponse(
                    success=False,
                    data={},
                    module='agents',
                    processing_time=processing_time,
                    error=f"HTTP {response.status_code}"
                )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                data={},
                module='agents',
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def safe_execute_command(self, command: str, dry_run: bool = True) -> QueryResponse:
        """Execute command via Module D: Safe Execution."""
        start_time = time.time()
        
        try:
            url = self.config.get_module_url('execution')
            if not url:
                return QueryResponse(
                    success=False,
                    data={},
                    module='execution',
                    processing_time=0,
                    error="Module D not configured"
                )
            
            response = await self.client.post(
                f"{url}/safe_execute",
                json={"command": command, "dry_run": dry_run}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                return QueryResponse(
                    success=True,
                    data=response.json(),
                    module='execution',
                    processing_time=processing_time
                )
            else:
                return QueryResponse(
                    success=False,
                    data={},
                    module='execution',
                    processing_time=processing_time,
                    error=f"HTTP {response.status_code}"
                )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                data={},
                module='execution',
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def escalate_query(self, query: str, confidence: float) -> QueryResponse:
        """Escalate query via Module E: Hybrid Gateway."""
        start_time = time.time()
        
        try:
            url = self.config.get_module_url('hybrid')
            if not url:
                return QueryResponse(
                    success=False,
                    data={},
                    module='hybrid',
                    processing_time=0,
                    error="Module E not configured"
                )
            
            response = await self.client.post(
                f"{url}/escalate",
                json={"query": query, "confidence": confidence}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                return QueryResponse(
                    success=True,
                    data=response.json(),
                    module='hybrid',
                    processing_time=processing_time
                )
            else:
                return QueryResponse(
                    success=False,
                    data={},
                    module='hybrid',
                    processing_time=processing_time,
                    error=f"HTTP {response.status_code}"
                )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                data={},
                module='hybrid',
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def process_full_query(self, query: str) -> Dict[str, Any]:
        """Process a complete query through the system workflow."""
        results = {
            'query': query,
            'timestamp': time.time(),
            'steps': []
        }
        
        # Step 1: Query Core Intelligence (A) with context from Knowledge Vault (B)
        core_response = await self.query_core_intelligence(query)
        results['steps'].append({
            'step': 'core_intelligence',
            'response': core_response
        })
        
        if core_response.success and core_response.data:
            confidence = core_response.data.get('confidence', 0.0)
            
            # Step 2: If confidence is low, escalate to Hybrid Gateway (E)
            if confidence < 0.5:
                escalation_response = await self.escalate_query(query, confidence)
                results['steps'].append({
                    'step': 'escalation',
                    'response': escalation_response
                })
            
            # Step 3: Check if response suggests a command or task
            response_text = core_response.data.get('response', '').lower()
            if any(keyword in response_text for keyword in ['command', 'execute', 'run', 'install']):
                # Suggest using proactive agents
                results['suggested_actions'] = ['proactive_task', 'safe_execution']
        else:
            # If core intelligence fails, add error information
            results['error'] = core_response.error or "Core intelligence module failed"
        
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global orchestrator instance
orchestrator = ModuleOrchestrator()