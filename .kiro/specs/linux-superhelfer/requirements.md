# Requirements Document

## Introduction

The Linux Superhelfer is a modular, local AI-powered tool designed to assist with Linux administration tasks. The system consists of 6 interconnected modules that communicate through standardized REST APIs, prioritizing local execution while providing hybrid capabilities for complex queries. The tool supports command generation, log analysis, documentation consultation, and safe command execution with human-in-the-loop controls.

## Requirements

### Requirement 1: Core Intelligence Engine (Module A)

**User Story:** As a Linux administrator, I want a local AI engine that can generate commands and provide responses to my queries, so that I can get assistance without relying on external services.

#### Acceptance Criteria

1. WHEN a user submits a query THEN the system SHALL process it using intelligent model routing: Llama 3.2 11B Vision (7.9GB) for general queries, Qwen3-Coder-30B (18-22GB) for Linux/code tasks, with VRAM monitoring and user confirmation for model switches
2. WHEN processing a query THEN the system SHALL return a response within 5 seconds
3. WHEN generating a response THEN the system SHALL calculate a confidence score based on output quality
4. IF confidence score is below 0.5 THEN the system SHALL flag for escalation to external services
5. WHEN Ollama is offline THEN the system SHALL return a fallback error message
6. WHEN receiving API requests THEN the system SHALL expose `/infer` endpoint accepting JSON with query string
7. WHEN responding to API calls THEN the system SHALL return JSON with response text and confidence float

### Requirement 2: Knowledge Management System (Module B)

**User Story:** As a Linux administrator, I want to upload and search through documentation (manpages, Python docs), so that I can get contextually relevant information for my queries.

#### Acceptance Criteria

1. WHEN uploading documents THEN the system SHALL accept PDF and TXT files up to 30MB total
2. WHEN processing uploads THEN the system SHALL chunk documents into 500-token segments
3. WHEN indexing documents THEN the system SHALL use nomic-embed-text via Ollama for embeddings
4. WHEN searching knowledge base THEN the system SHALL return results within 2 seconds
5. WHEN performing searches THEN the system SHALL return top 3 relevant snippets with threshold 0.6
6. WHEN storing data THEN the system SHALL persist embeddings in local ChromaDB file
7. WHEN receiving search requests THEN the system SHALL expose `/search` endpoint accepting query string
8. WHEN returning search results THEN the system SHALL provide JSON with list of relevant text snippets

### Requirement 2.5: Module A and B Integration for Context-Enhanced Responses

**User Story:** As a Linux administrator, I want the AI engine to automatically search the knowledge base and use relevant documentation to provide better, more informed responses to my queries.

#### Acceptance Criteria

1. WHEN Module A receives a query THEN it SHALL automatically search Module B for relevant context
2. WHEN context is found THEN Module A SHALL integrate it into the AI prompt for enhanced responses
3. WHEN context search fails THEN Module A SHALL continue with standard processing without context
4. WHEN generating responses THEN the system SHALL indicate which knowledge sources were used
5. WHEN Module B is unavailable THEN Module A SHALL operate normally without context enhancement
6. WHEN context is retrieved THEN it SHALL be filtered by relevance score above 0.6 threshold
7. WHEN providing enhanced responses THEN the system SHALL maintain response time under 7 seconds total
8. WHEN integrating context THEN the system SHALL expose `/infer_with_context` endpoint for explicit context usage

### Requirement 3: Proactive Agent System (Module C)

**User Story:** As a Linux administrator, I want the system to recognize task types and execute predefined workflows, so that I can automate common administration tasks.

#### Acceptance Criteria

1. WHEN receiving a query THEN the system SHALL identify task type based on keywords
2. WHEN task type is identified THEN the system SHALL execute appropriate predefined workflow
3. WHEN executing tasks THEN the system SHALL support log analysis and backup script generation
4. WHEN running workflows THEN the system SHALL maintain session state using dictionary storage
5. WHEN executing critical tasks THEN the system SHALL require human confirmation before proceeding
6. WHEN calling other modules THEN the system SHALL integrate with Core Intelligence (A) and Knowledge Vault (B)
7. WHEN receiving task requests THEN the system SHALL expose `/execute_task` endpoint accepting task type and parameters
8. WHEN completing tasks THEN the system SHALL return JSON with execution results

### Requirement 4: Safe Command Execution (Module D)

**User Story:** As a Linux administrator, I want to preview and safely execute system commands, so that I can avoid accidental system damage while automating tasks.

#### Acceptance Criteria

1. WHEN receiving a command THEN the system SHALL parse and analyze the command structure
2. WHEN analyzing commands THEN the system SHALL perform dry-run simulation showing preview
3. WHEN showing preview THEN the system SHALL wait for explicit user confirmation
4. WHEN user confirms THEN the system SHALL execute the command using subprocess
5. WHEN user denies THEN the system SHALL abort execution without changes
6. WHEN executing commands THEN the system SHALL log all executions for audit trail
7. WHEN receiving execution requests THEN the system SHALL expose `/safe_execute` endpoint
8. WHEN responding to execution requests THEN the system SHALL return JSON with preview and execution status

### Requirement 5: Hybrid Intelligence Gateway (Module E)

**User Story:** As a Linux administrator, I want the system to escalate complex queries to external AI services when local processing is insufficient, so that I can get comprehensive assistance for difficult problems.

#### Acceptance Criteria

1. WHEN receiving low confidence queries THEN the system SHALL escalate to external Grok API
2. WHEN confidence score is below 0.5 THEN the system SHALL trigger escalation workflow
3. WHEN escalating queries THEN the system SHALL send requests to Grok via webhook
4. WHEN receiving external responses THEN the system SHALL cache results in Knowledge Vault (B)
5. WHEN internet is unavailable THEN the system SHALL fallback to local processing only
6. WHEN handling escalations THEN the system SHALL expose `/escalate` endpoint accepting query string
7. WHEN returning escalated results THEN the system SHALL provide JSON with external response text

### Requirement 6: User Interface System (Module F)

**User Story:** As a Linux administrator, I want a web-based chat interface with optional voice capabilities, so that I can interact with the system through multiple input methods.

#### Acceptance Criteria

1. WHEN accessing the interface THEN the system SHALL provide browser-based chat UI using Streamlit
2. WHEN using chat interface THEN the system SHALL support text input and display responses
3. WHEN voice features are enabled THEN the system SHALL support speech-to-text using Whisper
4. WHEN voice features are enabled THEN the system SHALL support text-to-speech using gTTS
5. WHEN processing user queries THEN the system SHALL orchestrate calls to appropriate modules
6. WHEN routing queries THEN the system SHALL follow workflow: Query → Core (A) → Knowledge (B) → Agents (C)
7. WHEN managing sessions THEN the system SHALL log all user interactions
8. WHEN interface is responsive THEN the system SHALL adapt to different screen sizes

### Requirement 7: System Integration and API Standardization

**User Story:** As a system architect, I want all modules to communicate through standardized REST APIs, so that modules can be developed independently and integrated seamlessly.

#### Acceptance Criteria

1. WHEN modules start THEN each SHALL expose standardized REST API on ports 8000+
2. WHEN checking module health THEN each SHALL provide `/health` GET endpoint returning {"status": "ok"}
3. WHEN processing requests THEN each SHALL provide `/main` POST endpoint with standard JSON I/O
4. WHEN errors occur THEN each SHALL return standard JSON error format with message and code
5. WHEN integrating modules THEN the system SHALL use central YAML configuration file
6. WHEN adding new modules THEN the system SHALL support plug-and-play integration without code changes
7. WHEN modules communicate THEN they SHALL use HTTP requests via the requests library
8. WHEN documenting APIs THEN each module SHALL provide README.md with Swagger-format specifications

### Requirement 8: Performance and Reliability

**User Story:** As a Linux administrator, I want the system to be fast and reliable, so that it doesn't slow down my workflow.

#### Acceptance Criteria

1. WHEN processing simple queries THEN the system SHALL respond within 5 seconds
2. WHEN searching knowledge base THEN the system SHALL return results within 2 seconds
3. WHEN system runs locally THEN it SHALL handle 80% of tasks without external dependencies
4. WHEN using hardware resources THEN the system SHALL use intelligent VRAM management: 7.9GB for general tasks (Llama 3.2 11B), 18-22GB for specialized Linux/code tasks (Qwen3-Coder-30B)
5. WHEN switching models THEN the system SHALL monitor VRAM usage with pynvml, show warnings at >80% usage, and provide user confirmation with abort option
6. WHEN errors occur THEN the system SHALL provide meaningful error messages and recovery options
7. WHEN modules fail THEN other modules SHALL continue operating independently
8. WHEN system restarts THEN all persistent data SHALL be preserved