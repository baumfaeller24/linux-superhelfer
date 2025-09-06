#!/usr/bin/env python3
"""
Startup script for overnight optimization with enhanced monitoring.
"""

import asyncio
import os
import subprocess
import sys
import time
from datetime import datetime

def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        'optimization_logs',
        'optimization_logs/cycles',
        'optimization_logs/reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory ready: {directory}")

def create_optimization_summary():
    """Create initial optimization summary."""
    summary = {
        'start_time': datetime.now().isoformat(),
        'target_accuracy': 85.0,
        'baseline_accuracy': 80.0,
        'chatgpt_improvements': [
            'Unicode normalization for robust pattern matching',
            '3-class router with clear priorities (Fast → Heavy → Code)',
            'Enhanced mathematical pattern recognition',
            'Score-based routing decisions',
            'Debug information for transparency'
        ],
        'optimization_goals': [
            'Maintain 80%+ routing accuracy',
            'Improve mathematical query detection',
            'Optimize session management performance',
            'Collect data for further improvements'
        ]
    }
    
    with open('optimization_logs/optimization_summary.json', 'w') as f:
        import json
        json.dump(summary, f, indent=2)
    
    print("📋 Optimization summary created")

def print_startup_banner():
    """Print startup banner."""
    print("🌙" + "=" * 68 + "🌙")
    print("🚀 LINUX SUPERHELFER - OVERNIGHT OPTIMIZATION SYSTEM 🚀")
    print("🌙" + "=" * 68 + "🌙")
    print()
    print("📊 Current Status:")
    print("   ✅ ChatGPT routing improvements implemented")
    print("   ✅ Routing accuracy: 80.0% (target: 85%+)")
    print("   ✅ Session management active")
    print("   ✅ Mathematical pattern recognition enhanced")
    print()
    print("🎯 Tonight's Goals:")
    print("   • Run continuous optimization cycles")
    print("   • Test 1000+ queries across all categories")
    print("   • Monitor routing accuracy trends")
    print("   • Collect performance data")
    print("   • Identify further improvement opportunities")
    print()

async def main():
    """Main startup function."""
    print_startup_banner()
    
    # Setup
    print("🔧 Setting up optimization environment...")
    ensure_directories()
    create_optimization_summary()
    
    print()
    print("⚙️  Configuration:")
    
    # Get target hours
    target_hours = 8.0
    if len(sys.argv) > 1:
        try:
            target_hours = float(sys.argv[1])
            print(f"   • Target runtime: {target_hours} hours (from command line)")
        except ValueError:
            print(f"   • Target runtime: {target_hours} hours (default, invalid input)")
    else:
        print(f"   • Target runtime: {target_hours} hours (default)")
    
    print(f"   • Estimated queries: {int(target_hours * 200)} queries")
    print(f"   • Estimated cycles: {int(target_hours * 7.5)} cycles")
    print(f"   • Expected completion: {datetime.now().replace(hour=int(datetime.now().hour + target_hours) % 24).strftime('%H:%M')}")
    
    print()
    print("🚀 Starting optimization in 5 seconds...")
    print("   💡 Tip: Run 'python optimization_monitor.py' in another terminal for live monitoring")
    print()
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        await asyncio.sleep(1)
    
    print("🌙 OPTIMIZATION STARTED!")
    print("=" * 70)
    
    # Import and run optimizer
    from overnight_optimization_runner import OvernightOptimizer
    
    optimizer = OvernightOptimizer()
    await optimizer.run_overnight_optimization(target_hours)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Startup cancelled by user")
        sys.exit(0)