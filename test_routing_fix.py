#!/usr/bin/env python3
"""
Test script to verify the model routing fix.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from modules.module_a_core.model_router import ModelRouter

async def test_routing_fix():
    """Test the model routing with different queries."""
    
    print("🎯 TESTING MODEL ROUTING FIX")
    print("=" * 50)
    
    router = ModelRouter()
    
    test_queries = [
        ("Hallo, wie geht es dir?", "fast"),
        ("Zeige mir alle Python-Prozesse mit ps aux | grep python", "code"),
        ("Schreibe eine komplexe Python-Klasse für Datenbankverbindungen", "code"),
        ("Erkläre mir detailliert die Funktionsweise von Kubernetes", "code")
    ]
    
    for query, expected_model in test_queries:
        print(f"\n📝 Query: {query}")
        
        try:
            # Test routing decision
            routing_result = await router.route_query(query, skip_vram_check=True)
            
            print(f"   Expected: {expected_model}")
            print(f"   Selected: {routing_result.selected_model.value}")
            print(f"   Model: {routing_result.model_name}")
            print(f"   Reasoning: {routing_result.reasoning}")
            
            if routing_result.selected_model.value == expected_model:
                print("   ✅ CORRECT")
            else:
                print("   ❌ WRONG")
            
            # Test actual generation (quick test)
            print(f"   🔄 Testing generation...")
            generation_result = await router.generate_response(query[:50] + "?")
            
            if generation_result.get('success', True):
                response_preview = generation_result['response'][:100] + "..."
                print(f"   ✅ Generation successful: {response_preview}")
                print(f"   📊 Model used: {generation_result['model_used']}")
            else:
                print(f"   ❌ Generation failed: {generation_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 ROUTING TEST COMPLETED")

if __name__ == "__main__":
    asyncio.run(test_routing_fix())