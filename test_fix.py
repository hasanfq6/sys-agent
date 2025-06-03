#!/usr/bin/env python3
"""
Test script to verify the agent fix works properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent import NoStreamAgent
from rich.console import Console

def test_simple_task():
    """Test a simple task to verify the agent works."""
    console = Console()
    console.print("[bold green]🧪 Testing Agent Fix[/bold green]")
    
    # Create agent with a simple task
    agent = NoStreamAgent(
        objective="Create a simple text file with hello world message",
        verbose=True,
        max_steps=5
    )
    
    try:
        agent.run()
        console.print("[bold green]✅ Test completed successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Test failed: {e}[/bold red]")
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_task()
    sys.exit(0 if success else 1)