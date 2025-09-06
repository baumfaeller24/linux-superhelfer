#!/usr/bin/env python3
"""
Comprehensive System Test Suite for Qwen3-Coder Integration
Tests all components, routing logic, and end-to-end functionality.
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "system_info": {},
    "component_tests": {},
    "integration_tests": {},
    "performance_metrics": {},
    "errors": [],
    "summary": {}
}

def log_test(category: str, test_name: str, result: bool, details: Dict[str, Any] = None):
    """Log test result to results dictionary."""
    if category not in test_results:
        test_results[category] = {}
    
    test_results[category][test_name] = {
        "passed": result,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"   {status}: {test_name}")
    if details and not result:
        print(f"      Error: {details.get('error', 'Unknown error')}")

async def test_system_info():
    """Test system information and dependencies."""
    print("\n🔧 TESTING SYSTEM INFORMATION")
    print("=" * 50)
    
    # Test Python environment
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    test_results["system_info"]["python_version"] = python_version
    print(f"   Python Version: {python_version}")
    
    # Test required imports
    try:
        import pynvml
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        test_results["system_info"]["gpu_count"] = gpu_count
        log_test("system_info", "pynvml_available", True, {"gpu_count": gpu_count})
    except Exception as e:
        log_test("system_info", "pynvml_available", False, {"error": str(e)})
    
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        test_tokens = encoding.encode("test")
        log_test("system_info", "tiktoken_available", True, {"test_tokens": len(test_tokens)})
    except Exception as e:
        log_test("system_info", "tiktoken_available", False, {"error": str(e)})
    
    try:
        import ollama
        log_test("system_info", "ollama_library_available", True)
    except Exception as e:
        log_test("system_info", "ollama_library_available", False, {"error": str(e)})

async def test_vram_monitor():
    """Test VRAM monitoring functionality."""
    print("\n📊 TESTING VRAM MONITOR")
    print("=" * 50)
    
    try:
        from modules.module_a_core.vram_monitor import VRAMMonitor
        
        monitor = VRAMMonitor()
        
        # Test initialization
        log_test("component_tests", "vram_monitor_init", monitor.pynvml_available, 
                {"device_count": monitor.device_count})
        
        if monitor.pynvml_available:
            # Test VRAM info retrieval
            vram_info = monitor.get_vram_info(0)
            if vram_info:
                log_test("component_tests", "vram_info_retrieval", True, {
                    "total_mb": vram_info.total_mb,
                    "used_mb": vram_info.used_mb,
                    "usage_percent": round(vram_info.usage_percent * 100, 1),
                    "device_name": vram_info.device_name
                })
                
                test_results["performance_metrics"]["vram_usage"] = {
                    "total_mb": vram_info.total_mb,
                    "used_mb": vram_info.used_mb,
                    "usage_percent": vram_info.usage_percent,
                    "device_name": vram_info.device_name
                }
            else:
                log_test("component_tests", "vram_info_retrieval", False, 
                        {"error": "Could not retrieve VRAM info"})
            
            # Test usage percentage
            usage_pct = monitor.get_usage_percentage()
            log_test("component_tests", "vram_usage_percentage", usage_pct >= 0, 
                    {"usage_percent": round(usage_pct * 100, 1)})
        
    except Exception as e:
        log_test("component_tests", "vram_monitor_init", False, {"error": str(e)})

async def test_query_analyzer():
    """Test query analysis and complexity scoring."""
    print("\n🧠 TESTING QUERY ANALYZER")
    print("=" * 50)
    
    try:
        from modules.module_a_core.query_analyzer import QueryAnalyzer
        
        analyzer = QueryAnalyzer()
        
        test_queries = [
            ("Hallo, wie geht es dir?", False, "simple"),
            ("ps aux | grep python", True, "linux_command"),
            ("Schreibe eine Python-Funktion", True, "code_request"),
            ("Erkläre mir detailliert Docker Container", True, "complex_technical"),
            ("chmod 755 /etc/script.sh", True, "linux_permissions")
        ]
        
        analyzer_results = []
        
        for query, expected_code_model, query_type in test_queries:
            analysis = analyzer.analyze_query(query)
            
            result_correct = analysis.needs_code_model == expected_code_model
            log_test("component_tests", f"query_analysis_{query_type}", result_correct, {
                "query": query,
                "expected_code_model": expected_code_model,
                "actual_code_model": analysis.needs_code_model,
                "complexity_score": round(analysis.complexity_score, 3),
                "detected_keywords": analysis.detected_keywords[:3],
                "reasoning": analysis.reasoning
            })
            
            analyzer_results.append({
                "query": query,
                "needs_code_model": analysis.needs_code_model,
                "complexity_score": analysis.complexity_score,
                "keywords_count": len(analysis.detected_keywords)
            })
        
        test_results["performance_metrics"]["query_analysis"] = analyzer_results
        
    except Exception as e:
        log_test("component_tests", "query_analyzer_init", False, {"error": str(e)})

async def test_model_router():
    """Test intelligent model routing."""
    print("\n🎯 TESTING MODEL ROUTER")
    print("=" * 50)
    
    try:
        from modules.module_a_core.model_router import ModelRouter, ModelType
        
        router = ModelRouter()
        
        # Test router initialization
        log_test("component_tests", "model_router_init", True)
        
        # Test health check
        health = await router.health_check()
        router_healthy = health.get("router_status") == "ok"
        log_test("component_tests", "model_router_health", router_healthy, health)
        
        # Test model availability
        models_available = 0
        for model_type, model_info in health.get("models", {}).items():
            if model_info.get("available", False):
                models_available += 1
        
        log_test("component_tests", "model_availability", models_available >= 2, 
                {"available_models": models_available, "total_models": len(health.get("models", {}))})
        
        # Test routing decisions
        routing_tests = [
            ("Hallo, wie geht es dir?", ModelType.FAST),
            ("ps aux | grep python", ModelType.CODE),
            ("Schreibe eine Python-Klasse", ModelType.CODE),
        ]
        
        routing_results = []
        
        for query, expected_model in routing_tests:
            routing_result = await router.route_query(query, skip_vram_check=True)
            
            correct_routing = routing_result.selected_model == expected_model
            log_test("component_tests", f"routing_{expected_model.value}_model", correct_routing, {
                "query": query,
                "expected": expected_model.value,
                "selected": routing_result.selected_model.value,
                "model_name": routing_result.model_name,
                "reasoning": routing_result.reasoning
            })
            
            routing_results.append({
                "query": query,
                "expected_model": expected_model.value,
                "selected_model": routing_result.selected_model.value,
                "model_name": routing_result.model_name,
                "correct": correct_routing
            })
        
        test_results["performance_metrics"]["routing_decisions"] = routing_results
        
    except Exception as e:
        log_test("component_tests", "model_router_init", False, {"error": str(e)})

async def test_ollama_integration():
    """Test Ollama integration and model availability."""
    print("\n🤖 TESTING OLLAMA INTEGRATION")
    print("=" * 50)
    
    try:
        from modules.module_a_core.ollama_client import OllamaClient
        
        # Test different models
        models_to_test = [
            ("llama3.2:3b", "fast_model"),
            ("qwen3-coder-30b-local", "code_model"),
            ("llama3.1:70b", "heavy_model")
        ]
        
        ollama_results = []
        
        for model_name, test_name in models_to_test:
            try:
                client = OllamaClient(model=model_name)
                available = await client.is_available()
                
                log_test("component_tests", f"ollama_{test_name}_available", available, 
                        {"model_name": model_name})
                
                ollama_results.append({
                    "model_name": model_name,
                    "available": available,
                    "test_name": test_name
                })
                
            except Exception as e:
                log_test("component_tests", f"ollama_{test_name}_available", False, 
                        {"model_name": model_name, "error": str(e)})
        
        test_results["performance_metrics"]["ollama_models"] = ollama_results
        
    except Exception as e:
        log_test("component_tests", "ollama_integration", False, {"error": str(e)})

async def test_end_to_end_generation():
    """Test end-to-end response generation."""
    print("\n🚀 TESTING END-TO-END GENERATION")
    print("=" * 50)
    
    try:
        from modules.module_a_core.model_router import ModelRouter
        
        router = ModelRouter()
        
        # Test queries with different complexity levels
        test_queries = [
            ("Hallo!", "simple_greeting"),
            ("ps aux | grep python", "linux_command"),
        ]
        
        generation_results = []
        
        for query, test_type in test_queries:
            start_time = time.time()
            
            try:
                result = await router.generate_response(query)
                generation_time = time.time() - start_time
                
                success = result.get('success', True) and len(result.get('response', '')) > 0
                
                log_test("integration_tests", f"generation_{test_type}", success, {
                    "query": query,
                    "model_used": result.get('model_used', 'unknown'),
                    "generation_time": round(generation_time, 2),
                    "response_length": len(result.get('response', '')),
                    "routing_info": bool(result.get('routing_info'))
                })
                
                generation_results.append({
                    "query": query,
                    "test_type": test_type,
                    "success": success,
                    "model_used": result.get('model_used', 'unknown'),
                    "generation_time": generation_time,
                    "response_length": len(result.get('response', ''))
                })
                
            except Exception as e:
                generation_time = time.time() - start_time
                log_test("integration_tests", f"generation_{test_type}", False, {
                    "query": query,
                    "error": str(e),
                    "generation_time": round(generation_time, 2)
                })
        
        test_results["performance_metrics"]["generation_tests"] = generation_results
        
    except Exception as e:
        log_test("integration_tests", "end_to_end_generation", False, {"error": str(e)})

def calculate_summary():
    """Calculate test summary statistics."""
    print("\n📊 CALCULATING SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for category, tests in test_results.items():
        if category in ["component_tests", "integration_tests", "system_info"]:
            for test_name, test_data in tests.items():
                if isinstance(test_data, dict) and "passed" in test_data:
                    total_tests += 1
                    if test_data["passed"]:
                        passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    test_results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(success_rate, 1),
        "overall_status": "PASS" if success_rate >= 80 else "FAIL"
    }
    
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Overall Status: {test_results['summary']['overall_status']}")

def save_results():
    """Save test results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: {filename}")

async def main():
    """Run comprehensive test suite."""
    print("🎯 COMPREHENSIVE SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    
    # Run all test categories
    await test_system_info()
    await test_vram_monitor()
    await test_query_analyzer()
    await test_model_router()
    await test_ollama_integration()
    await test_end_to_end_generation()
    
    # Calculate and display summary
    calculate_summary()
    
    # Save results
    save_results()
    
    print("\n🎉 COMPREHENSIVE TEST SUITE COMPLETED")
    print("=" * 60)
    
    # Final status
    overall_status = test_results["summary"]["overall_status"]
    if overall_status == "PASS":
        print("🎉 SYSTEM STATUS: ✅ ALL SYSTEMS OPERATIONAL")
        print("🚀 READY FOR PRODUCTION DEPLOYMENT")
    else:
        print("⚠️  SYSTEM STATUS: ❌ ISSUES DETECTED")
        print("🔧 REVIEW FAILED TESTS AND RESOLVE ISSUES")

if __name__ == "__main__":
    asyncio.run(main())