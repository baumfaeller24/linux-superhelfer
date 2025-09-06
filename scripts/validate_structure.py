#!/usr/bin/env python3
"""
Validate project structure for Linux Superhelfer.
"""

import os
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists and report result."""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists


def validate_project_structure():
    """Validate the complete project structure."""
    print("Validating Linux Superhelfer project structure...\n")
    
    all_good = True
    
    # Core files
    files_to_check = [
        ("README.md", "Main README"),
        ("config.yaml", "Configuration file"),
        ("requirements.txt", "Python dependencies"),
        ("docker-compose.yml", "Docker composition"),
    ]
    
    # Shared components
    shared_files = [
        ("shared/__init__.py", "Shared package init"),
        ("shared/models.py", "Shared data models"),
        ("shared/config.py", "Configuration management"),
    ]
    
    # Module structure
    modules = ["module_a_core", "module_b_rag", "module_c_agents", 
               "module_d_execution", "module_e_hybrid", "module_f_ui"]
    
    module_files = []
    for module in modules:
        module_files.extend([
            (f"modules/{module}/__init__.py", f"{module} package init"),
            (f"modules/{module}/main.py", f"{module} main application"),
            (f"modules/{module}/README.md", f"{module} documentation"),
            (f"modules/{module}/Dockerfile", f"{module} Docker configuration"),
        ])
    
    # Test files
    test_files = [
        ("tests/__init__.py", "Test package init"),
        ("tests/conftest.py", "Pytest configuration"),
        ("tests/test_shared_models.py", "Shared models tests"),
    ]
    
    # Scripts
    script_files = [
        ("scripts/setup_dev.sh", "Development setup script"),
        ("scripts/start_dev.py", "Development startup script"),
        ("scripts/validate_structure.py", "Structure validation script"),
    ]
    
    # Data directory
    data_files = [
        ("data/.gitkeep", "Data directory placeholder"),
    ]
    
    # Check all files
    for files, category in [
        (files_to_check, "Core Files"),
        (shared_files, "Shared Components"),
        (module_files, "Module Files"),
        (test_files, "Test Files"),
        (script_files, "Script Files"),
        (data_files, "Data Directory"),
    ]:
        print(f"\n{category}:")
        for file_path, description in files:
            if not check_file_exists(file_path, description):
                all_good = False
    
    print(f"\n{'='*50}")
    if all_good:
        print("✓ All required files are present!")
        print("Project structure validation: PASSED")
    else:
        print("✗ Some files are missing!")
        print("Project structure validation: FAILED")
    
    return all_good


if __name__ == "__main__":
    validate_project_structure()