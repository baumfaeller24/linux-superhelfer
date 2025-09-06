"""
Chat Logger for Linux Superhelfer
Detailed logging of all chat interactions, model responses, and system events.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ChatLogger:
    """Comprehensive chat interaction logger."""
    
    def __init__(self, log_file: str = "chat_interactions.log"):
        self.log_file = Path(log_file)
        
        # Setup detailed logging
        self.logger = logging.getLogger("chat_logger")
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler with detailed format
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        
        # Detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Remove existing handlers and add our handler
        self.logger.handlers.clear()
        self.logger.addHandler(handler)
        
        # Log startup
        self.logger.info("=" * 80)
        self.logger.info("CHAT LOGGER INITIALIZED - Linux Superhelfer")
        self.logger.info("=" * 80)
    
    def log_user_query(self, query: str, session_id: str = None):
        """Log user input query."""
        self.logger.info(f"USER_QUERY | Session: {session_id or 'unknown'} | Query: '{query}'")
    
    def log_module_request(self, module: str, endpoint: str, payload: Dict[str, Any]):
        """Log request to backend module."""
        self.logger.debug(f"MODULE_REQUEST | Module: {module} | Endpoint: {endpoint} | Payload: {json.dumps(payload, ensure_ascii=False)}")
    
    def log_module_response(self, module: str, success: bool, response_data: Dict[str, Any], processing_time: float):
        """Log response from backend module."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"MODULE_RESPONSE | Module: {module} | Status: {status} | Time: {processing_time:.3f}s")
        
        if success and response_data:
            # Log key response metrics
            confidence = response_data.get('confidence', 'N/A')
            response_length = len(str(response_data.get('response', '')))
            self.logger.info(f"RESPONSE_METRICS | Confidence: {confidence} | Length: {response_length} chars")
            
            # Log full response (truncated for readability)
            response_text = str(response_data.get('response', ''))[:200]
            self.logger.debug(f"RESPONSE_TEXT | {response_text}...")
        else:
            error = response_data.get('error', 'Unknown error')
            self.logger.error(f"MODULE_ERROR | Module: {module} | Error: {error}")
    
    def log_ollama_interaction(self, model: str, prompt: str, response: str, processing_time: float, tokens: Dict[str, int] = None):
        """Log Ollama model interaction."""
        self.logger.info(f"OLLAMA_INTERACTION | Model: {model} | Time: {processing_time:.3f}s")
        self.logger.debug(f"OLLAMA_PROMPT | {prompt[:150]}...")
        self.logger.debug(f"OLLAMA_RESPONSE | {response[:200]}...")
        
        if tokens:
            self.logger.info(f"OLLAMA_TOKENS | Prompt: {tokens.get('prompt', 0)} | Response: {tokens.get('response', 0)}")
    
    def log_rag_search(self, query: str, results_count: int, sources: list, processing_time: float):
        """Log RAG knowledge search."""
        self.logger.info(f"RAG_SEARCH | Query: '{query}' | Results: {results_count} | Time: {processing_time:.3f}s")
        if sources:
            self.logger.debug(f"RAG_SOURCES | {', '.join(sources[:3])}...")
    
    def log_escalation(self, reason: str, confidence: float, escalated_to: str):
        """Log query escalation to external services."""
        self.logger.info(f"ESCALATION | Reason: {reason} | Confidence: {confidence:.3f} | Target: {escalated_to}")
    
    def log_safety_check(self, command: str, is_safe: bool, warnings: list):
        """Log safety validation for commands."""
        status = "SAFE" if is_safe else "BLOCKED"
        self.logger.info(f"SAFETY_CHECK | Command: '{command}' | Status: {status}")
        if warnings:
            self.logger.warning(f"SAFETY_WARNINGS | {', '.join(warnings)}")
    
    def log_session_event(self, event: str, session_id: str, details: Dict[str, Any] = None):
        """Log session management events."""
        self.logger.info(f"SESSION_EVENT | Event: {event} | Session: {session_id}")
        if details:
            self.logger.debug(f"SESSION_DETAILS | {json.dumps(details, ensure_ascii=False)}")
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log system errors."""
        self.logger.error(f"SYSTEM_ERROR | Type: {error_type} | Message: {error_message}")
        if context:
            self.logger.error(f"ERROR_CONTEXT | {json.dumps(context, ensure_ascii=False)}")
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics."""
        self.logger.info(f"PERFORMANCE | {json.dumps(metrics, ensure_ascii=False)}")
    
    def log_health_check(self, module: str, status: bool, response_time: float):
        """Log health check results."""
        status_text = "HEALTHY" if status else "UNHEALTHY"
        self.logger.info(f"HEALTH_CHECK | Module: {module} | Status: {status_text} | Time: {response_time:.3f}s")


# Global logger instance
chat_logger = ChatLogger()