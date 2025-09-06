---
inclusion: always
---

# Linux Superhelfer - System Backup & Restore Guide

## 🎯 ZWECK
Dieses Dokument dient als persistente Referenz für wichtige Systemzustände und Backup-Punkte, damit bei Sessionwechseln der Entwicklungsstand nicht verloren geht.

## 📋 BACKUP CHECKLIST - IMMER VOR WICHTIGEN ÄNDERUNGEN

### 1. System Status dokumentieren
```bash
# Module Status prüfen
netstat -tulpn | grep -E "800[0-5]"
curl -s http://localhost:8001/health && echo " - Module A OK"
curl -s http://localhost:8002/health && echo " - Module B OK"
curl -s http://localhost:8003/health && echo " - Module C OK"
curl -s http://localhost:8004/health && echo " - Module D OK"
curl -s http://localhost:8005/health && echo " - Module E OK"
curl -s http://localhost:8501 && echo " - Module F OK"
```

### 2. Git Commit mit aussagekräftiger Message
```bash
git add .
git commit -m "BACKUP: [Beschreibung des Zustands]"
git tag -a "backup-YYYY-MM-DD-HH-MM" -m "Backup: [Status]"
```

### 3. Backup-Dokumentation erstellen
- Status aller Module
- Bekannte Probleme
- Nächste Schritte
- Wichtige Konfigurationen

## 🏷️ BACKUP TAGS SYSTEM

### Format: `backup-YYYY-MM-DD-HH-MM-[STATUS]`
- **working**: Alle Module laufen, keine kritischen Fehler
- **partial**: Einige Module funktionieren, bekannte Probleme
- **broken**: System nicht funktionsfähig
- **milestone**: Wichtiger Entwicklungsstand erreicht

## 📚 RESTORE ANLEITUNG

### Bei Sessionwechsel IMMER prüfen:
1. Letzten Backup-Tag finden: `git tag -l "backup-*" | tail -5`
2. Backup-Dokumentation lesen
3. System Status prüfen
4. Bei Problemen: `git checkout [backup-tag]`