"""
Configuration Management for Healthcare MongoDB Library

Centralized configuration for environment variables and logging setup.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import logging
from typing import Optional
from decouple import config


class MongoDBConfig:
    """Configuration class for MongoDB connection and settings."""
    
    USER = config("MONGODB_USER", default="admin")
    PASSWORD = config("MONGODB_PASSWORD", default="password")
    HOST = config("MONGODB_HOST", default="localhost")
    PORT = config("MONGODB_PORT", default="27017")
    DATABASE = config("MONGODB_DATABASE", default="healthcare_db")
    
    CONNECTION_TIMEOUT = config("MONGODB_CONNECTION_TIMEOUT", default=5000, cast=int)
    SOCKET_TIMEOUT = config("MONGODB_SOCKET_TIMEOUT", default=5000, cast=int)
    MAX_POOL_SIZE = config("MONGODB_MAX_POOL_SIZE", default=10, cast=int)
    
    LOG_LEVEL = config("MONGODB_LOG_LEVEL", default="INFO")
    LOG_FORMAT = config("MONGODB_LOG_FORMAT", 
                       default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @classmethod
    def get_connection_string(cls) -> str:
        """
        Build MongoDB connection string from configuration.
        
        Returns:
            str: MongoDB connection string
        """
        return f"mongodb://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}?authSource=admin"
    
    @classmethod
    def get_connection_options(cls) -> dict:
        """
        Get MongoDB connection options.
        
        Returns:
            dict: Connection options dictionary
        """
        return {
            "serverSelectionTimeoutMS": cls.CONNECTION_TIMEOUT,
            "socketTimeoutMS": cls.SOCKET_TIMEOUT,
            "maxPoolSize": cls.MAX_POOL_SIZE,
        }


def setup_logging(name: str = "healthcare_mongodb", 
                 level: Optional[str] = None,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup logging for the MongoDB library.
    
    Args:
        name: Logger name
        level: Log level (overrides config if provided)
        format_string: Log format (overrides config if provided)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    log_level = level or MongoDBConfig.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    formatter = logging.Formatter(
        format_string or MongoDBConfig.LOG_FORMAT
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f"healthcare_mongodb.{name}") 