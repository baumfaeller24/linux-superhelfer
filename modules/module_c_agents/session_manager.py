"""
Session manager for Module C: Proactive Agents.
Manages stateful sessions and task execution context.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    PENDING_CONFIRMATION = "pending_confirmation"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class TaskExecution:
    """Task execution record."""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Session:
    """User session with task execution context."""
    session_id: str
    user_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    task_history: List[TaskExecution] = field(default_factory=list)
    pending_confirmations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired."""
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        return datetime.now() > expiry_time


class SessionManager:
    """Manages user sessions and task execution state."""
    
    def __init__(self, session_timeout_minutes: int = 30, max_sessions: int = 100):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Session timeout in minutes
            max_sessions: Maximum number of concurrent sessions
        """
        self.sessions: Dict[str, Session] = {}
        self.session_timeout_minutes = session_timeout_minutes
        self.max_sessions = max_sessions
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if session and not session.is_expired(self.session_timeout_minutes):
            session.update_activity()
            return session
        return None
    
    def add_pending_confirmation(self, session_id: str, confirmation_id: str, 
                                confirmation_data: Dict[str, Any]) -> bool:
        """Add pending confirmation to session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.pending_confirmations[confirmation_id] = {
            **confirmation_data,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=10)
        }
        session.status = SessionStatus.PENDING_CONFIRMATION
        logger.info(f"Added pending confirmation {confirmation_id} to session {session_id}")
        return True
    
    def resolve_confirmation(self, session_id: str, confirmation_id: str, 
                           approved: bool) -> Optional[Dict[str, Any]]:
        """Resolve a pending confirmation."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        confirmation = session.pending_confirmations.pop(confirmation_id, None)
        if confirmation:
            session.status = SessionStatus.ACTIVE
            confirmation["approved"] = approved
            logger.info(f"Resolved confirmation {confirmation_id}: approved={approved}")
        return confirmation
    
    def start_task_execution(self, session_id: str, task_id: str, task_type: str, 
                           parameters: Dict[str, Any]) -> bool:
        """Start task execution tracking."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        task_execution = TaskExecution(
            task_id=task_id,
            task_type=task_type,
            parameters=parameters,
            status="started",
            start_time=datetime.now()
        )
        session.task_history.append(task_execution)
        session.status = SessionStatus.EXECUTING
        logger.info(f"Started task execution {task_id} in session {session_id}")
        return True
    
    def complete_task_execution(self, session_id: str, task_id: str, 
                              result: Dict[str, Any], error: Optional[str] = None) -> bool:
        """Complete task execution tracking."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        for task_execution in reversed(session.task_history):
            if task_execution.task_id == task_id:
                task_execution.end_time = datetime.now()
                task_execution.result = result
                task_execution.error = error
                task_execution.status = "failed" if error else "completed"
                break
        
        session.status = SessionStatus.COMPLETED if not error else SessionStatus.FAILED
        logger.info(f"Completed task execution {task_id}: {'failed' if error else 'success'}")
        return True
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        active_sessions = sum(1 for s in self.sessions.values() if s.status == SessionStatus.ACTIVE)
        total_tasks = sum(len(s.task_history) for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_tasks_executed": total_tasks,
            "session_timeout_minutes": self.session_timeout_minutes
        }