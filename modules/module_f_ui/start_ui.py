#!/usr/bin/env python3
"""
Startup script for Module F (User Interface)
Launches the Streamlit web interface for Linux Superhelfer.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_backend_health():
    """Check if backend modules are running."""
    modules = {
        'Core Intelligence (A)': 'http://localhost:8001/health',
        'Knowledge Management (B)': 'http://localhost:8002/health'
    }
    
    print("🔍 Checking backend module health...")
    
    healthy_modules = 0
    for module_name, health_url in modules.items():
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {module_name}: Healthy")
                healthy_modules += 1
            else:
                print(f"   ❌ {module_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
    
    return healthy_modules, len(modules)

def start_streamlit_app():
    """Start the Streamlit application."""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    main_py_path = script_dir / "main.py"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(script_dir.parent.parent)  # Project root
    
    print("🚀 Starting Streamlit UI...")
    print(f"📁 App path: {main_py_path}")
    
    # Check if we're in venv and activate if needed
    venv_python = script_dir.parent.parent / "venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
        print("   Using virtual environment")
    else:
        python_cmd = sys.executable
        print("   Using system Python")
    
    # Start Streamlit
    cmd = [
        python_cmd, "-m", "streamlit", "run", 
        str(main_py_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down UI...")
    except Exception as e:
        print(f"❌ Failed to start UI: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    
    print("🎯 LINUX SUPERHELFER - MODULE F (USER INTERFACE)")
    print("=" * 60)
    
    # Check backend health
    healthy, total = check_backend_health()
    
    if healthy == 0:
        print("\n⚠️  WARNING: No backend modules are running!")
        print("   The UI will start but functionality will be limited.")
        print("   Start backend modules with: ./quick_start.sh")
        
        response = input("\n   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("   Startup cancelled.")
            return False
    
    elif healthy < total:
        print(f"\n⚠️  WARNING: Only {healthy}/{total} backend modules are healthy!")
        print("   Some features may not work correctly.")
        
        response = input("\n   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("   Startup cancelled.")
            return False
    
    else:
        print(f"\n✅ All backend modules healthy ({healthy}/{total})")
    
    print("\n🌐 Starting web interface...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    
    # Start the UI
    success = start_streamlit_app()
    
    if success:
        print("\n✅ UI started successfully!")
    else:
        print("\n❌ UI startup failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)