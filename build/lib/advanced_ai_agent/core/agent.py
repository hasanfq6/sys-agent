"""
Core agent implementation with modular architecture and rich output.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text
from rich import box

from .memory import MemoryManager
from .ai_interface import AIInterface
from ..tools.manager import ToolManager
from ..utils.json_extractor import JSONExtractor
from ..utils.prompt_builder import PromptBuilder
from ..utils.config import Config


class NoStreamAgent:
    """
    Advanced AI agent with modular architecture and rich output formatting.
    """
    
    def __init__(
        self, 
        objective: str, 
        verbose: bool = False,
        max_steps: int = 15,
        console: Optional[Console] = None,
        config: Optional[Config] = None
    ):
        self.console = console or Console()
        self.config = config or Config()
        self.objective = objective
        self.verbose = verbose or self.config.get("agent.verbose", False)
        self.max_steps = max_steps or self.config.get("agent.max_steps", 15)
        self.step = 0
        
        # Initialize components
        ai_config = self.config.get_ai_config()
        self.ai = AIInterface(
            provider=ai_config.get("provider", "auto"),
            **{k: v for k, v in ai_config.items() if k != "provider"}
        )
        
        memory_config = self.config.get_memory_config()
        self.memory = MemoryManager(
            max_memory_items=memory_config.get("max_items", 50)
        )
        
        self.tools = ToolManager(console=self.console)
        self.json_extractor = JSONExtractor()
        self.prompt_builder = PromptBuilder()
        
        # Display initialization
        self._display_banner()
    
    def _display_banner(self):
        """Display a rich banner with agent information."""
        banner_text = f"""
🤖 **NoStream AI Agent** v2.0
🎯 **Objective:** {self.objective}
📊 **Max Steps:** {self.max_steps}
🔧 **Available Tools:** {len(self.tools.get_available_tools())}
🧠 **AI Provider:** {self.ai.get_provider()}
        """
        
        panel = Panel(
            Markdown(banner_text),
            title="🚀 Agent Initialization",
            border_style="bright_blue",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def log(self, message: str, level: str = "info"):
        """Enhanced logging with rich formatting."""
        if not self.verbose:
            return
            
        styles = {
            "info": "blue",
            "warning": "yellow", 
            "error": "red",
            "success": "green",
            "debug": "dim"
        }
        
        style = styles.get(level, "white")
        self.console.print(f"[{style}]{message}[/{style}]")
    
    def _display_step_header(self):
        """Display step information in a rich format."""
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Label", style="bold cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Step", f"{self.step}/{self.max_steps}")
        table.add_row("Memory Items", str(len(self.memory.get_recent())))
        table.add_row("Tools Used", str(self.memory.get_tools_usage_count()))
        
        panel = Panel(
            table,
            title=f"🔄 Step {self.step}",
            border_style="green",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def _display_ai_response(self, response: str):
        """Display AI response with syntax highlighting."""
        if self.verbose:
            # Try to detect if it's JSON and highlight accordingly
            try:
                json.loads(response)
                syntax = Syntax(response, "json", theme="monokai", line_numbers=True)
            except:
                syntax = Syntax(response, "text", theme="monokai")
            
            panel = Panel(
                syntax,
                title="🧠 AI Response",
                border_style="magenta",
                box=box.ROUNDED
            )
            self.console.print(panel)
    
    def _display_action(self, thought: str, action: str, args: Dict[str, Any]):
        """Display the action being taken."""
        content = f"""
**Thought:** {thought}

**Action:** `{action}`

**Arguments:** 
```json
{json.dumps(args, indent=2)}
```
        """
        
        panel = Panel(
            Markdown(content),
            title="🎯 Action Plan",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def _display_result(self, result: str, success: bool = True):
        """Display action result with appropriate styling."""
        style = "green" if success else "red"
        title = "✅ Success" if success else "❌ Error"
        
        # Truncate long results
        display_result = result[:800] + "..." if len(result) > 800 else result
        
        panel = Panel(
            Text(display_result),
            title=title,
            border_style=style,
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def ask_ai(self, prompt: str) -> str:
        """Ask AI with progress indication."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("🤔 Thinking...", total=None)
            response = self.ai.ask(prompt)
            progress.remove_task(task)
        
        self._display_ai_response(response)
        return response
    
    def execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Execute an action using the tool manager."""
        try:
            result = self.tools.use_tool(action, args)
            self._display_result(result, success=True)
            return result
        except Exception as e:
            error_msg = f"Error executing {action}: {str(e)}"
            self._display_result(error_msg, success=False)
            return error_msg
    
    def run(self):
        """Main execution loop with enhanced error handling and display."""
        try:
            while self.step < self.max_steps:
                self.step += 1
                self._display_step_header()
                
                # Build and send prompt
                prompt = self.prompt_builder.build_main_prompt(
                    objective=self.objective,
                    memory=self.memory.get_recent(3),
                    available_tools=self.tools.get_available_tools(),
                    context={
                        "current_directory": os.getcwd(),
                        "step": self.step,
                        "max_steps": self.max_steps
                    }
                )
                
                response = self.ask_ai(prompt)
                
                try:
                    # Parse response with better error handling
                    parsed = self.json_extractor.extract_json_block(response)
                    thought = parsed.get("thought", "No thought provided.")
                    action = parsed.get("action")
                    args = parsed.get("args", {})
                    
                    # Validate action
                    if not action:
                        self.log("No action specified in AI response, using 'finish'", "warning")
                        action = "finish"
                    
                    self._display_action(thought, action, args)
                    
                    # Check for finish condition
                    if action and action.lower() == "finish":
                        self._display_completion()
                        break
                    
                    # Execute action
                    result = self.execute_action(action, args)
                    
                    # Store in memory
                    self.memory.add_step({
                        "step": self.step,
                        "thought": thought,
                        "action": action,
                        "args": args,
                        "result": result[:500]  # Truncate for memory efficiency
                    })
                    
                except Exception as e:
                    error_msg = f"Error processing step {self.step}: {str(e)}"
                    self.log(error_msg, "error")
                    
                    # Show the raw response for debugging
                    if self.verbose:
                        self.console.print(f"[red]Raw AI Response:[/red]\n{response[:1000]}")
                    
                    # Try fallback parsing
                    try:
                        fallback_result = self.json_extractor.extract_with_fallback(response)
                        thought = fallback_result.get("thought", "Fallback parsing used")
                        action = fallback_result.get("action", "finish")
                        args = fallback_result.get("args", {})
                        
                        self._display_action(thought, action, args)
                        
                        if action.lower() == "finish":
                            self._display_completion()
                            break
                        
                        result = self.execute_action(action, args)
                        self.memory.add_step({
                            "step": self.step,
                            "thought": thought,
                            "action": action,
                            "args": args,
                            "result": result[:500]
                        })
                    except Exception as fallback_error:
                        self.log(f"Fallback parsing also failed: {fallback_error}", "error")
                        # Force finish to prevent infinite loop
                        self._display_completion()
                        break
                    
                    self.memory.add_error(self.step, str(e))
                
                # Brief pause between steps
                time.sleep(0.5)
            
            if self.step >= self.max_steps:
                self._display_max_steps_reached()
                
        except KeyboardInterrupt:
            self._display_interruption()
        except Exception as e:
            self._display_fatal_error(str(e))
    
    def _display_completion(self):
        """Display completion message."""
        summary = self.get_summary()
        
        summary_text = f"""
**Mission Accomplished!** 🎉

**Summary:**
- Steps completed: {summary['steps_completed']}/{summary['max_steps']}
- Tools used: {summary['tools_used']} times
- Memory items: {summary['memory_items']}
- Success: {summary['success']}
        """
        
        panel = Panel(
            Markdown(summary_text),
            title="✅ Mission Accomplished",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(panel)
    
    def _display_max_steps_reached(self):
        """Display max steps reached message."""
        panel = Panel(
            Text(f"Maximum steps ({self.max_steps}) reached.", style="bold yellow"),
            title="⏰ Step Limit Reached",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def _display_interruption(self):
        """Display interruption message."""
        panel = Panel(
            Text("Agent execution interrupted by user.", style="bold red"),
            title="🛑 Interrupted",
            border_style="red",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def _display_fatal_error(self, error: str):
        """Display fatal error message."""
        panel = Panel(
            Text(f"Fatal error: {error}", style="bold red"),
            title="💥 Fatal Error",
            border_style="bright_red",
            box=box.DOUBLE
        )
        self.console.print(panel)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "objective": self.objective,
            "steps_completed": self.step,
            "max_steps": self.max_steps,
            "memory_items": len(self.memory.get_all()),
            "tools_used": self.memory.get_tools_usage_count(),
            "success": self.step < self.max_steps
        }
    
    def display_tools(self):
        """Display available tools in a rich table."""
        self.tools.display_tools_table()
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get help for a specific tool."""
        return self.tools.get_tool_help(tool_name)
    
    def save_memory(self, file_path: str):
        """Save memory to a file."""
        memory_data = self.memory.export_memory()
        with open(file_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
        self.log(f"Memory saved to {file_path}", "success")
    
    def load_memory(self, file_path: str):
        """Load memory from a file."""
        with open(file_path, 'r') as f:
            memory_data = json.load(f)
        self.memory.import_memory(memory_data)
        self.log(f"Memory loaded from {file_path}", "success")