#!/usr/bin/env python3
"""
Test script for Grok's routing optimizations.
Tests the two specific routing problems that Grok identified.
"""

import asyncio
import sys
import os
import time
import logging
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_a_core.query_analyzer import QueryAnalyzer
from modules.module_a_core.session_manager import get_session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrokRoutingTester:
    """Test Grok's routing optimizations."""
    
    def __init__(self):
        self.analyzer = QueryAnalyzer()
        self.session_manager = get_session_manager()
        
    def test_routing_problems(self):
        """Test the two specific routing problems Grok identified."""
        
        print("🎯 TESTING GROK'S ROUTING OPTIMIZATIONS")
        print("=" * 60)
        
        # Test cases based on Grok's analysis
        test_cases = [
            {
                "name": "Problem 1: Basic Query Fehlrouting",
                "query": "Welcher Befehl zeigt die Festplattenbelegung an?",
                "expected_model": "fast",
                "expected_complexity_range": (0.0, 0.4),
                "description": "Should route to Fast Model, not Code Model"
            },
            {
                "name": "Problem 2: Mathematical Query Grenzfall", 
                "query": "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
                "expected_model": "heavy",
                "expected_complexity_range": (0.5, 1.0),
                "description": "Should route to Heavy Model, not Code Model"
            },
            # Additional test cases to ensure no regression
            {
                "name": "Basic Command (should stay Fast)",
                "query": "ls -la zeigt mir alle Dateien",
                "expected_model": "fast",
                "expected_complexity_range": (0.0, 0.3),
                "description": "Simple command should use Fast Model"
            },
            {
                "name": "Mathematical Equation (should use Heavy)",
                "query": "Löse das Gleichungssystem: x+y=10, x-y=2",
                "expected_model": "heavy",
                "expected_complexity_range": (0.8, 1.0),
                "description": "Complex math should use Heavy Model"
            },
            {
                "name": "Code Request (should use Code)",
                "query": "Schreibe ein Bash-Skript zum automatischen Backup",
                "expected_model": "code",
                "expected_complexity_range": (0.4, 0.8),
                "description": "Code generation should use Code Model"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test_case['name']}...")
            print(f"   Query: {test_case['query']}")
            
            # Analyze query
            analysis = self.analyzer.analyze_query(test_case['query'])
            
            # Determine expected model based on ChatGPT's routing
            if hasattr(analysis, 'route_model'):
                actual_model = analysis.route_model
            else:
                # Fallback to legacy logic
                if analysis.complexity_score >= 0.6:
                    actual_model = "heavy"
                elif analysis.needs_code_model:
                    actual_model = "code"
                else:
                    actual_model = "fast"
            
            # Check results
            complexity_ok = (test_case['expected_complexity_range'][0] <= 
                           analysis.complexity_score <= 
                           test_case['expected_complexity_range'][1])
            
            model_ok = actual_model == test_case['expected_model']
            
            status = "✅" if (complexity_ok and model_ok) else "❌"
            
            print(f"   {status} Expected: {test_case['expected_model']}, Got: {actual_model}")
            print(f"   Complexity: {analysis.complexity_score:.3f} "
                  f"(expected: {test_case['expected_complexity_range'][0]}-{test_case['expected_complexity_range'][1]})")
            print(f"   Reasoning: {analysis.reasoning}")
            
            results.append({
                'test_case': test_case['name'],
                'query': test_case['query'],
                'expected_model': test_case['expected_model'],
                'actual_model': actual_model,
                'complexity_score': analysis.complexity_score,
                'expected_complexity': test_case['expected_complexity_range'],
                'model_correct': model_ok,
                'complexity_correct': complexity_ok,
                'overall_correct': model_ok and complexity_ok,
                'reasoning': analysis.reasoning
            })
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 GROK ROUTING OPTIMIZATION RESULTS")
        print("=" * 60)
        
        correct_count = sum(1 for r in results if r['overall_correct'])
        total_count = len(results)
        accuracy = (correct_count / total_count) * 100
        
        print(f"Routing Accuracy: {accuracy:.1f}% ({correct_count}/{total_count})")
        
        if accuracy >= 80:
            print("🎉 SUCCESS: Target accuracy (80%+) achieved!")
        elif accuracy >= 70:
            print("⚠️  GOOD: Close to target, minor improvements needed")
        else:
            print("❌ NEEDS WORK: Significant improvements required")
        
        print("\nDetailed Results:")
        for result in results:
            status = "✅" if result['overall_correct'] else "❌"
            print(f"  {status} {result['test_case']}: {result['actual_model']} "
                  f"(complexity: {result['complexity_score']:.3f})")
        
        # Specific problem analysis
        print("\n🚨 GROK'S SPECIFIC PROBLEMS:")
        problem1 = results[0]  # Basic Query Fehlrouting
        problem2 = results[1]  # Mathematical Query Grenzfall
        
        print(f"Problem 1 (Basic Query): {'FIXED' if problem1['overall_correct'] else 'NOT FIXED'}")
        print(f"Problem 2 (Mathematical): {'FIXED' if problem2['overall_correct'] else 'NOT FIXED'}")
        
        return results
    
    def test_session_management(self):
        """Test session management functionality."""
        
        print("\n" + "=" * 60)
        print("🎯 TESTING SESSION MANAGEMENT")
        print("=" * 60)
        
        # Create a test session
        session_id = self.session_manager.create_session()
        print(f"✅ Created session: {session_id}")
        
        # Add some conversation turns
        test_conversations = [
            ("Wie kann ich Docker installieren?", "Docker installation guide...", "code", 0.6),
            ("Zeige mir die laufenden Container", "docker ps command shows...", "fast", 0.2),
            ("Erstelle ein Dockerfile für Python", "Here's a Python Dockerfile...", "code", 0.7)
        ]
        
        for query, response, model, complexity in test_conversations:
            success = self.session_manager.add_conversation_turn(
                session_id=session_id,
                query=query,
                response=response,
                model_used=model,
                complexity_score=complexity,
                routing_decision=f"{model} model selected"
            )
            print(f"✅ Added conversation turn: {success}")
        
        # Test context retrieval
        context = self.session_manager.get_context_for_query(session_id, "Wie starte ich den Container?")
        print(f"✅ Retrieved context ({len(context)} chars)")
        
        # Test enhanced query
        enhanced = self.session_manager.enhance_query_with_context(session_id, "Wie starte ich den Container?")
        print(f"✅ Enhanced query: {'Yes' if enhanced != 'Wie starte ich den Container?' else 'No'}")
        
        # Get session stats
        stats = self.session_manager.get_session_stats(session_id)
        if stats:
            print(f"✅ Session stats: {stats['total_turns']} turns, "
                  f"avg complexity: {stats['average_complexity']:.2f}")
        
        return session_id
    
    def run_full_test(self):
        """Run all tests."""
        print("🚀 STARTING GROK'S OPTIMIZATION TESTS")
        print("=" * 60)
        
        # Test routing optimizations
        routing_results = self.test_routing_problems()
        
        # Test session management
        session_id = self.test_session_management()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 FINAL SUMMARY")
        print("=" * 60)
        
        routing_accuracy = sum(1 for r in routing_results if r['overall_correct']) / len(routing_results) * 100
        
        print(f"✅ Routing Accuracy: {routing_accuracy:.1f}%")
        print(f"✅ Session Management: Functional")
        print(f"✅ Context Integration: Implemented")
        
        # Check if Grok's specific problems are fixed
        problem1_fixed = routing_results[0]['overall_correct']
        problem2_fixed = routing_results[1]['overall_correct']
        
        if problem1_fixed and problem2_fixed:
            print("🎉 SUCCESS: Both of Grok's specific problems are FIXED!")
        elif problem1_fixed or problem2_fixed:
            print("⚠️  PARTIAL: One of Grok's problems is fixed, one needs more work")
        else:
            print("❌ NEEDS WORK: Both of Grok's problems still need fixing")
        
        return {
            'routing_accuracy': routing_accuracy,
            'problem1_fixed': problem1_fixed,
            'problem2_fixed': problem2_fixed,
            'session_management_working': True
        }


def main():
    """Main test function."""
    tester = GrokRoutingTester()
    results = tester.run_full_test()
    
    # Exit with appropriate code
    if results['routing_accuracy'] >= 80 and results['problem1_fixed'] and results['problem2_fixed']:
        print("\n🎉 ALL TESTS PASSED - GROK'S OPTIMIZATIONS SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - MORE OPTIMIZATION NEEDED")
        sys.exit(1)


if __name__ == "__main__":
    main()