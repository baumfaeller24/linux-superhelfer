# Linux Superhelfer

A modular, local AI-powered tool designed to assist with Linux administration tasks.

## Architecture

The system consists of 6 interconnected modules:

- **Module A**: Core Intelligence Engine (Port 8001)
- **Module B**: RAG Knowledge Vault (Port 8002)
- **Module C**: Proactive Agents (Port 8003)
- **Module D**: Safe Execution & Control (Port 8004)
- **Module E**: Hybrid Intelligence Gateway (Port 8005)
- **Module F**: User Interface (Port 8000)

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up
```

### Option 2: Development Setup
```bash
# Setup development environment
./scripts/setup_dev.sh

# Activate virtual environment
source venv/bin/activate

# Start all modules
python scripts/start_dev.py
```

Access the UI at: `http://localhost:8000`

## Project Structure

```
linux-superhelfer/
├── modules/                    # 6 independent modules
│   ├── module_a_core/         # Core Intelligence Engine (Port 8001)
│   ├── module_b_rag/          # RAG Knowledge Vault (Port 8002)
│   ├── module_c_agents/       # Proactive Agents (Port 8003)
│   ├── module_d_execution/    # Safe Execution & Control (Port 8004)
│   ├── module_e_hybrid/       # Hybrid Intelligence Gateway (Port 8005)
│   └── module_f_ui/           # User Interface (Port 8000)
├── shared/                    # Shared components and models
├── tests/                     # Test suite
├── scripts/                   # Development and deployment scripts
├── data/                      # Data storage for RAG module
├── config.yaml               # System configuration
└── requirements.txt          # Python dependencies
```

## Development

Each module is independently developed with standardized REST APIs:
- Health check: `GET /health`
- Main endpoint: `POST /main` (module-specific)
- Standard JSON request/response format

### Validation
```bash
python scripts/validate_structure.py
```

See individual module READMEs for specific development instructions.