"""
Advanced AI Agent System

A modular, extensible AI agent system with rich output formatting
and comprehensive tool integration.
"""

__version__ = "2.0.1"
__author__ = "AI Agent Team"
__email__ = "developer@example.com"

from .core.agent import NoStreamAgent
from .main import main

__all__ = ["NoStreamAgent", "main"]