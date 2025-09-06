# Module F: User Interface System

Web-based chat interface with intelligent routing integration for Linux Superhelfer.

## Overview

Module F provides a modern, responsive web interface built with Streamlit that allows users to interact with the Linux Superhelfer system through a chat-based interface. It integrates seamlessly with the intelligent model routing system and provides real-time feedback on system performance.

## Features

### ✅ Core Features
- **Web-based Chat Interface** - Clean, responsive Streamlit UI
- **Intelligent Routing Integration** - Direct integration with Module A's routing system
- **Real-time System Status** - Live monitoring of backend modules
- **Technical Details View** - Optional display of routing decisions and performance metrics
- **Session Management** - Persistent session logging and statistics
- **Example Query Suggestions** - Guided user experience with sample queries

### 🎤 Voice Features (Optional)
- **Speech-to-Text** - Using OpenAI Whisper (optional dependency)
- **Text-to-Speech** - Using Google Text-to-Speech (optional dependency)
- **Voice Controls** - Integrated voice input/output interface

### 📊 Advanced Features
- **Context Search Toggle** - Enable/disable automatic knowledge base integration
- **Performance Monitoring** - Response times, confidence scores, model usage
- **Session Analytics** - Query statistics and interaction history
- **Export Functionality** - Download session logs and system information

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Streamlit Web UI                        │
│                 (Port 8501)                            │
└─────────────────┬───────────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │ ModuleOrchestrator │
         │   (API Client)   │
         └─────┬─┬─────────┘
               │ │
    ┌──────────┘ └──────────┐
    │                       │
┌───▼───┐              ┌────▼────┐
│Module A│              │Module B │
│ :8001  │              │ :8002   │
│(Core)  │              │(Knowledge)│
└────────┘              └─────────┘
```

## Installation

### Required Dependencies
```bash
pip install streamlit requests
```

### Optional Dependencies (Voice Features)
```bash
pip install openai-whisper gtts
```

## Usage

### Quick Start
```bash
# Start backend modules first
./quick_start.sh

# Start UI
python modules/module_f_ui/start_ui.py
```

### Manual Start
```bash
# Set Python path
export PYTHONPATH=.

# Start Streamlit
streamlit run modules/module_f_ui/main.py --server.port 8501
```

### Access Interface
Open your browser and navigate to: `http://localhost:8501`

## API Integration

### Module A (Core Intelligence) Integration
- **Endpoint**: `POST /infer`
- **Features**: Intelligent model routing, confidence scoring, context enhancement
- **Response**: Includes routing decisions and performance metrics

### Module B (Knowledge Management) Integration  
- **Endpoint**: `POST /search`
- **Features**: Knowledge base search, document retrieval
- **Response**: Relevant document snippets with similarity scores

## Configuration

### Environment Variables
- `PYTHONPATH`: Set to project root for imports
- `STREAMLIT_SERVER_PORT`: UI port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Bind address (default: 0.0.0.0)

### Backend Module URLs
```python
modules = {
    'core': 'http://localhost:8001',
    'knowledge': 'http://localhost:8002'
}
```

## User Interface Components

### Main Chat Interface
- **Message History**: Persistent chat conversation
- **Input Field**: Text input with auto-focus
- **Example Queries**: Clickable sample queries for guidance
- **Response Display**: Formatted AI responses with metadata

### Sidebar Controls
- **System Status**: Real-time health monitoring
- **Settings**: Context search toggle, technical details view
- **Quick Actions**: Refresh, clear chat, system info
- **Session Info**: Statistics and session management

### Technical Details Panel (Optional)
- **Response Time**: Query processing duration
- **Confidence Score**: AI response confidence (0-1)
- **Model Used**: Which model processed the query
- **Routing Decision**: Why a specific model was selected
- **Context Sources**: Knowledge base sources used

## Session Management

### Features
- **Automatic Logging**: All interactions logged to JSON files
- **Session Statistics**: Query count, response times, duration
- **Export Functionality**: Download session data
- **Privacy**: All data stored locally

### Log Structure
```json
{
  "session_id": "ui_session_1234567890",
  "created_at": "2025-02-09T10:30:00",
  "interactions": [
    {
      "timestamp": "2025-02-09T10:30:15",
      "interaction_type": "query_sent",
      "data": {
        "query": "User query text",
        "metadata": {}
      }
    }
  ]
}
```

## Voice Features

### Speech-to-Text (Whisper)
- **Model**: OpenAI Whisper (base model)
- **Languages**: Multi-language support
- **Input**: Audio recording via browser
- **Output**: Transcribed text for chat input

### Text-to-Speech (gTTS)
- **Engine**: Google Text-to-Speech
- **Languages**: German (default), configurable
- **Output**: MP3 audio playback
- **Trigger**: Automatic for AI responses (optional)

## Performance Optimization

### Response Time Targets
- **UI Rendering**: <100ms for interface updates
- **Backend Communication**: Timeout handling for slow responses
- **Session Management**: Asynchronous logging to prevent UI blocking

### Resource Usage
- **Memory**: Minimal Streamlit overhead
- **Network**: Efficient API communication with backend modules
- **Storage**: Local session logs with automatic cleanup

## Error Handling

### Backend Module Failures
- **Graceful Degradation**: UI remains functional when modules are offline
- **Error Messages**: Clear user feedback for system issues
- **Retry Logic**: Automatic retry for transient failures

### Network Issues
- **Timeout Handling**: Configurable timeouts for API calls
- **Connection Errors**: User-friendly error messages
- **Offline Mode**: Basic functionality when backend unavailable

## Security Considerations

### Data Privacy
- **Local Processing**: All data remains on local system
- **No External Calls**: No data sent to external services
- **Session Isolation**: Each session is independent

### Input Validation
- **Query Sanitization**: Basic input validation and sanitization
- **File Upload Security**: Safe handling of voice input files
- **XSS Prevention**: Streamlit's built-in protections

## Development

### File Structure
```
modules/module_f_ui/
├── __init__.py              # Module initialization
├── main.py                  # Main Streamlit application
├── voice_handler.py         # Voice input/output functionality
├── session_manager.py       # Session logging and management
├── start_ui.py             # Startup script
└── README.md               # This documentation
```

### Adding New Features
1. **UI Components**: Add to `main.py` render functions
2. **Backend Integration**: Extend `ModuleOrchestrator` class
3. **Voice Features**: Modify `VoiceHandler` class
4. **Session Tracking**: Update `SessionManager` class

### Testing
```bash
# Start backend modules
./quick_start.sh

# Test UI startup
python modules/module_f_ui/start_ui.py

# Manual testing via browser
# Navigate to http://localhost:8501
```

## Troubleshooting

### Common Issues

#### UI Won't Start
```bash
# Check Python path
export PYTHONPATH=.

# Check Streamlit installation
pip install streamlit

# Check port availability
netstat -an | grep 8501
```

#### Backend Connection Errors
```bash
# Check backend module health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Restart backend modules
./stop_system.sh
./quick_start.sh
```

#### Voice Features Not Working
```bash
# Install optional dependencies
pip install openai-whisper gtts

# Check microphone permissions in browser
# Enable microphone access for localhost
```

### Performance Issues
- **Slow Response Times**: Check backend module performance
- **UI Lag**: Disable technical details view for better performance
- **Memory Usage**: Clear session data periodically

## API Reference

### ModuleOrchestrator Methods

#### `send_query(query: str, use_context: bool = True) -> Dict[str, Any]`
Send query to intelligent routing system.

**Parameters:**
- `query`: User query string
- `use_context`: Enable automatic context search

**Returns:**
```python
{
    'success': bool,
    'response': str,
    'confidence': float,
    'model_used': str,
    'response_time': float,
    'routing_info': {
        'selected_model': str,
        'reasoning': str,
        'complexity_score': float
    }
}
```

#### `get_system_status() -> Dict[str, Any]`
Get comprehensive system health status.

**Returns:**
```python
{
    'core': {'status': 'healthy|unhealthy|offline'},
    'knowledge': {'status': 'healthy|unhealthy|offline'},
    'router': {'status': 'healthy|unhealthy|offline'}
}
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: UI localization
- **Dark/Light Theme**: User preference themes
- **Advanced Analytics**: Usage patterns and optimization suggestions
- **Mobile Optimization**: Responsive design improvements
- **Keyboard Shortcuts**: Power user features

### Integration Opportunities
- **Module C Integration**: Proactive agent workflows
- **Module D Integration**: Safe command execution interface
- **Module E Integration**: External AI escalation UI
- **Custom Plugins**: Extensible UI component system

---

**Module F Status**: ✅ **Production Ready**  
**Last Updated**: 2025-02-09  
**Version**: 1.0.0