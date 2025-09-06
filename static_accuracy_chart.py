#!/usr/bin/env python3
"""
Static Accuracy Chart - Zeigt alle bisherigen Daten als Börsenchart
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import glob
import os
from datetime import datetime
import numpy as np

def create_static_chart():
    """Create a static chart with all current data."""
    
    # Load all cycle data from current session
    pattern1 = "optimization_logs/cycle_*_20250906_11*.json"
    pattern2 = "optimization_logs/cycle_*_20250906_12*.json"
    
    cycle_files = glob.glob(pattern1) + glob.glob(pattern2)
    
    if not cycle_files:
        print("❌ No cycle files found!")
        return
    
    # Sort by cycle number
    cycle_files.sort(key=lambda x: int(x.split('cycle_')[1].split('_')[0]))
    
    # Extract data
    timestamps = []
    accuracies = []
    cycle_numbers = []
    
    for file_path in cycle_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            cycle = data.get('cycle', 0)
            accuracy = data.get('accuracy', 0)
            timestamp = data.get('timestamp', datetime.now().timestamp())
            
            dt = datetime.fromtimestamp(timestamp)
            
            timestamps.append(dt)
            accuracies.append(accuracy)
            cycle_numbers.append(cycle)
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            continue
    
    if len(timestamps) < 2:
        print("❌ Not enough data points!")
        return
    
    print(f"✅ Loaded {len(timestamps)} data points")
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Dark theme
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#2d2d2d')
    
    # Title and labels
    ax.set_title('🚀 LINUX SUPERHELFER - ROUTING ACCURACY ENTWICKLUNG', 
                fontsize=18, fontweight='bold', color='white', pad=20)
    ax.set_xlabel('Zeit', fontsize=14, color='white')
    ax.set_ylabel('Genauigkeit (%)', fontsize=14, color='white')
    
    # Grid
    ax.grid(True, alpha=0.3, color='gray', linestyle='--')
    
    # Styling
    ax.tick_params(colors='white', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('white')
    
    # Y-axis range
    ax.set_ylim(0, 100)
    
    # Reference lines
    ax.axhline(y=80, color='gold', linestyle='--', alpha=0.8, linewidth=2, label='🎯 Ziel: 80%')
    ax.axhline(y=65.4, color='red', linestyle='--', alpha=0.8, linewidth=2, label='📊 Alte Baseline: 65.4%')
    
    # Main accuracy line (like stock price)
    ax.plot(timestamps, accuracies, 
           color='#00ff88', linewidth=3, 
           marker='o', markersize=4, 
           markerfacecolor='#00ff88',
           markeredgecolor='white',
           markeredgewidth=1,
           label='📈 Hybrid Routing Accuracy')
    
    # Fill area under curve
    ax.fill_between(timestamps, 0, accuracies, 
                   alpha=0.2, color='#00ff88')
    
    # Add trend line
    if len(accuracies) > 10:
        # Simple moving average
        window = min(10, len(accuracies) // 3)
        moving_avg = []
        for i in range(len(accuracies)):
            start = max(0, i - window + 1)
            avg = np.mean(accuracies[start:i+1])
            moving_avg.append(avg)
        
        ax.plot(timestamps, moving_avg, 
               color='orange', linewidth=2, alpha=0.8,
               linestyle='-', label=f'📊 Trend (MA{window})')
    
    # Format x-axis
    time_range = timestamps[-1] - timestamps[0]
    if time_range.total_seconds() > 3600:  # More than 1 hour
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    else:
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    
    # Statistics
    current_accuracy = accuracies[-1]
    max_accuracy = max(accuracies)
    min_accuracy = min(accuracies)
    avg_accuracy = np.mean(accuracies)
    
    # Trend calculation
    if len(accuracies) >= 10:
        recent_trend = np.mean(accuracies[-10:]) - np.mean(accuracies[-20:-10])
        trend_symbol = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "➡️"
    else:
        recent_trend = 0
        trend_symbol = "➡️"
    
    # Status color
    if current_accuracy >= 80:
        status_color = '#00ff88'
        status = "🎉 EXCELLENT!"
    elif current_accuracy >= 70:
        status_color = '#ffaa00'
        status = "✅ GOOD"
    elif current_accuracy >= 60:
        status_color = '#ff6600'
        status = "⚠️ NEEDS IMPROVEMENT"
    else:
        status_color = '#ff3333'
        status = "❌ POOR"
    
    # Add statistics text box
    stats_text = f"""📊 STATISTIKEN
Aktuell: {current_accuracy:.1f}% {trend_symbol}
Maximum: {max_accuracy:.1f}%
Minimum: {min_accuracy:.1f}%
Durchschnitt: {avg_accuracy:.1f}%
Cycles: {len(cycle_numbers)}
Trend: {recent_trend:+.1f}%

{status}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='white',
           verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='black', alpha=0.8))
    
    # Legend
    ax.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='white', fontsize=12)
    
    # Tight layout
    plt.tight_layout()
    
    # Show
    plt.show()
    
    print(f"📈 Chart zeigt {len(timestamps)} Datenpunkte")
    print(f"🎯 Aktuelle Accuracy: {current_accuracy:.1f}%")
    print(f"📊 Durchschnitt: {avg_accuracy:.1f}%")

if __name__ == "__main__":
    print("📈 STATIC ACCURACY CHART")
    print("=" * 40)
    create_static_chart()