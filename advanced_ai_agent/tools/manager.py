"""
Tool manager for organizing and executing tools.
"""

from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich import box

from .base_tools import ToolRegistry, BaseTool
from .system_tools import RunCommandTool, SystemInfoTool, ProcessManagerTool, EnvironmentTool
from .file_tools import ReadFileTool, WriteFileTool, ListDirectoryTool, FileOperationsTool, SearchFilesTool
from .web_tools import WebSearchTool, WebScrapeTool, DownloadFileTool, APIRequestTool
from .development_tools import GitTool, PythonAnalyzerTool, PackageManagerTool, CodeFormatterTool, TestRunnerTool


class ToolManager:
    """
    Manages all available tools and provides execution interface.
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.registry = ToolRegistry()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools."""
        # System tools
        self.registry.register(RunCommandTool(self.console))
        self.registry.register(SystemInfoTool(self.console))
        self.registry.register(ProcessManagerTool(self.console))
        self.registry.register(EnvironmentTool(self.console))
        
        # File tools
        self.registry.register(ReadFileTool(self.console))
        self.registry.register(WriteFileTool(self.console))
        self.registry.register(ListDirectoryTool(self.console))
        self.registry.register(FileOperationsTool(self.console))
        self.registry.register(SearchFilesTool(self.console))
        
        # Web tools
        self.registry.register(WebSearchTool(self.console))
        self.registry.register(WebScrapeTool(self.console))
        self.registry.register(DownloadFileTool(self.console))
        self.registry.register(APIRequestTool(self.console))
        
        # Development tools
        self.registry.register(GitTool(self.console))
        self.registry.register(PythonAnalyzerTool(self.console))
        self.registry.register(PackageManagerTool(self.console))
        self.registry.register(CodeFormatterTool(self.console))
        self.registry.register(TestRunnerTool(self.console))
    
    def register_tool(self, tool: BaseTool):
        """Register a custom tool."""
        self.registry.register(tool)
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available tools."""
        return self.registry.get_tools_info()
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return self.registry.get_tool_names()
    
    def use_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool with given arguments."""
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            available_tools = ", ".join(self.get_tool_names())
            return f"Unknown tool: {tool_name}. Available tools: {available_tools}"
        
        try:
            return tool.execute(**args)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def display_tools_table(self):
        """Display a rich table of available tools."""
        table = Table(title="🔧 Available Tools", box=box.ROUNDED)
        
        table.add_column("Tool Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Category", style="green")
        
        # Categorize tools
        categories = {
            "System": ["run_command", "get_system_info", "manage_process", "manage_environment"],
            "Files": ["read_file", "write_file", "list_directory", "file_operations", "search_files"],
            "Web": ["search_web", "scrape_web", "download_file", "api_request"],
            "Development": ["git_operations", "analyze_python", "manage_packages", "format_code", "run_tests"]
        }
        
        tools_info = self.get_available_tools()
        
        for category, tool_names in categories.items():
            for tool_name in tool_names:
                if tool_name in tools_info:
                    description = tools_info[tool_name]["description"]
                    # Truncate long descriptions
                    if len(description) > 60:
                        description = description[:57] + "..."
                    table.add_row(tool_name, description, category)
        
        self.console.print(table)
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get detailed help for a specific tool."""
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            return f"Tool '{tool_name}' not found"
        
        help_text = f"🔧 **{tool.get_name()}**\n\n"
        help_text += f"**Description:** {tool.get_description()}\n\n"
        help_text += "**Parameters:**\n"
        
        parameters = tool.get_parameters()
        if parameters:
            for param_name, param_info in parameters.items():
                param_type = param_info.get("type", "string")
                required = "Required" if param_info.get("required", False) else "Optional"
                default = param_info.get("default")
                description = param_info.get("description", "No description")
                
                help_text += f"- **{param_name}** ({param_type}, {required}): {description}"
                if default is not None:
                    help_text += f" (default: {default})"
                help_text += "\n"
        else:
            help_text += "No parameters required.\n"
        
        return help_text
    
    def validate_tool_args(self, tool_name: str, args: Dict[str, Any]) -> tuple[bool, str]:
        """Validate arguments for a tool."""
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            return False, f"Tool '{tool_name}' not found"
        
        try:
            tool.validate_parameters(**args)
            return True, "Arguments are valid"
        except Exception as e:
            return False, str(e)
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Get tools organized by category."""
        categories = {
            "System": ["run_command", "get_system_info", "manage_process", "manage_environment"],
            "Files": ["read_file", "write_file", "list_directory", "file_operations", "search_files"],
            "Web": ["search_web", "scrape_web", "download_file", "api_request"],
            "Development": ["git_operations", "analyze_python", "manage_packages", "format_code", "run_tests"]
        }
        
        # Filter to only include registered tools
        available_tools = set(self.get_tool_names())
        filtered_categories = {}
        
        for category, tools in categories.items():
            filtered_tools = [tool for tool in tools if tool in available_tools]
            if filtered_tools:
                filtered_categories[category] = filtered_tools
        
        return filtered_categories