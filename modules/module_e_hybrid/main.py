"""
Module E: Hybrid Intelligence Gateway
External API integration with caching and fallback handling.
"""

import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local models (shared not available)
from pydantic import BaseModel
from typing import Optional, Dict, Any

class HealthStatus(BaseModel):
    status: str
    details: Optional[Dict[str, Any]] = None
from external_api_client import external_api_client, ExternalResponse
from cache_manager import cache_manager
from confidence_evaluator import confidence_evaluator, EscalationDecision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hybrid Intelligence Gateway", 
    version="1.0.0",
    description="External AI integration with intelligent escalation and caching"
)


# Request/Response Models
class EscalateRequest(BaseModel):
    """Request model for escalation."""
    query: str = Field(..., description="Query to escalate")
    confidence: float = Field(..., description="Confidence score from Module A")
    context: Optional[str] = Field(None, description="Optional context information")
    response: Optional[str] = Field(None, description="Original response from Module A")


class EscalateResponse(BaseModel):
    """Response model for escalation."""
    success: bool
    escalated: bool
    external_response: Optional[str] = None
    source: str
    confidence: float
    processing_time: float
    cached: bool = False
    escalation_reason: Optional[str] = None
    error: Optional[str] = None


class ConfidenceEvaluationRequest(BaseModel):
    """Request model for confidence evaluation."""
    confidence: float = Field(..., description="Confidence score to evaluate")
    query: str = Field(..., description="Original query")
    context: Optional[str] = Field(None, description="Optional context")
    response: Optional[str] = Field(None, description="Original response")


class ConfidenceEvaluationResponse(BaseModel):
    """Response model for confidence evaluation."""
    should_escalate: bool
    reason: str
    confidence_score: float
    threshold_used: float
    escalation_priority: str


# API Endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint with external service status."""
    try:
        # Check internet connectivity
        internet_available = await external_api_client.check_internet_connectivity()
        
        # Check Module B connectivity for caching
        cache_available = await cache_manager.check_module_b_health()
        
        return HealthStatus(
            status="ok",
            details={
                "internet_connectivity": internet_available,
                "cache_available": cache_available,
                "external_apis": {
                    "grok": "configured" if not external_api_client.mock_mode else "mock_mode",
                    "openai": "not_implemented",
                    "anthropic": "not_implemented"
                }
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(status="error", details={"error": str(e)})


@app.get("/status")
async def get_status():
    """Get detailed module status and statistics."""
    try:
        # Get escalation statistics
        escalation_stats = confidence_evaluator.get_statistics()
        
        # Get cache statistics
        cache_stats = await cache_manager.get_cache_statistics()
        
        # Check external service availability
        internet_available = await external_api_client.check_internet_connectivity()
        cache_available = await cache_manager.check_module_b_health()
        
        return {
            "module": "Hybrid Intelligence Gateway",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "internet_connectivity": internet_available,
                "cache_service": cache_available,
                "external_apis": {
                    "grok": "available" if not external_api_client.mock_mode else "mock_mode",
                    "openai": "not_implemented",
                    "anthropic": "not_implemented"
                }
            },
            "statistics": {
                "escalation": escalation_stats,
                "cache": cache_stats
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.post("/escalate", response_model=EscalateResponse)
async def escalate_query(request: EscalateRequest):
    """
    Escalate query to external AI services with intelligent caching.
    
    This endpoint evaluates confidence scores and escalates low-confidence
    queries to external AI services, with automatic caching of responses.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Escalation request: confidence={request.confidence:.3f}, query='{request.query[:50]}...'")
        
        # Evaluate confidence and decide on escalation
        escalation_decision = confidence_evaluator.evaluate_confidence(
            confidence_score=request.confidence,
            query=request.query,
            context=request.context,
            response=request.response
        )
        
        # If escalation is not needed, return original response
        if not escalation_decision.should_escalate:
            processing_time = time.time() - start_time
            
            return EscalateResponse(
                success=True,
                escalated=False,
                external_response=request.response,
                source="local",
                confidence=request.confidence,
                processing_time=processing_time,
                cached=False,
                escalation_reason=escalation_decision.reason
            )
        
        # Check cache first
        cached_response = await cache_manager.get_cached_response(request.query, request.context)
        
        if cached_response:
            processing_time = time.time() - start_time
            
            logger.info(f"Returning cached response for query: {request.query[:50]}...")
            
            return EscalateResponse(
                success=cached_response.success,
                escalated=True,
                external_response=cached_response.response,
                source=cached_response.source,
                confidence=cached_response.confidence,
                processing_time=processing_time,
                cached=True,
                escalation_reason=escalation_decision.reason,
                error=cached_response.error
            )
        
        # Check internet connectivity
        if not await external_api_client.check_internet_connectivity():
            processing_time = time.time() - start_time
            
            logger.warning("No internet connectivity - cannot escalate to external APIs")
            
            return EscalateResponse(
                success=False,
                escalated=False,
                external_response=request.response,  # Fallback to original
                source="local_fallback",
                confidence=request.confidence,
                processing_time=processing_time,
                cached=False,
                escalation_reason="No internet connectivity",
                error="External APIs unavailable - no internet connection"
            )
        
        # Escalate to external API
        logger.info(f"Escalating to external API: {escalation_decision.reason}")
        
        external_response = await external_api_client.query_with_fallback(
            query=request.query,
            context=request.context
        )
        
        processing_time = time.time() - start_time
        
        # Cache the response if successful
        if external_response.success:
            cache_success = await cache_manager.store_response(
                query=request.query,
                response=external_response,
                context=request.context
            )
            
            if cache_success:
                logger.info("External response cached successfully")
            else:
                logger.warning("Failed to cache external response")
            
            # Update escalation success statistics
            confidence_evaluator.update_escalation_success(True)
        else:
            # Update escalation failure statistics
            confidence_evaluator.update_escalation_success(False)
        
        return EscalateResponse(
            success=external_response.success,
            escalated=True,
            external_response=external_response.response,
            source=external_response.source,
            confidence=external_response.confidence,
            processing_time=processing_time,
            cached=False,
            escalation_reason=escalation_decision.reason,
            error=external_response.error
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Escalation failed: {str(e)}"
        logger.error(error_msg)
        
        return EscalateResponse(
            success=False,
            escalated=False,
            external_response=request.response,  # Fallback to original
            source="error_fallback",
            confidence=request.confidence,
            processing_time=processing_time,
            cached=False,
            escalation_reason="Internal error",
            error=error_msg
        )


@app.post("/evaluate_confidence", response_model=ConfidenceEvaluationResponse)
async def evaluate_confidence_endpoint(request: ConfidenceEvaluationRequest):
    """
    Evaluate confidence score and provide escalation recommendation.
    
    This endpoint allows other modules to check if a query should be
    escalated without actually performing the escalation.
    """
    try:
        escalation_decision = confidence_evaluator.evaluate_confidence(
            confidence_score=request.confidence,
            query=request.query,
            context=request.context,
            response=request.response
        )
        
        return ConfidenceEvaluationResponse(
            should_escalate=escalation_decision.should_escalate,
            reason=escalation_decision.reason,
            confidence_score=escalation_decision.confidence_score,
            threshold_used=escalation_decision.threshold_used,
            escalation_priority=escalation_decision.escalation_priority
        )
        
    except Exception as e:
        logger.error(f"Confidence evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Confidence evaluation failed: {str(e)}")


@app.get("/cache/statistics")
async def get_cache_statistics():
    """Get cache usage statistics."""
    try:
        stats = await cache_manager.get_cache_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@app.post("/cache/clear_expired")
async def clear_expired_cache():
    """Clear expired cache entries."""
    try:
        cleared_count = await cache_manager.clear_expired_cache()
        return {
            "success": True,
            "message": f"Found {cleared_count} expired cache entries",
            "cleared_count": cleared_count
        }
    except Exception as e:
        logger.error(f"Failed to clear expired cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear expired cache: {str(e)}")


@app.get("/escalation/statistics")
async def get_escalation_statistics():
    """Get escalation statistics and metrics."""
    try:
        stats = confidence_evaluator.get_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get escalation statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get escalation statistics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)