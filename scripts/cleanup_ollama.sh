#!/bin/bash
# Ollama GPU Memory Cleanup Script

echo "🧹 Cleaning up Ollama GPU Memory..."

# Zeige aktuell geladene Models
echo "Currently loaded models:"
ollama ps

# Stoppe alle laufenden Ollama Prozesse
echo "Stopping Ollama processes..."
pkill -f ollama || echo "No Ollama processes found"

# Warte kurz
sleep 2

# Starte Ollama neu
echo "Restarting Ollama..."
ollama serve &
sleep 3

# Zeige GPU Memory Status
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Memory Status:"
    nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits
fi

echo "✅ Ollama cleanup completed"