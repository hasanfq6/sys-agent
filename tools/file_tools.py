"""
File and directory management tools.
"""

import os
import shutil
import glob
import mimetypes
from pathlib import Path
from typing import Dict, Any, List
from .base_tools import BaseTool


class ReadFileTool(BaseTool):
    """Tool for reading files."""
    
    def get_name(self) -> str:
        return "read_file"
    
    def get_description(self) -> str:
        return "Read the contents of a file"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
                "required": True
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to read (default: 100)",
                "required": False,
                "default": 100
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "required": False,
                "default": "utf-8"
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        path = kwargs["path"]
        max_lines = kwargs.get("max_lines", 100)
        encoding = kwargs.get("encoding", "utf-8")
        
        try:
            if not os.path.exists(path):
                return f"File not found: {path}"
            
            if not os.path.isfile(path):
                return f"Path is not a file: {path}"
            
            # Check file size
            file_size = os.path.getsize(path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return f"File too large ({file_size / 1024 / 1024:.1f}MB). Use a different approach for large files."
            
            with open(path, 'r', encoding=encoding) as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"... (truncated after {max_lines} lines)")
                        break
                    lines.append(line.rstrip())
                
                content = "\n".join(lines)
                
                # Add file info
                info = f"File: {path} ({file_size} bytes, {len(lines)} lines)\n"
                info += "=" * 50 + "\n"
                
                return info + content
                
        except UnicodeDecodeError:
            return f"Cannot read file {path}: Binary file or encoding issue"
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"


class WriteFileTool(BaseTool):
    """Tool for writing files."""
    
    def get_name(self) -> str:
        return "write_file"
    
    def get_description(self) -> str:
        return "Write content to a file"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "description": "Path to the file to write",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
                "required": True
            },
            "mode": {
                "type": "string",
                "description": "Write mode: 'write' (overwrite) or 'append'",
                "required": False,
                "default": "write"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "required": False,
                "default": "utf-8"
            },
            "create_dirs": {
                "type": "boolean",
                "description": "Create parent directories if they don't exist",
                "required": False,
                "default": True
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        path = kwargs["path"]
        content = kwargs["content"]
        mode = kwargs.get("mode", "write")
        encoding = kwargs.get("encoding", "utf-8")
        create_dirs = kwargs.get("create_dirs", True)
        
        try:
            # Create parent directories if needed
            if create_dirs:
                parent_dir = os.path.dirname(path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
            
            # Determine file mode
            file_mode = "a" if mode == "append" else "w"
            
            with open(path, file_mode, encoding=encoding) as f:
                f.write(content)
            
            file_size = os.path.getsize(path)
            action = "appended to" if mode == "append" else "written to"
            
            return f"✅ Content {action} {path} ({file_size} bytes)"
            
        except Exception as e:
            return f"Error writing file {path}: {str(e)}"


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""
    
    def get_name(self) -> str:
        return "list_directory"
    
    def get_description(self) -> str:
        return "List contents of a directory"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "description": "Path to the directory to list",
                "required": False,
                "default": "."
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Show hidden files (starting with .)",
                "required": False,
                "default": False
            },
            "recursive": {
                "type": "boolean",
                "description": "List recursively",
                "required": False,
                "default": False
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum recursion depth (default: 2)",
                "required": False,
                "default": 2
            }
        }
    
    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", ".")
        show_hidden = kwargs.get("show_hidden", False)
        recursive = kwargs.get("recursive", False)
        max_depth = kwargs.get("max_depth", 2)
        
        try:
            if not os.path.exists(path):
                return f"Directory not found: {path}"
            
            if not os.path.isdir(path):
                return f"Path is not a directory: {path}"
            
            items = []
            
            if recursive:
                for root, dirs, files in os.walk(path):
                    level = root.replace(path, '').count(os.sep)
                    if level >= max_depth:
                        dirs[:] = []  # Don't recurse deeper
                        continue
                    
                    indent = "  " * level
                    items.append(f"{indent}{os.path.basename(root)}/")
                    
                    subindent = "  " * (level + 1)
                    for file in files:
                        if not show_hidden and file.startswith('.'):
                            continue
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        items.append(f"{subindent}{file} ({size} bytes)")
            else:
                for item in sorted(os.listdir(path)):
                    if not show_hidden and item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        items.append(f"{item}/")
                    else:
                        size = os.path.getsize(item_path)
                        items.append(f"{item} ({size} bytes)")
            
            if not items:
                return f"Directory {path} is empty"
            
            header = f"Contents of {os.path.abspath(path)}:\n" + "=" * 50
            return header + "\n" + "\n".join(items)
            
        except Exception as e:
            return f"Error listing directory {path}: {str(e)}"


class FileOperationsTool(BaseTool):
    """Tool for file operations like copy, move, delete."""
    
    def get_name(self) -> str:
        return "file_operations"
    
    def get_description(self) -> str:
        return "Perform file operations: copy, move, delete, create directory"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation: 'copy', 'move', 'delete', 'mkdir', 'rmdir'",
                "required": True
            },
            "source": {
                "type": "string",
                "description": "Source path",
                "required": False
            },
            "destination": {
                "type": "string",
                "description": "Destination path (for copy/move operations)",
                "required": False
            },
            "recursive": {
                "type": "boolean",
                "description": "Recursive operation for directories",
                "required": False,
                "default": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        operation = kwargs["operation"]
        source = kwargs.get("source")
        destination = kwargs.get("destination")
        recursive = kwargs.get("recursive", False)
        
        try:
            if operation == "copy":
                if not source or not destination:
                    return "Both source and destination are required for copy operation"
                
                if not os.path.exists(source):
                    return f"Source not found: {source}"
                
                if os.path.isdir(source):
                    if recursive:
                        shutil.copytree(source, destination)
                        return f"✅ Directory copied from {source} to {destination}"
                    else:
                        return "Use recursive=true to copy directories"
                else:
                    shutil.copy2(source, destination)
                    return f"✅ File copied from {source} to {destination}"
            
            elif operation == "move":
                if not source or not destination:
                    return "Both source and destination are required for move operation"
                
                if not os.path.exists(source):
                    return f"Source not found: {source}"
                
                shutil.move(source, destination)
                return f"✅ Moved from {source} to {destination}"
            
            elif operation == "delete":
                if not source:
                    return "Source path is required for delete operation"
                
                if not os.path.exists(source):
                    return f"Path not found: {source}"
                
                if os.path.isdir(source):
                    if recursive:
                        shutil.rmtree(source)
                        return f"✅ Directory deleted: {source}"
                    else:
                        return "Use recursive=true to delete directories"
                else:
                    os.remove(source)
                    return f"✅ File deleted: {source}"
            
            elif operation == "mkdir":
                if not source:
                    return "Path is required for mkdir operation"
                
                os.makedirs(source, exist_ok=True)
                return f"✅ Directory created: {source}"
            
            elif operation == "rmdir":
                if not source:
                    return "Path is required for rmdir operation"
                
                if not os.path.exists(source):
                    return f"Directory not found: {source}"
                
                if not os.path.isdir(source):
                    return f"Path is not a directory: {source}"
                
                os.rmdir(source)
                return f"✅ Empty directory removed: {source}"
            
            else:
                return f"Unknown operation: {operation}"
                
        except Exception as e:
            return f"Error performing {operation}: {str(e)}"


class SearchFilesTool(BaseTool):
    """Tool for searching files and content."""
    
    def get_name(self) -> str:
        return "search_files"
    
    def get_description(self) -> str:
        return "Search for files by name or content"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "search_type": {
                "type": "string",
                "description": "Search type: 'name' or 'content'",
                "required": True
            },
            "query": {
                "type": "string",
                "description": "Search query (filename pattern or text content)",
                "required": True
            },
            "path": {
                "type": "string",
                "description": "Directory to search in (default: current directory)",
                "required": False,
                "default": "."
            },
            "file_pattern": {
                "type": "string",
                "description": "File pattern to limit search (e.g., '*.py')",
                "required": False,
                "default": "*"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 20)",
                "required": False,
                "default": 20
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        search_type = kwargs["search_type"]
        query = kwargs["query"]
        path = kwargs.get("path", ".")
        file_pattern = kwargs.get("file_pattern", "*")
        max_results = kwargs.get("max_results", 20)
        
        try:
            if not os.path.exists(path):
                return f"Search path not found: {path}"
            
            results = []
            
            if search_type == "name":
                # Search by filename
                pattern = os.path.join(path, "**", f"*{query}*")
                matches = glob.glob(pattern, recursive=True)
                
                for match in matches[:max_results]:
                    if os.path.isfile(match):
                        size = os.path.getsize(match)
                        results.append(f"📄 {match} ({size} bytes)")
                    else:
                        results.append(f"📁 {match}/")
            
            elif search_type == "content":
                # Search file contents
                pattern = os.path.join(path, "**", file_pattern)
                files = glob.glob(pattern, recursive=True)
                
                for file_path in files:
                    if not os.path.isfile(file_path):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if query.lower() in line.lower():
                                    results.append(f"📄 {file_path}:{line_num}: {line.strip()}")
                                    if len(results) >= max_results:
                                        break
                    except:
                        continue  # Skip binary files or files with encoding issues
                    
                    if len(results) >= max_results:
                        break
            
            else:
                return f"Unknown search type: {search_type}"
            
            if not results:
                return f"No results found for '{query}'"
            
            header = f"Search results for '{query}' ({len(results)} found):\n" + "=" * 50
            return header + "\n" + "\n".join(results)
            
        except Exception as e:
            return f"Error searching: {str(e)}"