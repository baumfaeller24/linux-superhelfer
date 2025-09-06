#!/usr/bin/env python3
"""
System Startup Script - Starts all modules for regular interface testing
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

class SystemManager:
    """Manages the startup and shutdown of all system modules."""
    
    def __init__(self):
        self.processes = {}
        self.running = True
    
    def start_module(self, name: str, command: list, port: int):
        """Start a module with the given command."""
        print(f"🚀 Starting {name} on port {port}...")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        try:
            process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[name] = {
                'process': process,
                'port': port,
                'command': command
            }
            
            # Give module time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"   ✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ {name} failed to start")
                print(f"      Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start {name}: {e}")
            return False
    
    def check_module_health(self, name: str, port: int):
        """Check if module is responding to health checks."""
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} health check passed")
                return True
            else:
                print(f"   ⚠️  {name} health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   ⚠️  {name} health check failed: {e}")
            return False
    
    def start_all_modules(self):
        """Start all system modules."""
        print("🎯 STARTING LINUX SUPERHELFER SYSTEM")
        print("=" * 50)
        
        modules = [
            {
                'name': 'Module A (Core Intelligence)',
                'command': [sys.executable, '-m', 'uvicorn', 'modules.module_a_core.main:app', 
                           '--host', '0.0.0.0', '--port', '8001'],
                'port': 8001
            },
            {
                'name': 'Module B (RAG Knowledge)',
                'command': [sys.executable, '-m', 'uvicorn', 'modules.module_b_rag.main:app', 
                           '--host', '0.0.0.0', '--port', '8002'],
                'port': 8002
            }
        ]
        
        started_modules = 0
        
        for module in modules:
            if self.start_module(module['name'], module['command'], module['port']):
                started_modules += 1
        
        print(f"\n📊 STARTUP SUMMARY")
        print(f"   Modules started: {started_modules}/{len(modules)}")
        
        if started_modules > 0:
            print(f"\n⏳ Waiting for modules to initialize...")
            time.sleep(5)
            
            print(f"\n🔍 HEALTH CHECKS")
            print("-" * 30)
            
            healthy_modules = 0
            for module in modules:
                if module['name'] in self.processes:
                    if self.check_module_health(module['name'], module['port']):
                        healthy_modules += 1
            
            print(f"\n📊 HEALTH SUMMARY")
            print(f"   Healthy modules: {healthy_modules}/{started_modules}")
            
            if healthy_modules > 0:
                print(f"\n🎉 SYSTEM READY FOR TESTING!")
                print(f"=" * 50)
                print(f"📋 AVAILABLE ENDPOINTS:")
                print(f"   • Module A (Core): http://localhost:8001")
                print(f"     - /health - Health check")
                print(f"     - /infer - Intelligent routing (NEW!)")
                print(f"     - /router_status - Model router status")
                print(f"     - /status - Module status")
                print(f"   • Module B (RAG): http://localhost:8002")
                print(f"     - /health - Health check")
                print(f"     - /search - Knowledge search")
                print(f"     - /status - Module status")
                
                print(f"\n🧠 INTELLIGENT ROUTING ACTIVE:")
                print(f"   • Simple queries → llama3.2:3b (Fast)")
                print(f"   • Linux/Code queries → qwen3-coder-30b-local (Code)")
                print(f"   • Complex queries → llama3.1:70b (Heavy)")
                
                print(f"\n🎯 TEST QUERIES TO TRY:")
                print(f"   1. 'Hallo, wie geht es dir?' (→ Fast Model)")
                print(f"   2. 'ps aux | grep python' (→ Code Model)")
                print(f"   3. 'Schreibe eine Python-Funktion' (→ Code Model)")
                print(f"   4. 'Erkläre Docker Container detailliert' (→ Code Model)")
                
                return True
        
        print(f"\n❌ SYSTEM STARTUP FAILED")
        return False
    
    def stop_all_modules(self):
        """Stop all running modules."""
        print(f"\n🛑 STOPPING ALL MODULES")
        print("-" * 30)
        
        for name, info in self.processes.items():
            try:
                process = info['process']
                if process.poll() is None:  # Process is still running
                    print(f"   Stopping {name}...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        print(f"   ⚠️  Force killing {name}...")
                        process.kill()
                        process.wait()
                        print(f"   ✅ {name} force stopped")
                else:
                    print(f"   ✅ {name} already stopped")
                    
            except Exception as e:
                print(f"   ❌ Error stopping {name}: {e}")
        
        print(f"🛑 All modules stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n\n🛑 Received shutdown signal...")
        self.running = False
        self.stop_all_modules()
        sys.exit(0)

def main():
    """Main function to start the system."""
    manager = SystemManager()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        if manager.start_all_modules():
            print(f"\n⌨️  PRESS CTRL+C TO STOP THE SYSTEM")
            print(f"🔄 System running... Use your regular interface to test!")
            
            # Keep the script running
            while manager.running:
                time.sleep(1)
        else:
            print(f"\n❌ Failed to start system")
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Shutdown requested by user...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        manager.stop_all_modules()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)