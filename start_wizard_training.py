#!/usr/bin/env python3
"""
Linux Wizard Training Starter
=============================

Startet das Overnight-Training mit verschiedenen Optionen und Monitoring.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_system_resources():
    """Prüft System-Ressourcen vor dem Training"""
    print("🔍 Checking system resources...")
    
    # Check available memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemAvailable:' in line:
                    available_mb = int(line.split()[1]) // 1024
                    print(f"   Available Memory: {available_mb} MB")
                    if available_mb < 1000:
                        print("   ⚠️  Warning: Low memory available")
    except:
        print("   Could not check memory")
    
    # Check disk space
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        print(f"   Disk Space: {result.stdout.split()[10]} available")
    except:
        print("   Could not check disk space")
    
    # Check if ollama is running
    try:
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True)
        if result.returncode == 0:
            print("   ✅ Ollama service is running")
        else:
            print("   ⚠️  Ollama service not detected")
    except:
        print("   Could not check Ollama status")

def setup_training_environment():
    """Richtet die Training-Umgebung ein"""
    print("🛠️  Setting up training environment...")
    
    # Create necessary directories
    Path("wizard_training_logs").mkdir(exist_ok=True)
    Path("wizard_knowledge_base").mkdir(exist_ok=True)
    
    # Stop any existing optimization processes
    try:
        subprocess.run(['pkill', '-f', 'overnight_optimization'], capture_output=True)
        subprocess.run(['pkill', '-f', 'optimization_monitor'], capture_output=True)
        print("   ✅ Stopped existing optimization processes")
    except:
        pass
    
    print("   ✅ Environment ready")

def start_training_with_monitoring():
    """Startet das Training mit Monitoring"""
    print("🚀 Starting Linux Wizard Training...")
    
    # Start the training process
    training_process = subprocess.Popen([
        sys.executable, 'linux_wizard_overnight_training.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(f"   Training Process PID: {training_process.pid}")
    print("   Training started successfully!")
    print("   Logs will be saved to: wizard_training_logs/")
    
    return training_process

def create_monitoring_script():
    """Erstellt ein Monitoring-Script"""
    monitoring_script = """#!/bin/bash
# Linux Wizard Training Monitor

echo "🧙‍♂️ Linux Wizard Training Monitor"
echo "=================================="

while true; do
    clear
    echo "🧙‍♂️ Linux Wizard Training Monitor - $(date)"
    echo "=================================="
    
    # Check if training is running
    if pgrep -f "linux_wizard_overnight_training.py" > /dev/null; then
        echo "✅ Training Status: RUNNING"
        echo "📊 Process Info:"
        ps aux | grep "linux_wizard_overnight_training.py" | grep -v grep
        echo ""
        
        # Show latest log entries
        echo "📝 Latest Training Logs:"
        if [ -d "wizard_training_logs" ]; then
            latest_log=$(ls -t wizard_training_logs/wizard_training_*.log 2>/dev/null | head -1)
            if [ -n "$latest_log" ]; then
                tail -10 "$latest_log"
            fi
        fi
        echo ""
        
        # Show system resources
        echo "💻 System Resources:"
        echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% usage"
        echo "Disk: $(df -h . | tail -1 | awk '{print $4}') available"
        
        # Show training statistics if available
        echo ""
        echo "📈 Training Progress:"
        if [ -d "wizard_training_logs" ]; then
            cycle_count=$(ls wizard_training_logs/cycle_*.json 2>/dev/null | wc -l)
            echo "Cycles Completed: $cycle_count"
            
            latest_cycle=$(ls -t wizard_training_logs/cycle_*.json 2>/dev/null | head -1)
            if [ -n "$latest_cycle" ]; then
                expertise_level=$(grep -o '"expertise_level": "[^"]*"' "$latest_cycle" | cut -d'"' -f4)
                echo "Current Expertise Level: $expertise_level"
            fi
        fi
        
    else
        echo "❌ Training Status: NOT RUNNING"
        echo ""
        echo "To start training, run:"
        echo "python3 start_wizard_training.py"
    fi
    
    echo ""
    echo "Press Ctrl+C to exit monitor"
    sleep 30
done
"""
    
    with open("monitor_wizard_training.sh", "w") as f:
        f.write(monitoring_script)
    
    os.chmod("monitor_wizard_training.sh", 0o755)
    print("   ✅ Monitoring script created: monitor_wizard_training.sh")

def main():
    print("🧙‍♂️ Linux Wizard Overnight Training Setup")
    print("==========================================")
    
    # Check system
    check_system_resources()
    print()
    
    # Setup environment
    setup_training_environment()
    print()
    
    # Create monitoring script
    create_monitoring_script()
    print()
    
    # Ask user for confirmation
    print("🎯 Training Configuration:")
    print("   - Max Cycles: 1000 (or until morning)")
    print("   - Cycle Interval: 30 seconds")
    print("   - Auto-stop: 7:00 AM")
    print("   - Logs: wizard_training_logs/")
    print()
    
    response = input("Start Linux Wizard Training? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        print()
        training_process = start_training_with_monitoring()
        
        print()
        print("🎉 Training Started Successfully!")
        print("================================")
        print(f"Training PID: {training_process.pid}")
        print("Monitor with: ./monitor_wizard_training.sh")
        print("Stop with: pkill -f linux_wizard_overnight_training")
        print()
        print("The system will train overnight and become a Linux Wizard! 🧙‍♂️✨")
        
        # Save PID for easy stopping
        with open("wizard_training.pid", "w") as f:
            f.write(str(training_process.pid))
        
    else:
        print("Training cancelled.")

if __name__ == "__main__":
    main()