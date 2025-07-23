"""
Custom exceptions for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""


class CeleryError(Exception):
    """Base exception for Celery-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize CeleryError.
        
        Args:
            message: Error message
            error_code: Optional error code
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TaskError(CeleryError):
    """Exception raised when a task fails."""
    
    def __init__(self, message: str, task_name: str = None, task_id: str = None):
        """
        Initialize TaskError.
        
        Args:
            message: Error message
            task_name: Name of the failed task
            task_id: ID of the failed task
        """
        self.task_name = task_name
        self.task_id = task_id
        super().__init__(message, "TASK_ERROR")


class BrokerConnectionError(CeleryError):
    """Exception raised when unable to connect to the message broker."""
    
    def __init__(self, message: str, broker_url: str = None):
        """
        Initialize BrokerConnectionError.
        
        Args:
            message: Error message
            broker_url: URL of the broker that failed to connect
        """
        self.broker_url = broker_url
        super().__init__(message, "BROKER_CONNECTION_ERROR")


class WorkerError(CeleryError):
    """Exception raised when there's an issue with the worker."""
    
    def __init__(self, message: str, worker_name: str = None):
        """
        Initialize WorkerError.
        
        Args:
            message: Error message
            worker_name: Name of the worker that encountered the error
        """
        self.worker_name = worker_name
        super().__init__(message, "WORKER_ERROR")


class BeatError(CeleryError):
    """Exception raised when there's an issue with the beat scheduler."""
    
    def __init__(self, message: str, schedule_name: str = None):
        """
        Initialize BeatError.
        
        Args:
            message: Error message
            schedule_name: Name of the schedule that encountered the error
        """
        self.schedule_name = schedule_name
        super().__init__(message, "BEAT_ERROR")


class ConfigurationError(CeleryError):
    """Exception raised when there's a configuration issue."""
    
    def __init__(self, message: str, config_key: str = None):
        """
        Initialize ConfigurationError.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        self.config_key = config_key
        super().__init__(message, "CONFIGURATION_ERROR") 