"""
Session Integration for Module A Core.
Implements Grok's session management recommendations.
"""

import logging
from typing import Optional, Dict, Any
from .session_manager import get_session_manager

logger = logging.getLogger(__name__)

class SessionIntegration:
    """Handles session integration for query processing."""
    
    def __init__(self):
        self.session_manager = get_session_manager()
    
    def handle_session_context(self, request, processed_query: str) -> tuple[str, str]:
        """
        Handle session context for a query request.
        
        Args:
            request: The request object (should have session_id attribute)
            processed_query: The preprocessed query
            
        Returns:
            tuple: (enhanced_query, session_id)
        """
        # GROK'S SESSION MANAGEMENT: Handle session context
        session_id = getattr(request, 'session_id', None)
        if session_id:
            # Get existing session or create new one
            session = self.session_manager.get_session(session_id)
            if not session:
                session_id = self.session_manager.create_session()
                logger.info(f"Created new session for invalid session_id: {session_id}")
        else:
            # Create new session if none provided
            session_id = self.session_manager.create_session()
            logger.info(f"Created new session: {session_id}")
        
        # GROK'S CONTEXT INTEGRATION: Enhance query with session context
        enhanced_query = processed_query
        if session_id:
            enhanced_query = self.session_manager.enhance_query_with_context(session_id, processed_query)
            if enhanced_query != processed_query:
                logger.info(f"Enhanced query with session context for session {session_id}")
        
        return enhanced_query, session_id
    
    def record_conversation_turn(
        self,
        session_id: str,
        original_query: str,
        response: str,
        model_used: str,
        complexity_score: float,
        routing_decision: str
    ) -> bool:
        """
        Record a conversation turn in the session.
        
        Args:
            session_id: Session identifier
            original_query: Original user query (not enhanced)
            response: System response
            model_used: Which model was used
            complexity_score: Query complexity score
            routing_decision: Routing decision reasoning
            
        Returns:
            bool: Success status
        """
        return self.session_manager.add_conversation_turn(
            session_id=session_id,
            query=original_query,
            response=response,
            model_used=model_used,
            complexity_score=complexity_score,
            routing_decision=routing_decision
        )
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics."""
        return self.session_manager.get_session_stats(session_id)


# Global session integration instance
session_integration = SessionIntegration()


def get_session_integration() -> SessionIntegration:
    """Get the global session integration instance."""
    return session_integration