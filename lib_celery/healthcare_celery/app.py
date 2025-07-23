"""
Celery application factory for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import logging
from typing import Optional
from celery import Celery
from .config import CeleryConfig
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)

celery = Celery("healthcare_celery")

celery.config_from_object(CeleryConfig)

logging.basicConfig(
    level=getattr(logging, CeleryConfig.worker_log_level),
    format=CeleryConfig.worker_log_format
)

logger.info(f"Celery app 'healthcare_celery' created successfully")
logger.info(f"Broker URL: {CeleryConfig.broker_url}")
logger.info(f"Result Backend: {CeleryConfig.result_backend}")


def create_celery_app(name: str = "healthcare_celery") -> Celery:
    """
    Create and configure a Celery application.
    
    Args:
        name: The name of the Celery application
        
    Returns:
        Celery: Configured Celery application
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        app = Celery(name)
        
        app.config_from_object(CeleryConfig)
        
        logging.basicConfig(
            level=getattr(logging, CeleryConfig.worker_log_level),
            format=CeleryConfig.worker_log_format
        )
        
        logger.info(f"Celery app '{name}' created successfully")
        logger.info(f"Broker URL: {CeleryConfig.broker_url}")
        logger.info(f"Result Backend: {CeleryConfig.result_backend}")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Celery app: {e}")
        raise ConfigurationError(f"Failed to create Celery app: {e}")


def get_celery_app() -> Celery:
    """
    Get the default Celery application instance.
    
    Returns:
        Celery: The default Celery application
    """
    return celery 