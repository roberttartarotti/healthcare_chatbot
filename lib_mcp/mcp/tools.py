"""
Healthcare MCP Tools

Tools for healthcare operations including patient management, lab results,
appointments, and background tasks.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import json
from typing import List, Dict, Any
from mcp.server import ServerSession, types
from mcp.server.stdio import stdio_server

from .config import get_logger
from .exceptions import ToolError


class HealthcareTools:
    """Healthcare tools for MCP server."""
    
    def __init__(self, mongo_client, celery_app=None):
        """
        Initialize healthcare tools.
        
        Args:
            mongo_client: MongoDB client instance
            celery_app: Celery app instance for background tasks
        """
        self.mongo_client = mongo_client
        self.celery_app = celery_app
        self.logger = get_logger("tools")
    
    def get_tools(self) -> List[types.Tool]:
        """
        Get list of available tools.
        
        Returns:
            List[types.Tool]: List of available healthcare tools
        """
        return [
            types.Tool(
                name="get_patient",
                description="Get patient information by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "Patient ID"}
                    },
                    "required": ["patient_id"]
                }
            ),
            types.Tool(
                name="create_patient",
                description="Create a new patient",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "Patient ID"},
                        "name": {"type": "string", "description": "Patient name"},
                        "age": {"type": "integer", "description": "Patient age"},
                        "gender": {"type": "string", "description": "Patient gender (male/female/other)"},
                        "email": {"type": "string", "description": "Patient email"},
                        "phone": {"type": "string", "description": "Patient phone number"}
                    },
                    "required": ["patient_id", "name", "age", "gender"]
                }
            ),
            types.Tool(
                name="get_lab_results",
                description="Get lab results for a patient",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "Patient ID"}
                    },
                    "required": ["patient_id"]
                }
            ),
            types.Tool(
                name="create_lab_result",
                description="Create a new lab result",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "result_id": {"type": "string", "description": "Lab result ID"},
                        "patient_id": {"type": "string", "description": "Patient ID"},
                        "test_name": {"type": "string", "description": "Test name"},
                        "value": {"type": "number", "description": "Test value"},
                        "unit": {"type": "string", "description": "Test unit"},
                        "status": {"type": "string", "description": "Test status (normal/abnormal/critical)"}
                    },
                    "required": ["result_id", "patient_id", "test_name", "value"]
                }
            ),
            types.Tool(
                name="schedule_appointment",
                description="Schedule a new appointment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "description": "Appointment ID"},
                        "patient_id": {"type": "string", "description": "Patient ID"},
                        "doctor_id": {"type": "string", "description": "Doctor ID"},
                        "appointment_date": {"type": "string", "description": "Appointment date (ISO format)"},
                        "duration_minutes": {"type": "integer", "description": "Appointment duration in minutes"},
                        "appointment_type": {"type": "string", "description": "Type of appointment"}
                    },
                    "required": ["appointment_id", "patient_id", "doctor_id", "appointment_date"]
                }
            ),
            types.Tool(
                name="generate_health_report",
                description="Generate a health report for a patient (background task)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "Patient ID"},
                        "report_type": {"type": "string", "description": "Type of report (basic/detailed)"}
                    },
                    "required": ["patient_id", "report_type"]
                }
            ),
            types.Tool(
                name="get_task_status",
                description="Get status of a background task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"}
                    },
                    "required": ["task_id"]
                }
            )
        ]
    
    async def handle_tool_call(self, session: ServerSession, name: str, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Handle tool calls.
        
        Args:
            session: MCP session
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            types.TextContent: Tool execution result
        """
        try:
            self.logger.info(f"Handling tool call: {name} with arguments: {arguments}")
            
            if name == "get_patient":
                return await self._get_patient(arguments)
            elif name == "create_patient":
                return await self._create_patient(arguments)
            elif name == "get_lab_results":
                return await self._get_lab_results(arguments)
            elif name == "create_lab_result":
                return await self._create_lab_result(arguments)
            elif name == "schedule_appointment":
                return await self._schedule_appointment(arguments)
            elif name == "generate_health_report":
                return await self._generate_health_report(arguments)
            elif name == "get_task_status":
                return await self._get_task_status(arguments)
            else:
                return types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling tool call {name}: {e}")
            return types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
    
    async def _get_patient(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Get patient information.
        
        Args:
            arguments: Tool arguments containing patient_id
            
        Returns:
            types.TextContent: Patient data or error message
        """
        patient_id = arguments.get("patient_id")
        patient = self.mongo_client.find_one("patients", {"patient_id": patient_id})
        
        if patient:
            return types.TextContent(
                type="application/json",
                data=patient
            )
        else:
            return types.TextContent(
                type="text",
                text=f"Patient with ID {patient_id} not found"
            )
    
    async def _create_patient(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Create a new patient.
        
        Args:
            arguments: Tool arguments containing patient data
            
        Returns:
            types.TextContent: Creation result
        """
        patient_data = {
            "patient_id": arguments["patient_id"],
            "name": arguments["name"],
            "age": arguments["age"],
            "gender": arguments["gender"],
            "email": arguments.get("email"),
            "phone": arguments.get("phone"),
            "created_at": "2025-07-22T00:00:00Z"
        }
        
        result = self.mongo_client.insert_one("patients", patient_data)
        
        return types.TextContent(
            type="text",
            text=f"Patient created successfully with ID: {result}"
        )
    
    async def _get_lab_results(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Get lab results for a patient.
        
        Args:
            arguments: Tool arguments containing patient_id
            
        Returns:
            types.TextContent: Lab results data
        """
        patient_id = arguments.get("patient_id")
        results = self.mongo_client.find_many("lab_results", {"patient_id": patient_id})
        
        return types.TextContent(
            type="application/json",
            data={"lab_results": results}
        )
    
    async def _create_lab_result(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Create a new lab result.
        
        Args:
            arguments: Tool arguments containing lab result data
            
        Returns:
            types.TextContent: Creation result
        """
        lab_data = {
            "result_id": arguments["result_id"],
            "patient_id": arguments["patient_id"],
            "test_name": arguments["test_name"],
            "value": arguments["value"],
            "unit": arguments.get("unit"),
            "status": arguments.get("status", "normal"),
            "created_at": "2025-07-22T00:00:00Z"
        }
        
        result = self.mongo_client.insert_one("lab_results", lab_data)
        
        return types.TextContent(
            type="text",
            text=f"Lab result created successfully with ID: {result}"
        )
    
    async def _schedule_appointment(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Schedule a new appointment.
        
        Args:
            arguments: Tool arguments containing appointment data
            
        Returns:
            types.TextContent: Scheduling result
        """
        appointment_data = {
            "appointment_id": arguments["appointment_id"],
            "patient_id": arguments["patient_id"],
            "doctor_id": arguments["doctor_id"],
            "appointment_date": arguments["appointment_date"],
            "duration_minutes": arguments.get("duration_minutes", 30),
            "appointment_type": arguments.get("appointment_type", "consultation"),
            "status": "scheduled",
            "created_at": "2025-07-22T00:00:00Z"
        }
        
        result = self.mongo_client.insert_one("appointments", appointment_data)
        
        return types.TextContent(
            type="text",
            text=f"Appointment scheduled successfully with ID: {result}"
        )
    
    async def _generate_health_report(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Generate a health report (background task).
        
        Args:
            arguments: Tool arguments containing patient_id and report_type
            
        Returns:
            types.TextContent: Task queuing result
        """
        if not self.celery_app:
            return types.TextContent(
                type="text",
                text="Error: Celery is not configured for background tasks"
            )
        
        patient_id = arguments["patient_id"]
        report_type = arguments["report_type"]
        
        task = self.celery_app.send_task(
            "healthcare.tasks.generate_health_report",
            args=[patient_id, report_type]
        )
        
        return types.TextContent(
            type="text",
            text=f"Health report generation queued successfully. Task ID: {task.id}"
        )
    
    async def _get_task_status(self, arguments: Dict[str, Any]) -> types.TextContent:
        """
        Get status of a background task.
        
        Args:
            arguments: Tool arguments containing task_id
            
        Returns:
            types.TextContent: Task status data
        """
        if not self.celery_app:
            return types.TextContent(
                type="text",
                text="Error: Celery is not configured for background tasks"
            )
        
        task_id = arguments["task_id"]
        
        task_result = self.celery_app.AsyncResult(task_id)
        
        status_data = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        }
        
        return types.TextContent(
            type="application/json",
            data=status_data
        ) 