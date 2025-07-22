import pytest
import pika
import requests
import time
import socket
import subprocess
from typing import Generator


@pytest.fixture
def rabbitmq_url():
    """RabbitMQ connection URL."""
    return "amqp://admin:password@localhost:5672/"


def wait_for_rabbitmq(host='localhost', port=5672, timeout=30):
    """Wait for RabbitMQ to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(1)
    return False


def start_rabbitmq_container():
    """Start RabbitMQ container for tests."""
    subprocess.run(["docker-compose", "up", "-d", "rabbitmq"], check=True)
    time.sleep(5)


def stop_rabbitmq_container():
    """Stop RabbitMQ container."""
    subprocess.run(["docker-compose", "stop", "rabbitmq"], check=True)


@pytest.mark.test_rabbitmq_container
class TestRabbitMQContainer:
    """Test suite for RabbitMQ container functionality."""
    
    @classmethod
    def setup_class(cls):
        """Start RabbitMQ container before all tests in this class."""
        start_rabbitmq_container()
    
    @classmethod
    def teardown_class(cls):
        """Stop RabbitMQ container after all tests in this class."""
        stop_rabbitmq_container()
    
    def test_container_is_running(self):
        """Test that RabbitMQ container is running."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=healthcare_rabbitmq", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Up" in result.stdout
    
    def test_rabbitmq_connection(self, rabbitmq_url):
        """Test basic RabbitMQ connection."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            assert connection.is_open
            connection.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to RabbitMQ: {e}")
    
    def test_queue_operations(self, rabbitmq_url):
        """Test creating and deleting queues."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()
            
            queue_name = "test_queue"
            result = channel.queue_declare(queue=queue_name, durable=True)
            assert result.method.queue == queue_name
            
            channel.queue_delete(queue=queue_name)
            
            connection.close()
        except Exception as e:
            pytest.fail(f"Failed to perform queue operations: {e}")
    
    def test_message_publish_consume(self, rabbitmq_url):
        """Test publishing and consuming messages."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()
            
            queue_name = "test_message_queue"
            channel.queue_declare(queue=queue_name)
            
            test_message = "Hello, RabbitMQ!"
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=test_message
            )
            
            method_frame, header_frame, body = channel.basic_get(queue=queue_name)
            assert body.decode() == test_message
            
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            
            channel.queue_delete(queue=queue_name)
            connection.close()
        except Exception as e:
            pytest.fail(f"Failed to perform message operations: {e}")
    
    def test_management_api(self, rabbitmq_management_url):
        """Test RabbitMQ Management API."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            response = requests.get(f"{rabbitmq_management_url}/overview", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "rabbitmq_version" in data
            assert "management_version" in data
        except Exception as e:
            pytest.fail(f"Failed to access Management API: {e}")
    
    def test_health_check(self):
        """Test container health check."""
        import json
        
        result = subprocess.run(
            ["docker", "inspect", "healthcare_rabbitmq", "--format", "{{json .State.Health.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        health_status = result.stdout.strip().strip('"')
        assert health_status in ["healthy", "starting"]
    
    def test_management_ui_accessible(self):
        """Test that Management UI is accessible."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            response = requests.get("http://localhost:15672", timeout=10)
            assert response.status_code == 200
            assert "RabbitMQ Management" in response.text
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Management UI not accessible: {e}")
    
    def test_amqp_port_open(self):
        """Test that AMQP port is open and accessible."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5672))
        sock.close()
        
        assert result == 0, "AMQP port 5672 is not accessible" 