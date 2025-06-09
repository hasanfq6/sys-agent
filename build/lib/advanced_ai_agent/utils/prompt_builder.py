"""
Advanced prompt building utilities for the AI agent.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class PromptBuilder:
    """
    Advanced prompt builder with templates and context management.
    """
    
    def __init__(self):
        self.templates = {
            "main": self._get_main_template(),
            "tool_help": self._get_tool_help_template(),
            "error_recovery": self._get_error_recovery_template(),
            "planning": self._get_planning_template()
        }
    
    def build_main_prompt(
        self, 
        objective: str, 
        memory: List[Dict[str, Any]], 
        available_tools: Dict[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the main prompt for the agent.
        
        Args:
            objective: The main objective
            memory: Recent memory items
            available_tools: Available tools and their descriptions
            context: Additional context information
            
        Returns:
            Formatted prompt string
        """
        # Prepare tools information
        tools_info = self._format_tools_info(available_tools)
        
        # Prepare memory context
        memory_context = self._format_memory_context(memory)
        
        # Prepare additional context
        context_info = self._format_context_info(context) if context else ""
        
        # Build the prompt
        prompt = self.templates["main"].format(
            objective=objective,
            tools_info=tools_info,
            memory_context=memory_context,
            context_info=context_info,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return prompt
    
    def build_error_recovery_prompt(
        self, 
        error: str, 
        last_action: Dict[str, Any], 
        objective: str,
        suggestions: List[str] = None
    ) -> str:
        """Build a prompt for error recovery."""
        suggestions_text = ""
        if suggestions:
            suggestions_text = "\n".join([f"- {s}" for s in suggestions])
        
        return self.templates["error_recovery"].format(
            error=error,
            last_action=json.dumps(last_action, indent=2),
            objective=objective,
            suggestions=suggestions_text
        )
    
    def build_planning_prompt(
        self, 
        objective: str, 
        available_tools: Dict[str, Dict[str, Any]],
        constraints: List[str] = None
    ) -> str:
        """Build a prompt for planning multiple steps."""
        tools_info = self._format_tools_info(available_tools)
        constraints_text = ""
        if constraints:
            constraints_text = "\n".join([f"- {c}" for c in constraints])
        
        return self.templates["planning"].format(
            objective=objective,
            tools_info=tools_info,
            constraints=constraints_text
        )
    
    def _format_tools_info(self, available_tools: Dict[str, Dict[str, Any]]) -> str:
        """Format tools information for the prompt."""
        if not available_tools:
            return "No tools available."
        
        tools_text = []
        
        # Group tools by category
        categories = {
            "System": ["run_command", "get_system_info", "manage_process", "manage_environment"],
            "Files": ["read_file", "write_file", "list_directory", "file_operations", "search_files"],
            "Web": ["search_web", "scrape_web", "download_file", "api_request"],
            "Development": ["git_operations", "analyze_python", "manage_packages", "format_code", "run_tests"]
        }
        
        for category, tool_names in categories.items():
            category_tools = []
            for tool_name in tool_names:
                if tool_name in available_tools:
                    tool_info = available_tools[tool_name]
                    description = tool_info["description"]
                    
                    # Format parameters
                    params = tool_info.get("parameters", {})
                    param_list = []
                    for param_name, param_info in params.items():
                        param_type = param_info.get("type", "string")
                        required = param_info.get("required", False)
                        req_marker = "*" if required else ""
                        param_list.append(f"{param_name}{req_marker}: {param_type}")
                    
                    params_str = f"({', '.join(param_list)})" if param_list else "()"
                    category_tools.append(f"  - {tool_name}{params_str}: {description}")
            
            if category_tools:
                tools_text.append(f"\n**{category} Tools:**")
                tools_text.extend(category_tools)
        
        return "\n".join(tools_text)
    
    def _format_memory_context(self, memory: List[Dict[str, Any]]) -> str:
        """Format memory context for the prompt."""
        if not memory:
            return "No previous actions taken."
        
        context_items = []
        for item in memory[-5:]:  # Last 5 items
            step = item.get("step", "?")
            thought = item.get("thought", "No thought")
            action = item.get("action", "unknown")
            result = item.get("result", "No result")
            
            # Truncate long results
            if len(result) > 200:
                result = result[:200] + "..."
            
            context_items.append(f"Step {step}: {action} - {thought}\nResult: {result}")
        
        return "\n\n".join(context_items)
    
    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """Format additional context information."""
        if not context:
            return ""
        
        info_parts = []
        
        if "current_directory" in context:
            info_parts.append(f"Current Directory: {context['current_directory']}")
        
        if "environment" in context:
            env = context["environment"]
            info_parts.append(f"Environment: {env}")
        
        if "constraints" in context:
            constraints = context["constraints"]
            if constraints:
                info_parts.append("Constraints:")
                info_parts.extend([f"- {c}" for c in constraints])
        
        if "preferences" in context:
            prefs = context["preferences"]
            if prefs:
                info_parts.append("Preferences:")
                for key, value in prefs.items():
                    info_parts.append(f"- {key}: {value}")
        
        return "\n".join(info_parts) if info_parts else ""
    
    def _get_main_template(self) -> str:
        """Get the main prompt template."""
        return """You are an advanced AI agent with access to a comprehensive set of tools. You operate with precision, efficiency, and clear communication.

🎯 **OBJECTIVE:** {objective}

🔧 **AVAILABLE TOOLS:**
{tools_info}

⚠️ **CRITICAL RULES:**
1. **Single Action Per Step**: Execute ONE action at a time
2. **JSON Response Only**: Respond with a single, valid JSON object - no markdown, no extra text
3. **Required Format**:
   {{
     "thought": "Clear description of what you're doing and why",
     "action": "tool_name",
     "args": {{ "parameter": "value" }}
   }}
4. **Finish When Done**: Use "finish" action when objective is complete
5. **Error Handling**: If a tool fails, analyze the error and try alternative approaches

📊 **CONTEXT:**
{context_info}

📝 **RECENT ACTIONS:**
{memory_context}

🕒 **Current Time:** {timestamp}

**What is your next action?** Respond with a single JSON object only."""
    
    def _get_tool_help_template(self) -> str:
        """Get the tool help template."""
        return """**Tool Help: {tool_name}**

**Description:** {description}

**Parameters:**
{parameters}

**Usage Example:**
```json
{{
  "thought": "I need to use {tool_name} to accomplish my goal",
  "action": "{tool_name}",
  "args": {example_args}
}}
```

**Tips:**
{tips}"""
    
    def _get_error_recovery_template(self) -> str:
        """Get the error recovery template."""
        return """An error occurred during the last action. Let's analyze and recover.

🎯 **OBJECTIVE:** {objective}

❌ **ERROR:** {error}

🔄 **LAST ACTION:**
{last_action}

💡 **RECOVERY SUGGESTIONS:**
{suggestions}

**Instructions:**
1. Analyze the error and understand what went wrong
2. Consider alternative approaches to achieve the same goal
3. If the error is due to missing dependencies or tools, try to install them
4. If the approach is fundamentally flawed, try a different strategy
5. Respond with a single JSON object for your next action

**What is your recovery action?**"""
    
    def _get_planning_template(self) -> str:
        """Get the planning template."""
        return """You need to create a plan to achieve the following objective.

🎯 **OBJECTIVE:** {objective}

🔧 **AVAILABLE TOOLS:**
{tools_info}

⚠️ **CONSTRAINTS:**
{constraints}

**Instructions:**
1. Break down the objective into smaller, manageable steps
2. Consider the order of operations and dependencies
3. Identify potential challenges and alternative approaches
4. Choose the most efficient path forward
5. Start with the first step

**Respond with your first action as a JSON object.**"""
    
    def add_custom_template(self, name: str, template: str):
        """Add a custom prompt template."""
        self.templates[name] = template
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        return list(self.templates.keys())