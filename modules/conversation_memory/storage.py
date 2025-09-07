"""
Storage engine for conversation memory system
Handles persistent storage and retrieval of conversations and sessions
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .models import ConversationEntry, Session


class ConversationStorage:
    """File-based storage for conversations and sessions"""
    
    def __init__(self, storage_dir: str = "conversation_data"):
        self.storage_dir = Path(storage_dir)
        self.conversations_dir = self.storage_dir / "conversations"
        self.sessions_dir = self.storage_dir / "sessions"
        self.archive_dir = self.storage_dir / "archive"
        
        # Create directories
        for directory in [self.storage_dir, self.conversations_dir, self.sessions_dir, self.archive_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Storage configuration
        self.max_conversations_per_file = 100
        self.auto_archive_days = 30
    
    def save_conversation(self, entry: ConversationEntry) -> bool:
        """Save a conversation entry to storage"""
        try:
            # Determine file path based on session and date
            date_str = entry.timestamp.strftime('%Y%m%d')
            filename = f"{entry.session_id}_{date_str}.json"
            filepath = self.conversations_dir / filename
            
            # Load existing conversations or create new list
            conversations = []
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations = data.get('conversations', [])
            
            # Add new conversation
            conversations.append(entry.to_dict())
            
            # Save back to file
            data = {
                'session_id': entry.session_id,
                'date': date_str,
                'conversation_count': len(conversations),
                'conversations': conversations
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved conversation {entry.id} to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save conversation {entry.id}: {e}")
            return False
    
    def load_session_conversations(self, session_id: str, limit: int = 50) -> List[ConversationEntry]:
        """Load conversations for a specific session"""
        conversations = []
        
        try:
            # Find all files for this session
            pattern = f"{session_id}_*.json"
            session_files = list(self.conversations_dir.glob(pattern))
            
            # Sort by date (newest first)
            session_files.sort(reverse=True)
            
            for filepath in session_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_conversations = data.get('conversations', [])
                    
                    # Convert to ConversationEntry objects
                    for conv_data in reversed(file_conversations):  # Newest first within file
                        if len(conversations) >= limit:
                            break
                        conversations.append(ConversationEntry.from_dict(conv_data))
                
                if len(conversations) >= limit:
                    break
            
            self.logger.info(f"Loaded {len(conversations)} conversations for session {session_id}")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Failed to load conversations for session {session_id}: {e}")
            return []
    
    def save_session(self, session: Session) -> bool:
        """Save a session to storage"""
        try:
            filename = f"{session.session_id}.json"
            filepath = self.sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved session {session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a specific session"""
        try:
            filename = f"{session_id}.json"
            filepath = self.sessions_dir / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Session.from_dict(data)
                
        except Exception as e:
            self.logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def list_active_sessions(self, user_id: str = None) -> List[Session]:
        """List all active sessions, optionally filtered by user"""
        sessions = []
        
        try:
            for filepath in self.sessions_dir.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    
                    # Filter by user if specified
                    if user_id and session.user_id != user_id:
                        continue
                    
                    # Only include active sessions
                    if session.status == "active" and not session.is_expired():
                        sessions.append(session)
            
            # Sort by last activity (most recent first)
            sessions.sort(key=lambda s: s.last_activity, reverse=True)
            
            self.logger.info(f"Found {len(sessions)} active sessions")
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to list active sessions: {e}")
            return []
    
    def search_conversations(self, query: str, session_id: str = None, limit: int = 20) -> List[ConversationEntry]:
        """Search conversations by text content"""
        results = []
        query_lower = query.lower()
        
        try:
            # Determine which files to search
            if session_id:
                pattern = f"{session_id}_*.json"
                search_files = list(self.conversations_dir.glob(pattern))
            else:
                search_files = list(self.conversations_dir.glob("*.json"))
            
            for filepath in search_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations = data.get('conversations', [])
                    
                    for conv_data in conversations:
                        # Search in query and response
                        query_text = conv_data.get('query', '').lower()
                        response_text = conv_data.get('response', '').lower()
                        
                        if query_lower in query_text or query_lower in response_text:
                            results.append(ConversationEntry.from_dict(conv_data))
                            
                            if len(results) >= limit:
                                break
                
                if len(results) >= limit:
                    break
            
            # Sort by timestamp (most recent first)
            results.sort(key=lambda c: c.timestamp, reverse=True)
            
            self.logger.info(f"Found {len(results)} conversations matching '{query}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search conversations: {e}")
            return []
    
    def archive_old_conversations(self, cutoff_days: int = 30) -> int:
        """Archive conversations older than cutoff_days"""
        archived_count = 0
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)
        
        try:
            for filepath in self.conversations_dir.glob("*.json"):
                # Check file modification time
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    # Move to archive
                    archive_path = self.archive_dir / filepath.name
                    filepath.rename(archive_path)
                    archived_count += 1
                    self.logger.info(f"Archived {filepath.name}")
            
            self.logger.info(f"Archived {archived_count} conversation files")
            return archived_count
            
        except Exception as e:
            self.logger.error(f"Failed to archive conversations: {e}")
            return 0
    
    def cleanup_expired_sessions(self, timeout_hours: int = 1) -> int:
        """Mark expired sessions as inactive"""
        cleaned_count = 0
        
        try:
            for filepath in self.sessions_dir.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                
                if session.is_expired(timeout_hours):
                    session.status = "inactive"
                    
                    # Save updated session
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
                    
                    cleaned_count += 1
                    self.logger.info(f"Marked session {session.session_id} as inactive")
            
            self.logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    def export_conversations(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export conversations for a session in specified format"""
        try:
            conversations = self.load_session_conversations(session_id)
            
            if format.lower() == "json":
                export_data = {
                    "session_id": session_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "conversation_count": len(conversations),
                    "conversations": [conv.to_dict() for conv in conversations]
                }
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                # Simple CSV export
                lines = ["timestamp,query,response,model_used,confidence_score"]
                for conv in conversations:
                    line = f'"{conv.timestamp.isoformat()}","{conv.query}","{conv.response}","{conv.model_used}",{conv.confidence_score}'
                    lines.append(line)
                return "\n".join(lines)
            
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to export conversations: {e}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                "conversation_files": len(list(self.conversations_dir.glob("*.json"))),
                "session_files": len(list(self.sessions_dir.glob("*.json"))),
                "archived_files": len(list(self.archive_dir.glob("*.json"))),
                "total_size_mb": 0
            }
            
            # Calculate total size
            total_size = 0
            for directory in [self.conversations_dir, self.sessions_dir, self.archive_dir]:
                for filepath in directory.rglob("*.json"):
                    total_size += filepath.stat().st_size
            
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {}