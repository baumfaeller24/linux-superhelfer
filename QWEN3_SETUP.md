# 🚀 Qwen3-Coder Integration Setup

## Überblick

Diese Anleitung führt Sie durch die Installation und Konfiguration der neuen intelligenten Modell-Routing-Funktionalität mit Qwen3-Coder Integration.

## 🔧 Installation

### 1. Python-Dependencies installieren

```bash
# Neue Dependencies für VRAM-Monitoring und Query-Analyse
pip install pynvml tiktoken

# Optional: Regex für erweiterte Textverarbeitung
pip install regex
```

### 2. Ollama-Modelle installieren

```bash
# Standard-Modell (Fast Model)
ollama pull llama3.2:11b-vision

# Code-Spezialist (Code Model) 
ollama pull qwen3-coder:30b-q4

# Fallback für extreme Komplexität (Heavy Model)
ollama pull llama3.1:70b
```

### 3. NVIDIA-Treiber prüfen

```bash
# VRAM-Monitoring testen
nvidia-smi

# Python-Integration testen
python -c "import pynvml; pynvml.nvmlInit(); print('VRAM monitoring ready')"
```

## 🧪 Funktionstest

```bash
# Test-Suite ausführen
python test_qwen3_integration.py
```

## 🎯 Neue Features

### Intelligente Modell-Auswahl

Das System wählt automatisch das beste Modell basierend auf:

- **Linux-Keywords**: `ps`, `grep`, `chmod`, `systemctl`, etc.
- **Code-Keywords**: `python`, `function`, `debug`, `git`, etc.
- **Komplexität**: Token-Anzahl, Schritt-für-Schritt-Anfragen
- **VRAM-Verfügbarkeit**: Automatische Warnungen bei hoher Nutzung

### Modell-Hierarchie

```
Llama 3.2 11B Vision (8GB)     → Alltägliche Queries
     ↓ (bei Linux/Code)
Qwen3-Coder-30B (20GB)         → Spezialisierte Tasks
     ↓ (bei extremer Komplexität)  
Llama 3.1 70B (42GB)           → Fallback
```

### VRAM-Management

- **Real-time Monitoring** mit pynvml
- **User-Warnungen** bei >80% VRAM-Nutzung
- **Abbruch-Option** zum Schutz anderer Anwendungen
- **Automatisches Fallback** bei Problemen

## 📡 API-Änderungen

### Neue Endpoints

```bash
# Intelligente Inference (Standard)
POST /infer

# Legacy-Inference (Rückwärtskompatibilität)
POST /infer_legacy

# Router-Status
GET /router_status
```

### Erweiterte Response

```json
{
  "response": "Antwort des Modells",
  "confidence": 0.85,
  "model_used": "qwen3-coder:30b-q4",
  "routing_info": {
    "selected_model": "code",
    "reasoning": "Linux keywords detected: ps, grep",
    "complexity_score": 0.7,
    "vram_check_passed": true
  },
  "vram_usage_percent": 0.65
}
```

## 🔍 Beispiel-Queries

### Fast Model (Llama 3.2 11B)
```
"Hallo, wie geht es dir?"
"Was ist die Hauptstadt von Deutschland?"
"Erkläre mir kurz, was KI ist"
```

### Code Model (Qwen3-Coder 30B)
```
"Zeige mir alle laufenden Prozesse mit ps"
"Schreibe eine Python-Funktion zum Kopieren von Dateien"
"Wie funktioniert chmod 755?"
"Erstelle ein Backup-Script für MySQL"
```

### Heavy Model (Llama 3.1 70B)
```
"Erkläre mir detailliert die Architektur von Kubernetes"
"Schreibe eine komplexe Microservice-Anwendung mit Docker"
"Analysiere und optimiere diesen 500-Zeilen Python-Code"
```

## ⚙️ Konfiguration

### VRAM-Schwellenwerte anpassen

```python
# In modules/module_a_core/model_router.py
model_router = ModelRouter()
model_router.vram_monitor.warning_threshold = 0.7  # 70% statt 80%
```

### Modell-Konfiguration

```python
# Eigene Modelle hinzufügen
self.models[ModelType.CUSTOM] = ModelConfig(
    name="your-custom-model:latest",
    vram_mb=15000,
    timeout=45,
    idle_unload_seconds=300,
    description="Custom specialized model"
)
```

## 🐛 Troubleshooting

### VRAM-Monitoring funktioniert nicht
```bash
# NVIDIA-Treiber prüfen
nvidia-smi

# pynvml neu installieren
pip uninstall pynvml
pip install pynvml
```

### Modell nicht verfügbar
```bash
# Ollama-Status prüfen
ollama list

# Modell manuell laden
ollama run qwen3-coder:30b-q4
```

### GUI-Warnungen funktionieren nicht
```bash
# tkinter testen
python -c "import tkinter; print('GUI available')"

# Auf headless Systemen: GUI-Warnungen deaktivieren
# show_gui=False in check_before_model_switch()
```

## 📊 Performance-Erwartungen

| Modell | VRAM | Antwortzeit | Use Case |
|--------|------|-------------|----------|
| Llama 3.2 11B | 8GB | 2-5s | Alltag |
| Qwen3-Coder 30B | 20GB | 5-10s | Linux/Code |
| Llama 3.1 70B | 42GB | 10-20s | Komplexität |

## 🎉 Fertig!

Das System ist jetzt bereit für intelligente Modell-Auswahl mit optimaler VRAM-Nutzung!

**Nächste Schritte:**
1. Test-Suite ausführen: `python test_qwen3_integration.py`
2. Module A starten: `python modules/module_a_core/main.py`
3. Erste Anfrage testen: `curl -X POST http://localhost:8001/infer -d '{"query": "ps aux | grep python"}'`