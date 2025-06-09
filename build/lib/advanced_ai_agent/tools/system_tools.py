"""
System-related tools for command execution and system information.
"""

import subprocess
import os
import platform
import psutil
import shutil
from typing import Dict, Any
from .base_tools import BaseTool


class RunCommandTool(BaseTool):
    """Tool for running shell commands."""
    
    def get_name(self) -> str:
        return "run_command"
    
    def get_description(self) -> str:
        return "Execute a shell command and return the output"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "cmd": {
                "type": "string",
                "description": "The shell command to execute",
                "required": True
            },
            "timeout": {
                "type": "integer", 
                "description": "Timeout in seconds (default: 30)",
                "required": False,
                "default": 30
            },
            "capture_stderr": {
                "type": "boolean",
                "description": "Whether to capture stderr (default: True)",
                "required": False,
                "default": True
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        cmd = kwargs["cmd"]
        timeout = kwargs.get("timeout", 30)
        capture_stderr = kwargs.get("capture_stderr", True)
        
        try:
            self.log(f"Executing: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout
            )
            
            output = result.stdout
            if capture_stderr and result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"
            
            # Truncate very long output
            if len(output) > 2000:
                output = output[:2000] + "\n... (output truncated)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Command execution error: {str(e)}"


class SystemInfoTool(BaseTool):
    """Tool for getting system information."""
    
    def get_name(self) -> str:
        return "get_system_info"
    
    def get_description(self) -> str:
        return "Get detailed system information"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "info_type": {
                "type": "string",
                "description": "Type of info: 'basic', 'cpu', 'memory', 'disk', 'network', 'all'",
                "required": False,
                "default": "basic"
            }
        }
    
    def execute(self, **kwargs) -> str:
        info_type = kwargs.get("info_type", "basic")
        
        try:
            if info_type == "basic" or info_type == "all":
                info = {
                    "platform": platform.platform(),
                    "system": platform.system(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version(),
                    "current_directory": os.getcwd(),
                    "user": os.getenv("USER", "unknown")
                }
            
            if info_type == "cpu" or info_type == "all":
                info.update({
                    "cpu_count": psutil.cpu_count(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else "N/A"
                })
            
            if info_type == "memory" or info_type == "all":
                memory = psutil.virtual_memory()
                info.update({
                    "memory_total": f"{memory.total / (1024**3):.2f} GB",
                    "memory_available": f"{memory.available / (1024**3):.2f} GB",
                    "memory_percent": f"{memory.percent}%"
                })
            
            if info_type == "disk" or info_type == "all":
                disk = psutil.disk_usage('/')
                info.update({
                    "disk_total": f"{disk.total / (1024**3):.2f} GB",
                    "disk_free": f"{disk.free / (1024**3):.2f} GB",
                    "disk_percent": f"{(disk.used / disk.total) * 100:.1f}%"
                })
            
            # Format output
            output = []
            for key, value in info.items():
                output.append(f"{key.replace('_', ' ').title()}: {value}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error getting system info: {str(e)}"


class ProcessManagerTool(BaseTool):
    """Tool for managing processes."""
    
    def get_name(self) -> str:
        return "manage_process"
    
    def get_description(self) -> str:
        return "List, kill, or get info about processes"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "description": "Action: 'list', 'kill', 'info'",
                "required": True
            },
            "process_name": {
                "type": "string",
                "description": "Process name (for kill/info actions)",
                "required": False
            },
            "pid": {
                "type": "integer",
                "description": "Process ID (for kill/info actions)",
                "required": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        action = kwargs["action"]
        
        try:
            if action == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Sort by CPU usage and take top 10
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
                
                output = ["Top processes by CPU usage:"]
                for proc in processes[:10]:
                    output.append(
                        f"PID: {proc['pid']}, Name: {proc['name']}, "
                        f"CPU: {proc['cpu_percent']:.1f}%, "
                        f"Memory: {proc['memory_percent']:.1f}%"
                    )
                
                return "\n".join(output)
            
            elif action == "kill":
                pid = kwargs.get("pid")
                process_name = kwargs.get("process_name")
                
                if not pid and not process_name:
                    return "Either 'pid' or 'process_name' must be provided for kill action"
                
                if pid:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    return f"Process {pid} terminated"
                else:
                    killed = 0
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'] == process_name:
                            proc.terminate()
                            killed += 1
                    return f"Terminated {killed} processes named '{process_name}'"
            
            elif action == "info":
                pid = kwargs.get("pid")
                process_name = kwargs.get("process_name")
                
                if not pid and not process_name:
                    return "Either 'pid' or 'process_name' must be provided for info action"
                
                if pid:
                    proc = psutil.Process(pid)
                else:
                    # Find process by name
                    for p in psutil.process_iter(['pid', 'name']):
                        if p.info['name'] == process_name:
                            proc = psutil.Process(p.info['pid'])
                            break
                    else:
                        return f"Process '{process_name}' not found"
                
                info = proc.as_dict(attrs=[
                    'pid', 'name', 'status', 'cpu_percent', 
                    'memory_percent', 'create_time', 'cmdline'
                ])
                
                output = []
                for key, value in info.items():
                    output.append(f"{key.replace('_', ' ').title()}: {value}")
                
                return "\n".join(output)
            
            else:
                return f"Unknown action: {action}"
                
        except psutil.NoSuchProcess:
            return "Process not found"
        except psutil.AccessDenied:
            return "Access denied to process"
        except Exception as e:
            return f"Error managing process: {str(e)}"


class EnvironmentTool(BaseTool):
    """Tool for managing environment variables."""
    
    def get_name(self) -> str:
        return "manage_environment"
    
    def get_description(self) -> str:
        return "Get, set, or list environment variables"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "description": "Action: 'get', 'set', 'list', 'unset'",
                "required": True
            },
            "variable": {
                "type": "string",
                "description": "Environment variable name",
                "required": False
            },
            "value": {
                "type": "string",
                "description": "Value to set (for set action)",
                "required": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        action = kwargs["action"]
        
        try:
            if action == "list":
                env_vars = []
                for key, value in sorted(os.environ.items()):
                    # Truncate long values
                    display_value = value[:50] + "..." if len(value) > 50 else value
                    env_vars.append(f"{key}={display_value}")
                
                return "\n".join(env_vars[:20])  # Show first 20
            
            elif action == "get":
                variable = kwargs.get("variable")
                if not variable:
                    return "Variable name is required for get action"
                
                value = os.getenv(variable)
                if value is None:
                    return f"Environment variable '{variable}' not found"
                return f"{variable}={value}"
            
            elif action == "set":
                variable = kwargs.get("variable")
                value = kwargs.get("value", "")
                
                if not variable:
                    return "Variable name is required for set action"
                
                os.environ[variable] = value
                return f"Set {variable}={value}"
            
            elif action == "unset":
                variable = kwargs.get("variable")
                if not variable:
                    return "Variable name is required for unset action"
                
                if variable in os.environ:
                    del os.environ[variable]
                    return f"Unset {variable}"
                else:
                    return f"Environment variable '{variable}' not found"
            
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Error managing environment: {str(e)}"