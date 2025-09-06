# Module E: Hybrid Intelligence Gateway

External API integration for complex queries with local caching.

## Features

- Escalation of low-confidence queries to external APIs
- Integration with Grok API for enhanced responses
- Response caching in Knowledge Vault
- Fallback handling for offline scenarios

## API Endpoints

- `GET /health` - Health check
- `POST /escalate` - Escalate queries to external services

## Configuration

- Port: 8005
- External API: Grok (configurable)
- Confidence threshold: 0.5 for escalation
- Cache storage: Via Module B (RAG)

## Development

```bash
cd modules/module_e_hybrid
python main.py
```