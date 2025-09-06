#!/usr/bin/env python3
"""
Test script for the new hybrid routing logic.
Tests critical queries that failed in the 96k overnight test.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_a_core.model_router import ModelRouter, ModelType
from modules.module_a_core.query_analyzer import QueryAnalyzer
import asyncio

# Test queries from the failed cases in overnight optimization
TEST_QUERIES = [
    # === BASIC COMMANDS (should be FAST) ===
    {
        "query": "Was macht der df Befehl bitte?",
        "expected": "fast",
        "category": "basic_commands",
        "description": "Simple command explanation"
    },
    {
        "query": "Wie kann ich alle laufenden Prozesse anzeigen bitte?",
        "expected": "fast", 
        "category": "basic_commands",
        "description": "Basic process listing"
    },
    {
        "query": "Kannst du mir helfen: was ist der unterschied zwischen ls und ll?",
        "expected": "fast",
        "category": "basic_commands", 
        "description": "Basic command comparison"
    },
    {
        "query": "Welcher Befehl zeigt die Festplattenbelegung an bitte?",
        "expected": "fast",
        "category": "basic_commands",
        "description": "Basic disk usage command"
    },
    
    # === MATHEMATICAL QUERIES (should be HEAVY) ===
    {
        "query": "Löse die Optimierungsaufgabe für Memory-Allocation?",
        "expected": "heavy",
        "category": "mathematical",
        "description": "Mathematical optimization problem"
    },
    {
        "query": "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
        "expected": "heavy",
        "category": "mathematical", 
        "description": "Mathematical calculation for technical purpose"
    },
    {
        "query": "Finde die optimale Anzahl von Worker-Threads für CPU-intensive Tasks",
        "expected": "heavy",
        "category": "mathematical",
        "description": "Optimization problem for system resources"
    },
    {
        "query": "Bestimme die mathematisch optimale Cache-Größe für Datenbank-Queries",
        "expected": "heavy",
        "category": "mathematical",
        "description": "Mathematical optimization for database performance"
    },
    
    # === INTERMEDIATE QUERIES (should be CODE) ===
    {
        "query": "Erkläre mir die Unterschiede zwischen verschiedenen Dateisystemen?",
        "expected": "code",
        "category": "intermediate",
        "description": "Complex technical explanation"
    },
    {
        "query": "Was sind Best Practices für Linux-Security-Hardening?",
        "expected": "code", 
        "category": "intermediate",
        "description": "Technical best practices"
    },
    {
        "query": "Was sind die Vor- und Nachteile von Docker vs. LXC?",
        "expected": "code",
        "category": "intermediate",
        "description": "Technical comparison"
    },
    
    # === CODE TASKS (should be CODE) ===
    {
        "query": "Erstelle ein Python-Tool für Netzwerk-Monitoring",
        "expected": "code",
        "category": "code_tasks",
        "description": "Programming task"
    },
    {
        "query": "Entwickle ein Shell-Skript für Log-Rotation",
        "expected": "code",
        "category": "code_tasks", 
        "description": "Shell scripting task"
    }
]

async def test_hybrid_routing():
    """Test the new hybrid routing logic."""
    print("🚀 TESTING HYBRID ROUTING LOGIC")
    print("=" * 60)
    
    # Initialize router (skip VRAM checks for testing)
    router = ModelRouter()
    
    results = {
        "total": 0,
        "correct": 0,
        "by_category": {}
    }
    
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        expected = test_case["expected"]
        category = test_case["category"]
        description = test_case["description"]
        
        # Route the query
        routing_result = await router.route_query(query, skip_vram_check=True)
        actual = routing_result.selected_model.value
        
        # Check result
        is_correct = actual == expected
        results["total"] += 1
        if is_correct:
            results["correct"] += 1
        
        # Track by category
        if category not in results["by_category"]:
            results["by_category"][category] = {"total": 0, "correct": 0}
        results["by_category"][category]["total"] += 1
        if is_correct:
            results["by_category"][category]["correct"] += 1
        
        # Print result
        status = "✅" if is_correct else "❌"
        print(f"{status} {category.upper()}")
        print(f"   Query: {query}")
        print(f"   Expected: {expected} | Actual: {actual}")
        print(f"   Description: {description}")
        if not is_correct:
            print(f"   Reasoning: {routing_result.reasoning}")
        print()
    
    # Print summary
    print("=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    overall_accuracy = (results["correct"] / results["total"]) * 100
    print(f"Overall Accuracy: {results['correct']}/{results['total']} ({overall_accuracy:.1f}%)")
    print()
    
    print("By Category:")
    for category, stats in results["by_category"].items():
        accuracy = (stats["correct"] / stats["total"]) * 100
        print(f"  {category.upper()}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    
    print()
    if overall_accuracy >= 80:
        print("🎉 EXCELLENT! Routing accuracy >= 80%")
    elif overall_accuracy >= 70:
        print("✅ GOOD! Routing accuracy >= 70%") 
    elif overall_accuracy >= 60:
        print("⚠️  NEEDS IMPROVEMENT! Routing accuracy < 70%")
    else:
        print("❌ POOR! Routing accuracy < 60%")
    
    return results

async def test_query_analyzer_integration():
    """Test that QueryAnalyzer provides the needed data."""
    print("\n🔍 TESTING QUERY ANALYZER INTEGRATION")
    print("=" * 60)
    
    analyzer = QueryAnalyzer()
    
    test_query = "Löse die Optimierungsaufgabe für Memory-Allocation?"
    analysis = analyzer.analyze_query(test_query)
    
    print(f"Query: {test_query}")
    print(f"Original Query: {analysis.original_query}")
    print(f"Route Model: {analysis.route_model}")
    print(f"Needs Code Model: {analysis.needs_code_model}")
    print(f"Complexity Score: {analysis.complexity_score}")
    print(f"Debug Info: {analysis.debug_info}")
    print()
    
    # Check if all needed fields are present
    checks = [
        ("original_query", analysis.original_query == test_query),
        ("route_model", hasattr(analysis, 'route_model') and analysis.route_model),
        ("debug_info", hasattr(analysis, 'debug_info') and analysis.debug_info is not None)
    ]
    
    all_good = True
    for field, check in checks:
        status = "✅" if check else "❌"
        print(f"{status} {field}: {'OK' if check else 'MISSING'}")
        if not check:
            all_good = False
    
    if all_good:
        print("\n✅ QueryAnalyzer integration is working correctly!")
    else:
        print("\n❌ QueryAnalyzer integration has issues!")
    
    return all_good

if __name__ == "__main__":
    async def main():
        print("🧪 HYBRID ROUTING TEST SUITE")
        print("Testing the new intelligent routing logic...")
        print()
        
        # Test QueryAnalyzer integration first
        analyzer_ok = await test_query_analyzer_integration()
        
        if not analyzer_ok:
            print("❌ Cannot proceed with routing tests - QueryAnalyzer issues detected!")
            return
        
        # Test hybrid routing
        results = await test_hybrid_routing()
        
        print("\n🎯 NEXT STEPS:")
        if results["correct"] / results["total"] < 0.8:
            print("- Analyze failed cases and improve patterns")
            print("- Adjust complexity thresholds")
            print("- Add more specific routing rules")
        else:
            print("- Start overnight optimization with new routing logic!")
            print("- Monitor performance improvements")
        
    asyncio.run(main())