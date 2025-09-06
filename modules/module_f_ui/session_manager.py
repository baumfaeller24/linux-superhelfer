"""
Session Manager for Module F
Handles user session management and interaction logging.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions and interaction logging."""
    
    def __init__(self, log_dir: str = "logs/ui_sessions"):
        self.log_dir = log_dir
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure log directory exists."""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def get_session_id(self) -> str:
        """Get or create session ID."""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"ui_session_{int(datetime.now().timestamp())}"
        return st.session_state.session_id
    
    def get_session_file_path(self) -> str:
        """Get path to session log file."""
        session_id = self.get_session_id()
        return os.path.join(self.log_dir, f"{session_id}.json")
    
    def log_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Log user interaction to session file."""
        try:
            session_id = self.get_session_id()
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                'session_id': session_id,
                'timestamp': timestamp,
                'interaction_type': interaction_type,
                'data': data
            }
            
            # Load existing session data
            session_file = self.get_session_file_path()
            session_data = self.load_session_data()
            
            # Add new interaction
            if 'interactions' not in session_data:
                session_data['interactions'] = []
            
            session_data['interactions'].append(log_entry)
            session_data['last_updated'] = timestamp
            
            # Save updated session data
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"Logged interaction: {interaction_type} for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
    
    def load_session_data(self) -> Dict[str, Any]:
        """Load session data from file."""
        session_file = self.get_session_file_path()
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load session data: {e}")
        
        # Return default session data
        return {
            'session_id': self.get_session_id(),
            'created_at': datetime.now().isoformat(),
            'interactions': []
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        session_data = self.load_session_data()
        interactions = session_data.get('interactions', [])
        
        if not interactions:
            return {
                'total_interactions': 0,
                'queries_sent': 0,
                'responses_received': 0,
                'session_duration': 0,
                'avg_response_time': 0
            }
        
        # Calculate statistics
        queries = [i for i in interactions if i['interaction_type'] == 'query_sent']
        responses = [i for i in interactions if i['interaction_type'] == 'response_received']
        
        # Calculate session duration
        first_interaction = datetime.fromisoformat(interactions[0]['timestamp'])
        last_interaction = datetime.fromisoformat(interactions[-1]['timestamp'])
        duration = (last_interaction - first_interaction).total_seconds()
        
        # Calculate average response time
        response_times = []
        for response in responses:
            response_time = response.get('data', {}).get('response_time', 0)
            if response_time > 0:
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_interactions': len(interactions),
            'queries_sent': len(queries),
            'responses_received': len(responses),
            'session_duration': duration,
            'avg_response_time': avg_response_time,
            'created_at': session_data.get('created_at'),
            'last_updated': session_data.get('last_updated')
        }
    
    def log_query(self, query: str, metadata: Dict[str, Any] = None):
        """Log user query."""
        self.log_interaction('query_sent', {
            'query': query,
            'metadata': metadata or {}
        })
    
    def log_response(self, response: str, metadata: Dict[str, Any] = None):
        """Log system response."""
        self.log_interaction('response_received', {
            'response': response[:200] + "..." if len(response) > 200 else response,
            'response_length': len(response),
            'metadata': metadata or {}
        })
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log error occurrence."""
        self.log_interaction('error_occurred', {
            'error': error,
            'context': context or {}
        })
    
    def log_system_event(self, event: str, data: Dict[str, Any] = None):
        """Log system event."""
        self.log_interaction('system_event', {
            'event': event,
            'data': data or {}
        })
    
    def render_session_info(self):
        """Render session information in sidebar."""
        stats = self.get_session_stats()
        
        st.sidebar.markdown("### 📊 Session Info")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric("Queries", stats['queries_sent'])
            st.metric("Responses", stats['responses_received'])
        
        with col2:
            duration_min = stats['session_duration'] / 60
            st.metric("Duration", f"{duration_min:.1f}m")
            st.metric("Avg Response", f"{stats['avg_response_time']:.1f}s")
        
        # Session details in expander
        with st.sidebar.expander("Session Details"):
            st.text(f"ID: {self.get_session_id()}")
            if stats['created_at']:
                created = datetime.fromisoformat(stats['created_at'])
                st.text(f"Started: {created.strftime('%H:%M:%S')}")
            
            if st.button("📥 Download Session Log"):
                session_data = self.load_session_data()
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(session_data, indent=2, default=str),
                    file_name=f"session_{self.get_session_id()}.json",
                    mime="application/json"
                )
    
    def clear_session(self):
        """Clear current session data."""
        try:
            session_file = self.get_session_file_path()
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith('session_') or key == 'messages':
                    del st.session_state[key]
            
            logger.info("Session cleared successfully")
            
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
    
    def export_all_sessions(self) -> List[Dict[str, Any]]:
        """Export all session data."""
        all_sessions = []
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.log_dir, filename)
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                        all_sessions.append(session_data)
        
        except Exception as e:
            logger.error(f"Failed to export sessions: {e}")
        
        return all_sessions