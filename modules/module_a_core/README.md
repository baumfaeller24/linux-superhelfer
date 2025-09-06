# Module A: Core Intelligence Engine

Local AI inference engine using Ollama with Llama 3.1 8B quantized model for Linux administration assistance.

## Features

- **Local AI Inference**: Uses Ollama with Llama 3.1 8B (Q4 quantized) for fast, private responses
- **Query Processing**: Input validation, preprocessing, and context extraction
- **Confidence Scoring**: Heuristic-based confidence calculation for response quality assessment
- **Escalation Logic**: Automatic flagging of low-confidence responses for external processing
- **Error Handling**: Comprehensive error handling with fallback messages
- **Health Monitoring**: Real-time status monitoring of Ollama service

## API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Inference
```http
POST /infer
Content-Type: application/json

{
  "query": "How do I check disk usage in Linux?",
  "context": "Linux administration"
}
```

**Response:**
```json
{
  "response": "Use the 'df -h' command to check disk usage in human-readable format...",
  "confidence": 0.85,
  "status": "high_confidence",
  "processing_time": 2.3,
  "model_used": "llama3.1:8b"
}
```

### Status Information
```http
GET /status
```

**Response:**
```json
{
  "module": "Core Intelligence Engine",
  "version": "1.0.0",
  "status": "operational",
  "ollama": {
    "available": true,
    "host": "localhost",
    "port": 11434,
    "model": "llama3.1:8b"
  },
  "endpoints": ["/health", "/infer", "/status"],
  "confidence_threshold": 0.5
}
```

## Configuration

The module uses the central `config.yaml` file:

```yaml
ollama:
  host: localhost
  port: 11434
  model: llama3.1:8b-instruct-q4_0
  embedding_model: nomic-embed-text

features:
  confidence_threshold: 0.5
```

## Confidence Scoring

The confidence calculator uses multiple heuristics:

- **Length Analysis**: Optimal responses are 50-500 characters
- **Uncertainty Detection**: Penalizes phrases like "maybe", "not sure"
- **Structure Assessment**: Rewards proper formatting and technical details
- **Specificity Scoring**: Higher scores for Linux commands and technical terms
- **Processing Time**: Considers generation speed as quality indicator

**Confidence Levels:**
- `high_confidence` (≥0.8): Response is reliable
- `medium_confidence` (0.5-0.8): Response is acceptable
- `low_confidence_escalate` (<0.5): Should be escalated to external services

## Usage Examples

### Using curl
```bash
# Health check
curl http://localhost:8001/health

# Simple query
curl -X POST http://localhost:8001/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I list files in Linux?"}'

# Query with context
curl -X POST http://localhost:8001/infer \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I check system logs?",
    "context": "Ubuntu 22.04 server administration"
  }'
```

### Using Python
```python
import requests

# Make inference request
response = requests.post("http://localhost:8001/infer", json={
    "query": "How do I check disk usage?",
    "context": "Linux administration"
})

data = response.json()
print(f"Response: {data['response']}")
print(f"Confidence: {data['confidence']}")
print(f"Status: {data['status']}")
```

## Development

### Local Development
```bash
# Navigate to module directory
cd modules/module_a_core

# Install dependencies (in virtual environment)
pip install -r ../../requirements.txt

# Start the module
python main.py
```

### Running Tests
```bash
# Run module-specific tests
python -m pytest tests/test_module_a_core.py -v

# Run with coverage
python -m pytest tests/test_module_a_core.py --cov=modules.module_a_core
```

### Docker Development
```bash
# Build module image
docker build -f modules/module_a_core/Dockerfile -t core-intelligence .

# Run container
docker run -p 8001:8001 -e PYTHONPATH=/app core-intelligence
```

## Troubleshooting

### Common Issues

**1. "LLM service unavailable" Error**
- Check if Ollama is running: `ollama list`
- Verify model is installed: `ollama pull llama3.1:8b`
- Check Ollama service: `systemctl status ollama` (if using systemd)

**2. Port 8001 Already in Use**
```bash
# Check what's using the port
sudo lsof -i :8001

# Kill the process if needed
sudo kill -9 <PID>
```

**3. Low Confidence Scores**
- Ensure queries are specific and well-formed
- Check if Ollama model is properly loaded
- Verify system resources (RAM, GPU memory)

**4. Slow Response Times**
- Check system resources (CPU, GPU utilization)
- Verify Ollama configuration for GPU acceleration
- Consider using smaller model if resources are limited

### Performance Optimization

**For NVIDIA RTX 5090:**
```bash
# Ensure CUDA is available for Ollama
nvidia-smi

# Use GPU-optimized model
ollama pull llama3.1:8b-instruct-q4_0

# Monitor GPU usage
watch -n 1 nvidia-smi
```

**Memory Optimization:**
- Use Q4 quantization for better memory efficiency
- Adjust Ollama's `num_ctx` parameter for context length
- Monitor memory usage with `htop` or `nvidia-smi`

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Query Processor │────│  Ollama Client  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐             │
         └──────────────│ Confidence Calc  │─────────────┘
                        └──────────────────┘
```

## Dependencies

- **FastAPI**: Web framework for API endpoints
- **Ollama**: Local LLM inference engine
- **Pydantic**: Data validation and serialization
- **PyYAML**: Configuration file parsing

## Performance Metrics

- **Target Response Time**: <5 seconds for typical queries
- **Confidence Threshold**: 0.5 (configurable)
- **Memory Usage**: ~8GB VRAM for Llama 3.1 8B Q4
- **Concurrent Requests**: Supports multiple concurrent requests (limited by GPU memory)