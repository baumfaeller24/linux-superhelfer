# Design-Dokument

## Überblick

Dieses Design implementiert sitzungsbasierte Kontextwahrnehmung für das Linux Superhelfer System durch Integration des bestehenden SessionManagers mit den API-Endpunkten und der UI. Die Lösung nutzt die bereits implementierte Sitzungsverwaltungsinfrastruktur und fügt minimale Änderungen hinzu, um die Systemstabilität zu erhalten.

## Architektur

### Analyse des aktuellen Zustands

Das System hat bereits:
- `SessionManager` Klasse in `modules/module_a_core/session_manager.py`
- Sitzungsverfolgungsfähigkeiten mit Gesprächshistorie
- Kontexterstellungs- und -verbesserungsmethoden
- Themenerkennung und Kontextkürzung

**Lücke:** Der `/infer` Endpunkt verwendet keine Sitzungsverwaltung, und die UI sendet keine Sitzungs-IDs.

### Vorgeschlagene Architektur

```
UI (Streamlit) 
    ↓ (sendet session_id + query)
Module A Core (/infer endpoint)
    ↓ (ruft Sitzungskontext ab)
SessionManager
    ↓ (verbessert Anfrage mit Kontext)
Model Router + Ollama
    ↓ (verarbeitet verbesserte Anfrage)
Response + Context Logging
```

## Components and Interfaces

### 1. API Interface Changes

**Modified InferRequest Model:**
```python
class InferRequest(BaseModel):
    query: str
    context: Optional[str] = None
    enable_context_search: Optional[bool] = True
    context_threshold: Optional[float] = 0.6
    session_id: Optional[str] = None  # NEW FIELD
```

**Enhanced InferResponse Model:**
```python
class InferResponse(BaseModel):
    # ... existing fields ...
    session_id: str  # NEW FIELD
    context_turns_used: int = 0  # NEW FIELD
    context_enhanced: bool = False  # NEW FIELD
```

### 2. Session Integration Flow

1. **Session ID Handling:**
   - If `session_id` provided: Use existing session or create if not found
   - If no `session_id`: Auto-generate new session ID
   - Return session ID in response for UI persistence

2. **Context Enhancement:**
   - Retrieve conversation history from SessionManager
   - Build context string from recent turns (last 5)
   - Enhance query with context using existing `enhance_query_with_context` method
   - Process enhanced query through existing model routing

3. **Response Logging:**
   - Add conversation turn to session using existing `add_conversation_turn` method
   - Include routing decision and complexity score
   - Update session activity timestamp

### 3. UI Integration

**Session State Management:**
```python
# In ModuleOrchestrator.__init__()
if 'session_id' not in st.session_state:
    st.session_state.session_id = None  # Will be set by first API call
```

**Modified send_query Method:**
```python
def send_query(self, query: str, use_context: bool = True) -> Dict[str, Any]:
    payload = {
        "query": query,
        "enable_context_search": use_context,
        "session_id": st.session_state.get('session_id')  # NEW
    }
    # ... rest of method
    # Store returned session_id in session_state
```

## Data Models

### Session Context Flow

```
User Query: "wer hat es erfunden?"
    ↓
SessionManager.get_context_for_query()
    ↓
Context: "Previous Q: was ist linux?\nPrevious A: Linux ist ein Open-Source-Betriebssystem..."
    ↓
Enhanced Query: "Context from previous conversation:\nPrevious Q: was ist linux?\n...\nCurrent query: wer hat es erfunden?"
    ↓
Model Router (with enhanced context)
    ↓
Response: "Linus Torvalds hat Linux 1991 erfunden..."
```

### Context Storage Structure

The existing `ConversationTurn` and `SessionContext` classes will be used as-is:

```python
@dataclass
class ConversationTurn:
    timestamp: float
    query: str
    response: str
    model_used: str
    complexity_score: float
    routing_decision: str

@dataclass  
class SessionContext:
    session_id: str
    created_at: float
    last_activity: float
    turns: List[ConversationTurn]
    user_preferences: Dict[str, Any]
    topic_context: List[str]
```

## Error Handling

### Session Management Errors

1. **Session Not Found:**
   - Create new session automatically
   - Log session creation
   - Continue processing normally

2. **Context Enhancement Failure:**
   - Log warning about context failure
   - Process query without context
   - Don't fail the entire request

3. **Session Storage Errors:**
   - Log error but continue processing
   - Response generation should not fail due to session issues
   - Graceful degradation to stateless mode

### Backward Compatibility

- Requests without `session_id` work normally (auto-generate session)
- Existing `/infer_single_model` endpoint unchanged
- All existing functionality preserved
- New fields in responses are optional/default values

## Testing Strategy

### Unit Tests

1. **Session Integration Tests:**
   - Test session creation on first request
   - Test context retrieval and enhancement
   - Test conversation turn logging
   - Test session timeout and cleanup

2. **Context Enhancement Tests:**
   - Test context building from conversation history
   - Test context truncation when too long
   - Test query enhancement formatting
   - Test fallback when no context available

3. **API Integration Tests:**
   - Test `/infer` endpoint with session_id
   - Test `/infer` endpoint without session_id
   - Test response format with new fields
   - Test error handling scenarios

### Integration Tests

1. **End-to-End Conversation Flow:**
   - Send initial query, verify session creation
   - Send follow-up query, verify context usage
   - Verify context appears in logs as "Context Used: True"
   - Test conversation across multiple turns

2. **UI Integration:**
   - Test session persistence in Streamlit
   - Test session ID handling in UI
   - Test conversation history display
   - Test session reset functionality

### Performance Tests

1. **Context Performance:**
   - Measure context retrieval time
   - Test with long conversation histories
   - Verify context truncation performance
   - Monitor memory usage with multiple sessions

2. **Session Cleanup:**
   - Test automatic session expiration
   - Verify cleanup performance with many sessions
   - Test session storage memory usage

## Implementation Notes

### Minimal Changes Approach

This design leverages existing infrastructure to minimize risk:
- Uses existing `SessionManager` class without modifications
- Adds optional fields to existing API models
- Maintains backward compatibility
- Reuses existing context enhancement logic

### Configuration

The existing session configuration will be used:
- Session timeout: 3600 seconds (1 hour)
- Max context length: 2000 tokens
- Max conversation turns: 20
- Context turns for enhancement: 5

### Monitoring and Logging

Enhanced logging will show:
- Session creation and lifecycle events
- Context usage statistics per query
- Context enhancement success/failure
- Session cleanup operations
- Context truncation events

This provides visibility into the context system performance and usage patterns.