"""
Version Management for Healthcare MCP Library

Dynamically retrieves version information from git.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import subprocess
import os
from typing import Optional


def get_git_version() -> str:
    """
    Get the current git version (tag or commit hash).
    
    Returns:
        str: Git version string or '0.1.0' as fallback
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return f"0.1.0-{result.stdout.strip()}"
            
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return "0.1.0"


__version__ = get_git_version() 