"""
Healthcare MCP Resources

Resources for providing contextual healthcare data to MCP clients.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass

from .config import get_logger
from .exceptions import ResourceError


@dataclass
class Resource:
    """Simple resource representation."""
    uri: str
    name: str
    description: str
    mime_type: str


class HealthcareResources:
    """Healthcare resources for MCP server."""
    
    def __init__(self, mongo_client):
        """
        Initialize healthcare resources.
        
        Args:
            mongo_client: MongoDB client instance
        """
        self.mongo_client = mongo_client
        self.logger = get_logger("resources")
    
    def get_resources(self) -> List[Resource]:
        """
        Get list of available resources.
        
        Returns:
            List[Resource]: List of available healthcare resources
        """
        return [
            Resource(
                uri="healthcare://patients",
                name="Patients",
                description="All patients in the system",
                mime_type="application/json"
            ),
            Resource(
                uri="healthcare://lab-results",
                name="Lab Results",
                description="All lab results in the system",
                mime_type="application/json"
            ),
            Resource(
                uri="healthcare://appointments",
                name="Appointments",
                description="All appointments in the system",
                mime_type="application/json"
            ),
            Resource(
                uri="healthcare://medications",
                name="Medications",
                description="All medications in the system",
                mime_type="application/json"
            ),
            Resource(
                uri="healthcare://system/status",
                name="System Status",
                description="Current system status and statistics",
                mime_type="application/json"
            )
        ]
    
    async def read_resource(self, session, uri: str) -> Dict[str, Any]:
        """
        Read a resource.
        
        Args:
            session: MCP session
            uri: Resource URI
            
        Returns:
            Dict[str, Any]: Resource content or error message
        """
        try:
            self.logger.info(f"Reading resource: {uri}")
            
            if uri == "healthcare://patients":
                return await self._read_patients_resource(session)
            elif uri == "healthcare://lab-results":
                return await self._read_lab_results_resource(session)
            elif uri == "healthcare://appointments":
                return await self._read_appointments_resource(session)
            elif uri == "healthcare://medications":
                return await self._read_medications_resource(session)
            elif uri == "healthcare://system/status":
                return await self._read_system_status_resource(session)
            else:
                return {
                    "success": False,
                    "error": f"Resource not found: {uri}"
                }
                
        except Exception as e:
            self.logger.error(f"Error reading resource {uri}: {e}")
            return {
                "success": False,
                "error": f"Error reading resource: {str(e)}"
            }
    
    async def _read_patients_resource(self, session) -> Dict[str, Any]:
        """
        Read patients resource.
        
        Args:
            session: MCP session
            
        Returns:
            Dict[str, Any]: Patients data
        """
        patients = self.mongo_client.find_many("patients", {})
        
        content = {
            "resource_type": "patients",
            "total_count": len(patients),
            "patients": patients
        }
        
        return {
            "success": True,
            "data": content,
            "mime_type": "application/json"
        }
    
    async def _read_lab_results_resource(self, session) -> Dict[str, Any]:
        """
        Read lab results resource.
        
        Args:
            session: MCP session
            
        Returns:
            Dict[str, Any]: Lab results data
        """
        lab_results = self.mongo_client.find_many("lab_results", {})
        
        content = {
            "resource_type": "lab_results",
            "total_count": len(lab_results),
            "lab_results": lab_results
        }
        
        return {
            "success": True,
            "data": content,
            "mime_type": "application/json"
        }
    
    async def _read_appointments_resource(self, session) -> Dict[str, Any]:
        """
        Read appointments resource.
        
        Args:
            session: MCP session
            
        Returns:
            Dict[str, Any]: Appointments data
        """
        appointments = self.mongo_client.find_many("appointments", {})
        
        content = {
            "resource_type": "appointments",
            "total_count": len(appointments),
            "appointments": appointments
        }
        
        return {
            "success": True,
            "data": content,
            "mime_type": "application/json"
        }
    
    async def _read_medications_resource(self, session) -> Dict[str, Any]:
        """
        Read medications resource.
        
        Args:
            session: MCP session
            
        Returns:
            Dict[str, Any]: Medications data
        """
        medications = self.mongo_client.find_many("medications", {})
        
        content = {
            "resource_type": "medications",
            "total_count": len(medications),
            "medications": medications
        }
        
        return {
            "success": True,
            "data": content,
            "mime_type": "application/json"
        }
    
    async def _read_system_status_resource(self, session) -> Dict[str, Any]:
        """
        Read system status resource.
        
        Args:
            session: MCP session
            
        Returns:
            Dict[str, Any]: System status data
        """
        patients_count = len(self.mongo_client.find_many("patients", {}))
        lab_results_count = len(self.mongo_client.find_many("lab_results", {}))
        appointments_count = len(self.mongo_client.find_many("appointments", {}))
        medications_count = len(self.mongo_client.find_many("medications", {}))
        
        content = {
            "resource_type": "system_status",
            "system_status": "healthy",
            "database_stats": {
                "patients": patients_count,
                "lab_results": lab_results_count,
                "appointments": appointments_count,
                "medications": medications_count
            },
            "total_records": patients_count + lab_results_count + appointments_count + medications_count
        }
        
        return {
            "success": True,
            "data": content,
            "mime_type": "application/json"
        } 