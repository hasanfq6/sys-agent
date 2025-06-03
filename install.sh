#!/bin/bash
# Advanced AI Agent System - Installation Script

echo "🚀 Installing Advanced AI Agent System..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install the package in development mode
echo "📦 Installing package..."
pip install -e .

# Check if installation was successful
if command -v ai-agent &> /dev/null; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 You can now use the AI agent with:"
    echo "   ai-agent 'your task here'"
    echo "   aiagent 'your task here'"
    echo "   agent 'your task here'"
    echo ""
    echo "📖 For help, run: ai-agent --help"
else
    echo "⚠️  Installation completed but command-line tools may not be available."
    echo "   You can still run the agent with: python main.py 'your task'"
fi

echo ""
echo "🔧 Testing installation..."
python -c "from advanced_ai_agent import NoStreamAgent; print('✅ Package import successful')"

echo ""
echo "🎯 Installation complete! Happy automating! 🤖"