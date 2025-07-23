"""
Healthcare Celery Library

A Celery tasks management library for the healthcare chatbot system.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

from .app import create_celery_app, get_celery_app
from .config import CeleryConfig
from .exceptions import CeleryError, TaskError
from .tasks import register_tasks
from .worker import start_worker
from .beat import start_beat

__version__ = "0.0.1"

__all__ = [
    "create_celery_app",
    "get_celery_app",
    "CeleryConfig", 
    "CeleryError",
    "TaskError",
    "register_tasks",
    "start_worker",
    "start_beat",
    "__version__",
] 