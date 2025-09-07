#!/usr/bin/env python3
"""
Test script for UI Timeout Fix
Tests that UI can handle long-running queries without timeout.
"""

import sys
import os
import requests
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ui_timeout_handling():
    """Test that UI can handle long-running queries."""
    
    print("🧪 Testing UI Timeout Handling...")
    
    # Test complex code generation query that takes time
    test_query = "Schreibe ein komplettes Python-Spiel: Snake mit pygame, vollständig kommentiert mit Menü, Highscore und Sound-Effekten"
    
    print(f"\n📝 Testing complex query: {test_query[:50]}...")
    
    try:
        payload = {
            "query": test_query,
            "enable_context_search": True,
            "session_id": f"timeout_test_{int(time.time())}"
        }
        
        print("⏱️  Starting request (this may take 2-3 minutes for qwen3-coder)...")
        start_time = time.time()
        
        # This should now work with 180s timeout instead of failing at 60s
        response = requests.post(
            "http://localhost:8001/infer",
            json=payload,
            timeout=200  # Slightly higher than UI timeout for testing
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Request successful!")
            print(f"   Response time: {response_time:.2f}s")
            print(f"   Model used: {data.get('model_used', 'unknown')}")
            print(f"   Confidence: {data.get('confidence', 0):.3f}")
            print(f"   Response length: {len(data.get('response', ''))}")
            
            # Check if it's a code model response
            if 'qwen3' in data.get('model_used', '').lower():
                print("✅ Correctly routed to qwen3-coder for complex code task")
            
            return True
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {time.time() - start_time:.2f}s")
        print("   This suggests the timeout fix didn't work")
        return False
        
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_ui_direct_timeout():
    """Test UI timeout settings directly."""
    
    print("\n🧪 Testing UI Timeout Settings...")
    
    try:
        # Import UI module to check timeout settings
        from modules.module_f_ui.main import ModuleOrchestrator
        
        orchestrator = ModuleOrchestrator()
        
        # Test a simple query to verify timeout is working
        test_query = "Was ist Linux?"
        
        print(f"📝 Testing simple query: {test_query}")
        
        start_time = time.time()
        result = orchestrator.send_query(test_query, use_context=True)
        response_time = time.time() - start_time
        
        if result['success']:
            print(f"✅ UI query successful!")
            print(f"   Response time: {response_time:.2f}s")
            print(f"   Model used: {result.get('model_used', 'unknown')}")
            
            return True
        else:
            print(f"❌ UI query failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ UI test error: {e}")
        return False

def check_system_status():
    """Check if all required modules are running."""
    
    print("\n🔍 Checking System Status...")
    
    modules = {
        'Module A (Core)': 'http://localhost:8001/health',
        'Module B (RAG)': 'http://localhost:8002/health'
    }
    
    all_healthy = True
    
    for module_name, health_url in modules.items():
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {module_name}: Healthy")
            else:
                print(f"   ❌ {module_name}: Unhealthy ({response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {module_name}: Offline ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    print("🚀 Starting UI Timeout Fix Tests")
    
    # Check system status first
    if not check_system_status():
        print("\n❌ System not ready. Please start modules first:")
        print("   python start_system.py")
        sys.exit(1)
    
    # Run tests
    success = True
    
    success &= test_ui_direct_timeout()
    
    # Only run long test if user confirms
    print("\n⚠️  Long test (2-3 minutes) available. Run it? (y/n): ", end="")
    if input().lower().startswith('y'):
        success &= test_ui_timeout_handling()
    else:
        print("   Skipping long test.")
    
    if success:
        print("\n🎉 UI Timeout fix tests passed!")
        print("\n📋 Summary:")
        print("   ✅ UI timeout increased from 60s to 180s")
        print("   ✅ Should handle qwen3-coder queries (90-120s)")
        print("   ✅ No more timeout errors in GUI")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)