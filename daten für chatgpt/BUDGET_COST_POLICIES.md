# Budget & Cost Policies

## Token & Query Caps

### Aktuelle Limits
- **Queries per Cycle**: 20 (QPC=20, umgebungsvariabel)
- **Sleep zwischen Cycles**: 5 Sekunden (OO_SLEEP_SECS=5)
- **Timeout per Model**:
  - Fast Model: 30s
  - Code Model: 30s (reduziert per Grok's Empfehlung)
  - Heavy Model: 120s

### Model VRAM Budgets
```python
self.models = {
    ModelType.FAST: ModelConfig(
        name="llama3.2:3b",
        vram_mb=2000,  # ~2GB
        timeout=30,
        idle_unload_seconds=0,  # Keep loaded
    ),
    ModelType.CODE: ModelConfig(
        name="qwen3-coder-30b-local", 
        vram_mb=18000,  # ~18GB
        timeout=30,
        idle_unload_seconds=600,  # 10 minutes
    ),
    ModelType.HEAVY: ModelConfig(
        name="llama3.1:70b",
        vram_mb=42000,  # ~42GB
        timeout=120,
        idle_unload_seconds=300,  # 5 minutes
    )
}
```

### Cost Scoring System (ChatGPT's Implementation)
```python
# Routing mistake costs
COST = {
    ('heavy','code'): 2.0,   # Heavy query routed to Code = 2.0 cost
    ('heavy','fast'): 3.0,   # Heavy query routed to Fast = 3.0 cost (worst)
    ('code','fast'): 1.0,    # Code query routed to Fast = 1.0 cost
    ('code','heavy'): 0.5,   # Code query routed to Heavy = 0.5 cost (acceptable)
    ('fast','code'): 0.5,    # Fast query routed to Code = 0.5 cost (acceptable)
    ('fast','heavy'): 1.0,   # Fast query routed to Heavy = 1.0 cost (wasteful)
}

# Cost Score Calculation
def _compute_kpis(self, results):
    wrong_cost = sum(COST.get((r['expected'], r['actual']), 1.0) 
                    for r in results if not r['correct'])
    cost_score = 100.0 * (1.0 - wrong_cost / len(results))
    return accuracy, cost_score, heavy_recall
```

### Acceptance Criteria
- **Heavy Recall Target**: ≥95%
- **Cost Score Target**: ≥85
- **Current Performance**: Heavy Recall ~40%, Cost Score ~57

## Caching: NICHT IMPLEMENTIERT

### Fehlende Caching-Features
- ❌ Query Result Caching
- ❌ Embedding Caching
- ❌ Model Response Caching
- ❌ Vector Search Result Caching

### Aktueller Workaround
- Models bleiben im VRAM geladen (idle_unload_seconds)
- Embedding Model bleibt persistent geladen

## Resource Management

### VRAM Monitoring
```python
class VRAMMonitor:
    def __init__(self, warning_threshold=0.8):
        self.warning_threshold = warning_threshold
    
    def check_before_model_switch(self, target_model, estimated_vram_mb, show_gui=True):
        # Prüft VRAM vor Model-Switch
        # Zeigt GUI-Warnung bei Überschreitung
```

### Model Idle Management
```python
async def _cleanup_idle_models(self):
    # Background task to unload idle models
    # Läuft alle 60 Sekunden
    # Entlädt Models nach idle_unload_seconds
```

### Batch Processing Limits
```python
# Embedding batch processing
batch_size = 10  # für bulk embedding
await asyncio.sleep(0.1)  # delay zwischen batches
```

## Performance Budgets

### Optimization Cycle Budget
- **Target Runtime**: 8 Stunden
- **Expected Cycles**: ~5,760 (alle 5 Sekunden)
- **Expected Queries**: ~115,200 total
- **Current Rate**: ~725 cycles/hour, ~14,500 queries/hour

### Error Handling Budget
- **Retry Logic**: Fallback zu Fast Model bei Fehlern
- **Timeout Handling**: Model-spezifische Timeouts
- **Graceful Degradation**: Zero-vector fallback für failed embeddings