#!/usr/bin/env python3
"""
Startup script for Module D: Safe Execution & Control
"""

import sys
import os
from pathlib import Path

# Add the module directory to Python path
module_dir = Path(__file__).parent
sys.path.insert(0, str(module_dir))

# Now import and run the main application
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)