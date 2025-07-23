"""
Configuration management for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import os
from typing import Optional
from decouple import config


class CeleryConfig:
    """Configuration class for Celery application."""
    
    broker_url: str = config(
        "CELERY_BROKER_URL",
        default="amqp://admin:password@localhost:5672/"
    )
    
    result_backend: str = config(
        "CELERY_RESULT_BACKEND", 
        default="rpc://"
    )
    
    task_serializer: str = config("CELERY_TASK_SERIALIZER", default="json")
    accept_content: list = config(
        "CELERY_ACCEPT_CONTENT", 
        default=["json"],
        cast=lambda v: v.split(",") if isinstance(v, str) else v
    )
    result_serializer: str = config("CELERY_RESULT_SERIALIZER", default="json")
    
    timezone: str = config("CELERY_TIMEZONE", default="America/Sao_Paulo")
    enable_utc: bool = config("CELERY_ENABLE_UTC", default=True, cast=bool)
    
    worker_concurrency: int = config("CELERY_WORKER_CONCURRENCY", default=4, cast=int)
    worker_prefetch_multiplier: int = config(
        "CELERY_WORKER_PREFETCH_MULTIPLIER", 
        default=1, 
        cast=int
    )
    worker_max_tasks_per_child: int = config(
        "CELERY_WORKER_MAX_TASKS_PER_CHILD",
        default=1000,
        cast=int
    )
    
    task_routes: dict = {
        "healthcare_celery.tasks.*": {"queue": "healthcare"},
        "healthcare_celery.tasks.high_priority.*": {"queue": "high_priority"},
        "healthcare_celery.tasks.low_priority.*": {"queue": "low_priority"},
    }
    
    task_default_queue: str = config("CELERY_TASK_DEFAULT_QUEUE", default="default")
    task_default_exchange: str = config("CELERY_TASK_DEFAULT_EXCHANGE", default="default")
    task_default_routing_key: str = config("CELERY_TASK_DEFAULT_ROUTING_KEY", default="default")
    
    beat_schedule: dict = {
        "health-check": {
            "task": "healthcare_celery.tasks.health_check",
            "schedule": 300.0,
        },
        "cleanup-old-tasks": {
            "task": "healthcare_celery.tasks.cleanup_old_tasks",
            "schedule": 3600.0,
        },
    }
    
    worker_log_level: str = config("CELERY_WORKER_LOG_LEVEL", default="INFO")
    worker_log_format: str = config(
        "CELERY_WORKER_LOG_FORMAT",
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    task_always_eager: bool = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)
    task_eager_propagates: bool = config("CELERY_TASK_EAGER_PROPAGATES", default=True, cast=bool)
    
    task_ignore_result: bool = config("CELERY_TASK_IGNORE_RESULT", default=False, cast=bool)
    task_store_eager_result: bool = config("CELERY_TASK_STORE_EAGER_RESULT", default=True, cast=bool)
    
    security_key: str = config("CELERY_SECURITY_KEY", default="")
    security_certificate: str = config("CELERY_SECURITY_CERTIFICATE", default="")
    security_cert_store: str = config("CELERY_SECURITY_CERT_STORE", default="")
    
    @classmethod
    def get_broker_url(cls) -> str:
        """Get the broker URL with proper formatting."""
        return cls.broker_url
    
    @classmethod
    def get_result_backend(cls) -> str:
        """Get the result backend URL."""
        return cls.result_backend
    
    @classmethod
    def get_task_routes(cls) -> dict:
        """Get task routing configuration."""
        return cls.task_routes
    
    @classmethod
    def get_beat_schedule(cls) -> dict:
        """Get beat schedule configuration."""
        return cls.beat_schedule 