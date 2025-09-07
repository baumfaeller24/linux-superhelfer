"""
Session Manager for conversation memory system
Handles session lifecycle, topic detection, and automatic cleanup
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import re
import glob
from pathlib import Path

from .models import Session, generate_session_id
from .storage import ConversationStorage


class SessionManager:
    """Manages conversation sessions and their lifecycle"""
    
    def __init__(self, storage: ConversationStorage, max_sessions_per_user: int = 10):
        self.storage = storage
        self.max_sessions_per_user = max_sessions_per_user
        self.logger = logging.getLogger(__name__)
        
        # Topic detection patterns (order matters - more specific first)
        self.topic_keywords = {
            "docker": ["docker", "container", "image", "dockerfile", "compose"],
            "user_management": ["user", "useradd", "passwd", "sudo", "account", "login"],
            "file_operations": ["file", "directory", "chmod", "chown", "ls", "cp", "mv", "rm"],
            "network": ["network", "ip", "ping", "ssh", "firewall", "port", "connection"],
            "system_admin": ["service", "systemctl", "process", "daemon", "cron", "log"],
            "package_management": ["apt", "yum", "dnf", "package", "update", "upgrade"],
            "security": ["security", "permission", "encryption", "key", "certificate", "firewall"],
            "performance": ["performance", "cpu", "memory", "disk", "load", "optimization"],
            "troubleshooting": ["error", "problem", "fix", "debug", "issue", "troubleshoot"],
            "programming": ["code", "script", "python", "bash", "programming", "development"]
        }
        
        # Session timeout configuration
        self.default_timeout_hours = 1
        self.max_inactive_hours = 24
    
    def create_session(self, user_id: str = "default_user", topic: str = "") -> Session:
        """Create a new conversation session"""
        try:
            # Check if user has too many active sessions
            active_sessions = self.get_user_sessions(user_id, active_only=True)
            
            if len(active_sessions) >= self.max_sessions_per_user:
                # Expire oldest session to make room
                oldest_session = min(active_sessions, key=lambda s: s.last_activity)
                oldest_session.status = "inactive"
                self.storage.save_session(oldest_session)
                self.logger.info(f"Expired oldest session {oldest_session.session_id} to make room")
            
            # Create new session
            session = Session(
                user_id=user_id,
                topic=topic,
                metadata={
                    "created_by": "session_manager",
                    "auto_created": topic == "",
                    "primary_language": "en"
                }
            )
            
            # Save session
            success = self.storage.save_session(session)
            if success:
                self.logger.info(f"Created new session {session.session_id} for user {user_id}")
                return session
            else:
                raise Exception("Failed to save session to storage")
                
        except Exception as e:
            self.logger.error(f"Failed to create session for user {user_id}: {e}")
            # Return a temporary session that won't be persisted
            return Session(user_id=user_id, topic="temporary")
    
    def get_active_session(self, user_id: str) -> Optional[Session]:
        """Get the most recent active session for a user"""
        try:
            active_sessions = self.get_user_sessions(user_id, active_only=True)
            
            if not active_sessions:
                return None
            
            # Return most recently active session
            return max(active_sessions, key=lambda s: s.last_activity)
            
        except Exception as e:
            self.logger.error(f"Failed to get active session for user {user_id}: {e}")
            return None
    
    def get_or_create_session(self, user_id: str, query: str = "") -> Session:
        """Get existing active session or create new one"""
        # Try to get existing active session
        session = self.get_active_session(user_id)
        
        if session and not session.is_expired(self.default_timeout_hours):
            # Update activity and return existing session
            session.update_activity()
            self.storage.save_session(session)
            return session
        
        # Create new session with topic detection
        detected_topic = self.detect_topic(query) if query else ""
        return self.create_session(user_id, detected_topic)
    
    def get_user_sessions(self, user_id: str, active_only: bool = False) -> List[Session]:
        """Get all sessions for a user"""
        try:
            all_sessions = self.storage.list_active_sessions(user_id)
            
            if active_only:
                return [s for s in all_sessions if s.status == "active" and not s.is_expired()]
            
            return all_sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []
    
    def detect_topic_change(self, query: str, current_session: Session) -> bool:
        """Detect if query represents a significant topic change"""
        try:
            # Get current topic
            current_topic = current_session.topic.lower() if current_session.topic else ""
            
            # Detect new topic from query
            new_topic = self.detect_topic(query)
            
            # If no clear topics detected, assume no change
            if not current_topic and not new_topic:
                return False
            
            # If current session has no topic, update it
            if not current_topic and new_topic:
                current_session.topic = new_topic
                current_session.metadata["topic_auto_detected"] = True
                self.storage.save_session(current_session)
                return False
            
            # Check if topics are different
            if new_topic and new_topic != current_topic:
                # Additional checks for topic change confidence
                topic_change_confidence = self._calculate_topic_change_confidence(
                    query, current_topic, new_topic
                )
                
                # Require high confidence for topic change
                return topic_change_confidence > 0.7
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to detect topic change: {e}")
            return False
    
    def detect_topic(self, text: str) -> str:
        """Detect the main topic from text content"""
        if not text:
            return ""
        
        text_lower = text.lower()
        topic_scores = {}
        
        # Score each topic based on keyword matches
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
            
            if score > 0:
                topic_scores[topic] = score
        
        # Return topic with highest score
        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])
            if best_topic[1] >= 1:  # Minimum score threshold
                return best_topic[0]
        
        return ""
    
    def _calculate_topic_change_confidence(self, query: str, current_topic: str, new_topic: str) -> float:
        """Calculate confidence score for topic change detection"""
        # Simple heuristic: higher confidence if query has strong indicators of new topic
        query_lower = query.lower()
        
        # Check for explicit topic change indicators
        topic_change_phrases = [
            "let's talk about", "now about", "switch to", "different topic",
            "new question", "another thing", "something else"
        ]
        
        for phrase in topic_change_phrases:
            if phrase in query_lower:
                return 0.9
        
        # Check keyword density for new topic
        new_topic_keywords = self.topic_keywords.get(new_topic, [])
        keyword_matches = sum(1 for keyword in new_topic_keywords if keyword in query_lower)
        
        if len(new_topic_keywords) > 0:
            keyword_density = keyword_matches / len(new_topic_keywords)
            return min(keyword_density * 2, 1.0)  # Scale to 0-1 range
        
        return 0.5  # Default moderate confidence
    
    def auto_expire_sessions(self, timeout_hours: int = None) -> List[str]:
        """Automatically expire inactive sessions"""
        if timeout_hours is None:
            timeout_hours = self.default_timeout_hours
        
        expired_session_ids = []
        
        try:
            # Get all sessions (including recently modified ones)
            session_files = glob.glob(str(self.storage.sessions_dir / "*.json"))
            
            for session_file in session_files:
                # Load each session fresh from disk
                session_id = Path(session_file).stem
                session = self.storage.load_session(session_id)
                
                if session and session.status == "active" and session.is_expired(timeout_hours):
                    session.status = "inactive"
                    session.metadata["expired_at"] = datetime.now().isoformat()
                    session.metadata["expired_reason"] = f"Inactive for {timeout_hours} hours"
                    
                    # Save updated session
                    success = self.storage.save_session(session)
                    if success:
                        expired_session_ids.append(session.session_id)
                        self.logger.info(f"Auto-expired session {session.session_id}")
            
            if expired_session_ids:
                self.logger.info(f"Auto-expired {len(expired_session_ids)} sessions")
            
            return expired_session_ids
            
        except Exception as e:
            self.logger.error(f"Failed to auto-expire sessions: {e}")
            return []
    
    def end_session(self, session_id: str, reason: str = "user_requested") -> bool:
        """Manually end a session"""
        try:
            session = self.storage.load_session(session_id)
            if not session:
                self.logger.warning(f"Session {session_id} not found")
                return False
            
            session.status = "inactive"
            session.metadata["ended_at"] = datetime.now().isoformat()
            session.metadata["end_reason"] = reason
            
            success = self.storage.save_session(session)
            if success:
                self.logger.info(f"Ended session {session_id} (reason: {reason})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session activity"""
        try:
            session = self.storage.load_session(session_id)
            if not session:
                return {}
            
            # Get conversations for this session
            conversations = self.storage.load_session_conversations(session_id)
            
            # Calculate session statistics
            total_conversations = len(conversations)
            if conversations:
                first_conversation = min(conversations, key=lambda c: c.timestamp)
                last_conversation = max(conversations, key=lambda c: c.timestamp)
                duration = last_conversation.timestamp - first_conversation.timestamp
                
                # Calculate average confidence
                avg_confidence = sum(c.confidence_score for c in conversations) / total_conversations
                
                # Count models used
                models_used = list(set(c.model_used for c in conversations if c.model_used))
            else:
                duration = timedelta(0)
                avg_confidence = 0.0
                models_used = []
            
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "topic": session.topic,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "total_conversations": total_conversations,
                "duration_minutes": duration.total_seconds() / 60,
                "average_confidence": round(avg_confidence, 3),
                "models_used": models_used,
                "is_expired": session.is_expired()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session summary for {session_id}: {e}")
            return {}
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Clean up very old inactive sessions"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            # This would require extending storage to support date-based cleanup
            # For now, we'll use the existing archive functionality
            archived_count = self.storage.archive_old_conversations(max_age_days)
            
            # Also cleanup expired sessions
            expired_count = len(self.auto_expire_sessions(self.max_inactive_hours))
            
            self.logger.info(f"Cleanup completed: {archived_count} conversations archived, {expired_count} sessions expired")
            
            return archived_count + expired_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {e}")
            return 0