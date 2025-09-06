#!/bin/bash
# Bulk Upload Script for Knowledge Base Population

echo "🚀 Linux Superhelfer Knowledge Base Population"
echo "=============================================="

# Check if RAG system is running
if ! curl -s http://localhost:8002/health > /dev/null; then
    echo "❌ RAG system not running on port 8002"
    exit 1
fi

echo "✅ RAG system is running"

# Create directories
mkdir -p knowledge_docs external_docs

# Method 1: Run Python population script
echo ""
echo "1. 📚 Running comprehensive population script..."
python3 scripts/populate_knowledge_base.py

# Method 2: Upload existing documentation
echo ""
echo "2. 📁 Uploading existing documentation files..."
if [ -d "docs" ]; then
    for file in docs/*.txt docs/*.md; do
        if [ -f "$file" ]; then
            echo "Uploading $(basename "$file")..."
            curl -s -X POST http://localhost:8002/upload \
                -F "files=@$file" > /dev/null
        fi
    done
fi

# Method 3: Create and upload system-specific docs
echo ""
echo "3. 🖥️  Creating system-specific documentation..."

# Current system info
echo "Current System Information and Commands

SYSTEM DETAILS:
$(uname -a)
$(lsb_release -a 2>/dev/null || cat /etc/os-release)

HARDWARE INFO:
CPU: $(lscpu | grep 'Model name' | cut -d: -f2 | xargs)
Memory: $(free -h | grep Mem | awk '{print $2}')
Disk: $(df -h / | tail -1 | awk '{print $2}')

INSTALLED PACKAGES (sample):
$(dpkg -l | head -20 2>/dev/null || rpm -qa | head -20 2>/dev/null || echo "Package manager not detected")

RUNNING SERVICES:
$(systemctl list-units --type=service --state=running | head -10)

NETWORK CONFIGURATION:
$(ip addr show | grep -E 'inet |^[0-9]')
" > knowledge_docs/current_system_info.txt

curl -s -X POST http://localhost:8002/upload \
    -F "files=@knowledge_docs/current_system_info.txt" > /dev/null

echo "✅ Uploaded current system info"

# Method 4: Download and process man pages
echo ""
echo "4. 📖 Processing essential man pages..."

essential_commands=(
    "ls" "grep" "find" "awk" "sed" "ps" "top" "df" "du" "free"
    "netstat" "ss" "systemctl" "journalctl" "crontab" "chmod" 
    "chown" "tar" "rsync" "ssh" "scp" "curl" "wget" "vim" "nano"
)

for cmd in "${essential_commands[@]}"; do
    if man "$cmd" > /dev/null 2>&1; then
        echo "Processing man page for $cmd..."
        man "$cmd" | col -b > "knowledge_docs/man_$cmd.txt"
        curl -s -X POST http://localhost:8002/upload \
            -F "files=@knowledge_docs/man_$cmd.txt" > /dev/null
    fi
done

# Check final status
echo ""
echo "5. 📊 Final Knowledge Base Status:"
curl -s http://localhost:8002/status | jq '.components.vector_store'

echo ""
echo "🎉 Knowledge Base Population Complete!"
echo ""
echo "Next steps:"
echo "- Test search: curl -X POST http://localhost:8002/search -H 'Content-Type: application/json' -d '{\"query\": \"memory\", \"top_k\": 3}'"
echo "- Test AI with context: curl -X POST http://localhost:8001/infer_with_context -H 'Content-Type: application/json' -d '{\"query\": \"How to check memory?\"}'"