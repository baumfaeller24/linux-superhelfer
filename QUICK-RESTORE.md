# 🚀 QUICK RESTORE GUIDE - Linux Superhelfer

## 📋 BEI SESSIONWECHSEL IMMER ZUERST LESEN!

### 🎯 LETZTER BEKANNTER GUTER ZUSTAND:
**Tag**: `backup-2025-09-06-2247-working`  
**Status**: ✅ Alle Module funktional, GUI repariert  
**Problem**: Mathematical Query Routing suboptimal  

### ⚡ SCHNELL-CHECK (30 Sekunden):
```bash
# 1. Environment prüfen
echo $VIRTUAL_ENV  # Sollte venv zeigen

# 2. Module Status
netstat -tulpn | grep -E "800[0-5]" | wc -l  # Sollte 5 zeigen

# 3. GUI Check
curl -s http://localhost:8501 >/dev/null && echo "GUI OK" || echo "GUI offline"
```

### 🔄 SYSTEM RESTART (falls nötig):
```bash
# Prozesse aufräumen
pkill -f "streamlit"
pkill -f "overnight_optimization"

# Module starten
python -m uvicorn modules.module_a_core.main:app --host 0.0.0.0 --port 8001 --log-level error &
python -m uvicorn modules.module_b_rag.main:app --host 0.0.0.0 --port 8002 --log-level error &
python -m uvicorn modules.module_c_agents.main:app --host 0.0.0.0 --port 8003 --log-level error &
python -m uvicorn modules.module_d_execution.main:app --host 0.0.0.0 --port 8004 --log-level error &
python -m uvicorn modules.module_e_hybrid.main:app --host 0.0.0.0 --port 8005 --log-level error &

# GUI starten
streamlit run modules/module_f_ui/main.py --server.port 8501 &

# Warten und prüfen
sleep 10
curl -s http://localhost:8001/health && echo " - Module A OK"
curl -s http://localhost:8002/health && echo " - Module B OK"
curl -s http://localhost:8003/health && echo " - Module C OK"
curl -s http://localhost:8004/health && echo " - Module D OK"
curl -s http://localhost:8005/health && echo " - Module E OK"
curl -s http://localhost:8501 >/dev/null && echo " - GUI OK"
```

### 🎯 FUNKTIONSTEST:
```bash
# Test Intelligent Routing
curl -X POST "http://localhost:8001/infer" \
  -H "Content-Type: application/json" \
  -d '{"query": "Welcher Befehl zeigt die Festplattenbelegung an?", "enable_context_search": true}'
```

### 📚 BACKUP WIEDERHERSTELLEN (bei Problemen):
```bash
git checkout backup-2025-09-06-2247-working
```

### 🔧 BEKANNTE PROBLEME & LÖSUNGEN:

#### Problem: GUI Import Error
**Symptom**: `from .voice_handler import VoiceHandler` Error  
**Lösung**: Bereits behoben in Backup, absolute Imports verwendet

#### Problem: Module C offline
**Symptom**: `Health check failed for agents`  
**Lösung**: `python -m uvicorn modules.module_c_agents.main:app --host 0.0.0.0 --port 8003 --log-level error &`

#### Problem: Mathematical Queries falsch geroutet
**Symptom**: Math-Queries gehen zu Code Model statt Heavy Model  
**Status**: Bekanntes Problem, System funktioniert aber

### 🎯 NÄCHSTE ENTWICKLUNGSSCHRITTE:
1. Mathematical Detection in Query Analyzer verbessern
2. Heavy Model Threshold für Math-Keywords senken
3. Qwen3-Coder für Math-Queries optimieren

---
**WICHTIG**: Dieses Dokument bei jeder Session zuerst lesen!