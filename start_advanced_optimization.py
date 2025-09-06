#!/usr/bin/env python3
"""
Startup script for ChatGPT's advanced overnight optimization system.
"""

import asyncio
import os
import sys
import time
from datetime import datetime

def print_advanced_banner():
    """Print enhanced startup banner."""
    print("🌙" + "=" * 78 + "🌙")
    print("🚀 LINUX SUPERHELFER - CHATGPT'S ADVANCED OPTIMIZATION 🚀")
    print("🌙" + "=" * 78 + "🌙")
    print()
    print("🎯 ChatGPT's Enhanced Features:")
    print("   ✅ Adversarial sampling & hard negatives")
    print("   ✅ Cost-aware metrics with penalty matrix")
    print("   ✅ Multi-armed bandit parameter tuning")
    print("   ✅ Curriculum sampling based on performance")
    print("   ✅ Confusion matrix analysis")
    print("   ✅ Parallel query processing")
    print("   ✅ Atomic JSON writes & robust logging")
    print()
    print("📊 Current Baseline:")
    print("   • Routing accuracy: 80.0%")
    print("   • Heavy recall target: ≥95%")
    print("   • Cost score target: ≥85")
    print()
    print("🎯 Tonight's Advanced Goals:")
    print("   • Test adversarial mutations & edge cases")
    print("   • Optimize router parameters with bandits")
    print("   • Build hard negative bank for future training")
    print("   • Achieve acceptance criteria consistently")
    print("   • Collect comprehensive performance data")
    print()

def setup_environment():
    """Setup environment variables and directories."""
    print("🔧 Setting up advanced optimization environment...")
    
    # Environment variables
    env_vars = {
        'QPC': '100',  # Queries Per Cycle
        'OO_SLEEP_SECS': '30'  # Sleep between cycles
    }
    
    for var, default in env_vars.items():
        if var not in os.environ:
            os.environ[var] = default
        print(f"   • {var}: {os.environ[var]}")
    
    # Directories
    directories = [
        'optimization_logs',
        'optimization_logs/cycles', 
        'conf',
        'reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print()

def show_configuration(target_hours: float):
    """Show optimization configuration."""
    print("⚙️  Advanced Configuration:")
    print(f"   • Target runtime: {target_hours} hours")
    print(f"   • Queries per cycle: {os.environ.get('QPC', '100')}")
    print(f"   • Sleep between cycles: {os.environ.get('OO_SLEEP_SECS', '30')}s")
    print(f"   • Estimated total queries: {int(target_hours * 200)}")
    print(f"   • Estimated cycles: {int(target_hours * 7.5)}")
    
    # Calculate expected completion time
    completion_hour = (datetime.now().hour + target_hours) % 24
    print(f"   • Expected completion: ~{int(completion_hour):02d}:00")
    print()
    
    print("🎰 Parameter Tuning:")
    print("   • 5 parameter sets in bandit pool")
    print("   • ε-greedy selection (ε=0.1)")
    print("   • Cost-score based rewards")
    print()
    
    print("🔍 Hard Negative Collection:")
    print("   • High-cost misroutes collected")
    print("   • Adversarial mutations generated")
    print("   • Oversampling in future cycles")
    print()

async def main():
    """Main startup function."""
    print_advanced_banner()
    
    # Setup
    setup_environment()
    
    # Get target hours
    target_hours = 8.0
    if len(sys.argv) > 1:
        try:
            target_hours = float(sys.argv[1])
            print(f"🕒 Target runtime: {target_hours} hours (from command line)")
        except ValueError:
            print(f"🕒 Target runtime: {target_hours} hours (default, invalid input)")
    else:
        print(f"🕒 Target runtime: {target_hours} hours (default)")
    
    print()
    show_configuration(target_hours)
    
    print("🚀 Starting advanced optimization in 5 seconds...")
    print("   💡 Tip: Run 'python advanced_monitor.py' in another terminal")
    print("   📊 Monitor: Cost score, confusion matrix, bandit progress")
    print()
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        await asyncio.sleep(1)
    
    print("🌙 ADVANCED OPTIMIZATION STARTED!")
    print("=" * 80)
    
    # Import and run advanced optimizer
    from advanced_overnight_optimizer import AdvancedOvernightOptimizer
    
    optimizer = AdvancedOvernightOptimizer()
    await optimizer.run_overnight_optimization(target_hours)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Advanced optimization startup cancelled")
        sys.exit(0)