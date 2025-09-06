#!/usr/bin/env python3
"""
Simple Test Interface for Regular Surface Testing
Interactive command-line interface to test the intelligent routing system.
"""

import requests
import json
import time
from datetime import datetime

class TestInterface:
    """Interactive test interface for the system."""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.session = requests.Session()
    
    def check_system_health(self):
        """Check if the system is running and healthy."""
        try:
            # Check Module A
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Module A (Core Intelligence) - ONLINE")
                
                # Check router status
                router_response = requests.get(f"{self.base_url}/router_status", timeout=5)
                if router_response.status_code == 200:
                    router_data = router_response.json()
                    router_health = router_data.get('router_health', {})
                    print(f"✅ Model Router - {router_health.get('router_status', 'unknown').upper()}")
                    
                    # Show available models
                    models = router_health.get('models', {})
                    print("📊 Available Models:")
                    for model_type, model_info in models.items():
                        status = "✅" if model_info.get('available') else "❌"
                        model_name = model_info.get('name', 'unknown')
                        print(f"   {status} {model_type}: {model_name}")
                
                return True
            else:
                print("❌ Module A - OFFLINE")
                return False
                
        except Exception as e:
            print(f"❌ System Health Check Failed: {e}")
            return False
    
    def send_query(self, query: str):
        """Send a query to the intelligent routing system."""
        print(f"\n🎯 SENDING QUERY")
        print(f"Query: {query}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            payload = {"query": query}
            response = requests.post(
                f"{self.base_url}/infer",
                json=payload,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key information
                model_used = data.get('model_used', 'unknown')
                confidence = data.get('confidence', 0)
                routing_info = data.get('routing_info', {})
                response_text = data.get('response', '')
                
                # Display results
                print(f"✅ SUCCESS")
                print(f"⏱️  Response Time: {response_time:.2f}s")
                print(f"🤖 Model Used: {model_used}")
                print(f"🎯 Confidence: {confidence:.3f}")
                
                if routing_info:
                    selected_model = routing_info.get('selected_model', 'unknown')
                    complexity = routing_info.get('complexity_score', 0)
                    reasoning = routing_info.get('reasoning', 'N/A')
                    
                    print(f"🧠 Routing Decision: {selected_model}")
                    print(f"📊 Complexity Score: {complexity:.3f}")
                    print(f"💭 Reasoning: {reasoning}")
                
                print(f"\n💬 RESPONSE:")
                print("-" * 30)
                # Show first 300 characters of response
                if len(response_text) > 300:
                    print(f"{response_text[:300]}...")
                    print(f"\n[Response truncated - {len(response_text)} total characters]")
                else:
                    print(response_text)
                
                return True
                
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ ERROR after {response_time:.2f}s: {e}")
            return False
    
    def run_predefined_tests(self):
        """Run a set of predefined test queries."""
        print("\n🧪 RUNNING PREDEFINED TESTS")
        print("=" * 60)
        
        test_queries = [
            {
                "query": "Hallo, wie geht es dir heute?",
                "expected": "Fast Model (llama3.2:3b)",
                "description": "Simple greeting - should use fast model"
            },
            {
                "query": "ps aux | grep python",
                "expected": "Code Model (qwen3-coder-30b-local)",
                "description": "Linux command - should use code model"
            },
            {
                "query": "Schreibe eine Python-Funktion zum Kopieren von Dateien",
                "expected": "Code Model (qwen3-coder-30b-local)",
                "description": "Code generation - should use code model"
            }
        ]
        
        results = []
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n📝 TEST {i}/3: {test['description']}")
            print(f"Expected: {test['expected']}")
            
            success = self.send_query(test['query'])
            results.append(success)
            
            if i < len(test_queries):
                print("\n" + "="*60)
        
        # Summary
        passed = sum(results)
        total = len(results)
        print(f"\n📊 TEST SUMMARY")
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        return passed == total
    
    def interactive_mode(self):
        """Run interactive mode for custom queries."""
        print("\n💬 INTERACTIVE MODE")
        print("=" * 60)
        print("Enter your queries to test the intelligent routing system.")
        print("Type 'quit' or 'exit' to stop, 'help' for commands.")
        print("-" * 60)
        
        while True:
            try:
                query = input("\n🎯 Your Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'help':
                    print("\n📋 AVAILABLE COMMANDS:")
                    print("   • Enter any query to test routing")
                    print("   • 'health' - Check system health")
                    print("   • 'test' - Run predefined tests")
                    print("   • 'quit' - Exit interactive mode")
                elif query.lower() == 'health':
                    self.check_system_health()
                elif query.lower() == 'test':
                    self.run_predefined_tests()
                elif query:
                    self.send_query(query)
                else:
                    print("⚠️  Please enter a query or command.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🎯 LINUX SUPERHELFER - TEST INTERFACE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    interface = TestInterface()
    
    # Check system health first
    print("🔍 CHECKING SYSTEM HEALTH...")
    if not interface.check_system_health():
        print("\n❌ System is not ready. Please start the system first:")
        print("   ./quick_start.sh")
        return False
    
    print("\n🎉 SYSTEM IS READY!")
    
    # Ask user what they want to do
    while True:
        print("\n📋 WHAT WOULD YOU LIKE TO DO?")
        print("1. Run predefined tests")
        print("2. Interactive mode (custom queries)")
        print("3. Check system health")
        print("4. Exit")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                interface.run_predefined_tests()
            elif choice == '2':
                interface.interactive_mode()
            elif choice == '3':
                interface.check_system_health()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("⚠️  Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    main()