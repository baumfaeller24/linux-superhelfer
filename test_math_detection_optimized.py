#!/usr/bin/env python3
"""
Optimized Mathematical Query Detection Test
Tests the enhanced mathematical pattern recognition
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules', 'module_a_core'))

from query_analyzer import QueryAnalyzer, MODEL_HEAVY, MODEL_CODE, MODEL_FAST

def test_mathematical_queries():
    """Test mathematical query detection with enhanced patterns."""
    
    analyzer = QueryAnalyzer()
    
    # Test cases that should route to HEAVY model
    heavy_test_cases = [
        # Pure mathematical problems
        "Mathematisches Problem: Es gibt drei ganze Zahlen x, y, z mit x+y+z=30",
        "Löse das Gleichungssystem: x + y = 10, x - y = 2",
        "Berechne die Fibonacci-Zahlen bis 100",
        "Bestimme die optimale Puffergröße für I/O-Operationen",
        "Finde alle ganzen Zahlen x, y, z die x² + y² = z² erfüllen",
        "Welche Werte haben x und y wenn x + 2y = 15 und 3x - y = 7?",
        "Mathematisch optimale Blockgröße für Dateisystem-Operationen",
        "Berechne die optimale Anzahl Worker-Threads für CPU-intensive Tasks",
        "Löse: 2x + 3y = 12 und x - y = 1",
        "Bestimme mathematisch die optimale Cache-Größe",
        
        # System optimization with mathematical context
        "Optimiere die Puffergröße mathematisch für maximalen Durchsatz",
        "Berechne die optimale Batch-Größe für Datenbankoperationen",
        "Mathematische Optimierung der Connection Pool Größe",
        "Bestimme die optimale Thread-Anzahl basierend auf CPU-Kernen",
        
        # Complex mathematical expressions
        "x = 5, y = 3, berechne x² + y² - 2xy",
        "Wenn x + y = 10 und xy = 21, finde x und y",
        "Löse die Bedingungen: x > 0, y > 0, x + y ≤ 100, xy maximal",
    ]
    
    # Test cases that should route to CODE model
    code_test_cases = [
        "Wie implementiere ich eine Fibonacci-Funktion in Python?",
        "Schreibe ein Python-Script für mathematische Berechnungen",
        "Erstelle eine Funktion zur Lösung von Gleichungssystemen",
        "Implementiere einen Algorithmus für Primzahlen",
        "Wie programmiere ich einen mathematischen Parser?",
    ]
    
    # Test cases that should route to FAST model
    fast_test_cases = [
        "Welcher Befehl zeigt die CPU-Auslastung?",
        "Wie liste ich alle Dateien auf?",
        "Was macht der ls Befehl?",
        "Welches Kommando zeigt Prozesse an?",
        "Hallo, wie geht es dir?",
    ]
    
    print("🔍 MATHEMATICAL QUERY DETECTION TEST")
    print("=" * 50)
    
    # Test HEAVY model routing
    print("\n1️⃣ HEAVY MODEL TESTS (Mathematical Problems):")
    print("-" * 45)
    heavy_correct = 0
    for i, query in enumerate(heavy_test_cases, 1):
        result = analyzer.analyze_query(query)
        is_correct = result.route_model == MODEL_HEAVY
        status = "✅" if is_correct else "❌"
        
        print(f"{status} Test {i:2d}: {result.route_model.upper()}")
        print(f"    Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        if not is_correct:
            print(f"    Expected: {MODEL_HEAVY}, Got: {result.route_model}")
            print(f"    Reasoning: {result.reasoning}")
            if hasattr(result, 'debug_info') and result.debug_info:
                print(f"    Debug: {result.debug_info}")
        print()
        
        if is_correct:
            heavy_correct += 1
    
    # Test CODE model routing
    print("\n2️⃣ CODE MODEL TESTS (Programming Tasks):")
    print("-" * 42)
    code_correct = 0
    for i, query in enumerate(code_test_cases, 1):
        result = analyzer.analyze_query(query)
        is_correct = result.route_model == MODEL_CODE
        status = "✅" if is_correct else "❌"
        
        print(f"{status} Test {i:2d}: {result.route_model.upper()}")
        print(f"    Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        if not is_correct:
            print(f"    Expected: {MODEL_CODE}, Got: {result.route_model}")
        print()
        
        if is_correct:
            code_correct += 1
    
    # Test FAST model routing
    print("\n3️⃣ FAST MODEL TESTS (Simple Commands):")
    print("-" * 40)
    fast_correct = 0
    for i, query in enumerate(fast_test_cases, 1):
        result = analyzer.analyze_query(query)
        is_correct = result.route_model == MODEL_FAST
        status = "✅" if is_correct else "❌"
        
        print(f"{status} Test {i:2d}: {result.route_model.upper()}")
        print(f"    Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        if not is_correct:
            print(f"    Expected: {MODEL_FAST}, Got: {result.route_model}")
        print()
        
        if is_correct:
            fast_correct += 1
    
    # Summary
    print("\n📊 RESULTS SUMMARY:")
    print("=" * 30)
    total_heavy = len(heavy_test_cases)
    total_code = len(code_test_cases)
    total_fast = len(fast_test_cases)
    total_tests = total_heavy + total_code + total_fast
    total_correct = heavy_correct + code_correct + fast_correct
    
    print(f"Heavy Model: {heavy_correct}/{total_heavy} ({heavy_correct/total_heavy*100:.1f}%)")
    print(f"Code Model:  {code_correct}/{total_code} ({code_correct/total_code*100:.1f}%)")
    print(f"Fast Model:  {fast_correct}/{total_fast} ({fast_correct/total_fast*100:.1f}%)")
    print(f"Overall:     {total_correct}/{total_tests} ({total_correct/total_tests*100:.1f}%)")
    
    # Return success status
    return total_correct == total_tests

if __name__ == "__main__":
    success = test_mathematical_queries()
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)