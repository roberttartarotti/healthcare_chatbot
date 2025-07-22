"""
Custom Exceptions for Healthcare MCP Library

Defines specific exception types for different error scenarios in the MCP server.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""


class MCPError(Exception):
    """Base exception for MCP operations."""
    pass


class ToolError(MCPError):
    """Raised when there's an issue with MCP tools."""
    pass


class ResourceError(MCPError):
    """Raised when there's an issue with MCP resources."""
    pass


class ServerError(MCPError):
    """Raised when there's an issue with the MCP server."""
    pass


class ConfigurationError(MCPError):
    """Raised when there's an issue with configuration."""
    pass


class ConnectionError(MCPError):
    """Raised when there's an issue connecting to external services."""
    pass 