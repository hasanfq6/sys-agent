"""
Development and programming tools.
"""

import subprocess
import os
import json
import ast
import re
from typing import Dict, Any, List
from .base_tools import BaseTool


class GitTool(BaseTool):
    """Tool for Git operations."""
    
    def get_name(self) -> str:
        return "git_operations"
    
    def get_description(self) -> str:
        return "Perform Git operations: status, add, commit, push, pull, log, etc."
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Git operation: status, add, commit, push, pull, log, branch, diff",
                "required": True
            },
            "args": {
                "type": "array",
                "description": "Additional arguments for the git command",
                "required": False,
                "default": []
            },
            "message": {
                "type": "string",
                "description": "Commit message (for commit operation)",
                "required": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        operation = kwargs["operation"]
        args = kwargs.get("args", [])
        message = kwargs.get("message", "")
        
        try:
            # Build git command
            cmd = ["git", operation]
            
            if operation == "commit" and message:
                cmd.extend(["-m", message])
            
            cmd.extend(args)
            
            self.log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"
            
            return output or f"Git {operation} completed successfully"
            
        except subprocess.TimeoutExpired:
            return f"Git {operation} timed out"
        except FileNotFoundError:
            return "Git is not installed or not in PATH"
        except Exception as e:
            return f"Error running git {operation}: {str(e)}"


class PythonAnalyzerTool(BaseTool):
    """Tool for analyzing Python code."""
    
    def get_name(self) -> str:
        return "analyze_python"
    
    def get_description(self) -> str:
        return "Analyze Python code for syntax, imports, functions, classes"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "file_path": {
                "type": "string",
                "description": "Path to Python file to analyze",
                "required": False
            },
            "code": {
                "type": "string",
                "description": "Python code to analyze (alternative to file_path)",
                "required": False
            },
            "analysis_type": {
                "type": "string",
                "description": "Type of analysis: 'syntax', 'structure', 'imports', 'all'",
                "required": False,
                "default": "all"
            }
        }
    
    def execute(self, **kwargs) -> str:
        file_path = kwargs.get("file_path")
        code = kwargs.get("code")
        analysis_type = kwargs.get("analysis_type", "all")
        
        if not file_path and not code:
            return "Either file_path or code must be provided"
        
        try:
            # Get code content
            if file_path:
                if not os.path.exists(file_path):
                    return f"File not found: {file_path}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                source = file_path
            else:
                source = "provided code"
            
            results = []
            results.append(f"Python code analysis for {source}:")
            results.append("=" * 50)
            
            # Syntax check
            if analysis_type in ["syntax", "all"]:
                try:
                    ast.parse(code)
                    results.append("✅ Syntax: Valid")
                except SyntaxError as e:
                    results.append(f"❌ Syntax Error: Line {e.lineno}: {e.msg}")
                    return "\n".join(results)
            
            # Parse AST for structure analysis
            if analysis_type in ["structure", "imports", "all"]:
                try:
                    tree = ast.parse(code)
                    
                    # Analyze imports
                    if analysis_type in ["imports", "all"]:
                        imports = []
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(f"import {alias.name}")
                            elif isinstance(node, ast.ImportFrom):
                                module = node.module or ""
                                for alias in node.names:
                                    imports.append(f"from {module} import {alias.name}")
                        
                        if imports:
                            results.append(f"\n📦 Imports ({len(imports)}):")
                            results.extend([f"  {imp}" for imp in imports])
                        else:
                            results.append("\n📦 Imports: None")
                    
                    # Analyze structure
                    if analysis_type in ["structure", "all"]:
                        classes = []
                        functions = []
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                                classes.append(f"{node.name} (methods: {len(methods)})")
                            elif isinstance(node, ast.FunctionDef):
                                # Only top-level functions
                                if isinstance(node.parent if hasattr(node, 'parent') else None, ast.Module):
                                    args = [arg.arg for arg in node.args.args]
                                    functions.append(f"{node.name}({', '.join(args)})")
                        
                        # Fix: manually find top-level functions
                        functions = []
                        for node in tree.body:
                            if isinstance(node, ast.FunctionDef):
                                args = [arg.arg for arg in node.args.args]
                                functions.append(f"{node.name}({', '.join(args)})")
                        
                        if classes:
                            results.append(f"\n🏗️ Classes ({len(classes)}):")
                            results.extend([f"  {cls}" for cls in classes])
                        
                        if functions:
                            results.append(f"\n⚙️ Functions ({len(functions)}):")
                            results.extend([f"  {func}" for func in functions])
                        
                        if not classes and not functions:
                            results.append("\n🏗️ Structure: No classes or functions found")
                
                except Exception as e:
                    results.append(f"❌ Analysis error: {str(e)}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Error analyzing Python code: {str(e)}"


class PackageManagerTool(BaseTool):
    """Tool for managing Python packages."""
    
    def get_name(self) -> str:
        return "manage_packages"
    
    def get_description(self) -> str:
        return "Manage Python packages: install, uninstall, list, search"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation: install, uninstall, list, show, search",
                "required": True
            },
            "package": {
                "type": "string",
                "description": "Package name (for install/uninstall/show/search)",
                "required": False
            },
            "version": {
                "type": "string",
                "description": "Specific version to install",
                "required": False
            },
            "upgrade": {
                "type": "boolean",
                "description": "Upgrade package if already installed",
                "required": False,
                "default": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        operation = kwargs["operation"]
        package = kwargs.get("package")
        version = kwargs.get("version")
        upgrade = kwargs.get("upgrade", False)
        
        try:
            if operation == "list":
                cmd = ["pip", "list"]
            elif operation == "install":
                if not package:
                    return "Package name is required for install operation"
                cmd = ["pip", "install"]
                if upgrade:
                    cmd.append("--upgrade")
                if version:
                    cmd.append(f"{package}=={version}")
                else:
                    cmd.append(package)
            elif operation == "uninstall":
                if not package:
                    return "Package name is required for uninstall operation"
                cmd = ["pip", "uninstall", "-y", package]
            elif operation == "show":
                if not package:
                    return "Package name is required for show operation"
                cmd = ["pip", "show", package]
            elif operation == "search":
                if not package:
                    return "Search term is required for search operation"
                # Note: pip search is deprecated, using alternative approach
                return f"Package search is deprecated in pip. Try: pip index versions {package}"
            else:
                return f"Unknown operation: {operation}"
            
            self.log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"
            
            return output or f"Package {operation} completed"
            
        except subprocess.TimeoutExpired:
            return f"Package {operation} timed out"
        except Exception as e:
            return f"Error managing packages: {str(e)}"


class CodeFormatterTool(BaseTool):
    """Tool for formatting code."""
    
    def get_name(self) -> str:
        return "format_code"
    
    def get_description(self) -> str:
        return "Format code using various formatters (black, autopep8, etc.)"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "file_path": {
                "type": "string",
                "description": "Path to file to format",
                "required": False
            },
            "code": {
                "type": "string",
                "description": "Code to format (alternative to file_path)",
                "required": False
            },
            "formatter": {
                "type": "string",
                "description": "Formatter to use: 'black', 'autopep8', 'yapf'",
                "required": False,
                "default": "black"
            },
            "language": {
                "type": "string",
                "description": "Programming language (python, javascript, etc.)",
                "required": False,
                "default": "python"
            }
        }
    
    def execute(self, **kwargs) -> str:
        file_path = kwargs.get("file_path")
        code = kwargs.get("code")
        formatter = kwargs.get("formatter", "black")
        language = kwargs.get("language", "python")
        
        if not file_path and not code:
            return "Either file_path or code must be provided"
        
        try:
            if language == "python":
                if formatter == "black":
                    # Try to use black
                    try:
                        if file_path:
                            cmd = ["black", "--check", "--diff", file_path]
                        else:
                            # For code string, we'd need to write to temp file
                            return "Code formatting from string requires file_path for black"
                        
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            return f"✅ Code is already formatted correctly"
                        else:
                            # Show what would be changed
                            return f"Formatting suggestions:\n{result.stdout}"
                            
                    except FileNotFoundError:
                        return "Black formatter not installed. Install with: pip install black"
                
                elif formatter == "autopep8":
                    try:
                        import autopep8
                        
                        if file_path:
                            with open(file_path, 'r') as f:
                                code = f.read()
                        
                        formatted = autopep8.fix_code(code)
                        
                        if code == formatted:
                            return "✅ Code is already formatted correctly"
                        else:
                            return f"Formatted code:\n{formatted}"
                            
                    except ImportError:
                        return "autopep8 not installed. Install with: pip install autopep8"
                
                else:
                    return f"Unsupported Python formatter: {formatter}"
            
            else:
                return f"Formatting for {language} is not yet supported"
                
        except Exception as e:
            return f"Error formatting code: {str(e)}"


class TestRunnerTool(BaseTool):
    """Tool for running tests."""
    
    def get_name(self) -> str:
        return "run_tests"
    
    def get_description(self) -> str:
        return "Run tests using pytest, unittest, or other test runners"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "test_path": {
                "type": "string",
                "description": "Path to test file or directory",
                "required": False,
                "default": "."
            },
            "test_runner": {
                "type": "string",
                "description": "Test runner: 'pytest', 'unittest', 'nose'",
                "required": False,
                "default": "pytest"
            },
            "verbose": {
                "type": "boolean",
                "description": "Verbose output",
                "required": False,
                "default": True
            },
            "pattern": {
                "type": "string",
                "description": "Test file pattern (for unittest)",
                "required": False,
                "default": "test*.py"
            }
        }
    
    def execute(self, **kwargs) -> str:
        test_path = kwargs.get("test_path", ".")
        test_runner = kwargs.get("test_runner", "pytest")
        verbose = kwargs.get("verbose", True)
        pattern = kwargs.get("pattern", "test*.py")
        
        try:
            if test_runner == "pytest":
                cmd = ["pytest", test_path]
                if verbose:
                    cmd.append("-v")
                cmd.extend(["--tb=short"])  # Shorter traceback format
                
            elif test_runner == "unittest":
                cmd = ["python", "-m", "unittest"]
                if verbose:
                    cmd.append("-v")
                cmd.extend(["discover", "-s", test_path, "-p", pattern])
                
            else:
                return f"Unsupported test runner: {test_runner}"
            
            self.log(f"Running tests: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Longer timeout for tests
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            # Add summary
            if result.returncode == 0:
                output += "\n✅ All tests passed!"
            else:
                output += f"\n❌ Tests failed (exit code: {result.returncode})"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Test execution timed out"
        except FileNotFoundError:
            return f"{test_runner} is not installed or not in PATH"
        except Exception as e:
            return f"Error running tests: {str(e)}"