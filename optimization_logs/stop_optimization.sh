#!/bin/bash
echo "🛑 Stopping autonomous optimization..."
kill 2168878 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Optimization process stopped"
else
    echo "⚠️  Process may have already stopped"
fi
pkill -f autonomous_optimization.py
echo "🏁 Cleanup complete"
