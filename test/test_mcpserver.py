"""
Test MCP Server

Tests for MCP server, tools, and resources.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import pytest
import os
import sys
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib_mcp'))

from healthcare_mcp.server import MCPServer
from healthcare_mcp.tools import HealthcareTools
from healthcare_mcp.resources import HealthcareResources
from healthcare_mcp.exceptions import ToolError, ServerError


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_server_initialization(self):
        """Test MCP server initialization."""
        mock_mongo_client = Mock()
        mock_celery_app = Mock()
    
        server = MCPServer(mock_mongo_client, mock_celery_app)
    
        assert server.mongo_client == mock_mongo_client
        assert server.celery_app == mock_celery_app
        assert server.tools is not None
        assert server.resources is not None
        assert server.logger is not None
    
    def test_server_initialization_without_celery(self):
        """Test MCP server initialization without Celery."""
        mock_mongo_client = Mock()
        
        server = MCPServer(mock_mongo_client)
        
        assert server.mongo_client == mock_mongo_client
        assert server.celery_app is None
        assert server.tools is not None
        assert server.resources is not None
    
    @pytest.mark.asyncio
    async def test_start_server(self):
        """Test starting the MCP server."""
        mock_mongo_client = Mock()
        server = MCPServer(mock_mongo_client)
        
        try:
            task = asyncio.create_task(server.start())
            
            await asyncio.sleep(0.1)
            
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
        except Exception as e:
            pytest.fail(f"Server start failed: {e}")


class TestHealthcareTools:
    """Test healthcare MCP tools."""
    
    def test_tools_initialization(self):
        """Test tools initialization."""
        mock_mongo_client = Mock()
        mock_celery_app = Mock()
        
        tools = HealthcareTools(mock_mongo_client, mock_celery_app)
        
        assert tools.mongo_client == mock_mongo_client
        assert tools.celery_app == mock_celery_app
    
    def test_get_tools(self):
        """Test getting list of available tools."""
        mock_mongo_client = Mock()
        tools = HealthcareTools(mock_mongo_client)
        
        tool_list = tools.get_tools()
        
        assert len(tool_list) > 0
        
        tool_names = [tool.name for tool in tool_list]
        assert "get_patient" in tool_names
        assert "create_patient" in tool_names
        assert "get_lab_results" in tool_names
        assert "create_lab_result" in tool_names
        assert "schedule_appointment" in tool_names
        assert "generate_health_report" in tool_names
        assert "get_task_status" in tool_names
    
    def test_tool_schemas(self):
        """Test tool input schemas."""
        mock_mongo_client = Mock()
        tools = HealthcareTools(mock_mongo_client)
        
        tool_list = tools.get_tools()
        
        get_patient_tool = next(t for t in tool_list if t.name == "get_patient")
        assert "patient_id" in get_patient_tool.input_schema["properties"]
        assert "patient_id" in get_patient_tool.input_schema["required"]
        
        create_patient_tool = next(t for t in tool_list if t.name == "create_patient")
        assert "name" in create_patient_tool.input_schema["properties"]
        assert "age" in create_patient_tool.input_schema["properties"]
        assert "gender" in create_patient_tool.input_schema["properties"]
        assert "patient_id" in create_patient_tool.input_schema["required"]
        assert "name" in create_patient_tool.input_schema["required"]
        assert "age" in create_patient_tool.input_schema["required"]
        assert "gender" in create_patient_tool.input_schema["required"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_get_patient(self):
        """Test handling get_patient tool call."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_one.return_value = {"patient_id": "P001", "name": "John Doe"}
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(None, "get_patient", {"patient_id": "P001"})
        
        assert result["success"] is True
        assert "data" in result
        mock_mongo_client.find_one.assert_called_once_with("patients", {"patient_id": "P001"})
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_get_patient_not_found(self):
        """Test handling get_patient tool call when patient not found."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_one.return_value = None
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(None, "get_patient", {"patient_id": "P999"})
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown_tool(self):
        """Test handling unknown tool call."""
        mock_mongo_client = Mock()
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(None, "unknown_tool", {})
        
        assert result["success"] is False
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_create_patient(self):
        """Test handling create_patient tool call."""
        mock_mongo_client = Mock()
        mock_mongo_client.insert_one.return_value = "P002"
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(
            None, 
            "create_patient", 
            {
                "patient_id": "P002",
                "name": "Jane Doe",
                "age": 28,
                "gender": "female"
            }
        )
        
        assert result["success"] is True
        assert "message" in result
        assert "created successfully" in result["message"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_get_lab_results(self):
        """Test handling get_lab_results tool call."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_many.return_value = [
            {"result_id": "LR001", "test_name": "glucose", "value": 95.0}
        ]
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(None, "get_lab_results", {"patient_id": "P001"})
        
        assert result["success"] is True
        assert "data" in result
        assert "lab_results" in result["data"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_generate_health_report_with_celery(self):
        """Test handling generate_health_report tool call with Celery."""
        mock_mongo_client = Mock()
        mock_celery_app = Mock()
        mock_task = Mock()
        mock_task.id = "task_123"
        mock_celery_app.send_task.return_value = mock_task
        
        tools = HealthcareTools(mock_mongo_client, mock_celery_app)
        
        result = await tools.handle_tool_call(
            None, 
            "generate_health_report", 
            {"patient_id": "P001", "report_type": "detailed"}
        )
        
        assert result["success"] is True
        assert "message" in result
        assert "task_123" in result["message"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_generate_health_report_without_celery(self):
        """Test handling generate_health_report tool call without Celery."""
        mock_mongo_client = Mock()
        tools = HealthcareTools(mock_mongo_client)
        
        result = await tools.handle_tool_call(
            None, 
            "generate_health_report", 
            {"patient_id": "P001", "report_type": "detailed"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "Celery" in result["error"]


class TestHealthcareResources:
    """Test healthcare MCP resources."""
    
    def test_resources_initialization(self):
        """Test resources initialization."""
        mock_mongo_client = Mock()
        
        resources = HealthcareResources(mock_mongo_client)
        
        assert resources.mongo_client == mock_mongo_client
    
    def test_get_resources(self):
        """Test getting list of available resources."""
        mock_mongo_client = Mock()
        resources = HealthcareResources(mock_mongo_client)
        
        resource_list = resources.get_resources()
        
        assert len(resource_list) > 0
        
        resource_uris = [resource.uri for resource in resource_list]
        assert "healthcare://patients" in resource_uris
        assert "healthcare://lab-results" in resource_uris
        assert "healthcare://appointments" in resource_uris
        assert "healthcare://medications" in resource_uris
        assert "healthcare://system/status" in resource_uris
    
    @pytest.mark.asyncio
    async def test_read_patients_resource(self):
        """Test reading patients resource."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_many.return_value = [
            {"patient_id": "P001", "name": "John Doe"},
            {"patient_id": "P002", "name": "Jane Doe"}
        ]
        resources = HealthcareResources(mock_mongo_client)
        
        result = await resources.read_resource(None, "healthcare://patients")
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["resource_type"] == "patients"
        assert result["data"]["total_count"] == 2
    
    @pytest.mark.asyncio
    async def test_read_lab_results_resource(self):
        """Test reading lab results resource."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_many.return_value = [
            {"result_id": "LR001", "test_name": "glucose", "value": 95.0},
            {"result_id": "LR002", "test_name": "cholesterol", "value": 180.0}
        ]
        resources = HealthcareResources(mock_mongo_client)
        
        result = await resources.read_resource(None, "healthcare://lab-results")
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["resource_type"] == "lab_results"
        assert result["data"]["total_count"] == 2
    
    @pytest.mark.asyncio
    async def test_read_system_status_resource(self):
        """Test reading system status resource."""
        mock_mongo_client = Mock()
        mock_mongo_client.find_many.side_effect = [
            [{"patient_id": "P001"}],
            [{"result_id": "LR001"}],
            [{"appointment_id": "A001"}],
            [{"medication_id": "M001"}]
        ]
        resources = HealthcareResources(mock_mongo_client)
        
        result = await resources.read_resource(None, "healthcare://system/status")
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["resource_type"] == "system_status"
        assert "database_stats" in result["data"]
    
    @pytest.mark.asyncio
    async def test_read_resource_not_found(self):
        """Test reading non-existent resource."""
        mock_mongo_client = Mock()
        resources = HealthcareResources(mock_mongo_client)
        
        result = await resources.read_resource(None, "healthcare://unknown")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__]) 