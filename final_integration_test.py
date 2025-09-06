#!/usr/bin/env python3
"""
Final Integration Test - FastAPI Server with Intelligent Routing
Tests the complete system including FastAPI endpoints.
"""

import asyncio
import sys
import os
import time
import json
import requests
import subprocess
from datetime import datetime
from threading import Thread

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

class FastAPITestServer:
    """Manages FastAPI test server lifecycle."""
    
    def __init__(self):
        self.process = None
        self.server_url = "http://127.0.0.1:8001"
    
    def start(self):
        """Start FastAPI server."""
        print("🚀 Starting FastAPI server...")
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        # Start server process
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "modules.module_a_core.main:app", 
             "--host", "127.0.0.1", "--port", "8001", "--log-level", "error"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(f"{self.server_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Server started successfully (attempt {i+1})")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Server failed to start within 30 seconds")
        return False
    
    def stop(self):
        """Stop FastAPI server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("🛑 Server stopped")

def test_fastapi_endpoints(server_url: str):
    """Test all FastAPI endpoints."""
    
    print("\n🌐 TESTING FASTAPI ENDPOINTS")
    print("=" * 50)
    
    results = {}
    
    # Test health endpoint
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        results["health"] = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
        print(f"   ✅ /health: {response.status_code}")
    except Exception as e:
        results["health"] = {"success": False, "error": str(e)}
        print(f"   ❌ /health: {e}")
    
    # Test router status endpoint
    try:
        response = requests.get(f"{server_url}/router_status", timeout=5)
        results["router_status"] = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
        print(f"   ✅ /router_status: {response.status_code}")
    except Exception as e:
        results["router_status"] = {"success": False, "error": str(e)}
        print(f"   ❌ /router_status: {e}")
    
    # Test status endpoint
    try:
        response = requests.get(f"{server_url}/status", timeout=5)
        results["status"] = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
        print(f"   ✅ /status: {response.status_code}")
    except Exception as e:
        results["status"] = {"success": False, "error": str(e)}
        print(f"   ❌ /status: {e}")
    
    return results

def test_intelligent_routing(server_url: str):
    """Test intelligent routing with different query types."""
    
    print("\n🧠 TESTING INTELLIGENT ROUTING")
    print("=" * 50)
    
    test_queries = [
        {
            "query": "Hallo, wie geht es dir heute?",
            "expected_model_type": "fast",
            "test_name": "simple_greeting"
        },
        {
            "query": "Zeige mir alle Python-Prozesse mit ps aux | grep python",
            "expected_model_type": "code", 
            "test_name": "linux_command"
        },
        {
            "query": "Schreibe eine Python-Funktion zum Kopieren von Dateien",
            "expected_model_type": "code",
            "test_name": "code_generation"
        }
    ]
    
    routing_results = []
    
    for test_case in test_queries:
        print(f"\n   📝 Testing: {test_case['test_name']}")
        print(f"      Query: {test_case['query']}")
        
        try:
            payload = {"query": test_case["query"]}
            start_time = time.time()
            
            response = requests.post(
                f"{server_url}/infer",
                json=payload,
                timeout=60  # Longer timeout for model generation
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract routing information
                routing_info = data.get('routing_info', {})
                model_used = data.get('model_used', 'unknown')
                selected_model = routing_info.get('selected_model', 'unknown')
                
                # Check if correct model type was selected
                correct_routing = False
                if test_case['expected_model_type'] == 'fast':
                    correct_routing = 'llama3.2:3b' in model_used or selected_model == 'fast'
                elif test_case['expected_model_type'] == 'code':
                    correct_routing = 'qwen3-coder' in model_used or selected_model == 'code'
                
                result = {
                    "test_name": test_case['test_name'],
                    "query": test_case['query'],
                    "success": True,
                    "correct_routing": correct_routing,
                    "expected_model_type": test_case['expected_model_type'],
                    "selected_model": selected_model,
                    "model_used": model_used,
                    "response_time": round(response_time, 2),
                    "response_length": len(data.get('response', '')),
                    "confidence": data.get('confidence', 0),
                    "routing_reasoning": routing_info.get('reasoning', 'N/A')
                }
                
                status = "✅" if correct_routing else "⚠️"
                print(f"      {status} Model: {selected_model} ({model_used})")
                print(f"      ⏱️  Time: {response_time:.2f}s")
                print(f"      🎯 Confidence: {data.get('confidence', 0):.3f}")
                print(f"      💭 Reasoning: {routing_info.get('reasoning', 'N/A')[:80]}...")
                
            else:
                result = {
                    "test_name": test_case['test_name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": round(response_time, 2)
                }
                print(f"      ❌ HTTP {response.status_code}: {response.text}")
            
            routing_results.append(result)
            
        except Exception as e:
            result = {
                "test_name": test_case['test_name'],
                "success": False,
                "error": str(e),
                "response_time": round(time.time() - start_time, 2)
            }
            routing_results.append(result)
            print(f"      ❌ Error: {e}")
    
    return routing_results

def test_legacy_endpoint(server_url: str):
    """Test legacy single model endpoint."""
    
    print("\n🔄 TESTING LEGACY ENDPOINT")
    print("=" * 50)
    
    try:
        payload = {"query": "Hallo, wie geht es dir?"}
        start_time = time.time()
        
        response = requests.post(
            f"{server_url}/infer_single_model",
            json=payload,
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            model_used = data.get('model_used', 'unknown')
            
            print(f"   ✅ Legacy endpoint working")
            print(f"   📊 Model used: {model_used}")
            print(f"   ⏱️  Response time: {response_time:.2f}s")
            
            return {
                "success": True,
                "model_used": model_used,
                "response_time": round(response_time, 2),
                "response_length": len(data.get('response', ''))
            }
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}

def generate_final_report(endpoint_results, routing_results, legacy_result):
    """Generate comprehensive final report."""
    
    print("\n📊 FINAL INTEGRATION TEST REPORT")
    print("=" * 60)
    
    # Calculate statistics
    total_endpoint_tests = len(endpoint_results)
    successful_endpoints = sum(1 for r in endpoint_results.values() if r.get('success', False))
    
    total_routing_tests = len(routing_results)
    successful_routing = sum(1 for r in routing_results if r.get('success', False))
    correct_routing = sum(1 for r in routing_results if r.get('correct_routing', False))
    
    # Performance metrics
    avg_response_time = 0
    if routing_results:
        response_times = [r.get('response_time', 0) for r in routing_results if r.get('success', False)]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"📋 ENDPOINT TESTS:")
    print(f"   Total: {total_endpoint_tests}")
    print(f"   Successful: {successful_endpoints}")
    print(f"   Success Rate: {(successful_endpoints/total_endpoint_tests*100):.1f}%")
    
    print(f"\n🧠 ROUTING TESTS:")
    print(f"   Total: {total_routing_tests}")
    print(f"   Successful: {successful_routing}")
    print(f"   Correct Routing: {correct_routing}")
    print(f"   Routing Accuracy: {(correct_routing/total_routing_tests*100):.1f}%")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"   Average Response Time: {avg_response_time:.2f}s")
    print(f"   Legacy Endpoint: {'✅ Working' if legacy_result.get('success') else '❌ Failed'}")
    
    # Overall status
    overall_success = (
        successful_endpoints == total_endpoint_tests and
        successful_routing == total_routing_tests and
        correct_routing >= total_routing_tests * 0.8  # 80% routing accuracy threshold
    )
    
    print(f"\n🎯 OVERALL STATUS:")
    if overall_success:
        print("   ✅ ALL SYSTEMS OPERATIONAL")
        print("   🚀 INTELLIGENT ROUTING FULLY FUNCTIONAL")
        print("   🎉 READY FOR PRODUCTION DEPLOYMENT")
    else:
        print("   ⚠️  SOME ISSUES DETECTED")
        print("   🔧 REVIEW FAILED TESTS")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "overall_success": overall_success,
            "endpoint_success_rate": round(successful_endpoints/total_endpoint_tests*100, 1),
            "routing_accuracy": round(correct_routing/total_routing_tests*100, 1),
            "avg_response_time": round(avg_response_time, 2)
        },
        "endpoint_results": endpoint_results,
        "routing_results": routing_results,
        "legacy_result": legacy_result
    }
    
    filename = f"final_integration_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {filename}")
    
    return overall_success

def main():
    """Run final integration test."""
    
    print("🎯 FINAL INTEGRATION TEST - QWEN3-CODER SYSTEM")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Start FastAPI server
    server = FastAPITestServer()
    
    try:
        if not server.start():
            print("❌ Failed to start server. Exiting.")
            return False
        
        # Run tests
        endpoint_results = test_fastapi_endpoints(server.server_url)
        routing_results = test_intelligent_routing(server.server_url)
        legacy_result = test_legacy_endpoint(server.server_url)
        
        # Generate final report
        success = generate_final_report(endpoint_results, routing_results, legacy_result)
        
        return success
        
    finally:
        # Always stop server
        server.stop()

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    sys.exit(exit_code)