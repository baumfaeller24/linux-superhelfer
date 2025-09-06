"""
Module D: Safe Execution & Control
Port: 8004

Provides safe command execution with preview, validation, and audit trail.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
import uvicorn

from models import CommandRequest, CommandResponse
from safe_executor import SafeExecutor
from execution_logger import execution_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Module D: Safe Execution & Control", version="1.0.0")

# Global executor instance
safe_executor = SafeExecutor()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get module status and statistics."""
    return {
        "module": "Safe Execution & Control",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "command_parsing": True,
            "dry_run_simulation": True,
            "safety_validation": True,
            "execution_logging": True
        }
    }

@app.post("/safe_execute", response_model=CommandResponse)
async def safe_execute(request: CommandRequest):
    """Execute command safely with preview and validation."""
    try:
        logger.info(f"Received execution request: {request.command} (dry_run: {request.dry_run})")
        
        response = await safe_executor.execute_command(request)
        
        logger.info(f"Execution completed: success={response.success}, executed={response.executed}")
        return response
        
    except Exception as e:
        logger.error(f"Safe execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.post("/preview", response_model=CommandResponse)
async def preview_command(request: CommandRequest):
    """Preview command effects without execution."""
    try:
        # Force dry run for preview
        request.dry_run = True
        return await safe_execute(request)
        
    except Exception as e:
        logger.error(f"Command preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@app.get("/logs/history")
async def get_execution_history(limit: int = 100, user: str = None, command: str = None):
    """Get execution history with optional filtering."""
    try:
        history = execution_logger.get_execution_history(
            limit=limit, 
            user=user, 
            command_pattern=command
        )
        return {
            "success": True,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get execution history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/logs/security")
async def get_security_events(limit: int = 50):
    """Get recent security events."""
    try:
        events = execution_logger.get_security_events(limit=limit)
        return {
            "success": True,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get security events: {str(e)}")

@app.get("/logs/statistics")
async def get_execution_statistics():
    """Get execution statistics and metrics."""
    try:
        stats = execution_logger.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)