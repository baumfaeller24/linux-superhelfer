#!/bin/bash
# Hardcore Linux Wizard Training Monitor

echo "🔥🧙‍♂️ HARDCORE Linux Wizard Training Monitor"
echo "=============================================="

while true; do
    clear
    echo "🔥🧙‍♂️ HARDCORE Training Monitor - $(date)"
    echo "=============================================="
    
    # Check if training is running
    if pgrep -f "hardcore_linux_wizard_training.py" > /dev/null; then
        echo "🔥 Status: HARDCORE TRAINING ACTIVE"
        echo ""
        
        # Process info
        echo "📊 Process Info:"
        ps aux | grep "hardcore_linux_wizard_training.py" | grep -v grep | head -5
        echo ""
        
        # Latest logs
        echo "📝 Latest Training Logs:"
        if [ -d "hardcore_wizard_logs" ]; then
            latest_log=$(ls -t hardcore_wizard_logs/hardcore_wizard_*.log 2>/dev/null | head -1)
            if [ -n "$latest_log" ]; then
                echo "Log: $latest_log"
                tail -8 "$latest_log" | grep -E "(Cycle|HARDCORE|Crisis|Chaos|Level)"
            fi
        fi
        echo ""
        
        # System resources
        echo "💻 System Resources:"
        echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2 " (" int($3/$2*100) "%)"}')"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% usage"
        echo "Load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
        echo "Disk: $(df -h . | tail -1 | awk '{print $4}') available"
        echo ""
        
        # Training statistics
        echo "📈 Hardcore Training Stats:"
        if [ -d "hardcore_wizard_logs" ]; then
            cycle_count=$(ls hardcore_wizard_logs/hardcore_cycle_*.json 2>/dev/null | wc -l)
            echo "Cycles Completed: $cycle_count"
            
            # Latest cycle info
            latest_cycle=$(ls -t hardcore_wizard_logs/hardcore_cycle_*.json 2>/dev/null | head -1)
            if [ -n "$latest_cycle" ]; then
                expertise=$(grep -o '"expertise_level": "[^"]*"' "$latest_cycle" | cut -d'"' -f4)
                stress=$(grep -o '"stress_level": [0-9.]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                points=$(grep -o '"hardcore_points": [0-9]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                
                echo "Expertise Level: $expertise"
                echo "Stress Level: ${stress}x"
                echo "Hardcore Points: $points"
                
                # Crisis info
                crisis=$(grep -o '"crisis_active": [a-z]*' "$latest_cycle" | cut -d':' -f2 | tr -d ' ')
                if [ "$crisis" = "true" ]; then
                    echo "🚨 CRISIS SCENARIO ACTIVE!"
                fi
            fi
            
            # State file info
            if [ -f "hardcore_wizard_logs/hardcore_state.json" ]; then
                survived=$(grep -o '"crisis_scenarios_survived": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
                stress_tests=$(grep -o '"stress_tests_passed": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
                echo "Crisis Scenarios Survived: $survived"
                echo "Stress Tests Passed: $stress_tests"
            fi
        fi
        
    else
        echo "❌ Status: NOT RUNNING"
        echo ""
        echo "To start hardcore training:"
        echo "python3 start_hardcore_wizard.py"
        echo ""
        
        # Show last session info if available
        if [ -f "hardcore_wizard_logs/hardcore_state.json" ]; then
            echo "📊 Last Session Stats:"
            cycles=$(grep -o '"cycles_completed": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
            level=$(grep -o '"expertise_level": "[^"]*"' "hardcore_wizard_logs/hardcore_state.json" | cut -d'"' -f4)
            points=$(grep -o '"hardcore_points": [0-9]*' "hardcore_wizard_logs/hardcore_state.json" | cut -d':' -f2 | tr -d ' ')
            
            echo "Final Cycles: $cycles"
            echo "Final Level: $level"
            echo "Final Points: $points"
        fi
    fi
    
    echo ""
    echo "🔥 Press Ctrl+C to exit monitor"
    echo "Commands: pkill -f hardcore_linux_wizard_training (stop)"
    sleep 15
done
