#!/usr/bin/env python3
"""
Hardcore Linux Wizard Training Launcher
======================================

Startet das extreme Training mit verschiedenen Härte-Graden.
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path

HARDCORE_PRESETS = {
    "gentle": {
        "max_cycles": 500,
        "cycle_interval_sec": 45,
        "stress_mode": False,
        "chaos_engineering": False,
        "hardcore_multiplier": 1.0,
        "description": "Sanftes Training für Einsteiger"
    },
    "normal": {
        "max_cycles": 1000,
        "cycle_interval_sec": 30,
        "stress_mode": True,
        "chaos_engineering": False,
        "hardcore_multiplier": 1.5,
        "description": "Standard Hardcore Training"
    },
    "extreme": {
        "max_cycles": 2000,
        "cycle_interval_sec": 15,
        "stress_mode": True,
        "chaos_engineering": True,
        "adaptive_difficulty": True,
        "crisis_scenarios": True,
        "hardcore_multiplier": 2.5,
        "description": "Extremes Training mit Chaos Engineering"
    },
    "insane": {
        "max_cycles": 5000,
        "cycle_interval_sec": 10,
        "parallel_modules": 12,
        "module_timeout_sec": 5,
        "stress_mode": True,
        "chaos_engineering": True,
        "adaptive_difficulty": True,
        "crisis_scenarios": True,
        "failure_injection": True,
        "hardcore_multiplier": 4.0,
        "description": "🔥 WAHNSINNIGES Training - nur für Experten!"
    },
    "godmode": {
        "max_cycles": 10000,
        "cycle_interval_sec": 5,
        "parallel_modules": 16,
        "module_timeout_sec": 3,
        "stress_mode": True,
        "chaos_engineering": True,
        "adaptive_difficulty": True,
        "crisis_scenarios": True,
        "failure_injection": True,
        "memory_pressure": True,
        "cpu_pressure": True,
        "hardcore_multiplier": 5.0,
        "description": "💀 GOD MODE - Absolute Härte, nur für Linux-Götter!"
    }
}

def show_system_info():
    """Zeigt System-Informationen"""
    print("🔍 System Analysis:")
    print("=" * 50)
    
    # CPU Info
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_lines = [line for line in f if 'model name' in line]
            if cpu_lines:
                cpu_name = cpu_lines[0].split(':')[1].strip()
                print(f"CPU: {cpu_name}")
                print(f"CPU Cores: {len(cpu_lines)}")
    except:
        print("CPU: Unknown")
    
    # Memory Info
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemTotal:' in line:
                    total_kb = int(line.split()[1])
                    total_gb = total_kb / (1024 * 1024)
                    print(f"Memory: {total_gb:.1f} GB")
                    break
    except:
        print("Memory: Unknown")
    
    # Disk Space
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            print(f"Disk Space: {parts[3]} available")
    except:
        print("Disk: Unknown")
    
    # Load Average
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().split()[:3]
            print(f"Load Average: {' '.join(load)}")
    except:
        print("Load: Unknown")
    
    print()

def check_prerequisites():
    """Prüft Voraussetzungen für Hardcore Training"""
    print("🔧 Checking Prerequisites:")
    print("=" * 50)
    
    issues = []
    
    # Python Version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print("✅ Python version OK")
    
    # Required modules
    required_modules = ['asyncio', 'psutil', 'numpy']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            issues.append(f"Missing module: {module}")
            print(f"❌ {module} missing")
    
    # Memory check
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemAvailable:' in line:
                    available_mb = int(line.split()[1]) // 1024
                    if available_mb < 2000:  # 2GB minimum
                        issues.append(f"Low memory: {available_mb}MB (2GB+ recommended)")
                    else:
                        print(f"✅ Memory OK: {available_mb}MB available")
                    break
    except:
        issues.append("Cannot check memory")
    
    # Disk space check
    try:
        result = subprocess.run(['df', '.'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            available_kb = int(lines[1].split()[3])
            available_gb = available_kb / (1024 * 1024)
            if available_gb < 5:  # 5GB minimum
                issues.append(f"Low disk space: {available_gb:.1f}GB (5GB+ recommended)")
            else:
                print(f"✅ Disk space OK: {available_gb:.1f}GB available")
    except:
        issues.append("Cannot check disk space")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        return False
    else:
        print("\n✅ All prerequisites met!")
        print()
        return True

def show_presets():
    """Zeigt verfügbare Härte-Grade"""
    print("🎯 Available Training Presets:")
    print("=" * 50)
    
    for name, config in HARDCORE_PRESETS.items():
        cycles = config.get('max_cycles', 1000)
        interval = config.get('cycle_interval_sec', 30)
        multiplier = config.get('hardcore_multiplier', 1.0)
        
        print(f"{name.upper():>8}: {config['description']}")
        print(f"         Cycles: {cycles}, Interval: {interval}s, Multiplier: {multiplier}x")
        
        features = []
        if config.get('stress_mode'): features.append("Stress")
        if config.get('chaos_engineering'): features.append("Chaos")
        if config.get('crisis_scenarios'): features.append("Crisis")
        if config.get('adaptive_difficulty'): features.append("Adaptive")
        
        if features:
            print(f"         Features: {', '.join(features)}")
        print()

def create_custom_config():
    """Erstellt eine benutzerdefinierte Konfiguration"""
    print("🛠️  Custom Configuration:")
    print("=" * 50)
    
    config = {}
    
    try:
        config['max_cycles'] = int(input("Max Cycles (1000): ") or "1000")
        config['cycle_interval_sec'] = int(input("Cycle Interval seconds (30): ") or "30")
        config['hardcore_multiplier'] = float(input("Hardcore Multiplier (2.0): ") or "2.0")
        
        print("\nFeatures (y/n):")
        config['stress_mode'] = input("Stress Mode (y): ").lower().strip() != 'n'
        config['chaos_engineering'] = input("Chaos Engineering (y): ").lower().strip() != 'n'
        config['crisis_scenarios'] = input("Crisis Scenarios (y): ").lower().strip() != 'n'
        config['adaptive_difficulty'] = input("Adaptive Difficulty (y): ").lower().strip() != 'n'
        
        return config
        
    except (ValueError, KeyboardInterrupt):
        print("\nUsing default configuration...")
        return HARDCORE_PRESETS['normal']

def save_config(config, filename="hardcore_config.json"):
    """Speichert Konfiguration"""
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to {filename}")

def start_training(config):
    """Startet das Hardcore Training"""
    print("🚀 Starting Hardcore Linux Wizard Training...")
    print("=" * 50)
    
    # Save config
    config_file = "hardcore_config.json"
    save_config(config, config_file)
    
    # Create monitoring script
    create_hardcore_monitor()
    
    # Start training process
    cmd = [sys.executable, 'hardcore_linux_wizard_training.py', '--config', config_file]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Config: {json.dumps(config, indent=2)}")
    print()
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"🔥 Training Process Started!")
        print(f"PID: {process.pid}")
        print(f"Logs: hardcore_wizard_logs/")
        print(f"Monitor: ./monitor_hardcore.sh")
        print(f"Stop: pkill -f hardcore_linux_wizard_training")
        
        # Save PID
        with open("hardcore_training.pid", "w") as f:
            f.write(str(process.pid))
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start training: {e}")
        return None

def create_hardcore_monitor():
    """Erstellt Monitoring-Script für Hardcore Training"""
    monitor_script = '''#!/bin/bash
# Hardcore Linux Wizard Training Monitor

echo "🔥🧙‍♂️ HARDCORE Linux Wizard Training Monitor"
echo "=============================================="

while true; do
    clear
    echo "🔥🧙‍♂️ HARDCORE Training Monitor - $(date)"
    echo "=============================================="
    
    # Check if training is running
    if pgrep -f "hardcore_linux_wizard_training.py" > /dev/null; then
        echo "🔥 Status: HARDCORE TRAINING ACTIVE"
        echo ""
        
        # Process info
        echo "📊 Process Info:"
        ps aux | grep "hardcore_linux_wizard_training.py" | grep -v grep | head -5
        echo ""
        
        # Latest logs
        echo "📝 Latest Training Logs:"
        if [ -d "hardcore_wizard_logs" ]; then
            latest_log=$(ls -t hardcore_wizard_logs/hardcore_wizard_*.log 2>/dev/null | head -1)
            if [ -n "$latest_log" ]; then
                echo "Log: $latest_log"
                tail -8 "$latest_log" | grep -E "(Cycle|HARDCORE|Crisis|Chaos|Level)"
            fi
        fi
        echo ""
        
        # System resources
        echo "💻 System Resources:"
        echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2 " (" int($3/$2*100) "%)"}')"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% usage"
        echo "Load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
        echo "Disk: $(df -h . | tail -1 | awk '{print $4}') available"
        echo ""
        
        # Training statistics
        echo "📈 Hardcore Training Stats:"
        if [ -d "hardcore_wizard_logs" ]; then
            cycle_count=$(ls hardcore_wizard_logs/hardcore_cycle_*.json 2>/dev/null | wc -l)
            echo "Cycles Completed: $cycle_count"
            
            # Latest cycle info
            latest_cycle=$(ls -t hardcore_wizard_logs/hardcore_cycle_*.json 2>/dev/null | head -1)
            if [ -n "$latest_cycle" ]; then
                expertise=$(grep -o '"expertise_level": "[^"]*"' "$latest_cycle" | cut -d'"' -f4)
                stress=$(grep -o '"stress_level": [0-9.]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                points=$(grep -o '"hardcore_points": [0-9]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                
                echo "Expertise Level: $expertise"
                echo "Stress Level: ${stress}x"
                echo "Hardcore Points: $points"
                
                # Crisis info
                crisis=$(grep -o '"crisis_active": [a-z]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                if [ "$crisis" = "true" ]; then
                    echo "🚨 CRISIS SCENARIO ACTIVE!"
                fi
            fi
            
            # State file info
            if [ -f "hardcore_wizard_logs/hardcore_state.json" ]; then
                survived=$(grep -o '"crisis_scenarios_survived": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
                stress_tests=$(grep -o '"stress_tests_passed": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
                echo "Crisis Scenarios Survived: $survived"
                echo "Stress Tests Passed: $stress_tests"
            fi
        fi
        
    else
        echo "❌ Status: NOT RUNNING"
        echo ""
        echo "To start hardcore training:"
        echo "python3 start_hardcore_wizard.py"
        echo ""
        
        # Show last session info if available
        if [ -f "hardcore_wizard_logs/hardcore_state.json" ]; then
            echo "📊 Last Session Stats:"
            cycles=$(grep -o '"cycles_completed": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
            level=$(grep -o '"expertise_level": "[^"]*"' "hardcore_wizard_logs/hardcore_state.json" | cut -d'"' -f4)
            points=$(grep -o '"hardcore_points": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
            
            echo "Final Cycles: $cycles"
            echo "Final Level: $level"
            echo "Final Points: $points"
        fi
    fi
    
    echo ""
    echo "🔥 Press Ctrl+C to exit monitor"
    echo "Commands: pkill -f hardcore_linux_wizard_training (stop)"
    sleep 15
done
'''
    
    with open("monitor_hardcore.sh", "w") as f:
        f.write(monitor_script)
    
    os.chmod("monitor_hardcore.sh", 0o755)
    print("✅ Hardcore monitor created: ./monitor_hardcore.sh")

def main():
    print("🔥🧙‍♂️ HARDCORE LINUX WIZARD TRAINING LAUNCHER")
    print("=" * 60)
    print()
    
    # System info
    show_system_info()
    
    # Prerequisites
    if not check_prerequisites():
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Aborted.")
            return
        print()
    
    # Show presets
    show_presets()
    
    # User selection
    print("Select training intensity:")
    print("1. gentle   - Sanftes Training")
    print("2. normal   - Standard Hardcore")
    print("3. extreme  - Extremes Training")
    print("4. insane   - Wahnsinniges Training")
    print("5. godmode  - Absolute Härte")
    print("6. custom   - Benutzerdefiniert")
    print()
    
    choice = input("Your choice (1-6): ").strip()
    
    config = None
    if choice == '1':
        config = HARDCORE_PRESETS['gentle']
    elif choice == '2':
        config = HARDCORE_PRESETS['normal']
    elif choice == '3':
        config = HARDCORE_PRESETS['extreme']
    elif choice == '4':
        config = HARDCORE_PRESETS['insane']
        print("⚠️  WARNING: INSANE mode is extremely resource intensive!")
        confirm = input("Are you sure? (y/N): ").lower().strip()
        if confirm != 'y':
            print("Wise choice. Selecting 'extreme' instead.")
            config = HARDCORE_PRESETS['extreme']
    elif choice == '5':
        config = HARDCORE_PRESETS['godmode']
        print("💀 WARNING: GOD MODE will push your system to its limits!")
        print("💀 This may cause system instability or crashes!")
        confirm = input("I understand the risks and want to proceed (type 'GODMODE'): ")
        if confirm != 'GODMODE':
            print("Selecting 'extreme' for safety.")
            config = HARDCORE_PRESETS['extreme']
    elif choice == '6':
        config = create_custom_config()
    else:
        print("Invalid choice, using 'normal'")
        config = HARDCORE_PRESETS['normal']
    
    print()
    print(f"Selected: {config.get('description', 'Custom Configuration')}")
    print(f"Max Cycles: {config.get('max_cycles', 1000)}")
    print(f"Interval: {config.get('cycle_interval_sec', 30)}s")
    print(f"Hardcore Multiplier: {config.get('hardcore_multiplier', 1.0)}x")
    print()
    
    final_confirm = input("Start hardcore training? (y/N): ").lower().strip()
    
    if final_confirm == 'y':
        process = start_training(config)
        if process:
            print()
            print("🎉 HARDCORE TRAINING LAUNCHED!")
            print("Your system will become a Linux Wizard overnight! 🔥🧙‍♂️")
            print()
            print("Monitor progress with: ./monitor_hardcore.sh")
    else:
        print("Training cancelled.")

if __name__ == "__main__":
    main()