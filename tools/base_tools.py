"""
Base tool interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from rich.console import Console


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the tool name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the tool description."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get the tool parameters schema."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters before execution."""
        required_params = self.get_parameters()
        for param, config in required_params.items():
            if config.get('required', False) and param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        return True
    
    def log(self, message: str, level: str = "info"):
        """Log a message with appropriate styling."""
        styles = {
            "info": "blue",
            "warning": "yellow",
            "error": "red", 
            "success": "green"
        }
        style = styles.get(level, "white")
        self.console.print(f"[{style}][{self.get_name()}] {message}[/{style}]")


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool."""
        self.tools[tool.get_name()] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self.tools.copy()
    
    def get_tool_names(self) -> List[str]:
        """Get all tool names."""
        return list(self.tools.keys())
    
    def get_tools_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all tools."""
        return {
            name: {
                "description": tool.get_description(),
                "parameters": tool.get_parameters()
            }
            for name, tool in self.tools.items()
        }