"""
Configuration Management for Healthcare MCP Library

Centralized configuration for environment variables and logging setup.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import logging
from typing import Optional
from decouple import config


class MCPConfig:
    """Configuration class for MCP server and settings."""
    
    HOST = config("MCP_HOST", default="localhost")
    PORT = config("MCP_PORT", default=8001, cast=int)
    PROTOCOL = config("MCP_PROTOCOL", default="stdio")
    
    MONGODB_USER = config("MONGODB_USER", default="admin")
    MONGODB_PASSWORD = config("MONGODB_PASSWORD", default="password")
    MONGODB_HOST = config("MONGODB_HOST", default="localhost")
    MONGODB_PORT = config("MONGODB_PORT", default="27017")
    MONGODB_DATABASE = config("MONGODB_DATABASE", default="healthcare_db")
    
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="amqp://admin:password@localhost:5672/")
    CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="rpc://")
    
    LOG_LEVEL = config("MCP_LOG_LEVEL", default="INFO")
    LOG_FORMAT = config("MCP_LOG_FORMAT", 
                       default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @classmethod
    def get_mongodb_connection_string(cls) -> str:
        """
        Build MongoDB connection string from configuration.
        
        Returns:
            str: MongoDB connection string
        """
        return f"mongodb://{cls.MONGODB_USER}:{cls.MONGODB_PASSWORD}@{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/{cls.MONGODB_DATABASE}"
    
    @classmethod
    def get_mcp_server_url(cls) -> str:
        """
        Get MCP server URL.
        
        Returns:
            str: MCP server URL
        """
        return f"{cls.PROTOCOL}://{cls.HOST}:{cls.PORT}"


def setup_logging(name: str = "healthcare_mcp", 
                 level: Optional[str] = None,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup logging for the MCP library.
    
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
    
    log_level = level or MCPConfig.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    formatter = logging.Formatter(
        format_string or MCPConfig.LOG_FORMAT
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
    return logging.getLogger(f"healthcare_mcp.{name}") 