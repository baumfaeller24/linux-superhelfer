# Logging Configuration & Beispiel-Log

## Logging-Konfiguration

### Overnight Optimization Runner
```python
# ChatGPT's Cleanup Fix 2: Robust logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_DIR / "overnight_optimization.log", maxBytes=5_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
```

### Query Analyzer Logging
```python
# ChatGPT's Fix 6: Enhanced logging with debug info
logger.info(f"Query analysis: route_model={route_model}, "
           f"complexity={complexity_score:.2f}, tokens={token_count}{debug_str}")

# Debug string includes:
# - reason={self.debug['route_reason']}
# - heavy_hits={len(self.debug['heavy_hits'])}
# - tech_hits={len(self.debug['tech_hits'])}
```

### RAG System Logging
```python
# Retriever logging
logger.info(f"Search completed: '{query}' -> {len(processed_results)} results in {search_time:.3f}s")

# Embedding Manager logging
logger.debug(f"Generated normalized embedding for text ({len(text)} chars): {len(normalized_embedding)} dimensions")
```

## Beispiel-Log eines kompletten Durchlaufs

### Cycle 671 (Vollständiger Durchlauf)
```
2025-09-06 14:37:37,982 - __main__ - INFO - 🚀 Starting optimization cycle 671

# Query Analysis (20 Queries)
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=fast, complexity=0.22, tokens=9, reason=fast_basic_command
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.33, tokens=6, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=heavy, complexity=0.50, tokens=7, reason=heavy_win_relaxed H:2.5 T:0.0, heavy_hits=2
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=heavy, complexity=0.30, tokens=9, reason=heavy_win_relaxed H:2.5 T:0.0, heavy_hits=2
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.50, tokens=9, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=fast, complexity=0.33, tokens=6, reason=fast_basic_command
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.40, tokens=5, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.40, tokens=6, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.40, tokens=8, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.33, tokens=6, reason=code_tech T:1.0
2025-09-06 14:37:37,982 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=fast, complexity=0.10, tokens=6, reason=fast_default
2025-09-06 14:37:37,983 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.40, tokens=5, reason=code_tech T:1.0
2025-09-06 14:37:37,983 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.40, tokens=5, reason=code_tech T:1.0
2025-09-06 14:37:37,983 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.39, tokens=7, reason=code_tech T:1.0
2025-09-06 14:37:37,983 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.36, tokens=11, reason=code_tech T:1.0

# KPI Calculation & Progress Report
2025-09-06 14:37:38,002 - __main__ - INFO - 📊 Progress: acc 52.7%, cost -12.8, heavyR 27.680833872010346
2025-09-06 14:37:38,002 - __main__ - INFO - ✅ Cycle 671 completed: 53.3% accuracy (16/30) in 0.0s
```

### Cycle 672 (Nächster Durchlauf mit Hard Negatives)
```
2025-09-06 14:37:43,004 - __main__ - INFO - 🚀 Starting optimization cycle 672

# Viele Fast-Default Queries (Hard Negatives Oversampling)
2025-09-06 14:37:43,006 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=fast, complexity=0.00, tokens=8, reason=fast_default
[... 10 weitere fast_default queries ...]

# Gemischte Queries
2025-09-06 14:37:43,007 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=code, complexity=0.39, tokens=7, reason=code_tech T:1.0
2025-09-06 14:37:43,007 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=heavy, complexity=0.79, tokens=7, reason=heavy_win_relaxed H:2.5 T:1.0, heavy_hits=2
2025-09-06 14:37:43,008 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=fast, complexity=0.22, tokens=9, reason=fast_basic_command
2025-09-06 14:37:43,008 - modules.module_a_core.query_analyzer - INFO - Query analysis: route_model=heavy, complexity=1.00, tokens=5, reason=heavy_win_relaxed H:2.0 T:1.0, heavy_hits=1

# Verschlechterte Performance durch Hard Negatives
2025-09-06 14:37:43,027 - __main__ - INFO - 📊 Progress: acc 51.7%, cost -16.3, heavyR 26.478910795087266
2025-09-06 14:37:43,027 - __main__ - INFO - ✅ Cycle 672 completed: 50.0% accuracy (15/30) in 0.0s
```

## Log-Analyse Erkenntnisse

### Routing-Verteilung
- **Fast Model**: ~40% (fast_basic_command, fast_default)
- **Code Model**: ~50% (code_tech T:1.0)
- **Heavy Model**: ~10% (heavy_win_relaxed H:2.5 T:0.0/1.0)

### Performance-Probleme
- **Accuracy**: 50-53% (Ziel: >80%)
- **Cost Score**: -12.8 bis -16.3 (Ziel: >85, negativ = sehr schlecht)
- **Heavy Recall**: ~27% (Ziel: >95%)

### ChatGPT's Fixes sichtbar
- ✅ `reason=heavy_win_relaxed` (Fix 3: Relaxed tie-break)
- ✅ `heavy_hits=2` (Fix 2: Enhanced math patterns)
- ✅ Sofortige Progress-Reports (Fix 7)
- ✅ Hard Negatives Oversampling (viele fast_default queries)

### Kritische Erkenntnisse
- **Negative Cost Scores** zeigen massive Fehlrouting-Kosten
- **Heavy Model wird zu selten gewählt** trotz ChatGPT's Fixes
- **Hard Negatives Oversampling funktioniert** (sichtbar in Cycle 672)