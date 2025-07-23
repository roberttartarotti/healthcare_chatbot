import pytest
import subprocess
import time
import requests
from decouple import config
from typing import Generator


def pytest_configure(config):
    """
    Register custom markers.
    
    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers", "test_rabbitmq_container: mark test to run RabbitMQ container tests"
    )
    config.addinivalue_line(
        "markers", "test_celery: mark test to run Celery tests"
    )


@pytest.fixture(scope="session")
def docker_compose() -> Generator[None, None, None]:
    """
    Start Docker Compose services before tests and keep them running.
    
    Yields:
        None: Fixture yields after services are started
    """
    print("🚀 Starting Docker Compose services...")
    
    subprocess.run(["docker-compose", "down", "--volumes", "--remove-orphans"], check=False)
    
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    yield
    
    print("✅ Docker Compose services are still running. Use 'docker-compose down' to stop them.")


@pytest.fixture
def rabbitmq_url() -> str:
    """
    Return RabbitMQ connection URL.
    
    Returns:
        str: RabbitMQ connection URL
    """
    user = config("RABBITMQ_USER", default="admin")
    password = config("RABBITMQ_PASSWORD", default="password")
    host = config("RABBITMQ_HOST", default="localhost")
    port = config("RABBITMQ_PORT", default="5672")
    vhost = config("RABBITMQ_VHOST", default="/")
    
    return f"amqp://{user}:{password}@{host}:{port}/{vhost}"


@pytest.fixture
def rabbitmq_management_url() -> str:
    """
    Return RabbitMQ Management API URL.
    
    Returns:
        str: RabbitMQ Management API URL
    """
    user = config("RABBITMQ_USER", default="admin")
    password = config("RABBITMQ_PASSWORD", default="password")
    host = config("RABBITMQ_HOST", default="localhost")
    port = config("RABBITMQ_MANAGEMENT_PORT", default="15672")
    
    return f"http://{user}:{password}@{host}:{port}/api"


@pytest.fixture
def celery_broker_url() -> str:
    """
    Return Celery broker URL (same as RabbitMQ URL).
    
    Returns:
        str: Celery broker URL
    """
    return rabbitmq_url()


@pytest.fixture
def celery_config() -> dict:
    """
    Return Celery configuration for testing.
    
    Returns:
        dict: Celery configuration
    """
    return {
        "broker_url": rabbitmq_url(),
        "result_backend": "rpc://",
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "America/Sao_Paulo",
        "enable_utc": True,
        "worker_concurrency": 2,
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 100,
        "task_always_eager": False,
        "task_eager_propagates": True,
        "task_ignore_result": False,
        "task_store_eager_result": True,
    } 