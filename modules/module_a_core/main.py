"""
Module A: Core Intelligence Engine
Provides local AI inference using Ollama with Llama 3.1 8B model.
"""

import time
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.models import HealthStatus, Query, Response, ErrorResponse
from shared.config import ConfigManager, get_module_url
from .ollama_client import OllamaClient, QueryProcessor
from .confidence import ConfidenceCalculator
from .knowledge_client import KnowledgeClient, ContextIntegrator
from .model_router import ModelRouter, ModelType
from .session_manager import get_session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chat interaction logger - save in project root
import os
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
chat_log_path = os.path.join(project_root, 'chat_interactions.log')
chat_logger = logging.getLogger('chat_interactions')
chat_handler = logging.FileHandler(chat_log_path)
chat_handler.setFormatter(logging.Formatter('%(message)s'))
chat_logger.addHandler(chat_handler)
chat_logger.setLevel(logging.INFO)
chat_logger.propagate = False

app = FastAPI(
    title="Core Intelligence Engine", 
    version="1.0.0",
    description="Local AI inference using Ollama with Llama 3.1 8B model"
)

# Initialize components
config_manager = ConfigManager()
config = config_manager.load_config()
ollama_config = config.ollama

# Initialize intelligent model router
model_router = ModelRouter(
    ollama_host=ollama_config.get('host', 'localhost'),
    ollama_port=ollama_config.get('port', 11434)
)

# Initialize session manager (Grok's session management implementation)
session_manager = get_session_manager()

# Legacy components for backward compatibility
ollama_client = OllamaClient(
    host=ollama_config.get('host', 'localhost'),
    port=ollama_config.get('port', 11434),
    model=ollama_config.get('model', 'llama3.1:8b')
)
query_processor = QueryProcessor()
confidence_calculator = ConfidenceCalculator()

# Initialize knowledge integration components
knowledge_client = KnowledgeClient(
    base_url=get_module_url('rag', config),
    timeout=5.0
)
context_integrator = ContextIntegrator(knowledge_client)


class InferRequest(BaseModel):
    """Request model for inference endpoint."""
    query: str
    context: Optional[str] = None
    enable_context_search: Optional[bool] = True
    context_threshold: Optional[float] = 0.6
    session_id: Optional[str] = None  # Session ID for conversation context tracking


class InferResponse(BaseModel):
    """Response model for inference endpoint."""
    model_config = {"protected_namespaces": ()}
    
    response: str
    confidence: float
    status: str
    processing_time: float
    model_used: str
    context_used: bool = False
    sources: Optional[list] = None
    routing_info: Optional[dict] = None
    vram_usage_percent: Optional[float] = None
    session_id: str  # Session ID for conversation tracking
    context_turns_used: int = 0  # Number of previous conversation turns used in context
    context_enhanced: bool = False  # Whether query was enhanced with conversation context


class ContextInferRequest(BaseModel):
    """Request model for context-enhanced inference endpoint."""
    query: str
    top_k: Optional[int] = 3
    threshold: Optional[float] = 0.6
    max_context_length: Optional[int] = 2000
    session_id: Optional[str] = None


class ContextInferResponse(BaseModel):
    """Response model for context-enhanced inference endpoint."""
    model_config = {"protected_namespaces": ()}
    
    response: str
    confidence: float
    status: str
    processing_time: float
    model_used: str
    context_used: bool
    sources: list
    context_snippets_count: int
    attribution: Optional[str] = None
    session_id: str
    context_turns_used: int = 0
    context_enhanced: bool = False


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint with Ollama availability."""
    try:
        ollama_available = await ollama_client.is_available()
        if ollama_available:
            return HealthStatus(status="ok", version="1.0.0")
        else:
            return HealthStatus(status="degraded - Ollama unavailable", version="1.0.0")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(status="error", version="1.0.0")


@app.post("/infer", response_model=InferResponse)
async def infer(request: InferRequest):
    """
    Process query using intelligent model routing with Qwen3-Coder integration.
    
    Args:
        request: InferRequest with query and context options
        
    Returns:
        InferResponse with generated response, confidence score, and routing metadata
        
    Raises:
        HTTPException: If query validation fails or all models are unavailable
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log query start
    chat_logger.info(f"\n[{timestamp}] QUERY START (Intelligent Routing)")
    chat_logger.info(f"User Query: \"{request.query}\"")
    chat_logger.info(f"Module: A (Core Intelligence with Model Router)")
    chat_logger.info(f"Context Search Enabled: {request.enable_context_search}")
    
    try:
        # Validate query
        if not query_processor.validate_query(request.query):
            raise HTTPException(
                status_code=400,
                detail="Invalid query: must be 3-2000 characters"
            )
        
        # Preprocess query
        processed_query = query_processor.preprocess_query(request.query)
        
        # Session management - handle session ID
        current_session_id = request.session_id
        if not current_session_id:
            # Create new session if none provided
            current_session_id = session_manager.create_session()
            logger.info(f"Created new session: {current_session_id}")
        else:
            # Verify existing session or create if not found
            session = session_manager.get_session(current_session_id)
            if not session:
                current_session_id = session_manager.create_session()
                logger.info(f"Session {request.session_id} not found, created new: {current_session_id}")
        
        # Initialize response tracking
        context_used = False
        sources = []
        final_query = processed_query
        context_turns_used = 0
        context_enhanced = False
        
        # Try to enhance with session context first (before RAG context)
        try:
            session_context = session_manager.get_context_for_query(current_session_id, processed_query)
            if session_context:
                # Enhance query with conversation context
                final_query = session_manager.enhance_query_with_context(current_session_id, processed_query)
                context_enhanced = True
                # Count conversation turns used
                session = session_manager.get_session(current_session_id)
                if session:
                    context_turns_used = min(len(session.turns), 5)  # Max 5 turns as per design
                logger.info(f"Enhanced query with session context from {context_turns_used} conversation turns")
        except Exception as e:
            logger.warning(f"Session context enhancement failed, continuing: {e}")
        
        # Enhance with context if enabled and no explicit context provided
        if request.enable_context_search and not request.context:
            try:
                context_config = {
                    "top_k": 3,
                    "threshold": request.context_threshold,
                    "max_context_length": 2000,
                    "enable_context": True
                }
                
                enhancement_result = await context_integrator.enhance_query_with_context(
                    processed_query, 
                    context_config
                )
                
                if enhancement_result["context_used"]:
                    final_query = enhancement_result["enhanced_query"]
                    sources = enhancement_result["sources"]
                    context_used = True
                    logger.info(f"Enhanced query with context from {len(sources)} sources")
                
            except Exception as e:
                logger.warning(f"Context enhancement failed, continuing without context: {e}")
        
        # Use explicit context if provided
        elif request.context:
            final_query = f"{processed_query}\n\nContext: {request.context}"
            context_used = True
        
        # Generate response using intelligent model routing
        generation_result = await model_router.generate_response(
            final_query, 
            context=None  # Context already integrated into query
        )
        
        processing_time = time.time() - start_time
        
        # Check if generation was successful
        if not generation_result.get('success', True):
            raise HTTPException(
                status_code=503,
                detail=generation_result.get('response', 'Model generation failed')
            )
        
        # Calculate confidence score
        confidence = confidence_calculator.calculate_confidence(
            response=generation_result['response'],
            query=processed_query,
            processing_time=processing_time,
            metadata=generation_result
        )
        
        # Determine status based on confidence
        if confidence >= 0.8:
            status = "high_confidence"
        elif confidence >= 0.5:
            status = "medium_confidence"
        else:
            status = "low_confidence_escalate"
        
        # Get VRAM usage for monitoring
        vram_usage = model_router.vram_monitor.get_usage_percentage()
        
        # Prepare routing info for response
        routing_info = None
        if 'routing_info' in generation_result:
            routing_result = generation_result['routing_info']
            routing_info = {
                "selected_model": routing_result.selected_model.value,
                "reasoning": routing_result.reasoning,
                "complexity_score": routing_result.analysis.complexity_score,
                "detected_keywords": routing_result.analysis.detected_keywords[:5],  # Limit for response size
                "vram_check_passed": routing_result.vram_check_passed,
                "user_confirmed": routing_result.user_confirmed
            }
        
        # Log successful response
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESPONSE")
        chat_logger.info(f"Model Response: \"{generation_result['response'][:200]}{'...' if len(generation_result['response']) > 200 else ''}\"")
        chat_logger.info(f"Model Used: {generation_result['model_used']}")
        chat_logger.info(f"Confidence Score: {confidence:.3f}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Context Used: {context_used or context_enhanced}")
        if context_enhanced:
            chat_logger.info(f"Session Context: {context_turns_used} conversation turns used")
        chat_logger.info(f"VRAM Usage: {vram_usage:.1%}")
        if routing_info:
            chat_logger.info(f"Routing: {routing_info['selected_model']} model, complexity {routing_info['complexity_score']:.2f}")
        chat_logger.info(f"Success: true")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.info(f"Query processed with intelligent routing: model={generation_result['model_used']}, confidence={confidence:.3f}, time={processing_time:.2f}s")
        
        # Log conversation turn to session
        try:
            routing_decision = routing_info.get('reasoning', 'No routing info') if routing_info else 'No routing info'
            complexity_score = routing_info.get('complexity_score', 0.0) if routing_info else 0.0
            
            session_manager.add_conversation_turn(
                session_id=current_session_id,
                query=processed_query,
                response=generation_result['response'],
                model_used=generation_result['model_used'],
                complexity_score=complexity_score,
                routing_decision=routing_decision
            )
            logger.info(f"Added conversation turn to session {current_session_id}")
        except Exception as e:
            logger.warning(f"Failed to log conversation turn to session: {e}")
        
        return InferResponse(
            response=generation_result['response'],
            confidence=confidence,
            status=status,
            processing_time=processing_time,
            model_used=generation_result['model_used'],
            context_used=context_used,
            sources=sources if sources else None,
            routing_info=routing_info,
            vram_usage_percent=vram_usage,
            session_id=current_session_id,
            context_turns_used=context_turns_used,
            context_enhanced=context_enhanced
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log error
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR")
        chat_logger.info(f"Error: {str(e)}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Success: false")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.error(f"Intelligent inference failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/infer_single_model", response_model=InferResponse)
async def infer_single_model(request: InferRequest):
    """
    Single model inference endpoint using fixed model (for backward compatibility).
    
    Args:
        request: InferRequest with query and context options
        
    Returns:
        InferResponse with generated response, confidence score, and metadata
        
    Raises:
        HTTPException: If query validation fails or Ollama is unavailable
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log query start
    chat_logger.info(f"\n[{timestamp}] QUERY START")
    chat_logger.info(f"User Query: \"{request.query}\"")
    chat_logger.info(f"Module: A (Core Intelligence)")
    chat_logger.info(f"Context Search Enabled: {request.enable_context_search}")
    
    try:
        # Validate query
        if not query_processor.validate_query(request.query):
            raise HTTPException(
                status_code=400,
                detail="Invalid query: must be 3-2000 characters"
            )
        
        # Preprocess query
        processed_query = query_processor.preprocess_query(request.query)
        
        # Initialize response tracking
        context_used = False
        sources = []
        final_query = processed_query
        
        # Enhance with context if enabled and no explicit context provided
        if request.enable_context_search and not request.context:
            try:
                context_config = {
                    "top_k": 3,
                    "threshold": request.context_threshold,
                    "max_context_length": 2000,
                    "enable_context": True
                }
                
                enhancement_result = await context_integrator.enhance_query_with_context(
                    processed_query, 
                    context_config
                )
                
                if enhancement_result["context_used"]:
                    final_query = enhancement_result["enhanced_query"]
                    sources = enhancement_result["sources"]
                    context_used = True
                    logger.info(f"Enhanced query with context from {len(sources)} sources")
                
            except Exception as e:
                logger.warning(f"Context enhancement failed, continuing without context: {e}")
        
        # Use explicit context if provided
        elif request.context:
            final_query = f"{processed_query}\n\nContext: {request.context}"
            context_used = True
        
        # Check Ollama availability
        if not await ollama_client.is_available():
            raise HTTPException(
                status_code=503,
                detail="LLM service unavailable - Ollama not accessible"
            )
        
        # Generate response
        generation_result = await ollama_client.generate_response(
            final_query, 
            None  # Context already integrated into query
        )
        
        processing_time = time.time() - start_time
        
        # Calculate confidence score
        confidence = confidence_calculator.calculate_confidence(
            response=generation_result['response'],
            query=processed_query,
            processing_time=processing_time,
            metadata=generation_result
        )
        
        # Determine status based on confidence
        if confidence >= 0.8:
            status = "high_confidence"
        elif confidence >= 0.5:
            status = "medium_confidence"
        else:
            status = "low_confidence_escalate"
        
        # Log successful response
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESPONSE")
        chat_logger.info(f"Model Response: \"{generation_result['response'][:200]}{'...' if len(generation_result['response']) > 200 else ''}\"")
        chat_logger.info(f"Confidence Score: {confidence:.3f}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Context Used: {context_used}")
        chat_logger.info(f"Success: true")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.info(f"Query processed: confidence={confidence:.3f}, time={processing_time:.2f}s, context_used={context_used}")
        
        return InferResponse(
            response=generation_result['response'],
            confidence=confidence,
            status=status,
            processing_time=processing_time,
            model_used=generation_result['model_used'],
            context_used=context_used,
            sources=sources if sources else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log error
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR")
        chat_logger.info(f"Error: {str(e)}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Success: false")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.error(f"Inference failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/infer_with_context", response_model=ContextInferResponse)
async def infer_with_context(request: ContextInferRequest):
    """
    Process query with explicit context enhancement from knowledge base.
    
    Args:
        request: ContextInferRequest with query and context search parameters
        
    Returns:
        ContextInferResponse with enhanced response and context attribution
        
    Raises:
        HTTPException: If query validation fails or Ollama is unavailable
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log query start
    chat_logger.info(f"\n[{timestamp}] QUERY START")
    chat_logger.info(f"User Query: \"{request.query}\"")
    chat_logger.info(f"Module: A (Core Intelligence)")
    chat_logger.info(f"Endpoint: /infer_with_context")
    
    try:
        # Validate query
        if not query_processor.validate_query(request.query):
            raise HTTPException(
                status_code=400,
                detail="Invalid query: must be 3-2000 characters"
            )
        
        # Preprocess query
        processed_query = query_processor.preprocess_query(request.query)
        
        # Enhance with context
        context_config = {
            "top_k": request.top_k,
            "threshold": request.threshold,
            "max_context_length": request.max_context_length,
            "enable_context": True
        }
        
        enhancement_result = await context_integrator.enhance_query_with_context(
            processed_query, 
            context_config
        )
        
        final_query = enhancement_result["enhanced_query"]
        sources = enhancement_result["sources"]
        context_used = enhancement_result["context_used"]
        snippets_count = len(enhancement_result["context_snippets"])
        
        # Check Ollama availability
        if not await ollama_client.is_available():
            raise HTTPException(
                status_code=503,
                detail="LLM service unavailable - Ollama not accessible"
            )
        
        # Generate response
        generation_result = await ollama_client.generate_response(
            final_query, 
            None  # Context already integrated into query
        )
        
        processing_time = time.time() - start_time
        
        # Calculate confidence score
        confidence = confidence_calculator.calculate_confidence(
            response=generation_result['response'],
            query=processed_query,
            processing_time=processing_time,
            metadata=generation_result
        )
        
        # Determine status based on confidence
        if confidence >= 0.8:
            status = "high_confidence"
        elif confidence >= 0.5:
            status = "medium_confidence"
        else:
            status = "low_confidence_escalate"
        
        # Create attribution
        attribution = None
        if context_used and sources:
            attribution_info = context_integrator.extract_response_attribution(
                generation_result['response'], 
                sources
            )
            attribution = attribution_info.get("attribution_note")
        
        # Log successful response
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESPONSE")
        chat_logger.info(f"Model Response: \"{generation_result['response'][:200]}{'...' if len(generation_result['response']) > 200 else ''}\"")
        chat_logger.info(f"Confidence Score: {confidence:.3f}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Context Used: {context_used}")
        chat_logger.info(f"Context Snippets: {snippets_count}")
        chat_logger.info(f"Success: true")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.info(f"Context-enhanced query processed: confidence={confidence:.3f}, time={processing_time:.2f}s, snippets={snippets_count}")
        
        return ContextInferResponse(
            response=generation_result['response'],
            confidence=confidence,
            status=status,
            processing_time=processing_time,
            model_used=generation_result['model_used'],
            context_used=context_used,
            sources=sources,
            context_snippets_count=snippets_count,
            attribution=attribution
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log error
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR")
        chat_logger.info(f"Error: {str(e)}")
        chat_logger.info(f"Processing Time: {processing_time:.2f}s")
        chat_logger.info(f"Success: false")
        chat_logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUERY END")
        chat_logger.info("=" * 80)
        
        logger.error(f"Context-enhanced inference failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/router_status")
async def get_router_status():
    """Get detailed model router status information."""
    try:
        router_health = await model_router.health_check()
        model_info = model_router.get_current_model_info()
        
        return {
            "module": "Core Intelligence Engine with Model Router",
            "version": "2.0.0",
            "router_health": router_health,
            "current_model_info": model_info,
            "features": {
                "intelligent_routing": True,
                "vram_monitoring": model_router.vram_monitor.pynvml_available,
                "qwen3_coder_integration": True,
                "context_enhancement": True
            }
        }
    except Exception as e:
        logger.error(f"Router status check failed: {e}")
        return {
            "module": "Core Intelligence Engine with Model Router",
            "version": "2.0.0",
            "status": "error",
            "error": str(e)
        }


@app.get("/status")
async def get_status():
    """Get detailed module status information."""
    try:
        ollama_available = await ollama_client.is_available()
        knowledge_available = await knowledge_client.health_check()
        
        overall_status = "operational"
        if not ollama_available:
            overall_status = "degraded - Ollama unavailable"
        elif not knowledge_available:
            overall_status = "degraded - Knowledge base unavailable"
        
        return {
            "module": "Core Intelligence Engine",
            "version": "1.0.0",
            "status": overall_status,
            "ollama": {
                "available": ollama_available,
                "host": ollama_client.host,
                "port": ollama_client.port,
                "model": ollama_client.model
            },
            "knowledge_base": {
                "available": knowledge_available,
                "base_url": knowledge_client.base_url,
                "timeout": knowledge_client.timeout
            },
            "endpoints": ["/health", "/infer", "/infer_single_model", "/infer_with_context", "/status", "/router_status"],
            "features": {
                "context_enhancement": True,
                "automatic_context_search": True,
                "confidence_threshold": config.features.get('confidence_threshold', 0.5)
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "module": "Core Intelligence Engine",
            "version": "1.0.0", 
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)