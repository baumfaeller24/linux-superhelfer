"""
Agent orchestrator for Module C: Proactive Agents.
Coordinates task execution, module integration, and workflow management.
"""

import logging
import asyncio
import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .task_classifier import TaskClassifier, TaskMatch, TaskType
from .session_manager import SessionManager, SessionStatus
from .task_handlers import TaskHandlerRegistry, TaskResult
from .module_client import ModuleClient, ModuleResponse

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Task execution request."""
    task_type: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None
    require_confirmation: bool = True
    enhance_with_ai: bool = True


@dataclass
class ExecutionResult:
    """Task execution result."""
    success: bool
    task_id: str
    task_type: str
    result: Dict[str, Any]
    sources: List[str]
    execution_time: float
    ai_enhanced: bool = False
    confirmation_required: bool = False
    confirmation_id: Optional[str] = None
    error: Optional[str] = None


class AgentOrchestrator:
    """Orchestrates proactive agent tasks and workflows."""
    
    def __init__(self, module_a_url: str = "http://localhost:8001", 
                 module_b_url: str = "http://localhost:8002"):
        """Initialize agent orchestrator."""
        self.task_classifier = TaskClassifier()
        self.session_manager = SessionManager()
        self.task_registry = TaskHandlerRegistry()
        self.module_client = ModuleClient(module_a_url, module_b_url)
        
        # Performance tracking
        self.execution_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "avg_execution_time": 0.0,
            "ai_enhanced_tasks": 0
        }
    
    async def classify_and_execute_task(self, query: str, session_id: Optional[str] = None,
                                      auto_confirm: bool = False) -> ExecutionResult:
        """Classify query and execute appropriate task."""
        start_time = time.time()
        task_id = str(uuid.uuid4())
        
        try:
            # Classify the task
            task_match = self.task_classifier.classify_task(query)
            
            if task_match.task_type == TaskType.UNKNOWN:
                return ExecutionResult(
                    success=False,
                    task_id=task_id,
                    task_type="unknown",
                    result={"error": "Could not classify task type from query"},
                    sources=[],
                    execution_time=time.time() - start_time,
                    error="Unknown task type"
                )
            
            # Create execution request
            execution_request = ExecutionRequest(
                task_type=task_match.task_type.value,
                parameters=task_match.extracted_params,
                session_id=session_id,
                require_confirmation=not auto_confirm,
                enhance_with_ai=True
            )
            
            # Execute the task
            return await self.execute_task(execution_request)
            
        except Exception as e:
            logger.error(f"Task classification and execution failed: {e}")
            return ExecutionResult(
                success=False,
                task_id=task_id,
                task_type="unknown",
                result={"error": str(e)},
                sources=[],
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def execute_task(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a task based on the execution request."""
        start_time = time.time()
        task_id = str(uuid.uuid4())
        
        try:
            # Update statistics
            self.execution_stats["total_tasks"] += 1
            
            # Get or create session
            if request.session_id:
                session = self.session_manager.get_session(request.session_id)
                if not session:
                    request.session_id = self.session_manager.create_session()
            else:
                request.session_id = self.session_manager.create_session()
            
            # Get task type enum
            try:
                task_type = TaskType(request.task_type)
            except ValueError:
                return ExecutionResult(
                    success=False,
                    task_id=task_id,
                    task_type=request.task_type,
                    result={"error": f"Unsupported task type: {request.task_type}"},
                    sources=[],
                    execution_time=time.time() - start_time,
                    error=f"Unsupported task type: {request.task_type}"
                )
            
            # Get task handler
            handler = self.task_registry.get_handler(task_type)
            if not handler:
                return ExecutionResult(
                    success=False,
                    task_id=task_id,
                    task_type=request.task_type,
                    result={"error": f"No handler available for task type: {request.task_type}"},
                    sources=[],
                    execution_time=time.time() - start_time,
                    error=f"No handler available for task type: {request.task_type}"
                )
            
            # Validate parameters
            try:
                validated_params = handler.validate_parameters(request.parameters)
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    task_id=task_id,
                    task_type=request.task_type,
                    result={"error": f"Parameter validation failed: {str(e)}"},
                    sources=[],
                    execution_time=time.time() - start_time,
                    error=f"Parameter validation failed: {str(e)}"
                )
            
            # Start task execution tracking
            self.session_manager.start_task_execution(
                request.session_id, task_id, request.task_type, validated_params
            )
            
            # Check if confirmation is required
            if request.require_confirmation and handler.requires_confirmation(validated_params):
                confirmation_id = str(uuid.uuid4())
                confirmation_message = handler.get_confirmation_message(validated_params)
                
                # Add pending confirmation
                self.session_manager.add_pending_confirmation(
                    request.session_id,
                    confirmation_id,
                    {
                        "task_id": task_id,
                        "task_type": request.task_type,
                        "parameters": validated_params,
                        "message": confirmation_message,
                        "handler": handler.__class__.__name__
                    }
                )
                
                return ExecutionResult(
                    success=True,
                    task_id=task_id,
                    task_type=request.task_type,
                    result={
                        "status": "pending_confirmation",
                        "confirmation_message": confirmation_message,
                        "confirmation_id": confirmation_id
                    },
                    sources=[],
                    execution_time=time.time() - start_time,
                    confirmation_required=True,
                    confirmation_id=confirmation_id
                )
            
            # Execute the task
            session = self.session_manager.get_session(request.session_id)
            context = session.context if session else {}
            
            # Enhance with AI if requested
            ai_response = None
            if request.enhance_with_ai:
                ai_response = await self._enhance_task_with_ai(
                    request.task_type, validated_params
                )
                if ai_response.success:
                    self.execution_stats["ai_enhanced_tasks"] += 1
                    context["ai_enhancement"] = ai_response.data
            
            # Execute the task
            task_result = await handler.execute(validated_params, context)
            
            # Complete task execution tracking
            self.session_manager.complete_task_execution(
                request.session_id, task_id, task_result.result, task_result.error
            )
            
            # Update statistics
            if task_result.success:
                self.execution_stats["successful_tasks"] += 1
            else:
                self.execution_stats["failed_tasks"] += 1
            
            execution_time = time.time() - start_time
            self._update_avg_execution_time(execution_time)
            
            # Prepare result
            result_data = task_result.result.copy()
            if ai_response and ai_response.success:
                result_data["ai_enhancement"] = {
                    "response": ai_response.data.get("response", ""),
                    "confidence": ai_response.data.get("confidence", 0.0),
                    "sources": ai_response.data.get("sources", [])
                }
            
            return ExecutionResult(
                success=task_result.success,
                task_id=task_id,
                task_type=request.task_type,
                result=result_data,
                sources=task_result.sources,
                execution_time=execution_time,
                ai_enhanced=ai_response.success if ai_response else False,
                error=task_result.error
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task execution failed: {e}")
            
            # Complete task execution with error
            if request.session_id:
                self.session_manager.complete_task_execution(
                    request.session_id, task_id, {}, str(e)
                )
            
            self.execution_stats["failed_tasks"] += 1
            self._update_avg_execution_time(execution_time)
            
            return ExecutionResult(
                success=False,
                task_id=task_id,
                task_type=request.task_type,
                result={"error": str(e)},
                sources=[],
                execution_time=execution_time,
                error=str(e)
            )
    
    async def confirm_task(self, session_id: str, confirmation_id: str, 
                          approved: bool) -> ExecutionResult:
        """Confirm or reject a pending task."""
        try:
            # Resolve confirmation
            confirmation = self.session_manager.resolve_confirmation(
                session_id, confirmation_id, approved
            )
            
            if not confirmation:
                return ExecutionResult(
                    success=False,
                    task_id="unknown",
                    task_type="confirmation",
                    result={"error": "Confirmation not found or expired"},
                    sources=[],
                    execution_time=0.0,
                    error="Confirmation not found or expired"
                )
            
            if not approved:
                return ExecutionResult(
                    success=True,
                    task_id=confirmation["task_id"],
                    task_type=confirmation["task_type"],
                    result={"status": "rejected", "message": "Task execution rejected by user"},
                    sources=[],
                    execution_time=0.0
                )
            
            # Execute the confirmed task directly
            task_id = confirmation["task_id"]
            task_type = confirmation["task_type"]
            validated_params = confirmation["parameters"]
            
            # Create execution request with existing session
            execution_request = ExecutionRequest(
                task_type=task_type,
                parameters=validated_params,
                session_id=session_id,
                require_confirmation=False,  # Already confirmed
                enhance_with_ai=True
            )
            
            # Execute the task and preserve the original task ID
            result = await self.execute_task(execution_request)
            result.task_id = task_id  # Ensure we keep the original task ID
            
            return result
            
        except Exception as e:
            logger.error(f"Task confirmation failed: {e}")
            return ExecutionResult(
                success=False,
                task_id="unknown",
                task_type="confirmation",
                result={"error": str(e)},
                sources=[],
                execution_time=0.0,
                error=str(e)
            )
    
    async def _enhance_task_with_ai(self, task_type: str, parameters: Dict[str, Any]) -> ModuleResponse:
        """Enhance task with AI assistance."""
        try:
            # Create task description
            task_descriptions = {
                "log_analyze": "Analyze system logs and troubleshoot issues",
                "backup_create": "Create backup scripts and data synchronization",
                "disk_check": "Check disk space and storage usage",
                "memory_check": "Monitor memory and RAM usage",
                "process_check": "List and monitor running processes"
            }
            
            description = task_descriptions.get(task_type, f"Execute {task_type} task")
            
            # Get AI enhancement
            return await self.module_client.enhance_task_with_ai(description, parameters)
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return ModuleResponse(success=False, data={}, error=str(e))
    
    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time."""
        total_tasks = self.execution_stats["total_tasks"]
        if total_tasks > 0:
            current_avg = self.execution_stats["avg_execution_time"]
            new_avg = ((current_avg * (total_tasks - 1)) + execution_time) / total_tasks
            self.execution_stats["avg_execution_time"] = new_avg
    
    async def get_task_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get task suggestions for a query."""
        suggestions = self.task_classifier.get_task_suggestions(query, min_confidence=0.1)
        
        result = []
        for suggestion in suggestions:
            result.append({
                "task_type": suggestion.task_type.value,
                "confidence": suggestion.confidence,
                "description": self.task_classifier.get_task_description(suggestion.task_type),
                "matched_keywords": suggestion.matched_keywords,
                "extracted_params": suggestion.extracted_params
            })
        
        return result
    
    def get_supported_tasks(self) -> List[Dict[str, Any]]:
        """Get list of supported tasks."""
        supported_tasks = self.task_registry.get_supported_tasks()
        
        result = []
        for task_type in supported_tasks:
            result.append({
                "task_type": task_type.value,
                "description": self.task_classifier.get_task_description(task_type),
                "handler_available": True
            })
        
        return result
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        module_status = await self.module_client.get_module_status()
        session_stats = self.session_manager.get_session_statistics()
        
        return {
            "orchestrator": {
                "status": "operational",
                "supported_tasks": len(self.task_registry.get_supported_tasks()),
                "execution_stats": self.execution_stats
            },
            "sessions": session_stats,
            "modules": module_status,
            "task_classifier": {
                "supported_task_types": len(self.task_classifier.get_supported_tasks())
            }
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.module_client.close()