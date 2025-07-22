# Healthcare MCP Library

A pure Model Context Protocol (MCP) server for healthcare chatbot systems with tools and resources.

## Features

- **MCP Tools**: Healthcare-specific tools for patient management, lab results, appointments
- **MCP Resources**: Contextual data resources for agents
- **Celery Integration**: Background task processing
- **MongoDB Integration**: Seamless connection to healthcare database
- **Comprehensive Logging**: Detailed operation tracking
- **Environment Configuration**: Flexible configuration management

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd lib_mcp

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Dependencies

- Python 3.8+
- MCP SDK >= 1.12.0
- Celery >= 5.3.0
- healthcare-mongodb >= 0.1.0

## Quick Start

### 1. Environment Setup

Create a `.env` file with your configuration:

```bash
# MCP Server Settings
MCP_HOST=localhost
MCP_PORT=8001
MCP_PROTOCOL=stdio

# MongoDB Settings
MONGODB_USER=admin
MONGODB_PASSWORD=password
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=healthcare_db

# Celery Settings
CELERY_BROKER_URL=amqp://admin:password@localhost:5672/
CELERY_RESULT_BACKEND=rpc://

# Logging
MCP_LOG_LEVEL=INFO
```

### 2. Start the MCP Server

```bash
# Start MCP server
start_mcpserver

# Or programmatically
python -c "
from mcp import MCPServer
from healthcare_mongodb import MongoDBClient

client = MongoDBClient()
client.connect()
server = MCPServer(client)
import asyncio
asyncio.run(server.start())
"
```

## API Reference

### MCP Tools

#### get_patient
Get patient information by patient ID.

```python
{
    "patient_id": "P001"
}
```

#### create_patient
Create a new patient record.

```python
{
    "patient_id": "P001",
    "name": "John Doe",
    "age": 35,
    "gender": "male",
    "email": "john@example.com",
    "phone": "+1234567890",
    "medical_history": ["diabetes"],
    "allergies": ["penicillin"]
}
```

#### get_lab_results
Get lab results for a patient.

```python
{
    "patient_id": "P001",
    "test_name": "glucose"  # optional
}
```

#### create_lab_result
Create a new lab result record.

```python
{
    "patient_id": "P001",
    "test_name": "glucose",
    "value": 95.0,
    "unit": "mg/dL",
    "status": "normal",
    "reference_range": "70-100 mg/dL",
    "notes": "Fasting glucose"
}
```

#### schedule_appointment
Schedule a new appointment.

```python
{
    "patient_id": "P001",
    "doctor_id": "D001",
    "appointment_date": "2025-07-25T14:00:00",
    "duration_minutes": 30,
    "appointment_type": "consultation",
    "notes": "Follow-up visit"
}
```

#### generate_health_report
Generate a comprehensive health report (background task).

```python
{
    "patient_id": "P001",
    "report_type": "detailed",
    "include_labs": true,
    "include_medications": true
}
```

#### get_task_status
Check the status of a background task.

```python
{
    "task_id": "abc123"
}
```

### MCP Resources

#### healthcare://patients
Access to all patient records.

#### healthcare://lab-results
Access to all laboratory test results.

#### healthcare://appointments
Access to all appointment records.

#### healthcare://medications
Access to all medication records.

#### healthcare://system/status
Current system status and health metrics.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | localhost | MCP server host |
| `MCP_PORT` | 8001 | MCP server port |
| `MCP_PROTOCOL` | stdio | MCP protocol |
| `MONGODB_USER` | admin | MongoDB username |
| `MONGODB_PASSWORD` | password | MongoDB password |
| `MONGODB_HOST` | localhost | MongoDB host |
| `MONGODB_PORT` | 27017 | MongoDB port |
| `MONGODB_DATABASE` | healthcare_db | MongoDB database name |
| `CELERY_BROKER_URL` | amqp://admin:password@localhost:5672/ | Celery broker URL |
| `CELERY_RESULT_BACKEND` | rpc:// | Celery result backend |
| `MCP_LOG_LEVEL` | INFO | Logging level |
| `MCP_LOG_FORMAT` | %(asctime)s - %(name)s - %(levelname)s - %(message)s | Log format |

## Development

### Project Structure

```
lib_mcp/
├── pyproject.toml          # Project configuration
├── setup.py               # Setup script
├── README.md              # This file
└── mcp/                   # Main package
    ├── __init__.py        # Package initialization
    ├── config.py          # Configuration management
    ├── server.py          # Pure MCP server
    ├── tools.py           # MCP tools implementation
    ├── resources.py       # MCP resources implementation
    ├── exceptions.py      # Custom exceptions
    └── version.py         # Dynamic versioning
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=mcp
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Integration Examples

### With LLM Agent

```python
from mcp import MCPServer
from healthcare_mongodb import MongoDBClient

# Initialize
client = MongoDBClient()
client.connect()
server = MCPServer(client)

# Agent can now use MCP tools and resources
# Tools: get_patient, create_patient, get_lab_results, etc.
# Resources: healthcare://patients, healthcare://lab-results, etc.
```

### With Celery Background Tasks

```python
from celery import Celery

# Initialize Celery
celery_app = Celery('healthcare')
celery_app.config_from_object('celeryconfig')

# Use with MCP server
server = MCPServer(mongo_client, celery_app)

# Now tools can trigger background tasks
# generate_health_report tool will queue Celery tasks
```

## Architecture

This library provides a **pure MCP server** that focuses solely on the Model Context Protocol:

```
┌─────────────────┐
│   LLM Agent     │
│                 │
│ • MCP Client    │◄──► MCP Protocol
│ • Tools         │
│ • Resources     │
└─────────────────┘
         │
         ▼
┌─────────────────────────┐
│    MCP Server           │
│                         │
│ • MCP Protocol          │
│ • Tools                 │
│ • Resources             │
│ • Celery Integration    │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│    MongoDB Library      │
│                         │
│ • Database Operations   │
│ • Data Models           │
└─────────────────────────┘
```

**Note**: For external system integrations (web apps, mobile apps, etc.), a separate REST API library will be created later.

## License

MIT License - see LICENSE file for details.

## Author

**Robert Tartarotti**
- Email: robert.tartarotti@gmail.com
- Date: July 22, 2025

## Version

This library uses dynamic versioning from git tags. Current version: 0.1.0 