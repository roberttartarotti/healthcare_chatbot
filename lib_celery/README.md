# Healthcare Celery Library

A Celery tasks management library for the healthcare chatbot system.

## Features

- **Task Management**: Asynchronous task processing for healthcare operations
- **Worker Management**: Configurable Celery workers with queue support
- **Beat Scheduler**: Periodic task scheduling for maintenance operations
- **Health Monitoring**: Built-in health check tasks
- **Error Handling**: Comprehensive exception handling and logging
- **Configuration**: Environment-based configuration management

## Installation

### Prerequisites

- Python 3.8+
- RabbitMQ (message broker)
- MongoDB (optional, for result backend)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/healthcare-chatbot/lib_celery.git
cd lib_celery
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create a `.env` file with your configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CELERY_BROKER_URL` | RabbitMQ broker URL | `amqp://admin:password@localhost:5672/` |
| `CELERY_RESULT_BACKEND` | Result backend URL | `rpc://` |
| `CELERY_WORKER_CONCURRENCY` | Number of worker processes | `4` |
| `CELERY_WORKER_LOG_LEVEL` | Logging level | `INFO` |
| `CELERY_TASK_SERIALIZER` | Task serialization format | `json` |
| `CELERY_TIMEZONE` | Timezone for tasks | `America/Sao_Paulo` |

### Task Queues

The library supports multiple queues for different priority levels:

- `healthcare`: Main healthcare tasks
- `high_priority`: Urgent tasks
- `low_priority`: Background tasks
- `default`: Default queue

## Usage

### Starting a Worker

```python
from healthcare_celery.worker import start_worker

# Start worker with default settings
start_worker()

# Start worker with custom settings
start_worker(
    queues=["healthcare", "high_priority"],
    concurrency=8,
    hostname="my-worker@%h"
)
```

### Starting Beat Scheduler

```python
from healthcare_celery.beat import start_beat

# Start beat scheduler
start_beat()
```

### Creating Tasks

```python
from healthcare_celery.tasks import process_healthcare_data

# Submit a task
result = process_healthcare_data.delay({
    "type": "patient_data",
    "patient_id": "12345",
    "data": {...}
})

# Get task result
task_result = result.get()
```

### Available Tasks

- `health_check`: System health monitoring
- `cleanup_old_tasks`: Clean up old task results
- `process_healthcare_data`: Process healthcare data
- `send_notification`: Send notifications

## Docker

### Building the Image

```bash
docker build -t healthcare-celery .
```

### Running with Docker Compose

The library is included in the main docker-compose.yml file:

```yaml
celery_worker:
  build:
    context: .
    dockerfile: lib_celery/Dockerfile
  environment:
    - CELERY_BROKER_URL=amqp://admin:password@rabbitmq:5672/
  depends_on:
    - rabbitmq
    - mongodb
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
mypy .
```

### Project Structure

```
lib_celery/
├── healthcare_celery/
│   ├── __init__.py
│   ├── app.py              # Celery application factory
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exceptions
│   ├── tasks.py            # Task definitions
│   ├── version.py          # Version management
│   ├── worker.py           # Worker management
│   └── beat.py             # Beat scheduler
├── Dockerfile
├── pyproject.toml
├── setup.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

Robert Tartarotti - robert.tartarotti@gmail.com 