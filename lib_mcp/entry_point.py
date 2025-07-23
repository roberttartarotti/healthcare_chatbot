"""
Entry point for the MCP server

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from healthcare_mcp.server import main

if __name__ == "__main__":
    main() 