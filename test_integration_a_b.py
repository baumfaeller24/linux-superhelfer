#!/usr/bin/env python3
"""
Integration test for Module A + Module B context enhancement.
Tests the complete workflow from query to context-enhanced response.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import httpx
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_module_integration():
    """Test Module A + Module B integration."""
    
    print("🔗 Testing Module A + Module B Integration")
    print("=" * 50)
    
    # Test configuration
    module_a_url = "http://localhost:8001"
    module_b_url = "http://localhost:8002"
    timeout = 10.0
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        
        # Test 1: Check both modules are running
        print("\n1. Checking module availability...")
        
        try:
            response_a = await client.get(f"{module_a_url}/health")
            response_b = await client.get(f"{module_b_url}/health")
            
            if response_a.status_code == 200 and response_b.status_code == 200:
                print("   ✅ Both modules are running")
            else:
                print(f"   ❌ Module health check failed: A={response_a.status_code}, B={response_b.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to connect to modules: {e}")
            return False
        
        # Test 2: Upload test document to Module B
        print("\n2. Uploading test document to Module B...")
        
        test_content = """Linux System Administration Commands

df -h: Check disk space usage in human-readable format
free -h: Check memory usage including RAM and swap
top: Display running processes and system resource usage
ps aux: List all running processes with detailed information
systemctl status: Check status of system services
journalctl -f: Follow system logs in real-time
netstat -tulpn: Show network connections and listening ports
iptables -L: List firewall rules
crontab -l: List scheduled cron jobs
mount: Display mounted filesystems"""
        
        try:
            base64_content = base64.b64encode(test_content.encode()).decode()
            
            upload_data = {
                "files": [base64_content],
                "metadata": {
                    "source": "linux_admin_commands.txt",
                    "type": "txt",
                    "category": "system_administration"
                }
            }
            
            response = await client.post(
                f"{module_b_url}/upload",
                json=upload_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"   ✅ Document uploaded: {upload_result['processed_files']} files, {upload_result['total_chunks']} chunks")
            else:
                print(f"   ❌ Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            return False
        
        # Test 3: Test Module B search directly
        print("\n3. Testing Module B search directly...")
        
        test_queries = [
            "How to check disk space?",
            "Memory usage command",
            "System processes"
        ]
        
        for query in test_queries:
            try:
                search_data = {
                    "query": query,
                    "top_k": 3,
                    "threshold": 0.6
                }
                
                response = await client.post(
                    f"{module_b_url}/search",
                    json=search_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    search_result = response.json()
                    print(f"   ✅ '{query}' -> {search_result['total_results']} results")
                    
                    for i, snippet in enumerate(search_result['snippets']):
                        print(f"      {i+1}. Score: {snippet['score']:.3f} - '{snippet['content'][:50]}...'")
                else:
                    print(f"   ❌ Search failed for '{query}': {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Search failed for '{query}': {e}")
        
        # Test 4: Test Module A without context
        print("\n4. Testing Module A without context...")
        
        try:
            infer_data = {
                "query": "How do I check disk space on Linux?",
                "enable_context_search": False
            }
            
            start_time = time.time()
            response = await client.post(
                f"{module_a_url}/infer",
                json=infer_data,
                headers={"Content-Type": "application/json"}
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response generated (no context)")
                print(f"      Confidence: {result['confidence']:.3f}")
                print(f"      Processing time: {processing_time:.2f}s")
                print(f"      Context used: {result.get('context_used', False)}")
                print(f"      Response preview: '{result['response'][:100]}...'")
            else:
                print(f"   ❌ Inference failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Inference failed: {e}")
        
        # Test 5: Test Module A with automatic context
        print("\n5. Testing Module A with automatic context...")
        
        try:
            infer_data = {
                "query": "How do I check disk space on Linux?",
                "enable_context_search": True,
                "context_threshold": 0.6
            }
            
            start_time = time.time()
            response = await client.post(
                f"{module_a_url}/infer",
                json=infer_data,
                headers={"Content-Type": "application/json"}
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response generated (with context)")
                print(f"      Confidence: {result['confidence']:.3f}")
                print(f"      Processing time: {processing_time:.2f}s")
                print(f"      Context used: {result.get('context_used', False)}")
                print(f"      Sources: {result.get('sources', [])}")
                print(f"      Response preview: '{result['response'][:100]}...'")
            else:
                print(f"   ❌ Context-enhanced inference failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Context-enhanced inference failed: {e}")
        
        # Test 6: Test explicit context endpoint
        print("\n6. Testing explicit context endpoint...")
        
        try:
            context_data = {
                "query": "What command shows memory usage?",
                "top_k": 3,
                "threshold": 0.5,
                "max_context_length": 1500
            }
            
            start_time = time.time()
            response = await client.post(
                f"{module_a_url}/infer_with_context",
                json=context_data,
                headers={"Content-Type": "application/json"}
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Context-enhanced response generated")
                print(f"      Confidence: {result['confidence']:.3f}")
                print(f"      Processing time: {processing_time:.2f}s")
                print(f"      Context used: {result['context_used']}")
                print(f"      Sources: {result['sources']}")
                print(f"      Context snippets: {result['context_snippets_count']}")
                print(f"      Attribution: {result.get('attribution', 'None')}")
                print(f"      Response preview: '{result['response'][:100]}...'")
            else:
                print(f"   ❌ Explicit context inference failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Explicit context inference failed: {e}")
        
        # Test 7: Test status endpoints
        print("\n7. Testing status endpoints...")
        
        try:
            response_a = await client.get(f"{module_a_url}/status")
            response_b = await client.get(f"{module_b_url}/status")
            
            if response_a.status_code == 200:
                status_a = response_a.json()
                print(f"   ✅ Module A status: {status_a['status']}")
                print(f"      Knowledge base available: {status_a.get('knowledge_base', {}).get('available', 'Unknown')}")
                print(f"      Features: {list(status_a.get('features', {}).keys())}")
            
            if response_b.status_code == 200:
                status_b = response_b.json()
                print(f"   ✅ Module B status: {status_b['status']}")
                print(f"      Total documents: {status_b.get('components', {}).get('vector_store', {}).get('total_documents', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ Status check failed: {e}")
        
        # Test 8: Performance comparison
        print("\n8. Performance comparison...")
        
        test_query = "How to check system processes in Linux?"
        
        # Without context
        try:
            start_time = time.time()
            response = await client.post(
                f"{module_a_url}/infer",
                json={"query": test_query, "enable_context_search": False}
            )
            time_without_context = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                confidence_without = result['confidence']
                print(f"   📊 Without context: {time_without_context:.2f}s, confidence: {confidence_without:.3f}")
            
        except Exception as e:
            print(f"   ❌ Performance test (no context) failed: {e}")
        
        # With context
        try:
            start_time = time.time()
            response = await client.post(
                f"{module_a_url}/infer",
                json={"query": test_query, "enable_context_search": True}
            )
            time_with_context = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                confidence_with = result['confidence']
                context_used = result.get('context_used', False)
                print(f"   📊 With context: {time_with_context:.2f}s, confidence: {confidence_with:.3f}, context: {context_used}")
                
                if 'time_without_context' in locals():
                    overhead = time_with_context - time_without_context
                    print(f"   📊 Context overhead: {overhead:.2f}s ({overhead/time_without_context*100:.1f}%)")
            
        except Exception as e:
            print(f"   ❌ Performance test (with context) failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration test completed!")
    return True

async def main():
    """Main test function."""
    print("Starting Module A + B Integration Test...")
    print("Make sure both modules are running:")
    print("  Module A: uvicorn modules.module_a_core.main:app --port 8001")
    print("  Module B: uvicorn modules.module_b_rag.main:app --port 8002")
    print()
    
    # Wait a moment for user to start modules if needed
    await asyncio.sleep(2)
    
    success = await test_module_integration()
    
    if success:
        print("\n✅ Integration test completed successfully!")
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())