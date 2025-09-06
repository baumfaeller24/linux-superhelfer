#!/usr/bin/env python3
"""
Test FastAPI server routing directly.
"""

import asyncio
import sys
import os
import uvicorn
from threading import Thread
import time
import requests

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def start_server():
    """Start FastAPI server in background."""
    try:
        # Import here to avoid import issues
        from modules.module_a_core.main import app
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
    except Exception as e:
        print(f"Server start failed: {e}")

def test_endpoints():
    """Test the FastAPI endpoints."""
    
    print("🎯 TESTING FASTAPI ROUTING")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test router status
    try:
        response = requests.get("http://127.0.0.1:8001/router_status", timeout=5)
        print(f"✅ Router status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Router health: {data.get('router_health', {}).get('router_status', 'unknown')}")
    except Exception as e:
        print(f"❌ Router status failed: {e}")
    
    # Test queries
    test_queries = [
        ("Hallo, wie geht es dir?", "fast"),
        ("ps aux | grep python", "code")
    ]
    
    for query, expected_model in test_queries:
        print(f"\n📝 Testing: {query}")
        
        try:
            payload = {"query": query}
            response = requests.post(
                "http://127.0.0.1:8001/infer", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get('model_used', 'unknown')
                routing_info = data.get('routing_info')
                
                print(f"   ✅ Response received")
                print(f"   📊 Model used: {model_used}")
                
                if routing_info:
                    selected_model = routing_info.get('selected_model', 'unknown')
                    print(f"   🎯 Routed to: {selected_model}")
                    print(f"   💭 Reasoning: {routing_info.get('reasoning', 'N/A')[:100]}...")
                    
                    if selected_model == expected_model:
                        print(f"   ✅ CORRECT ROUTING")
                    else:
                        print(f"   ❌ WRONG ROUTING (expected {expected_model})")
                else:
                    print(f"   ⚠️  No routing info (legacy endpoint?)")
                
                response_preview = data.get('response', '')[:100] + "..."
                print(f"   💬 Response: {response_preview}")
                
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n🎉 FASTAPI TEST COMPLETED")

if __name__ == "__main__":
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run tests
    test_endpoints()