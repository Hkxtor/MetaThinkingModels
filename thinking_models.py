#!/usr/bin/env python3
"""
ThinkingModels Entry Point

Main entry point for the ThinkingModels CLI application.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cli.main import cli

if __name__ == '__main__':
    cli()
