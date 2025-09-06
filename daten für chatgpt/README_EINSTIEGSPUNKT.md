# Linux Superhelfer - Einstiegspunkt und Aufrufbeispiele

## Haupteinstiegspunkte

### 1. System starten
```bash
python start_system.py
```

### 2. Overnight Optimization
```bash
# Standard 8-Stunden-Optimierung
python overnight_optimization_runner.py 8

# Mit Parametern
QPC=20 OO_SLEEP_SECS=5 python overnight_optimization_runner.py 8

# Monitor starten
python advanced_monitor.py
```

### 3. Query Analyzer testen
```bash
python modules/module_a_core/query_analyzer.py
```

### 4. RAG System testen
```bash
python modules/module_b_rag/main.py
```

## Verzeichnisstruktur
```
linux helfer mit kiro/
├── modules/
│   ├── module_a_core/          # Core Query Analysis & Routing
│   │   ├── query_analyzer.py   # Hauptrouting-Logik
│   │   ├── model_router.py     # Hybrid Routing
│   │   └── main.py
│   └── module_b_rag/           # RAG System
│       ├── retriever.py        # BM25 + Embedding Retrieval
│       ├── vector_store.py     # Embedding Storage
│       ├── embedding_manager.py # Embedding Models
│       ├── chunk_processor.py  # Text Chunking
│       └── document_loader.py  # Document Loading
├── optimization_logs/          # Optimization Results
├── overnight_optimization_runner.py  # Hauptoptimierung
├── advanced_monitor.py         # Live Monitoring
└── start_system.py            # System Entry Point
```

## Aktuelle Konfiguration
- **Queries per Cycle**: 20 (QPC=20)
- **Sleep zwischen Cycles**: 5 Sekunden (OO_SLEEP_SECS=5)
- **Ziel Heavy Recall**: ≥95%
- **Ziel Cost Score**: ≥85
- **Aktueller Status**: Heavy Recall ~40%, Cost Score ~57

## Problemstellung
Das System läuft stabil, aber Heavy-Detection ist zu schwach. Mathematical/Complex queries werden nicht korrekt als "heavy" klassifiziert.