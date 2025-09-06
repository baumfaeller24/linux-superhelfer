---
inclusion: always
---

# Linux Superhelfer - Projekt Operations Checkliste

## 🚨 IMMER VOR JEDER AKTION PRÜFEN:

### 1. Laufende Prozesse checken
```bash
# Optimization Routinen stoppen
pkill -f "overnight_optimization"
pkill -f "optimization_monitor"

# Aktuelle Prozesse anzeigen
ps aux | grep -E "(python|streamlit|ollama)" | grep -v grep
```

### 2. Virtual Environment aktivieren
```bash
# Prüfen ob venv aktiv ist
echo $VIRTUAL_ENV

# Falls nicht aktiv:
source venv/bin/activate  # oder entsprechender Pfad
```

### 3. Ollama Status prüfen
```bash
# Ollama Service Status
systemctl status ollama

# Verfügbare Modelle
ollama list

# VRAM Usage checken
nvidia-smi
```

### 4. Module Status prüfen
```bash
# Ports checken
netstat -tulpn | grep -E "800[0-5]"

# Module Health
curl -s http://localhost:8001/health 2>/dev/null || echo "Module A offline"
curl -s http://localhost:8002/health 2>/dev/null || echo "Module B offline"
```

## 🎯 NEUE HYBRIDSTRATEGIE - QWEN3-CODER INTEGRATION

### Modell-Routing Strategie:
- **Alltag/Schnell**: Llama 3.2 11B Vision (7.9GB VRAM)
- **Linux/Code**: Qwen3-Coder-30B Q4 (18-22GB VRAM) 
- **Extreme Cases**: Llama 3.1 70B (Fallback)

### VRAM Management:
- Monitoring mit pynvml
- Warnung bei >80% VRAM Usage
- User Confirmation für Model Switches
- Abort Option bei VRAM Problemen

## 📋 STANDARD STARTUP SEQUENCE:

1. **Environment Check**: venv, ollama, nvidia-smi
2. **Process Cleanup**: pkill optimization routines
3. **Module Startup**: start_system.py oder einzeln
4. **Health Verification**: curl health endpoints
5. **GUI Launch**: streamlit run oder python start

## 🔧 TROUBLESHOOTING CHECKLIST:

### Wenn Module nicht starten:
- Port bereits belegt? `netstat -tulpn | grep 800X`
- Dependencies installiert? `pip list | grep fastapi`
- Ollama erreichbar? `curl http://localhost:11434/api/tags`

### Wenn VRAM Probleme:
- Aktuelle Usage: `nvidia-smi`
- Ollama Modelle: `ollama ps`
- Model unload: `ollama stop <model>`

### Wenn Performance schlecht:
- Query Analyzer Logs prüfen
- Confidence Scores checken
- Hard Negatives Bank löschen: `rm -f optimization_logs/hard_bank.txt`

## 🎯 AKTUELLE IMPLEMENTIERUNG STATUS:

### ✅ FERTIG:
- Module A: Core Intelligence (mit Query Analyzer)
- Module B: RAG Knowledge Vault
- Module C: Proactive Agents  
- Module D: Safe Execution
- Module E: Hybrid Gateway
- Module F: UI (Streamlit)

### 🔄 IN ARBEIT:
- Qwen3-Coder Integration in Module A
- VRAM Monitoring System
- Model Router Optimierung

### ❌ TODO:
- Docker Containerization
- Central Config System
- Performance Testing
- Final Documentation