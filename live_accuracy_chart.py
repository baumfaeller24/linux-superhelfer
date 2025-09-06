#!/usr/bin/env python3
"""
Live Accuracy Chart - Börsenchart-Style für Routing Optimization
Zeigt die Genauigkeit in Echtzeit wie einen Aktienkurs an.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter
import pandas as pd
import json
import glob
import os
from datetime import datetime, timedelta
import numpy as np

class LiveAccuracyChart:
    """Live Chart für Routing Accuracy wie ein Börsenchart."""
    
    def __init__(self, log_directory="optimization_logs"):
        self.log_directory = log_directory
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.setup_chart()
        
        # Data storage
        self.timestamps = []
        self.accuracies = []
        self.cycle_numbers = []
        
        # Chart elements
        self.line = None
        self.fill = None
        
    def setup_chart(self):
        """Setup the chart styling like a stock chart."""
        # Dark theme like trading platforms
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#2d2d2d')
        
        # Title and labels
        self.ax.set_title('🚀 LINUX SUPERHELFER - LIVE ROUTING ACCURACY', 
                         fontsize=16, fontweight='bold', color='white', pad=20)
        self.ax.set_xlabel('Zeit', fontsize=12, color='white')
        self.ax.set_ylabel('Genauigkeit (%)', fontsize=12, color='white')
        
        # Grid
        self.ax.grid(True, alpha=0.3, color='gray', linestyle='--')
        
        # Styling
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        # Y-axis range (0-100%)
        self.ax.set_ylim(0, 100)
        
        # Add baseline reference lines
        self.ax.axhline(y=80, color='gold', linestyle='--', alpha=0.7, label='Ziel: 80%')
        self.ax.axhline(y=65.4, color='red', linestyle='--', alpha=0.7, label='Alte Baseline: 65.4%')
        
        # Legend
        self.ax.legend(loc='upper left', facecolor='#2d2d2d', edgecolor='white')
        
        plt.tight_layout()
    
    def load_latest_data(self):
        """Load the latest cycle data from log files."""
        try:
            # Find all cycle files from current session (starting from 11:47)
            pattern = os.path.join(self.log_directory, "cycle_*_20250906_11*.json")
            cycle_files = glob.glob(pattern)
            
            # Also include files from 12:xx (current hour)
            pattern2 = os.path.join(self.log_directory, "cycle_*_20250906_12*.json")
            cycle_files.extend(glob.glob(pattern2))
            
            if not cycle_files:
                return False
            
            # Sort by cycle number
            cycle_files.sort(key=lambda x: int(x.split('cycle_')[1].split('_')[0]))
            
            new_data = []
            for file_path in cycle_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Extract data
                    cycle = data.get('cycle', 0)
                    accuracy = data.get('accuracy', 0)
                    timestamp = data.get('timestamp', datetime.now().timestamp())
                    
                    # Convert timestamp to datetime
                    dt = datetime.fromtimestamp(timestamp)
                    
                    new_data.append({
                        'cycle': cycle,
                        'accuracy': accuracy,
                        'timestamp': dt
                    })
                    
                except (json.JSONDecodeError, KeyError, FileNotFoundError):
                    continue
            
            if not new_data:
                return False
            
            # Update data arrays
            self.timestamps = [d['timestamp'] for d in new_data]
            self.accuracies = [d['accuracy'] for d in new_data]
            self.cycle_numbers = [d['cycle'] for d in new_data]
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def update_chart(self, frame):
        """Update the chart with new data."""
        # Load latest data
        if not self.load_latest_data():
            return []
        
        if len(self.timestamps) < 2:
            return []
        
        # Clear previous plot elements ONLY if they exist
        if self.line:
            self.line.remove()
        if self.fill:
            self.fill.remove()
        
        # Clear previous text elements
        for txt in self.ax.texts:
            if 'Cycle' in txt.get_text():
                txt.remove()
        
        # Plot the accuracy line (like stock price) - ALWAYS CREATE NEW
        self.line, = self.ax.plot(self.timestamps, self.accuracies, 
                                 color='#00ff88', linewidth=2.5, 
                                 marker='o', markersize=3, 
                                 markerfacecolor='#00ff88',
                                 markeredgecolor='white',
                                 markeredgewidth=0.5)
        
        # Fill area under curve (like volume in stock charts)
        self.fill = self.ax.fill_between(self.timestamps, 0, self.accuracies, 
                                        alpha=0.2, color='#00ff88')
        
        # Update x-axis to show time properly
        if len(self.timestamps) > 1:
            time_range = self.timestamps[-1] - self.timestamps[0]
            if time_range.total_seconds() > 3600:  # More than 1 hour
                self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            else:
                self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        
        # Auto-adjust x-axis
        if self.timestamps:
            margin = timedelta(minutes=2)
            self.ax.set_xlim(self.timestamps[0] - margin, 
                           self.timestamps[-1] + margin)
        
        # Add current stats as text
        if self.accuracies:
            current_accuracy = self.accuracies[-1]
            current_cycle = self.cycle_numbers[-1]
            
            # Calculate trend
            if len(self.accuracies) >= 2:
                trend = self.accuracies[-1] - self.accuracies[-2]
                trend_symbol = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                trend_text = f"{trend:+.1f}%"
            else:
                trend_symbol = "➡️"
                trend_text = "0.0%"
            
            # Status text
            status_text = f"Cycle {current_cycle}: {current_accuracy:.1f}% {trend_symbol} {trend_text}"
            
            # Color based on performance
            if current_accuracy >= 80:
                color = '#00ff88'  # Green
                status = "🎉 EXCELLENT!"
            elif current_accuracy >= 70:
                color = '#ffaa00'  # Orange
                status = "✅ GOOD"
            elif current_accuracy >= 60:
                color = '#ff6600'  # Red-Orange
                status = "⚠️ NEEDS IMPROVEMENT"
            else:
                color = '#ff3333'  # Red
                status = "❌ POOR"
            
            # Clear previous text
            for txt in self.ax.texts:
                if 'Cycle' in txt.get_text():
                    txt.remove()
            
            # Add status text
            self.ax.text(0.02, 0.98, status_text, transform=self.ax.transAxes,
                        fontsize=14, fontweight='bold', color=color,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
            
            self.ax.text(0.02, 0.92, status, transform=self.ax.transAxes,
                        fontsize=12, fontweight='bold', color=color,
                        verticalalignment='top')
        
        return [self.line, self.fill]
    
    def start_live_chart(self, interval=5000):
        """Start the live chart with specified update interval (ms)."""
        print("🚀 Starting Live Accuracy Chart...")
        print("📊 Updating every 5 seconds")
        print("💡 Close the window to stop")
        
        # Animation
        ani = animation.FuncAnimation(self.fig, self.update_chart, 
                                    interval=interval, blit=False, cache_frame_data=False)
        
        # Show the chart
        plt.show()
        
        return ani


def main():
    """Main function to run the live chart."""
    print("📈 LIVE ACCURACY CHART - BÖRSENCHART STYLE")
    print("=" * 50)
    
    # Check if optimization is running
    log_dir = "optimization_logs"
    if not os.path.exists(log_dir):
        print("❌ Optimization logs directory not found!")
        print("   Make sure the optimization is running.")
        return
    
    # Find recent cycle files
    pattern = os.path.join(log_dir, "cycle_*_20250906_*.json")
    recent_files = glob.glob(pattern)
    
    if not recent_files:
        print("❌ No recent optimization data found!")
        print("   Make sure the overnight optimization is running.")
        return
    
    print(f"✅ Found {len(recent_files)} cycle files")
    print("🚀 Starting live chart...")
    
    # Create and start the chart
    chart = LiveAccuracyChart(log_dir)
    
    try:
        chart.start_live_chart(interval=5000)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\n👋 Chart stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()