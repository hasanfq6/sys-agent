#!/usr/bin/env python3
"""
Demo script for the Advanced AI Agent System
Shows the system capabilities with real AI integration.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from tools.manager import ToolManager
from utils.config import Config

def demo_tools():
    """Demonstrate the tool system."""
    console = Console()
    config = Config()
    tool_manager = ToolManager(console)
    
    console.print(Panel.fit(
        "🚀 Advanced AI Agent System Demo",
        style="bold blue",
        box=box.DOUBLE
    ))
    
    # Show available tools
    console.print("\n[bold cyan]📋 Available Tools:[/bold cyan]")
    tool_manager.display_tools_table()
    
    # Demonstrate some tools
    console.print("\n[bold cyan]🔧 Tool Demonstrations:[/bold cyan]")
    
    # System info
    console.print("\n[yellow]1. System Information:[/yellow]")
    try:
        result = tool_manager.use_tool("get_system_info", {})
        console.print(f"✅ {result[:200]}...")
    except Exception as e:
        console.print(f"❌ Error: {e}")
    
    # List directory
    console.print("\n[yellow]2. Directory Listing:[/yellow]")
    try:
        result = tool_manager.use_tool("list_directory", {"path": "."})
        console.print(f"✅ {result[:200]}...")
    except Exception as e:
        console.print(f"❌ Error: {e}")
    
    # Run a simple command
    console.print("\n[yellow]3. Command Execution:[/yellow]")
    try:
        result = tool_manager.use_tool("run_command", {"cmd": "echo 'Hello from the agent system!'"})
        console.print(f"✅ {result}")
    except Exception as e:
        console.print(f"❌ Error: {e}")
    
    # File operations
    console.print("\n[yellow]4. File Operations:[/yellow]")
    try:
        # Write a test file
        result = tool_manager.use_tool("write_file", {
            "path": "/tmp/agent_test.txt",
            "content": "This is a test file created by the AI agent system!"
        })
        console.print(f"✅ Write: {result}")
        
        # Read it back
        result = tool_manager.use_tool("read_file", {"path": "/tmp/agent_test.txt"})
        console.print(f"✅ Read: {result}")
        
        # Clean up
        os.remove("/tmp/agent_test.txt")
        console.print("✅ Cleanup: File removed")
    except Exception as e:
        console.print(f"❌ Error: {e}")

def demo_config():
    """Demonstrate the configuration system."""
    console = Console()
    config = Config()
    
    console.print("\n[bold cyan]⚙️ Configuration System:[/bold cyan]")
    
    # Show current config
    table = Table(title="Current Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Description", style="dim")
    
    settings = [
        ("Max Steps", str(config.get("max_steps", 15)), "Maximum execution steps"),
        ("Verbose", str(config.get("verbose", False)), "Detailed logging"),
        ("Timeout", str(config.get("timeout", 30)), "Command timeout (seconds)"),
        ("AI Provider", config.get("ai_provider", "auto"), "AI service provider"),
        ("Model", config.get("model", "default"), "AI model name"),
        ("Temperature", str(config.get("temperature", 0.7)), "Response creativity"),
        ("System Commands", str(config.get("allow_system_commands", True)), "Allow shell commands"),
        ("File Operations", str(config.get("allow_file_operations", True)), "Allow file modifications"),
        ("Network Access", str(config.get("allow_network_access", True)), "Allow web requests"),
    ]
    
    for setting, value, desc in settings:
        table.add_row(setting, value, desc)
    
    console.print(table)

def demo_ai_integration():
    """Demonstrate AI integration."""
    console = Console()
    
    console.print("\n[bold cyan]🤖 AI Integration Demo:[/bold cyan]")
    
    # Show available AI providers
    table = Table(title="Available AI Providers", box=box.ROUNDED)
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description", style="dim")
    
    providers = [
        ("auto", "✅ Available", "pytgpt AUTO provider (default)"),
        ("openai", "⚠️ Requires API key", "OpenAI GPT models"),
        ("anthropic", "⚠️ Requires API key", "Anthropic Claude models"),
    ]
    
    for provider, status, desc in providers:
        table.add_row(provider, status, desc)
    
    console.print(table)

def main():
    """Run the demo."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]🤖 Advanced AI Agent System[/bold blue]\n"
        "[dim]Modular • Rich Output • 20+ Tools • Secure • AI-Powered[/dim]",
        style="blue",
        box=box.DOUBLE
    ))
    
    try:
        demo_tools()
        demo_config()
        demo_ai_integration()
        
        console.print(Panel.fit(
            "[bold green]✅ Demo completed successfully![/bold green]\n"
            "[dim]The system is ready for production use.[/dim]\n\n"
            "[bold]Try these commands:[/bold]\n"
            "[cyan]python main.py \"Create a Python script that prints hello world\"[/cyan]\n"
            "[cyan]python main.py \"Search for Python tutorials online\" --verbose[/cyan]\n"
            "[cyan]python main.py \"Analyze the current directory structure\" --max-steps 10[/cyan]",
            style="green",
            box=box.ROUNDED
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")

if __name__ == "__main__":
    main()