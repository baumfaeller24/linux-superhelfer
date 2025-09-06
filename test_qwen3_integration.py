#!/usr/bin/env python3
"""
Test script for Qwen3-Coder integration.
Tests query analysis, VRAM monitoring, and model routing.
"""

import asyncio
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.module_a_core.query_analyzer import QueryAnalyzer
from modules.module_a_core.vram_monitor import VRAMMonitor
from modules.module_a_core.model_router import ModelRouter, ModelType


def test_query_analyzer():
    """Test the query analyzer with various queries."""
    print("🔍 TESTING QUERY ANALYZER")
    print("=" * 50)
    
    analyzer = QueryAnalyzer()
    
    test_queries = [
        "Hallo, wie geht es dir heute?",
        "Zeige mir alle laufenden Prozesse mit ps aux",
        "Wie kann ich eine Python-Funktion schreiben?",
        "Erkläre mir Schritt für Schritt, wie Docker Container funktionieren",
        "Was ist der Unterschied zwischen chmod 755 und chmod 644?",
        "Berechne die Fakultät von 10 mit einem rekursiven Algorithmus",
        "grep -r 'error' /var/log/ | head -20",
        "Erstelle ein Backup-Script für MySQL-Datenbanken"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        analysis = analyzer.analyze_query(query)
        
        print(f"   Code model needed: {'✅ YES' if analysis.needs_code_model else '❌ NO'}")
        print(f"   Complexity score: {analysis.complexity_score:.2f}")
        print(f"   Token count: {analysis.token_count}")
        print(f"   Keywords found: {len(analysis.detected_keywords)}")
        if analysis.detected_keywords:
            print(f"   Sample keywords: {', '.join(analysis.detected_keywords[:3])}")
        print(f"   Reasoning: {analysis.reasoning}")


def test_vram_monitor():
    """Test VRAM monitoring functionality."""
    print("\n\n📊 TESTING VRAM MONITOR")
    print("=" * 50)
    
    monitor = VRAMMonitor()
    
    if monitor.pynvml_available:
        print(f"✅ VRAM monitoring available ({monitor.device_count} GPU(s))")
        
        vram_info = monitor.get_vram_info()
        if vram_info:
            print(f"\nGPU: {vram_info.device_name}")
            print(f"Total VRAM: {vram_info.total_mb:,} MB")
            print(f"Used VRAM: {vram_info.used_mb:,} MB ({vram_info.usage_percent:.1%})")
            print(f"Free VRAM: {vram_info.free_mb:,} MB")
            
            # Test warning threshold
            if vram_info.usage_percent > 0.8:
                print("⚠️  High VRAM usage detected - warnings would be shown")
            else:
                print("✅ VRAM usage within normal range")
        else:
            print("❌ Could not retrieve VRAM information")
    else:
        print("❌ VRAM monitoring not available")
        print("   Install pynvml: pip install pynvml")


async def test_model_router():
    """Test model routing functionality."""
    print("\n\n🚀 TESTING MODEL ROUTER")
    print("=" * 50)
    
    router = ModelRouter()
    
    # Test health check
    health = await router.health_check()
    print("Router Health Check:")
    print(f"  Router status: {health['router_status']}")
    print(f"  VRAM monitoring: {'✅' if health['vram_monitoring'] else '❌'}")
    
    print("\nModel availability:")
    for model_name, model_info in health['models'].items():
        status = "✅ Available" if model_info['available'] else "❌ Unavailable"
        print(f"  {model_name}: {status} ({model_info['name']})")
    
    # Test routing decisions
    print("\nTesting routing decisions:")
    test_queries = [
        "Hallo, wie geht es dir?",
        "ps aux | grep python",
        "Schreibe eine komplexe Python-Klasse für Datenbankverbindungen",
        "Erkläre mir detailliert die Funktionsweise von Kubernetes Pods"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        routing_result = await router.route_query(query, skip_vram_check=True)
        
        print(f"  Selected model: {routing_result.selected_model.value}")
        print(f"  Model name: {routing_result.model_name}")
        print(f"  Complexity: {routing_result.analysis.complexity_score:.2f}")
        print(f"  Reasoning: {routing_result.reasoning}")


def test_installation_check():
    """Check if all required components are installed."""
    print("🔧 INSTALLATION CHECK")
    print("=" * 50)
    
    # Check pynvml
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        print(f"✅ pynvml: Available ({device_count} GPU(s))")
    except ImportError:
        print("❌ pynvml: Not installed (pip install pynvml)")
    except Exception as e:
        print(f"⚠️  pynvml: Error - {e}")
    
    # Check tiktoken
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        test_tokens = encoding.encode("test")
        print(f"✅ tiktoken: Available (test encoding: {len(test_tokens)} tokens)")
    except ImportError:
        print("❌ tiktoken: Not installed (pip install tiktoken)")
    except Exception as e:
        print(f"⚠️  tiktoken: Error - {e}")
    
    # Check tkinter
    try:
        import tkinter
        print("✅ tkinter: Available (GUI warnings supported)")
    except ImportError:
        print("⚠️  tkinter: Not available (GUI warnings disabled)")
    
    # Check ollama connectivity (basic)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama: Server accessible")
        else:
            print(f"⚠️  Ollama: Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama: Not accessible - {e}")


async def main():
    """Run all tests."""
    print("🎯 QWEN3-CODER INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Installation check
    test_installation_check()
    
    # Component tests
    test_query_analyzer()
    test_vram_monitor()
    await test_model_router()
    
    print("\n\n🎉 TEST SUITE COMPLETED")
    print("=" * 60)
    print("If all components show ✅, the integration is ready!")
    print("If you see ❌, install missing dependencies:")
    print("  pip install pynvml tiktoken")
    print("  ollama pull qwen3-coder:30b-q4")


if __name__ == "__main__":
    asyncio.run(main())