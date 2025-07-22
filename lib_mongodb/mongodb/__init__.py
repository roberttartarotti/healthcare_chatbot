"""
Healthcare MongoDB Library

A MongoDB library for healthcare chatbot system with patient data management,
lab results, and medical records operations.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

from .version import __version__
__author__ = "Robert Tartarotti"
__email__ = "robert.tartarotti@gmail.com"
__date__ = "July 22, 2025"

from .client import MongoDBClient
from .models import Patient, LabResult, Medication, Appointment
from .exceptions import MongoDBError, ConnectionError, ValidationError
from .config import MongoDBConfig, logger, get_logger

__all__ = [
    "MongoDBClient",
    "Patient",
    "LabResult", 
    "Medication",
    "Appointment",
    "MongoDBError",
    "ConnectionError",
    "ValidationError",
    "MongoDBConfig",
    "logger",
    "get_logger",
] 