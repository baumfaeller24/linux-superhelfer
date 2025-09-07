# Design Document - Conversation Memory System

## Overview

The Conversation Memory System adds persistent conversation history and context-aware processing to the Linux Superhelfer. It enables multi-turn conversations, context resolution, and intelligent reference handling while maintaining privacy and performance.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Processor │───▶│ Context Manager │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Response Cache  │◀───│ Response Handler │◀───│ Memory Storage  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Component Integration

The system integrates with existing Module A (Core Intelligence) by:
1. Intercepting queries before processing
2. Enriching queries with conversation context
3. Storing responses after generation
4. Providing context for future queries

## Components and Interfaces

### 1. Conversation Memory Manager

**Purpose:** Central coordinator for conversation history and context management

**Interface:**
```python
class ConversationMemoryManager:
    def store_interaction(self, query: str, response: str, metadata: dict) -> str
    def get_conversation_context(self, session_id: str, limit: int = 5) -> List[dict]
    def resolve_references(self, query: str, context: List[dict]) -> str
    def create_session(self, user_id: str = None) -> str
    def end_session(self, session_id: str) -> bool
    def search_history(self, query: str, session_id: str = None) -> List[dict]
```

**Key Responsibilities:**
- Session lifecycle management
- Context retrieval and filtering
- Reference resolution (pronouns, "that", "your suggestion")
- Conversation threading

### 2. Context Resolver

**Purpose:** Analyzes queries for references and resolves them using conversation history

**Interface:**
```python
class ContextResolver:
    def analyze_query(self, query: str) -> dict
    def resolve_pronouns(self, query: str, context: List[dict]) -> str
    def detect_references(self, query: str) -> List[str]
    def expand_query_with_context(self, query: str, context: List[dict]) -> str
```

**Resolution Patterns:**
- Pronouns: "it", "that", "this", "them"
- References: "your suggestion", "the previous answer", "what you said"
- Confirmations: "ja", "yes", "continue", "proceed"
- Negations: "no", "nein", "that's wrong"

### 3. Memory Storage Engine

**Purpose:** Persistent storage and retrieval of conversation data

**Interface:**
```python
class MemoryStorage:
    def save_interaction(self, interaction: ConversationEntry) -> bool
    def load_session_history(self, session_id: str, limit: int) -> List[ConversationEntry]
    def search_conversations(self, query: str, filters: dict) -> List[ConversationEntry]
    def archive_old_conversations(self, cutoff_date: datetime) -> int
    def export_conversations(self, session_id: str, format: str) -> str
```

**Storage Schema:**
```python
@dataclass
class ConversationEntry:
    id: str
    session_id: str
    timestamp: datetime
    query: str
    response: str
    model_used: str
    confidence_score: float
    processing_time: float
    context_used: bool
    metadata: dict
```

### 4. Session Manager

**Purpose:** Manages conversation sessions and boundaries

**Interface:**
```python
class SessionManager:
    def create_session(self, user_id: str = None) -> Session
    def get_active_session(self, user_id: str) -> Session
    def detect_topic_change(self, query: str, current_session: Session) -> bool
    def auto_expire_sessions(self) -> List[str]
```

**Session Logic:**
- Auto-create session on first query
- Detect topic changes using semantic similarity
- Auto-expire after 1 hour of inactivity
- Maximum 10 active sessions per user

## Data Models

### Conversation Entry Schema

```json
{
  "id": "conv_20250907_105436_001",
  "session_id": "session_20250907_105400",
  "timestamp": "2025-09-07T10:54:36.123Z",
  "query": "ja setze deinen vorschlag um!",
  "resolved_query": "ja setze deinen vorschlag um! [Context: Previous suggestion was to create a new user account using useradd command]",
  "response": "I'll implement the user account creation as suggested...",
  "model_used": "llama3.2:3b",
  "confidence_score": 0.690,
  "processing_time": 2.02,
  "context_used": true,
  "vram_usage": "24.0%",
  "routing_decision": "fast model, complexity 0.00",
  "metadata": {
    "references_resolved": ["deinen vorschlag"],
    "context_entries_used": 1,
    "topic": "user_management"
  }
}
```

### Session Schema

```json
{
  "session_id": "session_20250907_105400",
  "user_id": "default_user",
  "created_at": "2025-09-07T10:54:00.000Z",
  "last_activity": "2025-09-07T10:55:09.000Z",
  "status": "active",
  "topic": "user_management",
  "interaction_count": 2,
  "metadata": {
    "primary_language": "de",
    "complexity_level": "basic"
  }
}
```

## Error Handling

### Context Resolution Failures

**Scenario:** Cannot resolve reference in query
**Handling:** 
1. Log the ambiguous reference
2. Ask user for clarification
3. Provide options based on recent context
4. Fall back to processing without context

**Example:**
```
User: "Mach das nochmal"
System: "Ich bin mir nicht sicher, worauf sich 'das' bezieht. Meinten Sie:
1. Den useradd Befehl ausführen
2. Das System neu starten
3. Etwas anderes?"
```

### Storage Failures

**Scenario:** Cannot save conversation to storage
**Handling:**
1. Continue processing query without saving
2. Log error for debugging
3. Attempt retry with exponential backoff
4. Notify user if persistent failure

### Session Management Errors

**Scenario:** Session corruption or loss
**Handling:**
1. Create new session automatically
2. Attempt to recover from backup
3. Inform user about session reset
4. Continue with fresh context

## Testing Strategy

### Unit Tests

1. **Context Resolution Tests**
   - Test pronoun resolution with various contexts
   - Test reference detection accuracy
   - Test ambiguous query handling

2. **Storage Tests**
   - Test conversation persistence
   - Test search functionality
   - Test data integrity and encryption

3. **Session Management Tests**
   - Test session creation and expiration
   - Test topic change detection
   - Test concurrent session handling

### Integration Tests

1. **End-to-End Conversation Tests**
   - Multi-turn conversation scenarios
   - Context continuity across restarts
   - Performance with large conversation histories

2. **Module Integration Tests**
   - Integration with existing Module A
   - Query processing pipeline
   - Response enhancement with context

### Performance Tests

1. **Context Search Performance**
   - Search speed with 1000+ conversation entries
   - Memory usage during context resolution
   - Response time impact measurement

2. **Storage Performance**
   - Write/read performance benchmarks
   - Concurrent access handling
   - Archive operation efficiency

## Implementation Phases

### Phase 1: Core Memory Storage
- Implement basic conversation storage
- Create session management
- Add simple context retrieval

### Phase 2: Context Resolution
- Implement reference detection
- Add pronoun resolution
- Create query expansion logic

### Phase 3: Advanced Features
- Add semantic search
- Implement topic change detection
- Add conversation export/import

### Phase 4: Optimization
- Performance tuning
- Memory usage optimization
- Advanced caching strategies