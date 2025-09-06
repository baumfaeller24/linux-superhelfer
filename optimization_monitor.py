#!/usr/bin/env python3
"""
Real-time monitoring dashboard for overnight optimization.
Shows live progress and statistics.
"""

import json
import os
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_latest_progress() -> Optional[Dict[str, Any]]:
    """Load latest progress report."""
    try:
        with open("optimization_logs/latest_progress.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_accuracy_trend(accuracy_history: list) -> str:
    """Format accuracy trend with simple ASCII chart."""
    if not accuracy_history or len(accuracy_history) < 2:
        return "No trend data"
    
    recent = accuracy_history[-5:]
    trend_chars = []
    
    for i in range(1, len(recent)):
        if recent[i]['accuracy'] > recent[i-1]['accuracy']:
            trend_chars.append('↗')
        elif recent[i]['accuracy'] < recent[i-1]['accuracy']:
            trend_chars.append('↘')
        else:
            trend_chars.append('→')
    
    return ''.join(trend_chars)

def display_dashboard(report: Dict[str, Any]):
    """Display the monitoring dashboard."""
    clear_screen()
    
    print("🌙 LINUX SUPERHELFER - OVERNIGHT OPTIMIZATION MONITOR")
    print("=" * 70)
    print()
    
    # Basic stats
    runtime_str = format_duration(report['runtime_hours'] * 3600)
    print(f"⏱️  Runtime: {runtime_str} ({report['runtime_hours']:.1f} hours)")
    print(f"🔄 Cycles: {report['total_cycles']}")
    print(f"📝 Queries: {report['total_queries']:,}")
    print(f"⚡ Speed: {report['queries_per_hour']:.0f} queries/hour, {report['cycles_per_hour']:.1f} cycles/hour")
    print()
    
    # Accuracy metrics
    print("📊 ACCURACY METRICS")
    print("-" * 30)
    print(f"Overall Accuracy: {report['overall_accuracy']:.1f}%")
    print(f"Recent Accuracy:  {report['recent_accuracy']:.1f}%")
    
    # Accuracy trend
    if 'accuracy_trend' in report and report['accuracy_trend']:
        trend = format_accuracy_trend(report['accuracy_trend'])
        print(f"Trend (last 5):   {trend}")
    print()
    
    # Routing distribution
    print("🎯 ROUTING DISTRIBUTION")
    print("-" * 30)
    routing = report['routing_distribution']
    print(f"Fast Model:  {routing['fast']:.1f}%")
    print(f"Code Model:  {routing['code']:.1f}%")
    print(f"Heavy Model: {routing['heavy']:.1f}%")
    print()
    
    # Recent accuracy history (last 10 cycles)
    if 'accuracy_trend' in report and report['accuracy_trend']:
        print("📈 RECENT ACCURACY HISTORY")
        print("-" * 30)
        recent_cycles = report['accuracy_trend'][-10:]
        
        for cycle_data in recent_cycles:
            cycle_num = cycle_data['cycle']
            accuracy = cycle_data['accuracy']
            timestamp = datetime.fromtimestamp(cycle_data['timestamp'])
            time_str = timestamp.strftime("%H:%M:%S")
            
            # Simple bar chart
            bar_length = int(accuracy / 5)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            print(f"Cycle {cycle_num:3d} [{time_str}]: {bar} {accuracy:5.1f}%")
        print()
    
    # Status and next update
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕒 Last Update: {current_time}")
    print("🔄 Refreshing every 30 seconds... (Ctrl+C to exit)")
    print()
    
    # Performance indicators
    if report['recent_accuracy'] >= 85:
        print("🎉 EXCELLENT: System performing above target!")
    elif report['recent_accuracy'] >= 80:
        print("✅ GOOD: System meeting target accuracy")
    elif report['recent_accuracy'] >= 75:
        print("⚠️  WARNING: Accuracy below target")
    else:
        print("❌ CRITICAL: Significant accuracy issues")

def monitor_optimization():
    """Main monitoring loop."""
    print("🚀 Starting optimization monitor...")
    print("Waiting for optimization data...")
    
    try:
        while True:
            report = load_latest_progress()
            
            if report:
                display_dashboard(report)
            else:
                clear_screen()
                print("🌙 LINUX SUPERHELFER - OVERNIGHT OPTIMIZATION MONITOR")
                print("=" * 70)
                print()
                print("⏳ Waiting for optimization to start...")
                print("   No progress data found yet.")
                print()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🕒 Current Time: {current_time}")
                print("🔄 Checking every 30 seconds... (Ctrl+C to exit)")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        clear_screen()
        print("👋 Monitoring stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    monitor_optimization()