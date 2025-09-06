#!/usr/bin/env python3
"""
Safe System Startup Script for Linux Superhelfer
Starts all modules with timeout protection and health checks.
"""

import subprocess
import time
import requests
import sys
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import signal

class ModuleManager:
    def __init__(self):
        self.processes = []
        self.modules = {
            'Module B (RAG)': {
                'cmd': ['python', '-m', 'uvicorn', 'modules.module_b_rag.main:app', '--host', '0.0.0.0', '--port', '8002'],
                'port': 8002,
                'health_url': 'http://localhost:8002/health'
            },
            'Module C (Agents)': {
                'cmd': ['python', '-m', 'uvicorn', 'modules.module_c_agents.main:app', '--host', '0.0.0.0', '--port', '8003'],
                'port': 8003,
                'health_url': 'http://localhost:8003/health'
            },
            'Module D (Execution)': {
                'cmd': ['python', 'modules/module_d_execution/run.py'],
                'port': 8004,
                'health_url': 'http://localhost:8004/health'
            },
            'Module E (Hybrid)': {
                'cmd': ['python', 'modules/module_e_hybrid/main.py'],
                'port': 8005,
                'health_url': 'http://localhost:8005/health'
            },
            'Module A (Core)': {
                'cmd': ['python', '-m', 'uvicorn', 'modules.module_a_core.main:app', '--host', '0.0.0.0', '--port', '8001'],
                'port': 8001,
                'health_url': 'http://localhost:8001/health'
            }
        }
    
    def start_module(self, name, config):
        """Start a single module with timeout protection."""
        print(f"🚀 Starting {name}...")
        
        try:
            # Start process
            process = subprocess.Popen(
                config['cmd'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            self.processes.append((name, process))
            
            # Wait for startup (max 15 seconds)
            for i in range(15):
                try:
                    response = requests.get(config['health_url'], timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {name} started successfully on port {config['port']}")
                        return True
                except:
                    time.sleep(1)
            
            print(f"⚠️ {name} started but health check failed")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def start_all_modules(self):
        """Start all modules sequentially."""
        print("🐧 Starting Linux Superhelfer System...")
        
        success_count = 0
        for name, config in self.modules.items():
            if self.start_module(name, config):
                success_count += 1
            time.sleep(2)  # Brief pause between starts
        
        print(f"\n📊 System Status: {success_count}/{len(self.modules)} modules started")
        
        if success_count >= 3:  # At least 3 modules needed for basic functionality
            print("✅ System ready for testing!")
            return True
        else:
            print("❌ System startup failed - too few modules running")
            return False
    
    def start_ui(self):
        """Start the Streamlit UI."""
        print("🖥️ Starting Web UI...")
        
        try:
            ui_process = subprocess.Popen([
                'streamlit', 'run', 'modules/module_f_ui/main.py', 
                '--server.port', '8501'
            ])
            
            self.processes.append(('UI', ui_process))
            
            # Wait for UI to start
            time.sleep(5)
            
            try:
                response = requests.get('http://localhost:8501', timeout=5)
                print("✅ Web UI started successfully at http://localhost:8501")
                return True
            except:
                print("⚠️ UI started but may not be fully ready")
                return True
                
        except Exception as e:
            print(f"❌ Failed to start UI: {e}")
            return False
    
    def cleanup(self):
        """Clean shutdown of all processes."""
        print("\n🛑 Shutting down system...")
        
        for name, process in self.processes:
            try:
                # Send SIGTERM to process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"🔄 Stopped {name}")
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print("✅ System shutdown complete")

def main():
    manager = ModuleManager()
    
    try:
        # Start backend modules
        if manager.start_all_modules():
            # Start UI
            manager.start_ui()
            
            print("\n🎯 System is running!")
            print("📱 Access the UI at: http://localhost:8501")
            print("🔧 Press Ctrl+C to stop all modules")
            print("⌨️  Press Enter to stop all modules...")
            
            # Wait for user input or Ctrl+C
            try:
                input()
            except KeyboardInterrupt:
                pass
        
    except KeyboardInterrupt:
        print("\n⚠️ Received interrupt signal")
    
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()