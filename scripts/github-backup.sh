#!/bin/bash

# 🚀 GitHub Backup Script für Linux-Superhelfer
# Automatisiert den kompletten Backup-Prozess

set -e  # Exit bei Fehlern

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Linux-Superhelfer GitHub Backup${NC}"
echo "=================================="

# 1. Status prüfen
echo -e "${YELLOW}📊 Git Status prüfen...${NC}"
git status --porcelain

# 2. Backup-Message vom User
if [ -z "$1" ]; then
    echo -e "${YELLOW}💬 Backup-Beschreibung eingeben:${NC}"
    read -p "Beschreibung: " DESCRIPTION
else
    DESCRIPTION="$1"
fi

# 3. Status bestimmen
echo -e "${YELLOW}📋 System-Status wählen:${NC}"
echo "1) working - Alle Module funktional"
echo "2) partial - Einige Module funktional" 
echo "3) broken - System nicht funktionsfähig"
echo "4) milestone - Wichtiger Meilenstein"
read -p "Status (1-4): " STATUS_CHOICE

case $STATUS_CHOICE in
    1) STATUS="working" ;;
    2) STATUS="partial" ;;
    3) STATUS="broken" ;;
    4) STATUS="milestone" ;;
    *) STATUS="working" ;;
esac

# 4. Timestamp generieren
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
TAG_NAME="backup-${TIMESTAMP}-${STATUS}"

echo -e "${BLUE}📦 Backup wird erstellt...${NC}"
echo "Tag: $TAG_NAME"
echo "Beschreibung: $DESCRIPTION"

# 5. Git Operations
echo -e "${YELLOW}📁 Dateien hinzufügen...${NC}"
git add .

echo -e "${YELLOW}💾 Commit erstellen...${NC}"
git commit -m "BACKUP: $DESCRIPTION"

echo -e "${YELLOW}🏷️ Tag erstellen...${NC}"
git tag -a "$TAG_NAME" -m "Backup: $DESCRIPTION"

# 6. GitHub Push (falls Remote existiert)
if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}☁️ Zu GitHub pushen...${NC}"
    git push origin main
    git push origin --tags
    echo -e "${GREEN}✅ Backup erfolgreich zu GitHub gepusht!${NC}"
else
    echo -e "${RED}⚠️ Kein GitHub Remote gefunden!${NC}"
    echo -e "${YELLOW}Führe zuerst das GitHub Setup aus:${NC}"
    echo "Siehe: GITHUB-SETUP-ANLEITUNG.md"
fi

# 7. Backup-Dokumentation aktualisieren
echo -e "${YELLOW}📝 Backup-Dokumentation aktualisieren...${NC}"
cat > "LAST-BACKUP.md" << EOF
# Letztes Backup

**Datum**: $(date)
**Tag**: $TAG_NAME
**Status**: $STATUS
**Beschreibung**: $DESCRIPTION

## Restore-Befehl:
\`\`\`bash
git checkout $TAG_NAME
\`\`\`

## System-Status:
- Alle Module: $(if [ "$STATUS" = "working" ]; then echo "✅ Funktional"; else echo "❓ Prüfen"; fi)
- GUI: $(if [ "$STATUS" = "working" ]; then echo "✅ Repariert"; else echo "❓ Prüfen"; fi)
- Routing: $(if [ "$STATUS" = "working" ]; then echo "✅ Aktiv"; else echo "❓ Prüfen"; fi)

## Nächste Schritte:
- Mathematical Query Detection optimieren
- Performance-Tests durchführen
- Docker Containerization
EOF

echo -e "${GREEN}✅ Backup komplett!${NC}"
echo -e "${BLUE}📋 Backup-Info:${NC}"
echo "  Tag: $TAG_NAME"
echo "  Restore: git checkout $TAG_NAME"
echo "  Dokumentation: LAST-BACKUP.md"

# 8. Letzte 5 Backups anzeigen
echo -e "${BLUE}📚 Letzte Backups:${NC}"
git tag -l "backup-*" | tail -5