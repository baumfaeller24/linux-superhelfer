#!/bin/bash
# Stop Script for Linux Superhelfer System

echo "🛑 STOPPING LINUX SUPERHELFER SYSTEM"
echo "===================================================="

# Function to stop module by PID file
stop_module() {
    local name=$1
    local pid_file="${name// /_}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🛑 Stopping $name (PID: $pid)..."
        
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            sleep 2
            
            # Check if still running
            if kill -0 $pid 2>/dev/null; then
                echo "   ⚠️  Force killing $name..."
                kill -9 $pid
            fi
            echo "   ✅ $name stopped"
        else
            echo "   ✅ $name already stopped"
        fi
        
        rm -f "$pid_file"
    else
        echo "   ⚠️  No PID file for $name"
    fi
}

# Stop modules
stop_module "Module_A_Core"
stop_module "Module_B_RAG"

# Also kill any remaining uvicorn processes
echo ""
echo "🧹 Cleaning up any remaining processes..."
pkill -f "uvicorn.*module" 2>/dev/null || true
pkill -f "python.*uvicorn" 2>/dev/null || true

echo ""
echo "✅ SYSTEM STOPPED"
echo "===================================================="