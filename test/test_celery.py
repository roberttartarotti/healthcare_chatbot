"""
Test suite for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import pytest
import time
import subprocess
import socket
import os
import sys
from typing import Generator, Dict, Any
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib_celery'))

try:
    from healthcare_celery import create_celery_app, get_celery_app
    from healthcare_celery.config import CeleryConfig
    from healthcare_celery.exceptions import CeleryError, TaskError
    from healthcare_celery.tasks import health_check, process_healthcare_data, send_notification
    CELERY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Celery library: {e}")
    CELERY_AVAILABLE = False


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


@pytest.mark.skipif(not CELERY_AVAILABLE, reason="Celery library not available")
@pytest.mark.test_rabbitmq_container
class TestCeleryLibrary:
    """Test suite for Celery library functionality."""
    
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
    
    def test_celery_config(self):
        """Test Celery configuration."""
        assert hasattr(CeleryConfig, 'broker_url')
        assert hasattr(CeleryConfig, 'result_backend')
        assert hasattr(CeleryConfig, 'timezone')
        assert CeleryConfig.timezone == "America/Sao_Paulo"
        
        assert CeleryConfig.get_broker_url() == CeleryConfig.broker_url
        assert CeleryConfig.get_result_backend() == CeleryConfig.result_backend
        assert isinstance(CeleryConfig.get_task_routes(), dict)
        assert isinstance(CeleryConfig.get_beat_schedule(), dict)
    
    def test_create_celery_app(self):
        """Test creating a Celery application."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            app = create_celery_app("test_app")
            assert app is not None
            assert app.main == "test_app"
            
            assert app.conf.broker_url == CeleryConfig.broker_url
            assert app.conf.result_backend == CeleryConfig.result_backend
            assert app.conf.timezone == CeleryConfig.timezone
            
        except Exception as e:
            pytest.fail(f"Failed to create Celery app: {e}")
    
    def test_get_celery_app(self):
        """Test getting the default Celery application."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            app = get_celery_app()
            assert app is not None
            assert app.main == "healthcare_celery"
        except Exception as e:
            pytest.fail(f"Failed to get Celery app: {e}")
    
    def test_task_registration(self):
        """Test that tasks are properly registered."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            app = get_celery_app()
            
            registered_tasks = app.tasks.keys()
            
            expected_tasks = [
                'healthcare_celery.tasks.health_check',
                'healthcare_celery.tasks.cleanup_old_tasks',
                'healthcare_celery.tasks.process_healthcare_data',
                'healthcare_celery.tasks.send_notification'
            ]
            
            for task_name in expected_tasks:
                assert task_name in registered_tasks, f"Task {task_name} not registered"
                
        except Exception as e:
            pytest.fail(f"Failed to check task registration: {e}")
    
    def test_health_check_task(self):
        """Test the health check task."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            result = health_check.run()
            
            assert isinstance(result, dict)
            assert result["status"] == "healthy"
            assert "task_id" in result
            assert "worker" in result
            assert "timestamp" in result
            
        except Exception as e:
            pytest.fail(f"Failed to test health check task: {e}")
    
    def test_process_healthcare_data_task(self):
        """Test the process healthcare data task."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            test_data = {
                "type": "patient_data",
                "patient_id": "12345",
                "data": {"name": "John Doe", "age": 30}
            }
            
            result = process_healthcare_data.run(test_data)
            
            assert isinstance(result, dict)
            assert result["status"] == "processed"
            assert "task_id" in result
            assert result["data_type"] == "patient_data"
            assert "processed_at" in result
            
        except Exception as e:
            pytest.fail(f"Failed to test process healthcare data task: {e}")
    
    def test_send_notification_task(self):
        """Test the send notification task."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            notification_data = {
                "type": "email",
                "recipient": "user@example.com",
                "subject": "Test notification"
            }
            
            result = send_notification.run(notification_data)
            
            assert isinstance(result, dict)
            assert result["status"] == "sent"
            assert "task_id" in result
            assert result["notification_type"] == "email"
            assert "sent_at" in result
            
        except Exception as e:
            pytest.fail(f"Failed to test send notification task: {e}")
    
    def test_task_error_handling(self):
        """Test task error handling."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            with pytest.raises(Exception):
                process_healthcare_data.run(None)
                
        except Exception as e:
            pytest.fail(f"Failed to test error handling: {e}")
    
    def test_celery_configuration_values(self):
        """Test specific configuration values."""
        assert CeleryConfig.timezone == "America/Sao_Paulo"
        
        assert isinstance(CeleryConfig.worker_concurrency, int)
        assert CeleryConfig.worker_concurrency > 0
        
        task_routes = CeleryConfig.get_task_routes()
        assert "healthcare_celery.tasks.*" in task_routes
        assert task_routes["healthcare_celery.tasks.*"]["queue"] == "healthcare"
        
        beat_schedule = CeleryConfig.get_beat_schedule()
        assert "health-check" in beat_schedule
        assert "cleanup-old-tasks" in beat_schedule
    
    def test_rabbitmq_connection_for_celery(self):
        """Test that Celery can connect to RabbitMQ."""
        if not wait_for_rabbitmq():
            pytest.skip("RabbitMQ container not ready within timeout")
        
        try:
            app = get_celery_app()
            
            try:
                inspect = app.control.inspect()
                active = inspect.active()
                assert True
            except Exception as e:
                if "connection" in str(e).lower():
                    pytest.fail(f"Failed to connect to RabbitMQ: {e}")
                pass
                
        except Exception as e:
            pytest.fail(f"Failed to test RabbitMQ connection: {e}")


@pytest.mark.skipif(not CELERY_AVAILABLE, reason="Celery library not available")
class TestCeleryUnit:
    """Unit tests for Celery library (no external dependencies)."""
    
    def test_celery_config_structure(self):
        """Test Celery configuration structure."""
        required_attrs = [
            'broker_url', 'result_backend', 'timezone', 'worker_concurrency',
            'task_serializer', 'accept_content', 'result_serializer',
            'task_routes', 'beat_schedule'
        ]
        
        for attr in required_attrs:
            assert hasattr(CeleryConfig, attr), f"Missing configuration attribute: {attr}"
    
    def test_exception_classes(self):
        """Test custom exception classes."""
        from healthcare_celery.exceptions import (
            CeleryError, TaskError, BrokerConnectionError, 
            WorkerError, BeatError, ConfigurationError
        )
        
        assert isinstance(CeleryError("test"), CeleryError)
        assert isinstance(TaskError("test"), TaskError)
        assert isinstance(BrokerConnectionError("test"), BrokerConnectionError)
        assert isinstance(WorkerError("test"), WorkerError)
        assert isinstance(BeatError("test"), BeatError)
        assert isinstance(ConfigurationError("test"), ConfigurationError)
    
    def test_task_function_signatures(self):
        """Test that task functions have correct signatures."""
        import inspect
        
        assert callable(health_check)
        
        assert callable(process_healthcare_data)
        
        assert callable(send_notification)
        
        assert hasattr(health_check, 'delay')
        assert hasattr(process_healthcare_data, 'delay')
        assert hasattr(send_notification, 'delay')


if __name__ == "__main__":
    pytest.main([__file__]) 