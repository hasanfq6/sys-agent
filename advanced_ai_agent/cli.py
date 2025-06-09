#!/usr/bin/env python3
"""
Command-line interface entry point for the AI agent.
This module provides the console script entry points.
"""

from .main import main

def cli_main():
    """Entry point for console scripts."""
    main()

if __name__ == "__main__":
    cli_main()