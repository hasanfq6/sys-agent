# 🤖 Advanced AI Agent System

A next-generation AI agent with modular architecture, rich output formatting, and comprehensive tool integration.

## ✨ Features

### 🔧 **20+ Built-in Tools**
- **System Tools**: Command execution, process management, system info
- **File Tools**: Read/write files, directory operations, file search
- **Web Tools**: Web search, scraping, downloads, API requests
- **Development Tools**: Git operations, Python analysis, package management, testing

### 🧠 **Multiple AI Providers**
- **Auto**: Automatic provider selection using pytgpt
- **OpenAI**: GPT-3.5/GPT-4 integration
- **Anthropic**: Claude integration

### 💾 **Smart Memory Management**
- Context-aware memory with categorization
- Automatic memory optimization
- Import/export capabilities
- Search and retrieval functions

### 🎨 **Rich Output Formatting**
- Beautiful, informative displays using Rich library
- Syntax highlighting for code and JSON
- Progress indicators and status updates
- Organized tables and panels

### ⚙️ **Extensive Configuration**
- JSON-based configuration system
- Security constraints and permissions
- Tool category management
- Output customization

## 🚀 Quick Start

### Installation

```bash
# Clone or download the agent system
cd agent_system

# Install dependencies
pip install -r requirements.txt

# Or install with setup.py
pip install -e .
```

### Basic Usage

```bash
# Run a simple task
python main.py "Create a Python script that calculates fibonacci numbers"

# Enable verbose output
python main.py "Search for Python tutorials and save results" --verbose

# Limit execution steps
python main.py "Analyze current directory structure" --max-steps 10
```

### Advanced Usage

```bash
# List all available tools
python main.py --list-tools

# Get help for a specific tool
python main.py --tool-help read_file

# Show current configuration
python main.py --config

# Use specific AI provider
python main.py "Your task" --ai-provider openai

# Save and load memory
python main.py "Task 1" --save-memory session1.json
python main.py "Task 2" --load-memory session1.json
```

## 🔧 Available Tools

### System Tools
- `run_command`: Execute shell commands
- `get_system_info`: Get system information (CPU, memory, disk)
- `manage_process`: List, kill, or get info about processes
- `manage_environment`: Manage environment variables

### File Tools
- `read_file`: Read file contents with encoding support
- `write_file`: Write content to files with directory creation
- `list_directory`: List directory contents recursively
- `file_operations`: Copy, move, delete files and directories
- `search_files`: Search files by name or content

### Web Tools
- `search_web`: Search the web using DuckDuckGo
- `scrape_web`: Scrape content from web pages
- `download_file`: Download files from URLs
- `api_request`: Make HTTP API requests (GET, POST, PUT, DELETE)

### Development Tools
- `git_operations`: Git commands (status, add, commit, push, pull)
- `analyze_python`: Analyze Python code structure and syntax
- `manage_packages`: Install, uninstall, list Python packages
- `format_code`: Format code using black, autopep8
- `run_tests`: Run tests using pytest or unittest

## ⚙️ Configuration

The agent uses a JSON configuration file (`~/.agent_config.json`) with the following structure:

```json
{
  "agent": {
    "max_steps": 15,
    "verbose": false,
    "timeout": 30
  },
  "ai": {
    "provider": "auto",
    "model": "default",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "tools": {
    "enabled_categories": ["System", "Files", "Web", "Development"],
    "disabled_tools": [],
    "custom_tools": []
  },
  "security": {
    "allow_system_commands": true,
    "allow_file_operations": true,
    "allow_network_access": true,
    "restricted_paths": ["/etc", "/sys", "/proc"],
    "max_file_size": 10485760
  }
}
```

### Configuration Commands

```bash
# Show current configuration
python main.py --config

# Reset to defaults
python main.py --reset-config

# Use custom config file
python main.py "task" --config-file /path/to/config.json
```

## 🔒 Security Features

- **Path Restrictions**: Prevent access to sensitive system directories
- **File Size Limits**: Limit maximum file sizes for operations
- **Command Filtering**: Optional command execution restrictions
- **Network Controls**: Control web access permissions

## 📊 Memory Management

The agent maintains context through an intelligent memory system:

- **Step Memory**: Stores actions, thoughts, and results
- **Error Tracking**: Logs and categorizes errors
- **Tool Usage Stats**: Tracks tool usage patterns
- **Context Search**: Search memory for specific content

```python
# Access memory programmatically
agent = NoStreamAgent("objective")
agent.run()

# Export memory
agent.save_memory("session.json")

# Import memory
agent.load_memory("session.json")
```

## 🎯 Example Use Cases

### Development Tasks
```bash
python main.py "Create a REST API using Flask with user authentication"
python main.py "Analyze this Python project and suggest improvements"
python main.py "Set up a new Git repository and make initial commit"
```

### System Administration
```bash
python main.py "Check system health and generate a report"
python main.py "Find and clean up large files in the home directory"
python main.py "Monitor running processes and identify resource hogs"
```

### Research and Data Collection
```bash
python main.py "Research the latest Python web frameworks and create a comparison"
python main.py "Download and analyze data from a public API"
python main.py "Scrape product information from a website and save to CSV"
```

### File Management
```bash
python main.py "Organize files in Downloads folder by type"
python main.py "Create a backup of important configuration files"
python main.py "Search for duplicate files and create a report"
```

## 🛠️ Extending the Agent

### Adding Custom Tools

```python
from tools.base_tools import BaseTool

class CustomTool(BaseTool):
    def get_name(self) -> str:
        return "custom_tool"
    
    def get_description(self) -> str:
        return "Description of what this tool does"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "param1": {
                "type": "string",
                "description": "Parameter description",
                "required": True
            }
        }
    
    def execute(self, **kwargs) -> str:
        # Tool implementation
        return "Tool result"

# Register the tool
agent = NoStreamAgent("objective")
agent.tools.register_tool(CustomTool())
```

### Custom AI Providers

```python
from core.ai_interface import BaseAIInterface

class CustomAIInterface(BaseAIInterface):
    def ask(self, prompt: str) -> str:
        # Custom AI implementation
        return "AI response"

# Use custom provider
agent = NoStreamAgent("objective")
agent.ai = CustomAIInterface()
```

## 📝 Logging and Debugging

### Verbose Mode
```bash
python main.py "task" --verbose
```

### Debug Information
- Step-by-step execution details
- AI response formatting
- Tool execution logs
- Memory state changes

### Log Levels
- `info`: General information
- `warning`: Warning messages
- `error`: Error messages
- `success`: Success confirmations
- `debug`: Detailed debug information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Write tests for new functionality
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Rich**: For beautiful terminal output
- **Requests**: For HTTP functionality
- **BeautifulSoup**: For web scraping
- **psutil**: For system information
- **pytgpt**: For AI provider integration

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Errors**: Check file/directory permissions
3. **Network Issues**: Verify internet connection for web tools
4. **AI Provider Issues**: Check API keys and provider availability

### Getting Help

- Check the `--help` output for command usage
- Use `--tool-help TOOL_NAME` for specific tool information
- Enable `--verbose` mode for detailed execution logs
- Review the configuration with `--config`

---

**Happy Automating!** 🚀