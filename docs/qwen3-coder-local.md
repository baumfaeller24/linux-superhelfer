# Qwen3-Coder-30B-A3B-Instruct (lokal)

## Überblick

Dieses Modell dient als **lokale Experteninstanz** für komplexe Linux- und Code-Aufgaben im Linux Superhelfer System. Es ist speziell für anspruchsvolle Tasks optimiert und wird **nicht als Standard-LLM** verwendet, um die Latenz-Anforderung (<5s) einzuhalten.

## Zweck und Anwendungsfälle

### Primäre Einsatzgebiete:
- **Komplexe Skript-Optimierung** und Sicherheitsanalyse
- **Kernel-Log-Analyse** und System-Debugging  
- **Erweiterte Code-Generierung** für Linux-Administration
- **Sicherheitslücken-Identifikation** in Shell-Scripts
- **Deep Debugging** von Systemproblemen
- **Multi-Step-Workflows** mit mehreren Befehlen

### Integration in Linux Superhelfer:
- **Modul A**: Intelligente Eskalation bei komplexen Code-Anfragen
- **Modul C**: Erweiterte Agent-Workflows für Systemadministration
- **Modul D**: Komplexe Kommando-Validierung und -Optimierung

## Hardware-Anforderungen

| Komponente | Minimum | Empfohlen |
|------------|---------|-----------|
| **GPU** | NVIDIA RTX 4090 (24GB) | NVIDIA RTX 5090 (32GB) |
| **RAM** | 32GB | 64GB |
| **Speicher** | 25GB frei | 50GB frei |
| **VRAM** | 22GB verfügbar | 25GB verfügbar |

## Installation

### Automatische Installation:
```bash
bash scripts/setup_qwen3_coder.sh
```

### Manuelle Installation:
```bash
# 1. Basis-Modell laden
ollama pull qwen:30b-coder-instruct

# 2. Optimierte Version erstellen
ollama create qwen3-coder-30b-local -f Modelfile.qwen3-coder

# 3. Verfügbarkeit prüfen
ollama list | grep qwen3-coder
```

## Nutzung

### Direkte Nutzung:
```bash
# Einfache Anfrage
ollama run qwen3-coder-30b-local "Erkläre, wie man systemctl logs analysiert."

# Komplexe Code-Generierung
ollama run qwen3-coder-30b-local "Erstelle ein sicheres Backup-Script mit Fehlerbehandlung und Logging."
```

### API-Nutzung:
```bash
# REST API
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen3-coder-30b-local",
    "prompt": "Generiere ein sicheres Backup-Skript für /etc",
    "stream": false
  }'

# Mit Streaming
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen3-coder-30b-local", 
    "prompt": "Analysiere diesen Kernel-Log-Eintrag: kernel: segfault at 0 ip 00007f8b8c0e1000",
    "stream": true
  }'
```

### Integration in Module A:
```python
# Beispiel für model_router.py
async def generate_with_expert_model(self, query: str):
    """Nutze Qwen3-Coder für komplexe Anfragen."""
    client = OllamaClient(model="qwen3-coder-30b-local")
    return await client.generate_response(query)
```

## Performance-Charakteristiken

### Antwortzeiten:
- **Einfache Befehle**: 3-5 Sekunden
- **Code-Generierung**: 8-12 Sekunden  
- **Komplexe Analyse**: 15-25 Sekunden
- **Multi-Step-Workflows**: 20-40 Sekunden

### VRAM-Nutzung:
- **Idle**: ~2GB (Modell nicht geladen)
- **Aktiv**: ~20GB (Q4_K_M Quantisierung)
- **Peak**: ~22GB (bei langen Kontexten)

### Qualitäts-Metriken:
- **Code-Korrektheit**: 95%+ bei Linux-Befehlen
- **Sicherheits-Awareness**: Hoch (erkennt gefährliche Befehle)
- **Kontext-Verständnis**: Bis zu 8192 Token
- **Sprach-Support**: Deutsch und Englisch

## Troubleshooting

### Häufige Probleme:

| Problem | Symptom | Lösung |
|---------|---------|--------|
| **Out of Memory** | `CUDA out of memory` | Schließe andere LLMs, reduziere Kontext |
| **Modell nicht gefunden** | `model not found` | Führe `ollama create` erneut aus |
| **Sehr langsame Antwort** | >60s Antwortzeit | Normal bei komplexen Tasks, ggf. Anfrage vereinfachen |
| **Hohe VRAM-Nutzung** | System wird langsam | Nutze VRAM-Monitor, andere GPU-Apps schließen |
| **Verbindungsfehler** | API nicht erreichbar | Ollama-Server neu starten: `ollama serve` |

### Debug-Befehle:
```bash
# Modell-Status prüfen
ollama list | grep qwen3-coder

# VRAM-Nutzung überwachen  
nvidia-smi -l 1

# Ollama-Logs anzeigen
ollama logs

# Modell-Performance testen
time ollama run qwen3-coder-30b-local "echo 'test'"
```

### Erweiterte Konfiguration:

#### Kontext-Größe anpassen:
```bash
# Für längere Dokumente (mehr VRAM nötig)
ollama create qwen3-coder-extended -f - <<EOF
FROM qwen:30b-coder-instruct
PARAMETER quantization q4_K_M
PARAMETER num_ctx 16384
PARAMETER num_gpu 1
EOF
```

#### Performance-Tuning:
```bash
# Für schnellere Antworten (weniger Qualität)
ollama create qwen3-coder-fast -f - <<EOF
FROM qwen:30b-coder-instruct
PARAMETER quantization q4_0
PARAMETER num_ctx 4096
PARAMETER num_gpu 1
PARAMETER temperature 0.3
EOF
```

## Integration in Linux Superhelfer

### Modul A (Core Intelligence):
- Automatische Eskalation bei `complexity_score > 0.8`
- Fallback bei Standard-Modell-Fehlern
- Spezielle Prompts für Linux-Administration

### Modul C (Proactive Agents):
- Erweiterte Workflow-Generierung
- Komplexe Multi-Step-Prozesse
- Sicherheits-Validierung von Befehlen

### Modul D (Safe Execution):
- Erweiterte Kommando-Analyse
- Sicherheits-Bewertung komplexer Scripts
- Rollback-Strategien für kritische Operationen

## Sicherheitshinweise

⚠️ **Wichtige Sicherheitsaspekte:**

1. **Lokale Ausführung**: Alle Daten bleiben auf dem System
2. **Keine Telemetrie**: Qwen3-Coder sendet keine Daten extern
3. **Kommando-Validierung**: Immer Ausgaben vor Ausführung prüfen
4. **Ressourcen-Monitoring**: VRAM-Nutzung überwachen
5. **Backup-Strategie**: Vor kritischen Operationen Backups erstellen

## Wartung und Updates

### Modell aktualisieren:
```bash
# Neue Version laden
ollama pull qwen:30b-coder-instruct

# Lokales Modell neu erstellen
ollama create qwen3-coder-30b-local -f Modelfile.qwen3-coder
```

### Speicher-Cleanup:
```bash
# Ungenutzte Modelle entfernen
ollama rm old-model-name

# Cache leeren
ollama prune
```

## Support und Weiterentwicklung

- **Dokumentation**: Diese Datei regelmäßig aktualisieren
- **Performance-Logs**: Antwortzeiten und Qualität dokumentieren  
- **Feature-Requests**: Neue Anwendungsfälle sammeln
- **Integration-Tests**: Regelmäßige Tests mit anderen Modulen

---

**Erstellt**: $(date)  
**Version**: 1.0  
**Kompatibilität**: Linux Superhelfer v2.0+  
**Lizenz**: Lokale Nutzung gemäß Qwen-Lizenz