"""
Conversation Memory Manager - Core orchestrator for conversation memory system
Provides high-level interface for storing, retrieving, and managing conversations
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from .models import ConversationEntry, Session
from .storage import ConversationStorage
from .session_manager import SessionManager


class ConversationMemoryManager:
    """
    Central coordinator for conversation history and context management
    
    This is the main interface that other modules should use to interact
    with the conversation memory system.
    """
    
    def __init__(self, storage_dir: str = "conversation_data"):
        """Initialize the conversation memory manager"""
        self.storage = ConversationStorage(storage_dir)
        self.session_manager = SessionManager(self.storage)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_context_entries = 5
        self.auto_cleanup_enabled = True
        
        self.logger.info(f"ConversationMemoryManager initialized with storage: {storage_dir}")
    
    def store_interaction(self, query: str, response: str, metadata: dict, user_id: str = "default_user") -> str:
        """
        Store a complete interaction (query + response)
        
        Args:
            query: User's query
            response: System's response
            metadata: Additional metadata (model_used, confidence_score, etc.)
            user_id: User identifier
            
        Returns:
            Conversation entry ID
        """
        try:
            # Get or create session for this user
            session = self.session_manager.get_or_create_session(user_id, query)
            
            # Create conversation entry
            entry = ConversationEntry(
                session_id=session.session_id,
                query=query,
                response=response,
                model_used=metadata.get("model_used", ""),
                confidence_score=metadata.get("confidence_score", 0.0),
                processing_time=metadata.get("processing_time", 0.0),
                context_used=metadata.get("context_used", False),
                vram_usage=metadata.get("vram_usage", ""),
                routing_decision=metadata.get("routing_decision", ""),
                metadata=metadata
            )
            
            # Store conversation
            success = self.storage.save_conversation(entry)
            if not success:
                raise Exception("Failed to save conversation to storage")
            
            # Update session activity
            session.update_activity()
            self.storage.save_session(session)
            
            self.logger.info(f"Stored interaction {entry.id} in session {session.session_id}")
            
            # Auto-cleanup if enabled
            if self.auto_cleanup_enabled:
                self._auto_cleanup()
            
            return entry.id
            
        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")
            # Return a temporary ID to indicate failure
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_conversation_context(self, user_id: str = "default_user", limit: int = None) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return (default: self.max_context_entries)
            
        Returns:
            List of conversation context dictionaries
        """
        if limit is None:
            limit = self.max_context_entries
        
        try:
            # Get active session for user
            session = self.session_manager.get_active_session(user_id)
            if not session:
                self.logger.info(f"No active session found for user {user_id}")
                return []
            
            # Load recent conversations
            conversations = self.storage.load_session_conversations(session.session_id, limit)
            
            # Convert to context format
            context = []
            for conv in conversations:
                context.append({
                    "id": conv.id,
                    "timestamp": conv.timestamp.isoformat(),
                    "query": conv.query,
                    "response": conv.response,
                    "model_used": conv.model_used,
                    "confidence_score": conv.confidence_score,
                    "session_id": conv.session_id
                })
            
            self.logger.info(f"Retrieved {len(context)} context entries for user {user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation context for user {user_id}: {e}")
            return []
    
    def search_history(self, query: str, user_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversation history
        
        Args:
            query: Search query
            user_id: Optional user filter
            limit: Maximum results to return
            
        Returns:
            List of matching conversation dictionaries
        """
        try:
            # If user_id specified, search within their sessions only
            session_id = None
            if user_id:
                session = self.session_manager.get_active_session(user_id)
                if session:
                    session_id = session.session_id
            
            # Search conversations
            results = self.storage.search_conversations(query, session_id, limit)
            
            # Convert to dictionary format
            search_results = []
            for conv in results:
                search_results.append({
                    "id": conv.id,
                    "session_id": conv.session_id,
                    "timestamp": conv.timestamp.isoformat(),
                    "query": conv.query,
                    "response": conv.response,
                    "model_used": conv.model_used,
                    "confidence_score": conv.confidence_score,
                    "relevance_score": self._calculate_relevance_score(query, conv)
                })
            
            # Sort by relevance score (highest first)
            search_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            self.logger.info(f"Found {len(search_results)} results for query '{query}'")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Failed to search history: {e}")
            return []
    
    def create_session(self, user_id: str = "default_user", topic: str = "") -> str:
        """
        Manually create a new conversation session
        
        Args:
            user_id: User identifier
            topic: Optional topic for the session
            
        Returns:
            Session ID
        """
        try:
            session = self.session_manager.create_session(user_id, topic)
            self.logger.info(f"Created new session {session.session_id} for user {user_id}")
            return session.session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session for user {user_id}: {e}")
            return ""
    
    def end_session(self, session_id: str, reason: str = "user_requested") -> bool:
        """
        End a conversation session
        
        Args:
            session_id: Session to end
            reason: Reason for ending
            
        Returns:
            Success status
        """
        try:
            success = self.session_manager.end_session(session_id, reason)
            if success:
                self.logger.info(f"Ended session {session_id} (reason: {reason})")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def get_session_info(self, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Get information about user's current session
        
        Args:
            user_id: User identifier
            
        Returns:
            Session information dictionary
        """
        try:
            session = self.session_manager.get_active_session(user_id)
            if not session:
                return {"has_active_session": False}
            
            # Get session summary
            summary = self.session_manager.get_session_summary(session.session_id)
            summary["has_active_session"] = True
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get session info for user {user_id}: {e}")
            return {"has_active_session": False, "error": str(e)}
    
    def get_user_sessions(self, user_id: str, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            include_inactive: Whether to include inactive sessions
            
        Returns:
            List of session information dictionaries
        """
        try:
            sessions = self.session_manager.get_user_sessions(user_id, active_only=not include_inactive)
            
            session_list = []
            for session in sessions:
                summary = self.session_manager.get_session_summary(session.session_id)
                session_list.append(summary)
            
            self.logger.info(f"Retrieved {len(session_list)} sessions for user {user_id}")
            return session_list
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions for {user_id}: {e}")
            return []
    
    def export_conversations(self, user_id: str = None, session_id: str = None, format: str = "json") -> Optional[str]:
        """
        Export conversations in specified format
        
        Args:
            user_id: Optional user filter
            session_id: Optional session filter
            format: Export format ("json" or "csv")
            
        Returns:
            Exported data as string, or None if failed
        """
        try:
            if session_id:
                # Export specific session
                return self.storage.export_conversations(session_id, format)
            
            elif user_id:
                # Export all sessions for user
                sessions = self.session_manager.get_user_sessions(user_id)
                if not sessions:
                    return None
                
                # For now, export the most recent session
                # TODO: Implement multi-session export
                latest_session = max(sessions, key=lambda s: s.last_activity)
                return self.storage.export_conversations(latest_session.session_id, format)
            
            else:
                self.logger.warning("Export requires either user_id or session_id")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to export conversations: {e}")
            return None
    
    def cleanup_old_data(self, max_age_days: int = 30) -> Dict[str, int]:
        """
        Clean up old conversation data
        
        Args:
            max_age_days: Maximum age in days before cleanup
            
        Returns:
            Cleanup statistics
        """
        try:
            # Archive old conversations
            archived_conversations = self.storage.archive_old_conversations(max_age_days)
            
            # Expire old sessions
            expired_sessions = len(self.session_manager.auto_expire_sessions())
            
            # Additional cleanup
            cleaned_sessions = self.session_manager.cleanup_old_sessions(max_age_days)
            
            stats = {
                "archived_conversations": archived_conversations,
                "expired_sessions": expired_sessions,
                "cleaned_sessions": cleaned_sessions,
                "total_cleaned": archived_conversations + expired_sessions + cleaned_sessions
            }
            
            self.logger.info(f"Cleanup completed: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return {"error": str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            System statistics dictionary
        """
        try:
            # Storage stats
            storage_stats = self.storage.get_storage_stats()
            
            # Session stats
            all_sessions = self.session_manager.get_user_sessions("", active_only=False)  # Get all sessions
            active_sessions = [s for s in all_sessions if s.status == "active"]
            
            # Calculate additional metrics
            total_interactions = sum(s.interaction_count for s in all_sessions)
            
            stats = {
                "storage": storage_stats,
                "sessions": {
                    "total_sessions": len(all_sessions),
                    "active_sessions": len(active_sessions),
                    "total_interactions": total_interactions
                },
                "system": {
                    "auto_cleanup_enabled": self.auto_cleanup_enabled,
                    "max_context_entries": self.max_context_entries,
                    "storage_directory": str(self.storage.storage_dir)
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return {"error": str(e)}
    
    def _calculate_relevance_score(self, search_query: str, conversation: ConversationEntry) -> float:
        """Calculate relevance score for search results"""
        try:
            search_lower = search_query.lower()
            query_lower = conversation.query.lower()
            response_lower = conversation.response.lower()
            
            score = 0.0
            
            # Exact matches get highest score
            if search_lower in query_lower:
                score += 1.0
            if search_lower in response_lower:
                score += 0.8
            
            # Word matches
            search_words = search_lower.split()
            query_words = query_lower.split()
            response_words = response_lower.split()
            
            for word in search_words:
                if word in query_words:
                    score += 0.5
                if word in response_words:
                    score += 0.3
            
            # Boost recent conversations
            age_days = (datetime.now() - conversation.timestamp).days
            if age_days < 1:
                score *= 1.2
            elif age_days < 7:
                score *= 1.1
            
            # Boost high-confidence conversations
            if conversation.confidence_score > 0.8:
                score *= 1.1
            
            return min(score, 5.0)  # Cap at 5.0
            
        except Exception:
            return 0.0
    
    def _auto_cleanup(self):
        """Perform automatic cleanup if needed"""
        try:
            # Only run cleanup occasionally to avoid performance impact
            import random
            if random.random() < 0.1:  # 10% chance
                self.session_manager.auto_expire_sessions()
                
        except Exception as e:
            self.logger.error(f"Auto-cleanup failed: {e}")
    
    def resolve_references(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Resolve references in query using conversation context
        
        This is a placeholder for the context resolver that will be implemented in Task 4.
        For now, it just returns the original query.
        
        Args:
            query: Original query with potential references
            context: Conversation context
            
        Returns:
            Query with resolved references
        """
        # TODO: Implement in Task 4 (Context Resolver)
        return query