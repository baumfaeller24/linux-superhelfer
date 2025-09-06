#!/bin/bash
# setup_qwen3_coder.sh
# Setup: Qwen3-Coder-30B-A3B-Instruct (Q4_K_M) für lokale Expertennutzung

set -e

echo "🔍 Prüfe, ob Ollama installiert ist..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama nicht gefunden. Bitte installiere Ollama: https://ollama.com"
    exit 1
fi

echo "✅ Ollama gefunden: $(ollama --version)"

echo "🎨 Erstelle Modelfile für qwen3-coder-30b-local (Q4_K_M, 8K Kontext)..."
cat > Modelfile.qwen3-coder << 'EOF'
FROM qwen3-coder:30b
PARAMETER num_ctx 8192
PARAMETER num_gpu 1
EOF

echo "📥 Lade Basis-Modell qwen3-coder:30b herunter..."
ollama pull qwen3-coder:30b

echo "🔄 Erstelle optimiertes Modell qwen3-coder-30b-local..."
ollama create qwen3-coder-30b-local -f Modelfile.qwen3-coder

echo "🧪 Teste das Modell..."
echo "Teste mit einfacher Anfrage..."
ollama run qwen3-coder-30b-local "Schreibe einen kurzen Linux-Befehl um alle Python-Prozesse zu finden." --verbose

echo ""
echo "✅ Modell 'qwen3-coder-30b-local' erfolgreich erstellt und geladen!"
echo ""
echo "💡 Teste mit: ollama run qwen3-coder-30b-local 'Optimiere ein Bash-Skript für Sicherheit.'"
echo "🌐 API-Test: curl http://localhost:11434/api/generate -d '{\"model\": \"qwen3-coder-30b-local\", \"prompt\": \"ps aux | grep python\"}'"
echo ""
echo "ℹ️  Hinweis: Dieses Modell ist für komplexe Aufgaben vorgesehen. Nicht als Default-LLM nutzen."
echo "📊 VRAM-Nutzung: ~20GB (Q4_K_M Quantisierung)"
echo "⏱️  Erwartete Antwortzeit: 8-15 Sekunden bei komplexen Anfragen"

# Cleanup
rm -f Modelfile.qwen3-coder

echo ""
echo "🎉 Setup abgeschlossen! Das Modell ist bereit für Modul A Integration."