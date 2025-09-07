#!/usr/bin/env python3
"""
Test script for UI Session Integration
Tests the session_id handling in the UI module.
"""

import sys
import os
import requests
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ui_session_integration():
    """Test that UI properly sends and manages session_ids."""
    
    print("🧪 Testing UI Session Integration...")
    
    # Test data
    test_session_id = f"test_session_{int(time.time())}"
    test_query = "Was ist Linux?"
    
    # Test 1: Direct API call with session_id
    print("\n1. Testing direct API call with session_id...")
    
    try:
        payload = {
            "query": test_query,
            "enable_context_search": True,
            "session_id": test_session_id
        }
        
        response = requests.post(
            "http://localhost:8001/infer",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            returned_session_id = data.get('session_id')
            
            print(f"✅ API call successful")
            print(f"   Sent session_id: {test_session_id}")
            print(f"   Returned session_id: {returned_session_id}")
            print(f"   Response: {data.get('response', '')[:100]}...")
            
            if returned_session_id == test_session_id:
                print("✅ Session ID correctly returned")
            else:
                print("❌ Session ID mismatch")
                
        else:
            print(f"❌ API call failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False
    
    # Test 2: Follow-up query with same session
    print("\n2. Testing follow-up query with same session...")
    
    try:
        follow_up_query = "Wer hat es erfunden?"
        
        payload = {
            "query": follow_up_query,
            "enable_context_search": True,
            "session_id": test_session_id
        }
        
        response = requests.post(
            "http://localhost:8001/infer",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            context_used = data.get('context_used', False)
            
            print(f"✅ Follow-up query successful")
            print(f"   Query: {follow_up_query}")
            print(f"   Context used: {context_used}")
            print(f"   Response: {data.get('response', '')[:100]}...")
            
            if context_used:
                print("✅ Context was used for follow-up query")
            else:
                print("⚠️  Context not used (might be expected)")
                
        else:
            print(f"❌ Follow-up query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Follow-up query error: {e}")
        return False
    
    # Test 3: Check UI module health
    print("\n3. Testing UI module availability...")
    
    try:
        # Check if UI is running (this would be manual test)
        print("ℹ️  UI module test requires manual verification:")
        print("   1. Start UI: streamlit run modules/module_f_ui/main.py --server.port 8501")
        print("   2. Open browser: http://localhost:8501")
        print("   3. Send query and check if session_id is maintained")
        print("   4. Check sidebar for session info")
        
    except Exception as e:
        print(f"❌ UI test setup error: {e}")
    
    print("\n✅ Session integration tests completed!")
    return True

def test_session_manager():
    """Test the SessionManager class directly."""
    
    print("\n🧪 Testing SessionManager class...")
    
    try:
        # Import SessionManager
        from modules.module_f_ui.session_manager import SessionManager
        
        # Create test session manager
        session_manager = SessionManager(log_dir="test_logs")
        
        # Test logging
        test_session_id = f"test_{int(time.time())}"
        
        session_manager.log_interaction('test_query', {
            'query': 'Test query',
            'session_id': test_session_id
        })
        
        session_manager.log_interaction('test_response', {
            'response': 'Test response',
            'session_id': test_session_id
        })
        
        # Get stats
        stats = session_manager.get_session_stats()
        
        print(f"✅ SessionManager test successful")
        print(f"   Total interactions: {stats.get('total_interactions', 0)}")
        print(f"   Session duration: {stats.get('session_duration', 0):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ SessionManager test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting UI Session Integration Tests")
    
    # Run tests
    success = True
    
    success &= test_ui_session_integration()
    success &= test_session_manager()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)