#!/usr/bin/env python3
"""
ALICE Console Interface Launcher
Starts the text-based console interface for ALICE
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alice_core import console_interface

if __name__ == "__main__":
    print("Starting ALICE Console Interface...")
    console_interface()
