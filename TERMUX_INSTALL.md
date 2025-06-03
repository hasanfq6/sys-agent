# 📱 Termux Installation Guide

## Quick Installation for Termux

### Method 1: Automatic Installation (Recommended)
```bash
git clone https://github.com/hasanfq6/
cd advanced_ai_agent

# 2. Run the installation script
chmod +x install.sh
./install.sh

# 3. Test the installation
ai-agent --help
```

### Method 2: Manual Installation
```bash
# 1. Extract and navigate
unzip advanced_ai_agent_system_fixed.zip
cd advanced_ai_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install the package
pip install -e .

# 4. Test
ai-agent "create a test file"
```

### Method 3: Direct Usage (No Installation)
```bash
# 1. Extract the zip
unzip advanced_ai_agent_system_fixed.zip
cd advanced_ai_agent

# 2. Install dependencies only
pip install -r requirements.txt

# 3. Run directly
python main.py "your task here"
```

## 🔧 Troubleshooting

### If `ai-agent` command not found:
```bash
# Option A: Use python module
python -m advanced_ai_agent "your task"

# Option B: Use direct script
python main.py "your task"

# Option C: Add to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"
```

### If dependencies fail to install:
```bash
# Update pip first
pip install --upgrade pip

# Install dependencies one by one
pip install rich requests beautifulsoup4 psutil python-tgpt

# Then install the package
pip install -e .
```

## 🚀 Usage Examples

```bash
# Create files
ai-agent "create a hello world python script"

# System information
ai-agent "what's my system status"

# Web search
ai-agent "search for python tutorials"

# File analysis
ai-agent "analyze the files in this directory"

# With options
ai-agent "create a complex script" --verbose --max-steps 10
```

## 📞 Support

If you encounter issues:
1. Try Method 3 (Direct Usage) first
2. Check that all dependencies are installed
3. Use `python main.py` instead of `ai-agent`
4. Run with `--verbose` flag for debugging

Happy automating! 🤖
