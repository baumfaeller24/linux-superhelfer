#!/usr/bin/env python3
"""
Real-time monitoring dashboard for autonomous optimization.
Shows live progress and metrics.
"""

import json
import time
import os
from datetime import datetime
import subprocess

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def load_progress():
    """Load current optimization progress."""
    try:
        if os.path.exists('optimization_progress.json'):
            with open('optimization_progress.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def display_dashboard():
    """Display real-time optimization dashboard."""
    while True:
        clear_screen()
        
        print("🚀 AUTONOMOUS LINUX OPTIMIZATION DASHBOARD")
        print("=" * 60)
        print(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if optimization is running
        try:
            result = subprocess.run(['pgrep', '-f', 'autonomous_optimization.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                pid = result.stdout.strip()
                print(f"✅ Optimization Process: RUNNING (PID: {pid})")
            else:
                print("❌ Optimization Process: NOT RUNNING")
        except:
            print("❓ Optimization Process: UNKNOWN")
        
        print()
        
        # Load and display progress
        progress = load_progress()
        if progress:
            metrics = progress.get('metrics', {})
            
            print("📊 CURRENT METRICS")
            print("-" * 30)
            print(f"Total Tests: {metrics.get('total_tests', 0)}")
            print(f"Successful Routes: {metrics.get('successful_routes', 0)}")
            print(f"Failed Routes: {metrics.get('failed_routes', 0)}")
            
            if metrics.get('total_tests', 0) > 0:
                accuracy = (metrics.get('successful_routes', 0) / metrics.get('total_tests', 1)) * 100
                print(f"Routing Accuracy: {accuracy:.1f}%")
            
            print(f"Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
            print(f"Avg Confidence: {metrics.get('avg_confidence', 0):.3f}")
            
            print()
            print("🤖 MODEL USAGE")
            print("-" * 20)
            model_usage = metrics.get('model_usage', {})
            total_usage = sum(model_usage.values())
            
            for model, count in model_usage.items():
                if total_usage > 0:
                    percentage = (count / total_usage) * 100
                    print(f"{model.upper()}: {count} ({percentage:.1f}%)")
                else:
                    print(f"{model.upper()}: {count}")
            
            print()
            print("🕐 TIMING")
            print("-" * 15)
            start_time = datetime.fromisoformat(progress.get('start_time', ''))
            current_time = datetime.fromisoformat(progress.get('current_time', ''))
            runtime = current_time - start_time
            
            print(f"Started: {start_time.strftime('%H:%M:%S')}")
            print(f"Runtime: {str(runtime).split('.')[0]}")
            
            # Recent results
            recent = progress.get('recent_results', [])
            if recent:
                print()
                print("📋 RECENT TESTS")
                print("-" * 20)
                for result in recent[-5:]:  # Show last 5
                    status = "✅" if result.get('routing_correct') else "⚠️"
                    category = result.get('category', 'unknown')
                    model = result.get('actual_model', 'unknown')
                    confidence = result.get('confidence', 0)
                    print(f"{status} {category}: {model} ({confidence:.3f})")
        
        else:
            print("📊 No optimization data available yet...")
            print("Waiting for first test cycle to complete...")
        
        print()
        print("🎮 CONTROLS")
        print("-" * 15)
        print("Press Ctrl+C to exit monitor")
        print("To stop optimization: ./stop_optimization.sh")
        
        # Wait 10 seconds before refresh
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break

if __name__ == "__main__":
    display_dashboard()