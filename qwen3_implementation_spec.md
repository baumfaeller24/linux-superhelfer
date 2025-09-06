# 🎯 Qwen3-Coder Implementation Specification

## Model Configuration

### Primary Models
```yaml
models:
  fast:
    name: "llama3.2:11b-vision"
    vram_usage: "7.9GB"
    use_case: "General queries, quick responses"
    
  code:
    name: "qwen3-coder:30b-q4"
    vram_usage: "18-22GB" 
    use_case: "Linux commands, shell scripts, code generation"
    
  heavy:
    name: "llama3.1:70b"
    vram_usage: "42GB"
    use_case: "Extreme complexity fallback"
```

## Query Analysis Logic

### Code/Linux Detection
```python
class QueryAnalyzer:
    def __init__(self):
        self.linux_keywords = [
            "befehl", "command", "script", "bash", "shell",
            "systemctl", "grep", "awk", "sed", "find", "chmod", 
            "chown", "mount", "df", "ps", "top", "htop", "ssh",
            "rsync", "tar", "zip", "cron", "service", "docker"
        ]
        
        self.code_keywords = [
            "programmiere", "code", "function", "class", "debug",
            "error", "exception", "syntax", "python", "javascript",
            "compile", "build", "test", "git", "repository"
        ]
    
    def needs_code_model(self, query: str) -> bool:
        """Determines if query needs specialized code model"""
        query_lower = query.lower()
        
        # Check for Linux/code keywords
        if any(kw in query_lower for kw in self.linux_keywords + self.code_keywords):
            return True
            
        # Check token count for complexity
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(query))
        
        if token_count > 500:
            return True
            
        return False
```

## VRAM Monitoring System

### Real-time VRAM Check
```python
import pynvml
import tkinter.messagebox as msgbox

class VRAMMonitor:
    def __init__(self):
        pynvml.nvmlInit()
        self.device_count = pynvml.nvmlDeviceGetCount()
    
    def get_vram_usage(self) -> float:
        """Returns VRAM usage as percentage (0.0-1.0)"""
        if self.device_count == 0:
            return 0.0
            
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return info.used / info.total
    
    def check_before_model_switch(self, target_model: str) -> bool:
        """Check VRAM before switching to larger model"""
        usage = self.get_vram_usage()
        
        if usage > 0.8:  # 80% threshold
            return msgbox.askokcancel(
                "VRAM-Warnung",
                f"Aktuelle VRAM-Nutzung: {usage:.1%}\n"
                f"Wechsel zu {target_model} könnte andere Anwendungen beeinträchtigen.\n\n"
                "Trotzdem fortfahren?"
            )
        return True
```

## Model Router Implementation

### Intelligent Routing Logic
```python
class ModelRouter:
    def __init__(self):
        self.analyzer = QueryAnalyzer()
        self.vram_monitor = VRAMMonitor()
        self.current_model = "llama3.2:11b-vision"
        
    async def route_query(self, query: str) -> str:
        """Routes query to appropriate model"""
        
        # Analyze query complexity
        needs_code_model = self.analyzer.needs_code_model(query)
        
        if needs_code_model:
            # Check VRAM before switching
            if not self.vram_monitor.check_before_model_switch("qwen3-coder:30b-q4"):
                return "Abgebrochen: VRAM-Warnung vom Benutzer bestätigt"
            
            # Switch to code model
            target_model = "qwen3-coder:30b-q4"
        else:
            # Use fast model for general queries
            target_model = "llama3.2:11b-vision"
        
        # Process with selected model
        response = await self.process_with_model(target_model, query)
        
        # Schedule model unload after idle timeout
        if target_model != "llama3.2:11b-vision":
            self.schedule_model_unload(target_model, timeout=600)  # 10 minutes
            
        return response
```

## API Endpoint Updates

### Enhanced Inference Endpoint
```python
@app.post("/infer")
async def infer_with_routing(request: QueryRequest):
    """Enhanced inference with intelligent model routing"""
    
    router = ModelRouter()
    
    try:
        # Route to appropriate model
        response = await router.route_query(request.query)
        
        # Calculate confidence
        confidence = calculate_confidence(response)
        
        return {
            "response": response,
            "confidence": confidence,
            "model_used": router.current_model,
            "vram_usage": router.vram_monitor.get_vram_usage(),
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        return {"error": str(e), "fallback": "Fast model unavailable"}
```

## Installation Commands

### Model Setup
```bash
# Install required models
ollama pull llama3.2:11b-vision
ollama pull qwen3-coder:30b-q4

# Install Python dependencies
pip install pynvml tiktoken

# Test VRAM monitoring
python -c "import pynvml; pynvml.nvmlInit(); print('VRAM monitoring ready')"
```

## Configuration Updates

### Module A Config
```yaml
# config/module_a.yaml
models:
  routing_enabled: true
  vram_monitoring: true
  warning_threshold: 0.8
  
  fast_model:
    name: "llama3.2:11b-vision"
    timeout: 30
    
  code_model:
    name: "qwen3-coder:30b-q4"
    timeout: 60
    idle_unload: 600
    
  heavy_model:
    name: "llama3.1:70b"
    timeout: 120
    idle_unload: 300
```

## Performance Expectations

### Response Times
- **Fast Model**: 2-5 seconds (general queries)
- **Code Model**: 5-10 seconds (Linux/code tasks)
- **Model Switch**: +2-3 seconds (loading time)

### VRAM Usage
- **Idle**: ~8GB (fast model loaded)
- **Code Tasks**: ~20GB (code model active)
- **Peak**: ~42GB (heavy model if needed)

This implementation provides intelligent, user-friendly VRAM management while maximizing performance for Linux administration tasks.