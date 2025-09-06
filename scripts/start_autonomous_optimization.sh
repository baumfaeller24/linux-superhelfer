#!/bin/bash

# Autonomous Linux Superhelfer Optimization Starter
# Runs continuous optimization while user is away

echo "🚀 Starting Autonomous Linux Optimization System"
echo "================================================"

# Check if system is running
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ Linux Superhelfer system not running on port 8001"
    echo "Please start the system first with: python start_system.py"
    exit 1
fi

if ! curl -s http://localhost:8002/health > /dev/null; then
    echo "❌ Knowledge base not running on port 8002"
    echo "Please start the system first with: python start_system.py"
    exit 1
fi

echo "✅ System health check passed"
echo ""

# Create optimization directory
mkdir -p optimization_logs
cd optimization_logs

# Start optimization with nohup for background execution
echo "🔄 Starting autonomous optimization process..."
echo "📁 Logs will be saved in: $(pwd)"
echo "🛑 To stop: kill \$(pgrep -f autonomous_optimization.py)"
echo ""

# Run optimization in background
nohup python3 ../scripts/autonomous_optimization.py > autonomous_optimization_output.log 2>&1 &

OPTIMIZATION_PID=$!
echo "✅ Optimization process started with PID: $OPTIMIZATION_PID"
echo "📊 Monitor progress with: tail -f optimization_logs/autonomous_optimization.log"
echo "📈 View live output with: tail -f optimization_logs/autonomous_optimization_output.log"
echo ""

# Create stop script
cat > stop_optimization.sh << EOF
#!/bin/bash
echo "🛑 Stopping autonomous optimization..."
kill $OPTIMIZATION_PID 2>/dev/null
if [ \$? -eq 0 ]; then
    echo "✅ Optimization process stopped"
else
    echo "⚠️  Process may have already stopped"
fi
pkill -f autonomous_optimization.py
echo "🏁 Cleanup complete"
EOF

chmod +x stop_optimization.sh

echo "🎯 AUTONOMOUS OPTIMIZATION ACTIVE"
echo "================================="
echo "The system will now:"
echo "  • Test Linux expertise continuously"
echo "  • Analyze routing performance"
echo "  • Generate optimization recommendations"
echo "  • Save progress every cycle"
echo ""
echo "📋 Control Commands:"
echo "  Stop optimization: ./stop_optimization.sh"
echo "  View progress: tail -f autonomous_optimization.log"
echo "  Check system: curl http://localhost:8001/health"
echo ""
echo "🕐 The optimization will run until you return and stop it."
echo "💡 Estimated improvement cycle: 5 minutes per iteration"
echo ""
echo "Happy optimizing! 🚀"