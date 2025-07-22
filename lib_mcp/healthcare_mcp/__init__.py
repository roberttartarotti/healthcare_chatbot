"""
Healthcare MCP Library

A Model Context Protocol server for healthcare chatbot system with tools,
resources, and REST API integration.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

from .version import __version__

__author__ = "Robert Tartarotti"
__email__ = "robert.tartarotti@gmail.com"
__date__ = "July 22, 2025"

from .tools import HealthcareTools
from .resources import HealthcareResources
from .config import MCPConfig, logger, get_logger

__all__ = [
    "HealthcareTools",
    "HealthcareResources",
    "MCPConfig",
    "logger",
    "get_logger",
] 