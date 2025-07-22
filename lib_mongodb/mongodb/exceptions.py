"""
Custom Exceptions for Healthcare MongoDB Library

Defines specific exception types for different error scenarios in the healthcare system.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""


class MongoDBError(Exception):
    """Base exception for MongoDB operations."""
    pass


class ConnectionError(MongoDBError):
    """Raised when there's an issue connecting to MongoDB."""
    pass


class ValidationError(MongoDBError):
    """Raised when data validation fails."""
    pass


class NotFoundError(MongoDBError):
    """Raised when a document is not found in the database."""
    pass


class DuplicateError(MongoDBError):
    """Raised when trying to insert a duplicate document."""
    pass


class ConfigurationError(MongoDBError):
    """Raised when there's an issue with configuration."""
    pass 