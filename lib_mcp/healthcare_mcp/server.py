"""
Healthcare MCP Server

Pure MCP server implementation for healthcare chatbot system with tools and resources.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import asyncio
import sys
import json
from typing import Dict, Any

from .config import get_logger
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
    
    async def start(self):
        """
        Start the MCP server.
        
        Raises:
            ServerError: If server fails to start
        """
        self.logger.info("Starting MCP server...")
        
        try:
            self.logger.info("MCP server is ready!")
            self.logger.info("Available tools:")
            for tool in self.tools.get_tools():
                self.logger.info(f"  - {tool.name}: {tool.description}")
            
            self.logger.info("Available resources:")
            for resource in self.resources.get_resources():
                self.logger.info(f"  - {resource.uri}: {resource.description}")
            
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise ServerError(f"Failed to start MCP server: {e}")


def main():
    """Main entry point for the MCP server."""
    from mongodb.client import MongoDBClient
    
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