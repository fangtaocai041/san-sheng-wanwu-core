#!/usr/bin/env python3
"""Launcher script for silicon-agent CLI.

Installed by pip as 'silicon-agent' console_scripts entry point.
"""
import sys
from pathlib import Path

# Add project root to sys.path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.main import main

if __name__ == "__main__":
    main()
