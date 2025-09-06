"""
Module F: User Interface System
Streamlit-based web interface for Linux Superhelfer with intelligent routing integration.
"""

import streamlit as st
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import ConfigManager
from modules.module_f_ui.voice_handler import VoiceHandler
from modules.module_f_ui.session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Linux Superhelfer",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ModuleOrchestrator:
    """Orchestrates communication between UI and backend modules."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Module endpoints
        self.modules = {
            'core': 'http://localhost:8001',
            'knowledge': 'http://localhost:8002'
        }
        
        # Initialize components
        self.voice_handler = VoiceHandler()
        self.session_manager = SessionManager()
        
        # Session state initialization
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"session_{int(time.time())}"
    
    def check_module_health(self, module_name: str) -> Dict[str, Any]:
        """Check health status of a specific module."""
        try:
            url = f"{self.modules[module_name]}/health"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'status': 'offline',
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {}
        
        for module_name in self.modules.keys():
            status[module_name] = self.check_module_health(module_name)
        
        # Check router status specifically
        try:
            response = requests.get(f"{self.modules['core']}/router_status", timeout=5)
            if response.status_code == 200:
                status['router'] = {
                    'status': 'healthy',
                    'data': response.json()
                }
            else:
                status['router'] = {'status': 'unhealthy'}
        except:
            status['router'] = {'status': 'offline'}
        
        return status
    
    def send_query(self, query: str, use_context: bool = True) -> Dict[str, Any]:
        """Send query to Core Intelligence with intelligent routing."""
        try:
            # Prepare payload
            payload = {
                "query": query,
                "enable_context_search": use_context
            }
            
            # Send to intelligent routing endpoint
            start_time = time.time()
            response = requests.post(
                f"{self.modules['core']}/infer",
                json=payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract routing information
                routing_info = data.get('routing_info', {})
                
                return {
                    'success': True,
                    'response': data.get('response', ''),
                    'confidence': data.get('confidence', 0),
                    'model_used': data.get('model_used', 'unknown'),
                    'response_time': response_time,
                    'context_used': data.get('context_used', False),
                    'sources': data.get('sources', []),
                    'routing_info': {
                        'selected_model': routing_info.get('selected_model', 'unknown'),
                        'reasoning': routing_info.get('reasoning', 'N/A'),
                        'complexity_score': routing_info.get('complexity_score', 0),
                        'vram_check_passed': routing_info.get('vram_check_passed', True)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'response_time': response_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def search_knowledge(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Search knowledge base directly."""
        try:
            payload = {
                "query": query,
                "top_k": top_k,
                "threshold": 0.6
            }
            
            response = requests.post(
                f"{self.modules['knowledge']}/search",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'results': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def render_sidebar():
    """Render sidebar with system status and controls."""
    st.sidebar.title("🐧 Linux Superhelfer")
    st.sidebar.markdown("---")
    
    # System Status
    st.sidebar.subheader("📊 System Status")
    
    orchestrator = ModuleOrchestrator()
    status = orchestrator.get_system_status()
    
    # Core Intelligence Status
    core_status = status.get('core', {})
    if core_status.get('status') == 'healthy':
        st.sidebar.success("✅ Core Intelligence (A)")
    else:
        st.sidebar.error(f"❌ Core Intelligence: {core_status.get('error', 'Unknown')}")
    
    # Knowledge Management Status
    knowledge_status = status.get('knowledge', {})
    if knowledge_status.get('status') == 'healthy':
        st.sidebar.success("✅ Knowledge Management (B)")
    else:
        st.sidebar.error(f"❌ Knowledge Management: {knowledge_status.get('error', 'Unknown')}")
    
    # Router Status
    router_status = status.get('router', {})
    if router_status.get('status') == 'healthy':
        st.sidebar.success("✅ Intelligent Routing")
        
        # Show available models
        router_data = router_status.get('data', {})
        router_health = router_data.get('router_health', {})
        models = router_health.get('models', {})
        
        if models:
            st.sidebar.markdown("**Available Models:**")
            for model_type, model_info in models.items():
                if model_info.get('available'):
                    model_name = model_info.get('name', 'unknown')
                    st.sidebar.text(f"✅ {model_type}: {model_name}")
                else:
                    st.sidebar.text(f"❌ {model_type}: offline")
    else:
        st.sidebar.error("❌ Intelligent Routing")
    
    st.sidebar.markdown("---")
    
    # Settings
    st.sidebar.subheader("⚙️ Settings")
    
    use_context = st.sidebar.checkbox(
        "Enable Context Search",
        value=True,
        help="Automatically search knowledge base for relevant context"
    )
    
    show_technical_details = st.sidebar.checkbox(
        "Show Technical Details",
        value=False,
        help="Display routing information and performance metrics"
    )
    
    st.sidebar.markdown("---")
    
    # Quick Actions
    st.sidebar.subheader("🚀 Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Status"):
        st.rerun()
    
    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.sidebar.button("📊 System Info"):
        st.session_state.show_system_info = True
    
    return use_context, show_technical_details

def render_message(message: Dict[str, Any], show_technical: bool = False):
    """Render a chat message with optional technical details."""
    
    if message['role'] == 'user':
        with st.chat_message("user"):
            st.write(message['content'])
    
    elif message['role'] == 'assistant':
        with st.chat_message("assistant"):
            st.write(message['content'])
            
            # Show technical details if enabled
            if show_technical and 'metadata' in message:
                metadata = message['metadata']
                
                with st.expander("🔧 Technical Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Response Time", f"{metadata.get('response_time', 0):.2f}s")
                        st.metric("Confidence", f"{metadata.get('confidence', 0):.3f}")
                        
                    with col2:
                        st.metric("Model Used", metadata.get('model_used', 'unknown'))
                        context_used = "✅ Yes" if metadata.get('context_used') else "❌ No"
                        st.metric("Context Used", context_used)
                    
                    # Routing information
                    routing_info = metadata.get('routing_info', {})
                    if routing_info:
                        st.markdown("**Routing Decision:**")
                        st.text(f"Selected: {routing_info.get('selected_model', 'unknown')}")
                        st.text(f"Complexity: {routing_info.get('complexity_score', 0):.3f}")
                        st.text(f"Reasoning: {routing_info.get('reasoning', 'N/A')}")
                    
                    # Sources if available
                    sources = metadata.get('sources', [])
                    if sources:
                        st.markdown("**Knowledge Sources:**")
                        for i, source in enumerate(sources[:3], 1):
                            st.text(f"{i}. {source}")

def render_example_queries():
    """Render example queries for user guidance."""
    st.markdown("### 💡 Try these example queries:")
    
    examples = [
        {
            "query": "Hallo, wie geht es dir?",
            "description": "Simple greeting (Fast Model)",
            "icon": "👋"
        },
        {
            "query": "Zeige mir alle Python-Prozesse mit ps aux | grep python",
            "description": "Linux command help (Code Model)",
            "icon": "🐍"
        },
        {
            "query": "Schreibe eine Python-Funktion zum Kopieren von Dateien",
            "description": "Code generation (Code Model)",
            "icon": "💻"
        },
        {
            "query": "Erkläre mir detailliert, wie Docker Container funktionieren",
            "description": "Complex technical explanation (Code/Heavy Model)",
            "icon": "🐳"
        }
    ]
    
    cols = st.columns(2)
    
    for i, example in enumerate(examples):
        col = cols[i % 2]
        
        with col:
            if st.button(
                f"{example['icon']} {example['query'][:30]}...",
                key=f"example_{i}",
                help=example['description']
            ):
                # Add to chat and process
                st.session_state.messages.append({
                    'role': 'user',
                    'content': example['query'],
                    'timestamp': datetime.now()
                })
                st.rerun()

def main():
    """Main Streamlit application."""
    
    # Render sidebar
    use_context, show_technical_details = render_sidebar()
    
    # Main content area
    st.title("🐧 Linux Superhelfer Chat")
    st.markdown("Intelligent AI assistant with specialized Linux and coding expertise")
    
    # Initialize orchestrator
    orchestrator = ModuleOrchestrator()
    
    # Show system info if requested
    if st.session_state.get('show_system_info', False):
        with st.expander("📊 Detailed System Information", expanded=True):
            status = orchestrator.get_system_status()
            st.json(status)
        st.session_state.show_system_info = False
    
    # Display chat messages
    for message in st.session_state.messages:
        render_message(message, show_technical_details)
    
    # Show example queries if no messages
    if not st.session_state.messages:
        render_example_queries()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Linux administration..."):
        # Add user message
        user_message = {
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process query and get response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking... (Intelligent routing in progress)"):
                result = orchestrator.send_query(prompt, use_context)
            
            if result['success']:
                response = result['response']
                st.write(response)
                
                # Add assistant message with metadata
                assistant_message = {
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now(),
                    'metadata': {
                        'response_time': result.get('response_time', 0),
                        'confidence': result.get('confidence', 0),
                        'model_used': result.get('model_used', 'unknown'),
                        'context_used': result.get('context_used', False),
                        'sources': result.get('sources', []),
                        'routing_info': result.get('routing_info', {})
                    }
                }
                st.session_state.messages.append(assistant_message)
                
                # Show technical details immediately if enabled
                if show_technical_details:
                    with st.expander("🔧 Technical Details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Response Time", f"{result.get('response_time', 0):.2f}s")
                            st.metric("Confidence", f"{result.get('confidence', 0):.3f}")
                            
                        with col2:
                            st.metric("Model Used", result.get('model_used', 'unknown'))
                            context_used = "✅ Yes" if result.get('context_used') else "❌ No"
                            st.metric("Context Used", context_used)
                        
                        # Routing information
                        routing_info = result.get('routing_info', {})
                        if routing_info:
                            st.markdown("**Routing Decision:**")
                            st.text(f"Selected: {routing_info.get('selected_model', 'unknown')}")
                            st.text(f"Complexity: {routing_info.get('complexity_score', 0):.3f}")
                            st.text(f"Reasoning: {routing_info.get('reasoning', 'N/A')}")
            else:
                error_message = f"❌ Error: {result['error']}"
                st.error(error_message)
                
                # Add error message
                assistant_message = {
                    'role': 'assistant',
                    'content': error_message,
                    'timestamp': datetime.now()
                }
                st.session_state.messages.append(assistant_message)

if __name__ == "__main__":
    main()