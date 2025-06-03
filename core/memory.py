"""
Memory management for the AI agent.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
import json


class MemoryManager:
    """
    Manages agent memory with categorization and retrieval capabilities.
    """
    
    def __init__(self, max_memory_items: int = 50):
        self.max_memory_items = max_memory_items
        self.steps: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.tools_usage: defaultdict = defaultdict(int)
        self.context_cache: Dict[str, Any] = {}
    
    def add_step(self, step_data: Dict[str, Any]):
        """Add a step to memory."""
        self.steps.append(step_data)
        
        # Track tool usage
        if 'action' in step_data:
            self.tools_usage[step_data['action']] += 1
        
        # Maintain memory limit
        if len(self.steps) > self.max_memory_items:
            self.steps.pop(0)
    
    def add_error(self, step: int, error: str):
        """Add an error to memory."""
        self.errors.append({
            "step": step,
            "error": error,
            "timestamp": self._get_timestamp()
        })
    
    def get_recent(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get recent memory items."""
        return self.steps[-count:] if self.steps else []
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all memory items."""
        return self.steps
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.errors
    
    def get_tools_usage_count(self) -> int:
        """Get total number of tools used."""
        return sum(self.tools_usage.values())
    
    def get_tools_usage_stats(self) -> Dict[str, int]:
        """Get tools usage statistics."""
        return dict(self.tools_usage)
    
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search memory for specific content."""
        results = []
        query_lower = query.lower()
        
        for step in self.steps:
            # Search in thought, action, and result
            searchable_text = " ".join([
                str(step.get('thought', '')),
                str(step.get('action', '')),
                str(step.get('result', ''))
            ]).lower()
            
            if query_lower in searchable_text:
                results.append(step)
        
        return results
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context."""
        if not self.steps:
            return "No previous actions taken."
        
        recent_actions = [step.get('action', 'unknown') for step in self.get_recent(5)]
        tools_used = list(self.tools_usage.keys())
        
        summary = f"""
Recent actions: {', '.join(recent_actions)}
Tools used: {', '.join(tools_used)}
Total steps: {len(self.steps)}
Errors encountered: {len(self.errors)}
        """.strip()
        
        return summary
    
    def clear(self):
        """Clear all memory."""
        self.steps.clear()
        self.errors.clear()
        self.tools_usage.clear()
        self.context_cache.clear()
    
    def export_memory(self) -> Dict[str, Any]:
        """Export memory to a dictionary."""
        return {
            "steps": self.steps,
            "errors": self.errors,
            "tools_usage": dict(self.tools_usage),
            "context_cache": self.context_cache
        }
    
    def import_memory(self, memory_data: Dict[str, Any]):
        """Import memory from a dictionary."""
        self.steps = memory_data.get("steps", [])
        self.errors = memory_data.get("errors", [])
        self.tools_usage = defaultdict(int, memory_data.get("tools_usage", {}))
        self.context_cache = memory_data.get("context_cache", {})
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()