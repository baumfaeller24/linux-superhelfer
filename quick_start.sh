#!/bin/bash
# Quick Start Script for Linux Superhelfer System

echo "🎯 STARTING LINUX SUPERHELFER SYSTEM"
echo "===================================================="

# Activate virtual environment and set Python path
source venv/bin/activate
export PYTHONPATH=.

# Function to start module in background
start_module() {
    local name=$1
    local module=$2
    local port=$3
    
    echo "🚀 Starting $name on port $port..."
    
    # Start module in background (with venv activated)
    source venv/bin/activate && python -m uvicorn $module --host 0.0.0.0 --port $port --log-level error > /dev/null 2>&1 &
    local pid=$!
    
    # Save PID for later cleanup
    echo $pid > "${name// /_}.pid"
    
    # Wait a moment for startup
    sleep 2
    
    # Check if process is still running
    if kill -0 $pid 2>/dev/null; then
        echo "   ✅ $name started (PID: $pid)"
        return 0
    else
        echo "   ❌ $name failed to start"
        return 1
    fi
}

# Start modules
echo ""
start_module "Module_A_Core" "modules.module_a_core.main:app" 8001
start_module "Module_B_RAG" "modules.module_b_rag.main:app" 8002

echo ""
echo "⏳ Waiting for modules to initialize..."
sleep 3

echo ""
echo "🔍 CHECKING MODULE HEALTH"
echo "------------------------------------"

# Check Module A
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ Module A (Core Intelligence) - HEALTHY"
else
    echo "   ❌ Module A (Core Intelligence) - NOT RESPONDING"
fi

# Check Module B  
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ✅ Module B (RAG Knowledge) - HEALTHY"
else
    echo "   ❌ Module B (RAG Knowledge) - NOT RESPONDING"
fi

echo ""
echo "🎉 SYSTEM READY FOR TESTING!"
echo "===================================================="
echo "📋 AVAILABLE ENDPOINTS:"
echo "   • Module A: http://localhost:8001"
echo "     - /infer (Intelligent Routing) ⭐ NEW!"
echo "     - /router_status (Model Router Info)"
echo "     - /health, /status"
echo ""
echo "   • Module B: http://localhost:8002" 
echo "     - /search (Knowledge Search)"
echo "     - /health, /status"
echo ""
echo "🧠 INTELLIGENT ROUTING ACTIVE:"
echo "   • Simple queries → llama3.2:3b (Fast, ~1s)"
echo "   • Linux/Code → qwen3-coder-30b-local (Code, ~15s)"
echo "   • Complex → llama3.1:70b (Heavy, ~30s)"
echo ""
echo "🎯 TEST THESE QUERIES:"
echo "   1. 'Hallo, wie geht es dir?' → Fast Model"
echo "   2. 'ps aux | grep python' → Code Model" 
echo "   3. 'Schreibe eine Python-Funktion' → Code Model"
echo ""
echo "🛑 TO STOP: Run './stop_system.sh'"
echo "===================================================="