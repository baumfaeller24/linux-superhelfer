"""
Data models for conversation memory system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import json


@dataclass
class ConversationEntry:
    """Represents a single conversation exchange (query + response)"""
    
    # Core identification
    id: str = field(default_factory=lambda: f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}")
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Conversation content
    query: str = ""
    resolved_query: str = ""  # Query after context resolution
    response: str = ""
    
    # Processing metadata
    model_used: str = ""
    confidence_score: float = 0.0
    processing_time: float = 0.0
    context_used: bool = False
    vram_usage: str = ""
    routing_decision: str = ""
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "resolved_query": self.resolved_query,
            "response": self.response,
            "model_used": self.model_used,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "context_used": self.context_used,
            "vram_usage": self.vram_usage,
            "routing_decision": self.routing_decision,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEntry':
        """Create from dictionary (JSON deserialization)"""
        entry = cls()
        entry.id = data.get("id", entry.id)
        entry.session_id = data.get("session_id", "")
        entry.timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        entry.query = data.get("query", "")
        entry.resolved_query = data.get("resolved_query", "")
        entry.response = data.get("response", "")
        entry.model_used = data.get("model_used", "")
        entry.confidence_score = data.get("confidence_score", 0.0)
        entry.processing_time = data.get("processing_time", 0.0)
        entry.context_used = data.get("context_used", False)
        entry.vram_usage = data.get("vram_usage", "")
        entry.routing_decision = data.get("routing_decision", "")
        entry.metadata = data.get("metadata", {})
        return entry
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ConversationEntry':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class Session:
    """Represents a conversation session containing multiple exchanges"""
    
    # Core identification
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}")
    user_id: str = "default_user"
    
    # Session lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, inactive, archived
    
    # Session content
    topic: str = ""
    interaction_count: int = 0
    
    # Session metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status,
            "topic": self.topic,
            "interaction_count": self.interaction_count,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create from dictionary (JSON deserialization)"""
        session = cls()
        session.session_id = data.get("session_id", session.session_id)
        session.user_id = data.get("user_id", "default_user")
        session.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        session.last_activity = datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat()))
        session.status = data.get("status", "active")
        session.topic = data.get("topic", "")
        session.interaction_count = data.get("interaction_count", 0)
        session.metadata = data.get("metadata", {})
        return session
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.interaction_count += 1
    
    def is_expired(self, timeout_hours: int = 1) -> bool:
        """Check if session is expired based on inactivity"""
        if self.status != "active":
            return True
        
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > (timeout_hours * 3600)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Session':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


def generate_conversation_id() -> str:
    """Generate a unique conversation ID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"conv_{timestamp}_{unique_id}"


def generate_session_id() -> str:
    """Generate a unique session ID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"session_{timestamp}_{unique_id}"