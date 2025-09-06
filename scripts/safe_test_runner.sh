#!/bin/bash
# Safe Test Runner mit GPU Memory Management

echo "🚀 Starting Safe Test Runner..."

# 1. Cleanup vor dem Test
echo "1. Pre-test cleanup..."
./scripts/cleanup_ollama.sh

# 2. Warte auf Ollama Startup
echo "2. Waiting for Ollama to be ready..."
sleep 5

# 3. Führe Tests aus
echo "3. Running integration tests..."
source venv/bin/activate
python test_integration_a_b.py

# 4. Cleanup nach dem Test
echo "4. Post-test cleanup..."
./scripts/cleanup_ollama.sh

echo "✅ Safe test run completed!"