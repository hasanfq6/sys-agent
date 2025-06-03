#!/usr/bin/env python3
"""
Setup script for the Advanced AI Agent System.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="advanced-ai-agent",
    version="2.0.0",
    description="Advanced AI Agent System with modular architecture and rich output",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Hasan",
    author_email="hasanfq818@gmail.com",
    url="https://github.com/example/advanced-ai-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.3.0",
            "python-tgpt>=0.7.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-agent=advanced_ai_agent.cli:cli_main",
            "aiagent=advanced_ai_agent.cli:cli_main",
            "agent=advanced_ai_agent.cli:cli_main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
