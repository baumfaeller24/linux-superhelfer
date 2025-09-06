#!/bin/bash
# Overnight Model Download Script for Qwen3-Coder Integration
# Run this before going to sleep: ./download_models_overnight.sh

echo "🌙 Starting overnight model download..."
echo "Started at: $(date)"
echo "This will download ~70GB of models"
echo ""

# Create log file
LOG_FILE="model_download_$(date +%Y%m%d_%H%M%S).log"
echo "Log file: $LOG_FILE"

# Function to download with progress and error handling
download_model() {
    local model=$1
    local size=$2
    
    echo "📥 Downloading $model (~$size)..."
    echo "Started $model at $(date)" >> "$LOG_FILE"
    
    if ollama pull "$model" 2>&1 | tee -a "$LOG_FILE"; then
        echo "✅ $model download completed at $(date)"
        echo "✅ $model completed at $(date)" >> "$LOG_FILE"
    else
        echo "❌ $model download failed at $(date)"
        echo "❌ $model failed at $(date)" >> "$LOG_FILE"
    fi
    echo ""
}

# Download models in order of importance
echo "Starting downloads in priority order..."
echo ""

# Priority 1: Fast model (essential)
download_model "llama3.2:11b-vision" "8GB"

# Priority 2: Code model (most important for our use case)
download_model "qwen3-coder:30b-q4" "20GB"

# Priority 3: Heavy model (fallback)
download_model "llama3.1:70b" "42GB"

# Summary
echo "🎉 All downloads completed!"
echo "Finished at: $(date)"
echo ""
echo "📊 Download Summary:"
ollama list | grep -E "(llama3.2:11b-vision|qwen3-coder:30b-q4|llama3.1:70b)"
echo ""
echo "💾 Total disk usage:"
du -sh ~/.ollama/models/ 2>/dev/null || echo "Could not calculate disk usage"
echo ""
echo "🚀 System ready for Qwen3-Coder integration!"
echo "Next steps:"
echo "  1. pip install pynvml tiktoken"
echo "  2. python test_qwen3_integration.py"
echo "  3. Start Module A: python modules/module_a_core/main.py"

# Final log entry
echo "All downloads completed at $(date)" >> "$LOG_FILE"
echo "Log saved to: $LOG_FILE"