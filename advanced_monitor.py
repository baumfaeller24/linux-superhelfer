#!/usr/bin/env python3
"""
Advanced monitoring dashboard for enhanced overnight optimization.
Shows cost-aware metrics, confusion matrix, and parameter tuning progress.
"""

import json
import os
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_json_safe(path, retries=3, delay=0.2) -> Optional[Dict[str, Any]]:
    """ChatGPT's Cleanup Fix: Safe JSON loading with retries."""
    for attempt in range(retries):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return None
    return None

def load_latest_progress() -> Optional[Dict[str, Any]]:
    """Load latest progress report with absolute path."""
    from pathlib import Path
    
    # ChatGPT's Cleanup Fix 1: Consistent paths
    BASE = Path(__file__).resolve().parent
    LOG_DIR = BASE / "optimization_logs"
    
    return load_json_safe(LOG_DIR / "latest_progress.json")

def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_confusion_matrix(confusion_matrix: Dict[str, int]) -> str:
    """Format confusion matrix as ASCII table."""
    if not confusion_matrix:
        return "No data"
    
    models = ['fast', 'code', 'heavy']
    
    # Parse confusion matrix
    matrix = {}
    for expected in models:
        matrix[expected] = {}
        for actual in models:
            key = f"('{expected}', '{actual}')"
            matrix[expected][actual] = confusion_matrix.get(key, 0)
    
    # Format as table
    lines = []
    lines.append("     │ fast │ code │heavy │")
    lines.append("─────┼──────┼──────┼──────┤")
    
    for expected in models:
        row = f"{expected:4s} │"
        for actual in models:
            count = matrix[expected][actual]
            row += f"{count:5d} │"
        lines.append(row)
    
    return "\n".join(lines)

def format_bandit_stats(bandit_stats: Dict[int, Dict[str, float]]) -> str:
    """Format bandit statistics."""
    if not bandit_stats:
        return "No bandit data"
    
    lines = []
    lines.append("Arm │ Count │ Avg Reward │ Status")
    lines.append("────┼───────┼─────────────┼────────")
    
    best_arm = max(bandit_stats.items(), key=lambda x: x[1]['avg_reward'])
    
    for arm_idx, stats in bandit_stats.items():
        count = stats['count']
        avg_reward = stats['avg_reward']
        status = "🏆 BEST" if arm_idx == best_arm[0] and count > 0 else ""
        
        lines.append(f" {arm_idx}  │ {count:5d} │ {avg_reward:10.1f} │ {status}")
    
    return "\n".join(lines)

def is_stale(report: Dict[str, Any], max_age_minutes: int = 3) -> bool:
    """Check if report is stale."""
    if not report:
        return True
    
    report_time = report.get('timestamp', 0)
    current_time = time.time()
    age_minutes = (current_time - report_time) / 60
    
    return age_minutes > max_age_minutes

def display_advanced_dashboard(report: Dict[str, Any]):
    """Display the advanced monitoring dashboard."""
    clear_screen()
    
    # ChatGPT's Cleanup Fix 3: Terminal robustness
    try:
        import shutil
        terminal_width = shutil.get_terminal_size().columns
    except:
        terminal_width = 80
    
    header_width = min(78, terminal_width - 2)
    
    print("🌙" + "=" * header_width + "🌙")
    print("🚀 LINUX SUPERHELFER - ADVANCED OVERNIGHT OPTIMIZATION 🚀")
    print("🌙" + "=" * header_width + "🌙")
    print()
    
    # ChatGPT's Cleanup Fix 2: Check if data is stale
    stale = is_stale(report)
    if stale:
        print("⚠️  DATA STALE - Last update > 3 minutes ago")
        print()
    
    # Basic stats
    cycle = report.get('total_cycles', 0)
    query_count = 20  # Fixed query count per cycle
    total_queries = report.get('total_queries', 0)
    cycle_time = 0.0  # Not tracked in progress report
    
    print(f"🔄 Cycle: {cycle}")
    print(f"📝 Queries this cycle: {query_count}")
    print(f"📊 Total queries: {total_queries:,}")
    print(f"⏱️  Cycle time: {cycle_time:.1f}s")
    print()
    
    # ChatGPT's Cleanup Fix 2: Display new KPIs
    accuracy = report.get('recent_accuracy', 0)
    cost_score = report.get('recent_cost_score', 0)
    heavy_recall = report.get('recent_heavy_recall')
    hard_negatives = report.get('hard_negatives', 0)
    
    print(f"🔍 Hard Negatives Collected: {hard_negatives}")
    print()
    
    print("🚦 STATUS INDICATORS")
    print("-" * 20)
    
    # Accuracy status
    if accuracy >= 85:
        print(f"✅ Accuracy: EXCELLENT ({accuracy:.1f}%)")
    elif accuracy >= 80:
        print(f"✅ Accuracy: GOOD ({accuracy:.1f}%)")
    else:
        print(f"❌ Accuracy: NEEDS IMPROVEMENT ({accuracy:.1f}%)")
    
    # Cost score status
    if cost_score >= 85:
        print(f"✅ Cost Score: EXCELLENT ({cost_score:.1f})")
    elif cost_score >= 75:
        print(f"✅ Cost Score: GOOD ({cost_score:.1f})")
    else:
        print(f"❌ Cost Score: NEEDS IMPROVEMENT ({cost_score:.1f})")
    
    # Heavy recall status (critical)
    if heavy_recall is None:
        print("❌ Heavy Recall: BELOW TARGET (n/a%)")
    elif heavy_recall >= 95:
        print(f"✅ Heavy Recall: TARGET MET ({heavy_recall:.1f}%)")
    elif heavy_recall >= 90:
        print(f"🟡 Heavy Recall: CLOSE TO TARGET ({heavy_recall:.1f}%)")
    else:
        print(f"❌ Heavy Recall: BELOW TARGET ({heavy_recall:.1f}%)")
    
    print()

    
    # Acceptance criteria check
    print("🎯 ACCEPTANCE CRITERIA")
    print("-" * 22)
    heavy_ok = heavy_recall is not None and heavy_recall >= 95
    cost_ok = cost_score >= 85
    
    heavy_display = f"{heavy_recall:.1f}%" if heavy_recall is not None else "n/a%"
    print(f"Heavy Recall ≥ 95%: {'✅' if heavy_ok else '❌'} ({heavy_display})")
    print(f"Cost Score ≥ 85:    {'✅' if cost_ok else '❌'} ({cost_score:.1f})")
    
    if heavy_ok and cost_ok:
        print("🎉 ALL ACCEPTANCE CRITERIA MET!")
    else:
        print("⚠️  Some criteria not yet met")
    
    print()
    
    # Footer
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕒 Last Update: {current_time}")
    print("🔄 Refreshing every 30 seconds... (Ctrl+C to exit)")

def monitor_advanced_optimization():
    """Main monitoring loop for advanced optimization."""
    print("🚀 Starting advanced optimization monitor...")
    print("Waiting for optimization data...")
    
    try:
        while True:
            report = load_latest_progress()
            
            if report:
                display_advanced_dashboard(report)
            else:
                clear_screen()
                print("🌙 LINUX SUPERHELFER - ADVANCED OPTIMIZATION MONITOR")
                print("=" * 60)
                print()
                print("⏳ Waiting for advanced optimization to start...")
                print("   No progress data found yet.")
                print()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🕒 Current Time: {current_time}")
                print("🔄 Checking every 30 seconds... (Ctrl+C to exit)")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        clear_screen()
        print("👋 Advanced monitoring stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    monitor_advanced_optimization()