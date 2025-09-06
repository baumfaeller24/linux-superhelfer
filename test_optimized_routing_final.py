#!/usr/bin/env python3
"""
Final Integration Test for Optimized Mathematical Query Detection
Tests the complete routing system with real-world scenarios
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules', 'module_a_core'))

from query_analyzer import QueryAnalyzer, MODEL_HEAVY, MODEL_CODE, MODEL_FAST

def test_real_world_scenarios():
    """Test with real-world query scenarios."""
    
    analyzer = QueryAnalyzer()
    
    # Real-world test scenarios
    test_scenarios = [
        # Mathematical Problems (HEAVY)
        ("Löse das Gleichungssystem: 2x + 3y = 12, x - y = 1", MODEL_HEAVY, "Pure mathematical equation system"),
        ("Bestimme die optimale Puffergröße für I/O-Operationen mathematisch", MODEL_HEAVY, "System optimization with math"),
        ("Berechne Fibonacci-Zahlen bis 1000", MODEL_HEAVY, "Mathematical sequence calculation"),
        ("Finde alle x, y, z mit x² + y² = z² und x < 100", MODEL_HEAVY, "Mathematical constraint problem"),
        ("Mathematisch optimale Thread-Anzahl für CPU-intensive Tasks", MODEL_HEAVY, "Performance optimization with math"),
        
        # Programming Tasks (CODE)
        ("Implementiere eine Fibonacci-Funktion in Python", MODEL_CODE, "Programming implementation"),
        ("Schreibe ein Script zur Lösung von Gleichungssystemen", MODEL_CODE, "Mathematical programming"),
        ("Wie erstelle ich eine REST API mit FastAPI?", MODEL_CODE, "Web development"),
        ("Erstelle einen Parser für mathematische Ausdrücke", MODEL_CODE, "Parser programming"),
        ("Implementiere einen Algorithmus für Primzahlen", MODEL_CODE, "Algorithm implementation"),
        
        # Simple Commands (FAST)
        ("Welcher Befehl zeigt alle laufenden Prozesse?", MODEL_FAST, "Basic Linux command"),
        ("Wie liste ich alle Dateien auf?", MODEL_FAST, "File listing command"),
        ("Was macht der ls Befehl?", MODEL_FAST, "Command explanation"),
        ("Welches Kommando zeigt die CPU-Auslastung?", MODEL_FAST, "System monitoring command"),
        ("Hallo, wie geht es dir heute?", MODEL_FAST, "General conversation"),
        
        # Edge Cases
        ("Optimiere die Datenbankperformance", MODEL_CODE, "Technical optimization without math"),
        ("Erkläre mir Docker Container Schritt für Schritt", MODEL_CODE, "Complex technical explanation"),
        ("x = 5, berechne x² + 2x + 1", MODEL_HEAVY, "Simple mathematical calculation"),
        ("Wie funktioniert Git?", MODEL_CODE, "Technical concept explanation"),
        ("pwd", MODEL_FAST, "Single command"),
    ]
    
    print("🔍 FINAL INTEGRATION TEST - OPTIMIZED ROUTING")
    print("=" * 55)
    
    passed = 0
    failed = 0
    
    for i, (query, expected, description) in enumerate(test_scenarios, 1):
        result = analyzer.analyze_query(query)
        is_correct = result.route_model == expected
        status = "✅" if is_correct else "❌"
        
        print(f"{status} Test {i:2d}: {result.route_model.upper()} (expected: {expected.upper()})")
        print(f"    Query: {query}")
        print(f"    Context: {description}")
        
        if not is_correct:
            print(f"    ⚠️  Expected: {expected}, Got: {result.route_model}")
            print(f"    Reasoning: {result.reasoning}")
            failed += 1
        else:
            passed += 1
        print()
    
    # Summary
    total = len(test_scenarios)
    success_rate = (passed / total) * 100
    
    print("📊 FINAL RESULTS:")
    print("=" * 25)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("\n🎉 EXCELLENT! Mathematical Query Detection OPTIMIZED!")
        print("🚀 Ready for production use!")
    elif success_rate >= 90:
        print("\n✅ GOOD! Minor optimizations may be needed.")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT! Check failed test cases.")
    
    return success_rate >= 95

def test_performance_benchmarks():
    """Test routing performance with various query types."""
    
    analyzer = QueryAnalyzer()
    
    # Performance test queries
    performance_queries = [
        "Löse x + y = 10, x - y = 2",  # Mathematical
        "Implementiere Quicksort in Python",  # Programming
        "ls -la",  # Simple command
        "Bestimme optimale Puffergröße für maximalen I/O-Durchsatz",  # Complex math
        "Welcher Befehl zeigt Festplattenspeicher?",  # Basic question
    ]
    
    print("\n⚡ PERFORMANCE BENCHMARK:")
    print("-" * 30)
    
    import time
    
    for query in performance_queries:
        start_time = time.time()
        result = analyzer.analyze_query(query)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Query: {query[:40]}{'...' if len(query) > 40 else ''}")
        print(f"Route: {result.route_model.upper()}, Time: {processing_time:.2f}ms")
        print()
    
    print("✅ Performance test completed!")

if __name__ == "__main__":
    print("🚀 STARTING OPTIMIZED ROUTING TESTS...\n")
    
    # Run integration test
    success = test_real_world_scenarios()
    
    # Run performance benchmark
    test_performance_benchmarks()
    
    if success:
        print("\n🎯 OPTIMIZATION COMPLETE!")
        print("Mathematical Query Detection is now PRODUCTION READY! 🚀")
        sys.exit(0)
    else:
        print("\n❌ OPTIMIZATION INCOMPLETE!")
        print("Some test cases still failing.")
        sys.exit(1)