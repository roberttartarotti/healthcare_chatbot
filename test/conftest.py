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