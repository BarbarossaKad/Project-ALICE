#!/usr/bin/env python3
"""
ALICE Web Interface Launcher
Starts the browser-based Gradio interface for ALICE
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alice_web_interface import main

if __name__ == "__main__":
    print("Starting ALICE Web Interface...")
    print("Opening browser at http://localhost:7860")
    print("\nPress Ctrl+C to stop the server")
    main()
