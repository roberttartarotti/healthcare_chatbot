# Healthcare Chatbot

A healthcare chatbot system using MongoDB, MCP (Model Context Protocol), and Celery with RabbitMQ.

## Setup

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# RabbitMQ Configuration
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your_secure_password
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
RABBITMQ_VHOST=/

# Docker Compose Project Name
COMPOSE_PROJECT_NAME=healthcare_chatbot
```

### 2. Install Dependencies

```bash
# Install test dependencies
pip install -r test/requirements-test.txt
```

### 3. Run Tests

```bash
# Run RabbitMQ container tests
pytest test/ -m test_rabbitmq_container -v
```

## Docker Services

- **RabbitMQ**: Message broker for Celery tasks
  - AMQP Port: 5672
  - Management UI: http://localhost:15672

## Project Structure

```
├── docker-compose.yml          # Docker services configuration
├── test/                       # Test suite
│   ├── conftest.py            # Pytest configuration
│   ├── test_rabbitmq_container.py  # RabbitMQ tests
│   └── requirements-test.txt   # Test dependencies
├── scripts/                    # Utility scripts
│   └── clean_docker.sh        # Docker cleanup script
└── .env                       # Environment variables (create this)
```
