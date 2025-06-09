#!/usr/bin/env python3
"""
Advanced AI Agent System - Command Line Interface
"""

import argparse
import sys
import os
from pathlib import Path

from .core.agent import NoStreamAgent
from rich.console import Console


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Advanced AI Agent System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Create a hello world file"
  python main.py "Search for Python tutorials" --verbose
  python main.py "Analyze this directory" --max-steps 10
        """
    )
    
    parser.add_argument(
        'objective',
        help='The objective or task for the AI agent to accomplish'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    parser.add_argument(
        '--max-steps',
        type=int,
        default=15,
        help='Maximum number of steps the agent can take (default: 15)'
    )
    
    parser.add_argument(
        '--ai-provider',
        choices=['auto', 'openai', 'mock'],
        default='auto',
        help='AI provider to use (default: auto)'
    )
    
    args = parser.parse_args()
    
    # Create and run the agent
    try:
        agent = NoStreamAgent(
            objective=args.objective,
            verbose=args.verbose,
            max_steps=args.max_steps
        )
        
        agent.run()
        
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]⚠️ Agent interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()