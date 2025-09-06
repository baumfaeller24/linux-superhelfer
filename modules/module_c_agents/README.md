# Module C: Proactive Agents

Task classification and automated workflow execution for Linux administration.

## Features

- Task type identification from user queries
- Predefined workflows for common admin tasks
- Integration with Core Intelligence and Knowledge Vault
- Session management and state tracking

## API Endpoints

- `GET /health` - Health check
- `POST /execute_task` - Execute predefined tasks

## Supported Tasks

- Log analysis and issue identification
- Backup script generation
- System monitoring and health checks

## Configuration

- Port: 8003
- Session storage: In-memory dictionary
- Confirmation required for critical tasks

## Development

```bash
cd modules/module_c_agents
python main.py
```