"""
Session Manager for context-aware conversations.
Implements Grok's recommendations for session management and context storage.
"""

import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    timestamp: float
    query: str
    response: str
    model_used: str
    complexity_score: float
    routing_decision: str

@dataclass
class SessionContext:
    """Session context with conversation history."""
    session_id: str
    created_at: float
    last_activity: float
    turns: List[ConversationTurn]
    user_preferences: Dict[str, Any]
    topic_context: List[str]  # Detected topics/domains
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at,
            'last_activity': self.last_activity,
            'turns': [asdict(turn) for turn in self.turns],
            'user_preferences': self.user_preferences,
            'topic_context': self.topic_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Create from dictionary."""
        turns = [ConversationTurn(**turn_data) for turn_data in data.get('turns', [])]
        return cls(
            session_id=data['session_id'],
            created_at=data['created_at'],
            last_activity=data['last_activity'],
            turns=turns,
            user_preferences=data.get('user_preferences', {}),
            topic_context=data.get('topic_context', [])
        )


class SessionManager:
    """
    Manages user sessions and conversation context.
    Implements Grok's recommendations for context-aware routing.
    """
    
    def __init__(self, storage_backend: str = "memory", max_context_length: int = 2000):
        """
        Initialize session manager.
        
        Args:
            storage_backend: "memory", "file", or "redis" (Grok's recommendation)
            max_context_length: Maximum tokens in context (Grok's token limit management)
        """
        self.storage_backend = storage_backend
        self.max_context_length = max_context_length
        self.sessions: Dict[str, SessionContext] = {}
        self.session_timeout = 3600  # 1 hour timeout
        
        logger.info(f"SessionManager initialized with {storage_backend} backend, "
                   f"max_context_length={max_context_length}")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        current_time = time.time()
        
        session = SessionContext(
            session_id=session_id,
            created_at=current_time,
            last_activity=current_time,
            turns=[],
            user_preferences={},
            topic_context=[]
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session by ID, checking for timeout."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        current_time = time.time()
        
        # Check if session has timed out
        if current_time - session.last_activity > self.session_timeout:
            logger.info(f"Session {session_id} timed out, removing")
            del self.sessions[session_id]
            return None
        
        return session
    
    def add_conversation_turn(
        self,
        session_id: str,
        query: str,
        response: str,
        model_used: str,
        complexity_score: float,
        routing_decision: str
    ) -> bool:
        """
        Add a conversation turn to the session.
        
        Args:
            session_id: Session identifier
            query: User query
            response: System response
            model_used: Which model was used
            complexity_score: Query complexity score
            routing_decision: Routing decision reasoning
            
        Returns:
            bool: Success status
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
        
        turn = ConversationTurn(
            timestamp=time.time(),
            query=query,
            response=response,
            model_used=model_used,
            complexity_score=complexity_score,
            routing_decision=routing_decision
        )
        
        session.turns.append(turn)
        session.last_activity = time.time()
        
        # Update topic context based on query content
        self._update_topic_context(session, query)
        
        # Trim context if too long (Grok's token limit management)
        self._trim_context_if_needed(session)
        
        logger.info(f"Added turn to session {session_id}, total turns: {len(session.turns)}")
        return True
    
    def get_context_for_query(self, session_id: str, current_query: str) -> str:
        """
        Get relevant context for current query.
        Implements Grok's context-aware routing recommendations.
        
        Args:
            session_id: Session identifier
            current_query: Current user query
            
        Returns:
            str: Formatted context string
        """
        session = self.get_session(session_id)
        if not session or not session.turns:
            return ""
        
        # Get recent turns (last 3-5 turns for context)
        recent_turns = session.turns[-5:]
        
        # Build context string
        context_parts = []
        
        # Add topic context if relevant
        if session.topic_context:
            context_parts.append(f"Conversation topics: {', '.join(session.topic_context[-3:])}")
        
        # Add recent conversation history
        for turn in recent_turns:
            # Truncate long responses for context
            response_preview = turn.response[:200] + "..." if len(turn.response) > 200 else turn.response
            context_parts.append(f"Previous Q: {turn.query}")
            context_parts.append(f"Previous A: {response_preview}")
        
        context = "\n".join(context_parts)
        
        # Ensure context doesn't exceed token limit
        if len(context.split()) > self.max_context_length:
            # Truncate to fit within limit
            words = context.split()
            context = " ".join(words[:self.max_context_length])
            context += "\n[Context truncated due to length]"
        
        return context
    
    def enhance_query_with_context(self, session_id: str, query: str) -> str:
        """
        Enhance query with relevant context for better routing.
        Implements Grok's context integration recommendations.
        
        Args:
            session_id: Session identifier
            query: Original user query
            
        Returns:
            str: Enhanced query with context
        """
        context = self.get_context_for_query(session_id, query)
        
        if not context:
            return query
        
        # Format enhanced query
        enhanced_query = f"""Context from previous conversation:
{context}

Current query: {query}"""
        
        return enhanced_query
    
    def _update_topic_context(self, session: SessionContext, query: str):
        """Update topic context based on query content."""
        query_lower = query.lower()
        
        # Detect topics/domains
        topics = []
        
        if any(kw in query_lower for kw in ['docker', 'container', 'kubernetes']):
            topics.append('containerization')
        
        if any(kw in query_lower for kw in ['python', 'javascript', 'java', 'code']):
            topics.append('programming')
        
        if any(kw in query_lower for kw in ['bash', 'shell', 'linux', 'command']):
            topics.append('linux_administration')
        
        if any(kw in query_lower for kw in ['git', 'github', 'repository', 'commit']):
            topics.append('version_control')
        
        if any(kw in query_lower for kw in ['network', 'ssh', 'firewall', 'port']):
            topics.append('networking')
        
        if any(kw in query_lower for kw in ['database', 'sql', 'mysql', 'postgres']):
            topics.append('database')
        
        # Add new topics to context
        for topic in topics:
            if topic not in session.topic_context:
                session.topic_context.append(topic)
        
        # Keep only recent topics (last 10)
        session.topic_context = session.topic_context[-10:]
    
    def _trim_context_if_needed(self, session: SessionContext):
        """Trim conversation history if it gets too long."""
        max_turns = 20  # Keep last 20 turns maximum
        
        if len(session.turns) > max_turns:
            # Keep the most recent turns
            session.turns = session.turns[-max_turns:]
            logger.info(f"Trimmed session {session.session_id} to {max_turns} turns")
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics for monitoring."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        model_usage = {}
        total_complexity = 0
        
        for turn in session.turns:
            model = turn.model_used
            model_usage[model] = model_usage.get(model, 0) + 1
            total_complexity += turn.complexity_score
        
        avg_complexity = total_complexity / len(session.turns) if session.turns else 0
        
        return {
            'session_id': session_id,
            'total_turns': len(session.turns),
            'duration_minutes': (time.time() - session.created_at) / 60,
            'model_usage': model_usage,
            'average_complexity': avg_complexity,
            'topics': session.topic_context,
            'last_activity': datetime.fromtimestamp(session.last_activity).isoformat()
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired_sessions)


# Global session manager instance
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return session_manager