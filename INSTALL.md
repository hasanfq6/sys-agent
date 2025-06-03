# 🚀 Installation Guide - Advanced AI Agent System

## 📦 Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# Clone or download the package
cd advanced_ai_agent

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

### Method 2: From Requirements

```bash
# Install dependencies first
pip install -r requirements.txt

# Then run directly
python main.py "your task here"
```

### Method 3: System-wide Installation

```bash
# Install globally (requires sudo on Linux/Mac)
sudo pip install .

# Or for user only
pip install --user .
```

## 🎯 Command Line Usage

After installation, you can use any of these commands:

```bash
# Primary command
ai-agent "create a hello world file"

# Alternative commands
aiagent "what's my system info"
agent "search for Python tutorials"

# With options
ai-agent "analyze this directory" --verbose --max-steps 10
```

## 📋 Available Options

```bash
ai-agent --help

Advanced AI Agent System

positional arguments:
  objective             The objective or task for the AI agent to accomplish

options:
  -h, --help            show this help message and exit
  --verbose, -v         Enable verbose output for debugging
  --max-steps MAX_STEPS
                        Maximum number of steps the agent can take (default: 15)

Examples:
  ai-agent "Create a hello world file"
  ai-agent "Search for Python tutorials" --verbose
  ai-agent "Analyze this directory" --max-steps 10
```

## 🔧 Development Installation

For developers who want to modify the code:

```bash
# Clone the repository
git clone <repository-url>
cd advanced_ai_agent

# Install in development mode
pip install -e ".[dev]"

# Install all optional dependencies
pip install -e ".[all]"
```

## 🐛 Troubleshooting

### Common Issues:

1. **Command not found after installation**
   ```bash
   # Check if pip bin directory is in PATH
   python -m pip show advanced-ai-agent
   
   # Or run directly
   python -m advanced_ai_agent "your task"
   ```

2. **Permission errors**
   ```bash
   # Use --user flag
   pip install --user .
   ```

3. **Missing dependencies**
   ```bash
   # Install all requirements
   pip install -r requirements.txt
   ```

4. **Python version issues**
   ```bash
   # Check Python version (requires 3.8+)
   python --version
   
   # Use specific Python version
   python3.9 -m pip install .
   ```

## 🌟 Verification

Test your installation:

```bash
# Test basic functionality
ai-agent "create a simple test file"

# Test with verbose output
ai-agent "what's my system info" --verbose

# Test web search
ai-agent "search for current weather"
```

## 🔄 Updating

To update to the latest version:

```bash
# If installed in development mode
git pull
pip install -e .

# If installed normally
pip uninstall advanced-ai-agent
pip install .
```

## 🗑️ Uninstallation

```bash
# Remove the package
pip uninstall advanced-ai-agent

# Clean up any remaining files
rm -rf ~/.cache/advanced-ai-agent  # if any cache exists
```

---

## 📞 Support

If you encounter any issues:

1. Check the [README.md](README.md) for basic usage
2. Run with `--verbose` flag for detailed debugging
3. Check the [FEATURES.md](FEATURES.md) for available tools
4. Review the [BUGFIX_REPORT.md](BUGFIX_REPORT.md) for known issues

The agent system is now production-ready and fully installable! 🎉