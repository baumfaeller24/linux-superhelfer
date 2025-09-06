#!/usr/bin/env python3
"""
Test Grok's routing optimizations
"""

import requests
import json
import time

def test_routing_optimization():
    """Test the improved routing with Grok's recommendations."""
    
    test_cases = [
        # Basic Linux commands (should use Fast Model)
        {
            "query": "Welcher Befehl zeigt die Festplattenbelegung an?",
            "expected_model": "fast",
            "category": "basic"
        },
        {
            "query": "ls -la zeigt mir alle Dateien",
            "expected_model": "fast", 
            "category": "basic"
        },
        
        # Mathematical queries (should use Heavy Model with lowered threshold)
        {
            "query": "Löse das Gleichungssystem: x+y=10, x-y=2",
            "expected_model": "heavy",
            "category": "mathematical"
        },
        {
            "query": "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
            "expected_model": "heavy",
            "category": "mathematical"
        },
        {
            "query": "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
            "expected_model": "heavy",
            "category": "mathematical"
        },
        
        # Intermediate Linux tasks (should use Code Model)
        {
            "query": "Schreibe ein Bash-Skript zum automatischen Backup",
            "expected_model": "code",
            "category": "intermediate"
        }
    ]
    
    print("🎯 TESTING GROK'S ROUTING OPTIMIZATIONS")
    print("=" * 50)
    
    results = []
    correct_routes = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test['category']} query...")
        print(f"   Query: {test['query'][:60]}...")
        
        try:
            response = requests.post(
                'http://localhost:8001/infer',
                json={'query': test['query']},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_model = data.get('routing_info', {}).get('selected_model', 'unknown')
                complexity = data.get('routing_info', {}).get('complexity_score', 0)
                confidence = data.get('confidence', 0)
                response_time = data.get('processing_time', 0)
                
                is_correct = actual_model == test['expected_model']
                if is_correct:
                    correct_routes += 1
                
                status = "✅" if is_correct else "❌"
                print(f"   {status} Expected: {test['expected_model']}, Got: {actual_model}")
                print(f"   Complexity: {complexity:.3f}, Confidence: {confidence:.3f}")
                print(f"   Response Time: {response_time:.2f}s")
                
                results.append({
                    'test': test,
                    'actual_model': actual_model,
                    'complexity': complexity,
                    'confidence': confidence,
                    'response_time': response_time,
                    'correct': is_correct
                })
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Small delay between tests
    
    # Summary
    accuracy = (correct_routes / len(test_cases)) * 100
    print(f"\n🎯 GROK OPTIMIZATION RESULTS")
    print("=" * 40)
    print(f"Routing Accuracy: {accuracy:.1f}% ({correct_routes}/{len(test_cases)})")
    
    if accuracy >= 80:
        print("🎉 SUCCESS: Target accuracy (80%+) achieved!")
    elif accuracy >= 60:
        print("⚠️  IMPROVEMENT: Better than before (47%), but not yet at target")
    else:
        print("❌ NEEDS WORK: Still below expectations")
    
    # Detailed analysis
    print(f"\nDetailed Results:")
    for result in results:
        category = result['test']['category']
        correct = "✅" if result['correct'] else "❌"
        print(f"  {correct} {category}: {result['actual_model']} (complexity: {result['complexity']:.3f})")
    
    return results

if __name__ == "__main__":
    test_routing_optimization()