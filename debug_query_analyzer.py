#!/usr/bin/env python3
"""Debug script for query analyzer."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_a_core.query_analyzer import QueryAnalyzer

def debug_query(query: str):
    """Debug a specific query."""
    analyzer = QueryAnalyzer()
    
    print(f"Debugging query: '{query}'")
    print("=" * 60)
    
    query_lower = query.lower()
    
    # Check detected keywords
    detected_linux = [kw for kw in analyzer.linux_keywords if kw in query_lower]
    detected_code = [kw for kw in analyzer.code_keywords if kw in query_lower]
    detected_complexity = [kw for kw in analyzer.complexity_indicators if kw in query_lower]
    
    print(f"Linux keywords: {detected_linux}")
    print(f"Code keywords: {detected_code}")
    print(f"Complexity keywords: {detected_complexity}")
    
    # Check if bestimme is in complexity indicators
    print(f"'bestimme' in complexity_indicators: {'bestimme' in analyzer.complexity_indicators}")
    print(f"Complexity indicators: {analyzer.complexity_indicators}")
    
    # Check mathematical patterns
    mathematical_indicators = [
        r'mathematisch.{0,20}optimal',
        r'optimal.{0,20}puffer',
        r'bestimme.{0,20}optimal',
        r'berechne.{0,20}optimal',
        r'fibonacci.{0,10}zahlen',
        r'gleichungssystem',
        r'i/o.{0,10}operation',
        r'puffergröße.{0,20}operation',
        r'mathematisch.{0,20}puffer',
        r'bestimme.{0,20}mathematisch',
        r'optimal.{0,10}größe',
        r'puffergröße.{0,10}i/o',
    ]
    
    import re
    print(f"\nMathematical pattern matches:")
    for pattern in mathematical_indicators:
        match = re.search(pattern, query_lower)
        if match:
            print(f"  ✅ {pattern}: {match.group()}")
        else:
            print(f"  ❌ {pattern}: No match")
    
    # Run full analysis
    analysis = analyzer.analyze_query(query)
    print(f"\nFull analysis:")
    print(f"  needs_code_model: {analysis.needs_code_model}")
    print(f"  complexity_score: {analysis.complexity_score}")
    print(f"  reasoning: {analysis.reasoning}")

if __name__ == "__main__":
    debug_query("Bestimme die mathematisch optimale Puffergröße für I/O-Operationen")