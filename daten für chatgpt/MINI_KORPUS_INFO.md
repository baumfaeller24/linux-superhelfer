# Mini-Korpus zum Reproduzieren

## Verfügbare Daten

### Code-Korpus
- **Python Files**: ~20 Hauptdateien
- **Total Lines of Code**: 10,769 Zeilen
- **Hauptkomponenten**:
  - Query Analyzer (1,200+ Zeilen)
  - Model Router (800+ Zeilen) 
  - RAG System (2,000+ Zeilen)
  - Optimization Runner (600+ Zeilen)

### Optimization Logs
- **Total Log Files**: 3,757 Dateien
- **Cycle Results**: ~1,000+ JSON files
- **Progress Reports**: ~500+ JSON files
- **Hard Negatives**: 1 TXT file mit ~500 Einträgen

### Test Queries Dataset
```python
# Aus overnight_optimization_runner.py
test_queries = {
    'basic_commands': [
        "Welcher Befehl zeigt die Festplattenbelegung an?",
        "Wie kann ich alle laufenden Prozesse anzeigen?",
        "Welches Kommando listet alle Dateien auf?",
        # ... 10 total
    ],
    'mathematical': [
        "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
        "Löse das Gleichungssystem: x+y=10, x-y=2",
        "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
        # ... 10 total
    ],
    'code_tasks': [
        "Schreibe ein Bash-Skript zum automatischen Backup",
        "Erstelle eine Python-Funktion für Datei-Synchronisation",
        # ... 10 total
    ],
    'intermediate': [
        "Erkläre mir die Unterschiede zwischen verschiedenen Dateisystemen",
        "Wie funktioniert die Speicherverwaltung in Linux?",
        # ... 10 total
    ]
}
```

## Reproduzierbare Testumgebung

### Minimaler Datensatz für Reproduktion
1. **Query Analyzer** (`modules/module_a_core/query_analyzer.py`)
2. **Test Queries** (40 queries in 4 Kategorien)
3. **Hard Negatives** (`optimization_logs/hard_bank.txt`)
4. **Latest Progress** (`optimization_logs/latest_progress.json`)
5. **Sample Cycle Results** (5-10 JSON files)

### Reproduktions-Kommandos
```bash
# 1. Test Query Analyzer direkt
python modules/module_a_core/query_analyzer.py

# 2. Mini-Optimization Run (1 Stunde)
QPC=20 OO_SLEEP_SECS=5 python overnight_optimization_runner.py 1

# 3. Monitor starten
python advanced_monitor.py

# 4. Hard Negatives analysieren
head -50 optimization_logs/hard_bank.txt
```

## Datenqualität

### Vollständigkeit
- ✅ **Routing Logic**: Komplett implementiert
- ✅ **Test Queries**: 40 labeled queries
- ✅ **Hard Negatives**: 500+ real misrouting examples
- ✅ **Performance Logs**: 3,700+ cycle results
- ❌ **RAG Korpus**: Kein großer Dokumenten-Korpus

### Reproduzierbarkeit
- ✅ **Deterministic Patterns**: Regex-basierte Routing-Regeln
- ✅ **Configurable Parameters**: QPC, OO_SLEEP_SECS
- ✅ **Atomic Logging**: Konsistente JSON-Struktur
- ✅ **Error Handling**: Graceful degradation

## Empfohlene Korpus-Größe für ChatGPT
- **Code Files**: 5-10 Kern-Dateien (~3,000 Zeilen)
- **Test Queries**: 40 labeled examples
- **Hard Negatives**: 100 top examples
- **Cycle Results**: 10 representative JSON files
- **Config Files**: requirements.txt, README