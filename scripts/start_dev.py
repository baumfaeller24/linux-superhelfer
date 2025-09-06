#!/usr/bin/env python3
"""
Development startup script for Linux Superhelfer
Starts all modules in the correct order for development testing.
"""

import subprocess
import time
import sys
import os
import requests
from typing import List, Dict, Any


class ModuleStarter:
    """Manages startup of all system modules."""
    
    def __init__(self):
        self.modules = [
            {
                'name': 'Module A - Core Intelligence',
                'command': ['python', '-m', 'uvicorn', 'modules.module_a_core.main:app', '--host', '0.0.0.0', '--port', '8001'],
                'port': 8001,
                'health_endpoint': '/health'
            },
            {
                'name': 'Module B - RAG Knowledge Vault',
                'command': ['python', '-m', 'uvicorn', 'modules.module_b_rag.main:app', '--host', '0.0.0.0', '--port', '8002'],
                'port': 8002,
                'health_endpoint': '/health'
            },
            {
                'name': 'Module C - Proactive Agents',
                'command': ['python', '-m', 'uvicorn', 'modules.module_c_agents.main:app', '--host', '0.0.0.0', '--port', '8003'],
                'port': 8003,
                'health_endpoint': '/health'
            },
            {
                'name': 'Module D - Safe Execution',
                'command': ['python', 'modules/module_d_execution/run.py'],
                'port': 8004,
                'health_endpoint': '/health'
            },
            {
                'name': 'Module E - Hybrid Gateway',
                'command': ['python', '-m', 'uvicorn', 'modules.module_e_hybrid.main:app', '--host', '0.0.0.0', '--port', '8005'],
                'port': 8005,
                'health_endpoint': '/health'
            },
            {
                'name': 'Module F - User Interface',
                'command': ['streamlit', 'run', 'modules/module_f_ui/main.py', '--server.port', '8501'],
                'port': 8501,
                'health_endpoint': '/'
            }
        ]
        self.processes: List[subprocess.Popen] = []
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=2)
            return False  # Port is occupied
        except requests.exceptions.RequestException:
            return True  # Port is available
    
    def wait_for_module(self, module: Dict[str, Any], timeout: int = 30) -> bool:
        """Wait for a module to become healthy."""
        print(f"  Waiting for {module['name']} on port {module['port']}...")
        
        for attempt in range(timeout):
            try:
                url = f"http://localhost:{module['port']}{module['health_endpoint']}"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"  ✅ {module['name']} is healthy!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if attempt % 5 == 0 and attempt > 0:
                print(f"    Still waiting... ({attempt}/{timeout}s)")
        
        print(f"  ❌ {module['name']} failed to start within {timeout}s")
        return False
    
    def start_module(self, module: Dict[str, Any]) -> bool:
        """Start a single module."""
        print(f"\n🚀 Starting {module['name']}...")
        
        # Check if port is already in use
        if not self.check_port_available(module['port']):
            print(f"  ⚠️  Port {module['port']} already in use, skipping...")
            return True
        
        try:
            # Start the process
            process = subprocess.Popen(
                module['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.processes.append(process)
            print(f"  📋 Process started with PID: {process.pid}")
            
            # Wait for module to become healthy
            return self.wait_for_module(module)
            
        except Exception as e:
            print(f"  ❌ Failed to start {module['name']}: {e}")
            return False
    
    def start_all_modules(self) -> bool:
        """Start all modules in sequence."""
        print("🐧 Linux Superhelfer - Development Startup")
        print("=" * 50)
        
        success_count = 0
        
        for module in self.modules:
            if self.start_module(module):
                success_count += 1
            else:
                print(f"\n❌ Failed to start {module['name']}")
                print("Stopping already started modules...")
                self.stop_all_modules()
                return False
            
            # Small delay between module starts
            time.sleep(2)
        
        print(f"\n🎉 Successfully started {success_count}/{len(self.modules)} modules!")
        print("\n📊 System Status:")
        print("-" * 30)
        
        for module in self.modules:
            status = "✅ Running" if self.check_module_health(module) else "❌ Failed"
            print(f"  {module['name']}: {status} (Port {module['port']})")
        
        print(f"\n🌐 Access the UI at: http://localhost:8501")
        print("🔧 Press Ctrl+C to stop all modules")
        
        return True
    
    def check_module_health(self, module: Dict[str, Any]) -> bool:
        """Check if a module is healthy."""
        try:
            url = f"http://localhost:{module['port']}{module['health_endpoint']}"
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def stop_all_modules(self):
        """Stop all started modules."""
        print("\n🛑 Stopping all modules...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ Stopped process {process.pid}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  🔪 Killed process {process.pid}")
            except Exception as e:
                print(f"  ❌ Error stopping process: {e}")
        
        self.processes.clear()
        print("🏁 All modules stopped")
    
    def run_interactive(self):
        """Run in interactive mode with graceful shutdown."""
        try:
            if self.start_all_modules():
                print("\n⌨️  Press Enter to stop all modules...")
                input()
        except KeyboardInterrupt:
            print("\n\n🛑 Received interrupt signal...")
        finally:
            self.stop_all_modules()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Linux Superhelfer Development Startup Script")
        print("Usage: python scripts/start_dev.py")
        print("Starts all modules and waits for user input to stop them.")
        return
    
    starter = ModuleStarter()
    starter.run_interactive()


if __name__ == "__main__":
    main()