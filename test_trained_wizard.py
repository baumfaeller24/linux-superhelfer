#!/usr/bin/env python3
"""
Test Script für den trainierten Linux Wizard
===========================================

Testet die Fähigkeiten des über Nacht trainierten Systems.
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def load_training_results():
    """Lädt die Training-Ergebnisse"""
    state_file = Path("hardcore_wizard_logs/hardcore_state.json")
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return None

def show_training_summary():
    """Zeigt eine Zusammenfassung des Trainings"""
    print("🧙‍♂️ LINUX WIZARD TRAINING RESULTS")
    print("=" * 50)
    
    results = load_training_results()
    if not results:
        print("❌ No training results found!")
        return
    
    print(f"🎯 Final Expertise Level: {results.get('expertise_level', 'Unknown')}")
    print(f"🔥 Hardcore Points: {results.get('hardcore_points', 0):,}")
    print(f"📊 Cycles Completed: {results.get('cycles_completed', 0)}")
    print(f"🧠 Knowledge Gained: {results.get('knowledge_gained', 0)}")
    print(f"🎨 Patterns Learned: {results.get('patterns_learned', 0)}")
    print(f"💪 Stress Tests Passed: {results.get('stress_tests_passed', 0)}")
    print(f"🚨 Crisis Scenarios Survived: {results.get('crisis_scenarios_survived', 0)}")
    print(f"⚡ Performance Score: {results.get('performance_score', 0)}")
    
    # Training Duration
    if 'started_at' in results and 'saved_at' in results:
        start = datetime.fromisoformat(results['started_at'])
        end = datetime.fromisoformat(results['saved_at'])
        duration = end - start
        print(f"⏱️  Training Duration: {duration}")
    
    print()

def test_system_commands():
    """Testet verschiedene System-Commands"""
    print("🔧 TESTING SYSTEM COMMANDS")
    print("=" * 50)
    
    test_commands = [
        ("System Info", "uname -a"),
        ("Memory Usage", "free -h"),
        ("Disk Usage", "df -h /"),
        ("CPU Info", "lscpu | head -10"),
        ("Network Interfaces", "ip addr show | head -20"),
        ("Running Processes", "ps aux | head -10"),
        ("System Load", "uptime"),
        ("Kernel Version", "cat /proc/version")
    ]
    
    for test_name, command in test_commands:
        print(f"\n🧪 {test_name}:")
        print("-" * 30)
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ SUCCESS")
                # Zeige erste paar Zeilen der Ausgabe
                lines = result.stdout.strip().split('\n')[:3]
                for line in lines:
                    print(f"   {line}")
                if len(result.stdout.strip().split('\n')) > 3:
                    print("   ...")
            else:
                print(f"❌ FAILED: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
        except Exception as e:
            print(f"💥 ERROR: {e}")

def test_advanced_commands():
    """Testet erweiterte Linux-Commands"""
    print("\n🚀 TESTING ADVANCED COMMANDS")
    print("=" * 50)
    
    advanced_tests = [
        ("Find Large Files", "find /tmp -type f -size +1M 2>/dev/null | head -5"),
        ("Network Connections", "ss -tuln | head -10"),
        ("System Services", "systemctl list-units --type=service --state=running | head -5"),
        ("Environment Variables", "env | grep -E '^(PATH|HOME|USER)' | head -3"),
        ("File Permissions", "ls -la /etc/passwd /etc/shadow 2>/dev/null"),
        ("Mounted Filesystems", "mount | grep -E '^/' | head -5"),
        ("Kernel Modules", "lsmod | head -5"),
        ("System Logs", "journalctl --no-pager -n 3 2>/dev/null || echo 'No journalctl access'")
    ]
    
    success_count = 0
    total_tests = len(advanced_tests)
    
    for test_name, command in advanced_tests:
        print(f"\n🧪 {test_name}:")
        print("-" * 30)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ SUCCESS")
                lines = result.stdout.strip().split('\n')[:2]
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                success_count += 1
            else:
                print(f"❌ FAILED or NO OUTPUT")
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
        except Exception as e:
            print(f"💥 ERROR: {e}")
    
    print(f"\n📊 Advanced Tests: {success_count}/{total_tests} successful ({success_count/total_tests*100:.1f}%)")

def test_performance_commands():
    """Testet Performance-Monitoring Commands"""
    print("\n⚡ TESTING PERFORMANCE MONITORING")
    print("=" * 50)
    
    perf_tests = [
        ("CPU Usage", "top -bn1 | grep 'Cpu(s)' | head -1"),
        ("Memory Details", "cat /proc/meminfo | grep -E '^(MemTotal|MemFree|MemAvailable):'"),
        ("Load Average", "cat /proc/loadavg"),
        ("Disk I/O", "iostat 2>/dev/null | head -5 || echo 'iostat not available'"),
        ("Network Stats", "cat /proc/net/dev | head -3"),
        ("Process Count", "ps aux | wc -l"),
        ("Open Files", "lsof 2>/dev/null | wc -l || echo 'lsof not available'"),
        ("System Uptime", "cat /proc/uptime")
    ]
    
    for test_name, command in perf_tests:
        print(f"\n🧪 {test_name}:")
        print("-" * 30)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ SUCCESS")
                output = result.stdout.strip()
                if output:
                    lines = output.split('\n')[:2]
                    for line in lines:
                        print(f"   {line}")
            else:
                print(f"❌ FAILED")
        except Exception as e:
            print(f"💥 ERROR: {e}")

def test_wizard_knowledge():
    """Testet das erworbene Wizard-Wissen"""
    print("\n🧙‍♂️ TESTING WIZARD KNOWLEDGE")
    print("=" * 50)
    
    # Lade die gelernten Patterns
    cycle_files = list(Path("hardcore_wizard_logs").glob("hardcore_cycle_*.json"))
    if not cycle_files:
        print("❌ No training cycles found!")
        return
    
    # Analysiere die letzten Zyklen
    recent_cycles = sorted(cycle_files)[-5:]  # Letzte 5 Zyklen
    
    total_success = 0
    total_modules = 0
    module_performance = {}
    
    for cycle_file in recent_cycles:
        with open(cycle_file, 'r') as f:
            cycle_data = json.load(f)
        
        results = cycle_data.get('results', [])
        for module_name, status, result, duration in results:
            if module_name not in module_performance:
                module_performance[module_name] = {'success': 0, 'total': 0, 'avg_time': 0}
            
            module_performance[module_name]['total'] += 1
            if status == 'ok':
                module_performance[module_name]['success'] += 1
                total_success += 1
            total_modules += 1
    
    print(f"📊 Overall Performance: {total_success}/{total_modules} ({total_success/total_modules*100:.1f}%)")
    print("\n🎯 Module Performance:")
    
    for module, perf in module_performance.items():
        success_rate = perf['success'] / perf['total'] * 100
        status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
        print(f"   {status_emoji} {module}: {perf['success']}/{perf['total']} ({success_rate:.1f}%)")

def show_system_status():
    """Zeigt den aktuellen System-Status"""
    print("\n💻 CURRENT SYSTEM STATUS")
    print("=" * 50)
    
    # Prüfe ob das ursprüngliche System noch läuft
    try:
        result = subprocess.run(['pgrep', '-f', 'start_system.py'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Original Linux-Superhelfer System: RUNNING")
        else:
            print("❌ Original Linux-Superhelfer System: NOT RUNNING")
    except:
        print("❓ Original System Status: UNKNOWN")
    
    # Prüfe Ollama
    try:
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Ollama Service: RUNNING")
        else:
            print("❌ Ollama Service: NOT RUNNING")
    except:
        print("❓ Ollama Status: UNKNOWN")
    
    # System Resources
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip().split()[:3]
            print(f"📊 Load Average: {' '.join(load)}")
    except:
        pass
    
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'Mem:' in line:
                    print(f"💾 {line}")
                    break
    except:
        pass

def main():
    print("🧙‍♂️✨ LINUX WIZARD SYSTEM TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Training Summary
    show_training_summary()
    
    # System Status
    show_system_status()
    
    # Basic Commands
    test_system_commands()
    
    # Advanced Commands
    test_advanced_commands()
    
    # Performance Monitoring
    test_performance_commands()
    
    # Wizard Knowledge
    test_wizard_knowledge()
    
    print("\n🎉 WIZARD TEST COMPLETED!")
    print("=" * 60)
    
    # Final Assessment
    results = load_training_results()
    if results:
        level = results.get('expertise_level', 'Unknown')
        points = results.get('hardcore_points', 0)
        
        if points > 20000:
            assessment = "🔥 ELITE LINUX WIZARD"
        elif points > 15000:
            assessment = "⚡ ADVANCED LINUX MASTER"
        elif points > 10000:
            assessment = "💪 SKILLED LINUX WARRIOR"
        elif points > 5000:
            assessment = "🎯 COMPETENT LINUX USER"
        else:
            assessment = "🌱 LINUX APPRENTICE"
        
        print(f"Final Assessment: {assessment}")
        print(f"Expertise Level: {level}")
        print(f"Hardcore Points: {points:,}")

if __name__ == "__main__":
    main()