"""
Module C: Proactive Agents
Task automation and workflow execution for Linux administration.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from shared.models import HealthStatus
from shared.config import ConfigManager, get_module_url
from .agent_orchestrator import AgentOrchestrator, ExecutionRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Proactive Agents",
    version="1.0.0",
    description="Task automation and workflow execution for Linux administration"
)

# Initialize configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Get module URLs
try:
    module_a_url = get_module_url('core', config)
    module_b_url = get_module_url('rag', config)
except Exception as e:
    logger.warning(f"Failed to get module URLs from config: {e}")
    module_a_url = "http://localhost:8001"
    module_b_url = "http://localhost:8002"

# Initialize orchestrator
orchestrator = AgentOrchestrator(module_a_url, module_b_url)

# Initialize web fetch agent
from modules.module_c_agents.web_fetch_agent import WebFetchAgent
web_fetch_agent = WebFetchAgent()


# Request/Response Models
class ExecuteTaskRequest(BaseModel):
    """Request model for task execution."""
    task_type: str = Field(..., description="Type of task to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    require_confirmation: bool = Field(True, description="Whether to require human confirmation")
    enhance_with_ai: bool = Field(True, description="Whether to enhance with AI assistance")


class ClassifyTaskRequest(BaseModel):
    """Request model for task classification."""
    query: str = Field(..., description="User query to classify")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    auto_confirm: bool = Field(False, description="Auto-confirm tasks (for testing)")


class ConfirmTaskRequest(BaseModel):
    """Request model for task confirmation."""
    session_id: str = Field(..., description="Session ID")
    confirmation_id: str = Field(..., description="Confirmation ID")
    approved: bool = Field(..., description="Whether the task is approved")


class TaskSuggestionRequest(BaseModel):
    """Request model for task suggestions."""
    query: str = Field(..., description="Query to get suggestions for")


class ExecuteTaskResponse(BaseModel):
    """Response model for task execution."""
    success: bool = Field(..., description="Whether execution was successful")
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task executed")
    result: Dict[str, Any] = Field(..., description="Task execution result")
    sources: List[str] = Field(..., description="Sources used for task execution")
    execution_time: float = Field(..., description="Execution time in seconds")
    ai_enhanced: bool = Field(False, description="Whether AI enhancement was used")
    confirmation_required: bool = Field(False, description="Whether confirmation is required")
    confirmation_id: Optional[str] = Field(None, description="Confirmation ID if required")
    error: Optional[str] = Field(None, description="Error message if failed")


class TaskSuggestion(BaseModel):
    """Task suggestion model."""
    task_type: str = Field(..., description="Task type")
    confidence: float = Field(..., description="Confidence score")
    description: str = Field(..., description="Task description")
    matched_keywords: List[str] = Field(..., description="Matched keywords")
    extracted_params: Dict[str, str] = Field(..., description="Extracted parameters")


class SupportedTask(BaseModel):
    """Supported task model."""
    task_type: str = Field(..., description="Task type")
    description: str = Field(..., description="Task description")
    handler_available: bool = Field(..., description="Whether handler is available")


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint with module integration status."""
    try:
        # Check orchestrator status
        system_status = await orchestrator.get_system_status()
        
        # Determine overall health
        modules_status = system_status.get("modules", {})
        integration_status = modules_status.get("integration_status", "unknown")
        
        if integration_status == "operational":
            return HealthStatus(status="ok", version="1.0.0")
        elif integration_status == "degraded":
            return HealthStatus(status="degraded - Some modules unavailable", version="1.0.0")
        else:
            return HealthStatus(status="error - Module integration failed", version="1.0.0")
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(status="error", version="1.0.0")


@app.post("/execute_task", response_model=ExecuteTaskResponse)
async def execute_task(request: ExecuteTaskRequest):
    """
    Execute a specific task with given parameters.
    
    Args:
        request: Task execution request
        
    Returns:
        ExecuteTaskResponse with execution results
        
    Raises:
        HTTPException: If task execution fails
    """
    try:
        # Create execution request
        execution_request = ExecutionRequest(
            task_type=request.task_type,
            parameters=request.parameters,
            session_id=request.session_id,
            require_confirmation=request.require_confirmation,
            enhance_with_ai=request.enhance_with_ai
        )
        
        # Execute task
        result = await orchestrator.execute_task(execution_request)
        
        logger.info(f"Task executed: {result.task_type} (success: {result.success}, time: {result.execution_time:.2f}s)")
        
        return ExecuteTaskResponse(
            success=result.success,
            task_id=result.task_id,
            task_type=result.task_type,
            result=result.result,
            sources=result.sources,
            execution_time=result.execution_time,
            ai_enhanced=result.ai_enhanced,
            confirmation_required=result.confirmation_required,
            confirmation_id=result.confirmation_id,
            error=result.error
        )
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )


@app.post("/classify_and_execute", response_model=ExecuteTaskResponse)
async def classify_and_execute_task(request: ClassifyTaskRequest):
    """
    Classify user query and execute appropriate task.
    
    Args:
        request: Task classification and execution request
        
    Returns:
        ExecuteTaskResponse with execution results
        
    Raises:
        HTTPException: If classification or execution fails
    """
    try:
        # Classify and execute
        result = await orchestrator.classify_and_execute_task(
            query=request.query,
            session_id=request.session_id,
            auto_confirm=request.auto_confirm
        )
        
        logger.info(f"Query classified and executed: '{request.query}' -> {result.task_type} (success: {result.success})")
        
        return ExecuteTaskResponse(
            success=result.success,
            task_id=result.task_id,
            task_type=result.task_type,
            result=result.result,
            sources=result.sources,
            execution_time=result.execution_time,
            ai_enhanced=result.ai_enhanced,
            confirmation_required=result.confirmation_required,
            confirmation_id=result.confirmation_id,
            error=result.error
        )
        
    except Exception as e:
        logger.error(f"Task classification and execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task classification and execution failed: {str(e)}"
        )


@app.post("/confirm_task", response_model=ExecuteTaskResponse)
async def confirm_task(request: ConfirmTaskRequest):
    """
    Confirm or reject a pending task.
    
    Args:
        request: Task confirmation request
        
    Returns:
        ExecuteTaskResponse with confirmation result
        
    Raises:
        HTTPException: If confirmation fails
    """
    try:
        result = await orchestrator.confirm_task(
            session_id=request.session_id,
            confirmation_id=request.confirmation_id,
            approved=request.approved
        )
        
        logger.info(f"Task confirmation: {request.confirmation_id} -> approved: {request.approved}")
        
        return ExecuteTaskResponse(
            success=result.success,
            task_id=result.task_id,
            task_type=result.task_type,
            result=result.result,
            sources=result.sources,
            execution_time=result.execution_time,
            ai_enhanced=result.ai_enhanced,
            confirmation_required=result.confirmation_required,
            confirmation_id=result.confirmation_id,
            error=result.error
        )
        
    except Exception as e:
        logger.error(f"Task confirmation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task confirmation failed: {str(e)}"
        )


@app.post("/suggest_tasks", response_model=List[TaskSuggestion])
async def suggest_tasks(request: TaskSuggestionRequest):
    """
    Get task suggestions for a user query.
    
    Args:
        request: Task suggestion request
        
    Returns:
        List of task suggestions
        
    Raises:
        HTTPException: If suggestion generation fails
    """
    try:
        suggestions = await orchestrator.get_task_suggestions(request.query)
        
        result = [
            TaskSuggestion(
                task_type=suggestion["task_type"],
                confidence=suggestion["confidence"],
                description=suggestion["description"],
                matched_keywords=suggestion["matched_keywords"],
                extracted_params=suggestion["extracted_params"]
            )
            for suggestion in suggestions
        ]
        
        logger.info(f"Generated {len(result)} task suggestions for query: '{request.query}'")
        
        return result
        
    except Exception as e:
        logger.error(f"Task suggestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task suggestion failed: {str(e)}"
        )


@app.get("/supported_tasks", response_model=List[SupportedTask])
async def get_supported_tasks():
    """
    Get list of supported task types.
    
    Returns:
        List of supported tasks
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        supported_tasks = orchestrator.get_supported_tasks()
        
        result = [
            SupportedTask(
                task_type=task["task_type"],
                description=task["description"],
                handler_available=task["handler_available"]
            )
            for task in supported_tasks
        ]
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get supported tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported tasks: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """Get detailed module status information."""
    try:
        system_status = await orchestrator.get_system_status()
        
        return {
            "module": "Proactive Agents",
            "version": "1.0.0",
            "status": "operational",
            "system_status": system_status,
            "endpoints": [
                "/health", "/execute_task", "/classify_and_execute", 
                "/confirm_task", "/suggest_tasks", "/supported_tasks", "/web_fetch", "/status"
            ],
            "features": {
                "task_classification": True,
                "ai_enhancement": True,
                "human_confirmation": True,
                "session_management": True,
                "module_integration": True
            },
            "configuration": {
                "module_a_url": module_a_url,
                "module_b_url": module_b_url
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "module": "Proactive Agents",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }


class WebFetchRequest(BaseModel):
    """Request model for web fetch task."""
    query: str = Field(..., description="Search query for web content")
    max_sources: int = Field(3, description="Maximum number of sources to fetch")
    auto_upload: bool = Field(True, description="Automatically upload to knowledge base")


class WebFetchResponse(BaseModel):
    """Response model for web fetch task."""
    success: bool = Field(..., description="Whether fetch was successful")
    query: str = Field(..., description="Original search query")
    sources_found: int = Field(..., description="Number of sources found")
    sources_uploaded: int = Field(..., description="Number of sources uploaded")
    sources: List[Dict[str, Any]] = Field(..., description="Source details")
    errors: List[str] = Field(..., description="Any errors encountered")
    execution_time: float = Field(..., description="Execution time in seconds")


@app.post("/web_fetch", response_model=WebFetchResponse)
async def web_fetch(request: WebFetchRequest):
    """
    Fetch relevant documentation from the web and add to knowledge base.
    
    Args:
        request: Web fetch request with query and parameters
        
    Returns:
        WebFetchResponse with fetch results
        
    Raises:
        HTTPException: If web fetch fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting web fetch for query: {request.query}")
        
        # Execute web fetch
        result = await web_fetch_agent.execute_web_fetch(
            query=request.query,
            max_sources=request.max_sources
        )
        
        execution_time = time.time() - start_time
        
        return WebFetchResponse(
            success=len(result.get("errors", [])) == 0,
            query=result["query"],
            sources_found=result["sources_found"],
            sources_uploaded=result["sources_uploaded"],
            sources=result["sources"],
            errors=result["errors"],
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Web fetch failed: {e}")
        
        return WebFetchResponse(
            success=False,
            query=request.query,
            sources_found=0,
            sources_uploaded=0,
            sources=[],
            errors=[str(e)],
            execution_time=execution_time
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await orchestrator.cleanup()
        logger.info("Module C shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown cleanup failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)