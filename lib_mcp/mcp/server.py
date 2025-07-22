"""
Healthcare MCP Server

Pure MCP server implementation for healthcare chatbot system with tools and resources.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import asyncio
import sys
from mcp.server import Server, ServerSession
from mcp.server.stdio import stdio_server

from .config import MCPConfig, get_logger
from .tools import HealthcareTools
from .resources import HealthcareResources
from .exceptions import ServerError


class MCPServer:
    """Pure MCP server for healthcare system with tools and resources."""
    
    def __init__(self, mongo_client, celery_app=None):
        """
        Initialize MCP server.
        
        Args:
            mongo_client: MongoDB client instance
            celery_app: Celery app instance for background tasks
        """
        self.mongo_client = mongo_client
        self.celery_app = celery_app
        self.logger = get_logger("server")
        
        self.tools = HealthcareTools(mongo_client, celery_app)
        self.resources = HealthcareResources(mongo_client)
        
        self.mcp_server = Server("healthcare-mcp-server")
        self._setup_mcp_handlers()
    
    def _setup_mcp_handlers(self):
        """Setup MCP server handlers."""
        
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> list:
            """List available tools."""
            self.logger.info("Listing tools")
            return self.tools.get_tools()
        
        @self.mcp_server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> dict:
            """Handle tool calls."""
            self.logger.info(f"Calling tool: {name}")
            result = await self.tools.handle_tool_call(None, name, arguments)
            return result.dict()
        
        @self.mcp_server.list_resources()
        async def handle_list_resources() -> list:
            """List available resources."""
            self.logger.info("Listing resources")
            return self.resources.get_resources()
        
        @self.mcp_server.read_resource()
        async def handle_read_resource(uri: str) -> dict:
            """Read a resource."""
            self.logger.info(f"Reading resource: {uri}")
            result = await self.resources.read_resource(None, uri)
            return result.dict()
    
    async def start(self):
        """
        Start the MCP server.
        
        Raises:
            ServerError: If server fails to start
        """
        self.logger.info("Starting MCP server...")
        
        try:
            async with stdio_server() as (read, write):
                await self.mcp_server.run(
                    read,
                    write,
                    ServerSession(
                        server_name="healthcare-mcp-server",
                        server_version="1.0.0",
                        capabilities={
                            "tools": {"listChanged": True},
                            "resources": {"listChanged": True}
                        }
                    )
                )
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise ServerError(f"Failed to start MCP server: {e}")


def main():
    """Main entry point for the MCP server."""
    from healthcare_mongodb import MongoDBClient
    
    mongo_client = MongoDBClient()
    
    try:
        mongo_client.connect()
        
        mcp_server = MCPServer(mongo_client)
        
        asyncio.run(mcp_server.start())
        
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        mongo_client.disconnect()


if __name__ == "__main__":
    main() 