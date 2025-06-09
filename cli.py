#!/usr/bin/env python3
"""
Command-line interface entry point for the AI agent.
This module provides the console script entry points.
"""

import sys
import os

# Add the package directory to Python path
#package_dir = os.path.dirname(os.path.abspath(__file__))
#if package_dir not in sys.path:
  #  sys.path.insert(0, package_dir)

from .main import main

def cli_main():
    """Entry point for console scripts."""
    main()

if __name__ == "__main__":
    cli_main()
