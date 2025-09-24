#!/usr/bin/env python3
"""
ALICE Setup and Installation Script
Creates the complete directory structure and installs dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class ALICESetup:
    """Setup utility for ALICE system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.base_dir = Path.cwd()
        
    def print_banner(self):
        """Print setup banner"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    ALICE SYSTEM SETUP                       ║
║          Artificial Learning Intelligent                    ║
║             Conversational Entity                           ║
╚══════════════════════════════════════════════════════════════╝

Setting up your local AI companion system...
""")
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ required. Current version:", sys.version)
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    
    def create_directory_structure(self):
        """Create necessary directories"""
        print("\n📁 Creating directory structure...")
        
        directories = [
            "data",
            "models", 
            "logs",
            "configs",
            "exports",
            "backups",
            "personas",
            "plugins"
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(exist_ok=True)
            print(f"   ✅ Created: {directory}/")
        
        print("✅ Directory structure created")
    
    def install_dependencies(self, gpu_support=True, dev_mode=False):
        """Install required Python packages"""
        print("\n📦 Installing dependencies...")
        
        # Core requirements
        core_packages = [
            "torch>=2.0.0",
            "transformers>=4.30.0", 
            "tokenizers",
            "accelerate",
            "gradio>=4.0.0",
            "pyyaml",
            "numpy",
            "sqlite3"  # Usually built-in
        ]
        
        # GPU-specific packages
        gpu_packages = [
            "torch[cuda]" if gpu_support else "torch[cpu]"
        ]
        
        # Development packages
        dev_packages = [
            "pytest",
            "black",
            "flake8",
            "jupyter"
        ] if dev_mode else []
        
        # Optional packages for advanced features
        optional_packages = [
            "sentence-transformers",  # For embeddings
            "langchain",  # For advanced chains
            "faiss-cpu",  # For vector search
            "streamlit",  # Alternative UI
            "flask"  # For custom APIs
        ]
        
        all_packages = core_packages + gpu_packages + (dev_packages if dev_mode else [])
        
        for package in all_packages:
            print(f"   📦 Installing {package}...")
            try:
                subprocess.run([
                    self.python_executable, "-m", "pip", "install", package
                ], check=True, capture_output=True, text=True)
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Warning: Failed to install {package}")
                print(f"      Error: {e.stderr}")
        
        # Ask about optional packages
        print("\n🔧 Optional packages for advanced features:")
        for package in optional_packages:
            install = input(f"Install {package}? (y/N): ").lower().startswith('y')
            if install:
                try:
                    subprocess.run([
                        self.python_executable, "-m", "pip", "install", package
                    ], check=True, capture_output=True, text=True)
                    print(f"   ✅ Installed {package}")
                except subprocess.CalledProcessError:
                    print(f"   ❌ Failed to install {package}")
    
    def create_default_config(self):
        """Create default configuration files"""
        print("\n⚙️  Creating default configuration...")
        
        # Default ALICE config
        config_content = """# ALICE Configuration File
current_mode: assistant
max_context_length: 2048
temperature: 0.7
top_p: 0.9
max_tokens: 150
model_name: "gpt2"  # Start with lightweight model
safety_level: moderate
memory_retention_days: 30
log_conversations: true
web_interface_port: 7860

# Model preferences by hardware
# Pi 4B: "gpt2" or "distilgpt2"  
# Gaming PC: "microsoft/DialoGPT-medium", "EleutherAI/gpt-neo-125m"
# High-end: "mistralai/Mistral-7B-v0.1", "meta-llama/Llama-2-7b-chat-hf"
"""
        
        config_path = self.base_dir / "alice_config.yaml"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Persona customization template
        persona_template = """{
    "assistant": {
        "name": "ALICE Assistant",
        "personality": "Professional, helpful, and informative. Focuses on practical assistance.",
        "style": "Clear, concise, and organized responses. Uses bullet points when appropriate.",
        "restrictions": ["Keep responses PG-13", "Focus on factual information", "Avoid controversial topics"],
        "greeting": "Hello! I'm ALICE in Assistant mode. How can I help you today?",
        "custom_prompts": {
            "system": "You are a helpful AI assistant focused on providing accurate information and practical assistance.",
            "context": "Previous conversation context will be provided to maintain continuity."
        }
    }
}"""
        
        persona_path = self.base_dir / "personas" / "custom_personas.json"
        with open(persona_path, 'w') as f:
            f.write(persona_template)
        
        print("✅ Configuration files created")
    
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        print("\n🚀 Creating startup scripts...")
        
        # Console startup script
        console_script = f"""#!/usr/bin/env python3
# ALICE Console Interface Launcher

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alice_core import console_interface

if __name__ == "__main__":
    console_interface()
"""
        
        with open(self.base_dir / "start_console.py", 'w') as f:
            f.write(console_script)
        
        # Web interface startup script  
        web_script = f"""#!/usr/bin/env python3
# ALICE Web Interface Launcher

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alice_web_interface import main

if __name__ == "__main__":
    main()
"""
        
        with open(self.base_dir / "start_web.py", 'w') as f:
            f.write(web_script)
        
        # Make scripts executable on Unix systems
        if self.system != "windows":
            os.chmod(self.base_dir / "start_console.py", 0o755)
            os.chmod(self.base_dir / "start_web.py", 0o755)
        
        # Batch files for Windows
        if self.system == "windows":
            console_bat = f"""@echo off
cd /d "%~dp0"
python start_console.py
pause
"""
            with open(self.base_dir / "start_console.bat", 'w') as f:
                f.write(console_bat)
                
            web_bat = f"""@echo off
cd /d "%~dp0"
python start_web.py
pause
"""
            with open(self.base_dir / "start_web.bat", 'w') as f:
                f.write(web_bat)
        
        print("✅ Startup scripts created")
    
    def detect_hardware(self):
        """Detect hardware capabilities and suggest optimal settings"""
        print("\n🖥️  Detecting hardware capabilities...")
        
        # Check for CUDA
        cuda_available = False
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"✅ CUDA GPU detected: {gpu_name} ({gpu_memory:.1f}GB)")
            else:
                print("⚠️  No CUDA GPU detected - will use CPU")
        except ImportError:
            print("⚠️  PyTorch not installed - cannot detect GPU")
        
        # Check RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / 1024**3
            print(f"💾 RAM: {ram_gb:.1f}GB")
            
            # Suggest models based on available resources
            if cuda_available and gpu_memory >= 8:
                print("🎯 Recommended models: Mistral-7B, Llama-2-7B")
            elif ram_gb >= 16:
                print("🎯 Recommended models: GPT-Neo-2.7B, DialoGPT-large")
            elif ram_gb >= 8:
                print("🎯 Recommended models: GPT-Neo-125M, DialoGPT-medium")
            else:
                print("🎯 Recommended models: DistilGPT2, GPT2-small")
                
        except ImportError:
            print("⚠️  Cannot detect RAM - install psutil for hardware detection")
        
    def create_documentation(self):
        """Create comprehensive documentation"""
        print("\n📚 Creating documentation...")
        
        readme_content = """# ALICE - Artificial Learning Intelligent Conversational Entity

## Overview
ALICE is a locally-hosted, multi-modal AI companion system designed for flexibility, privacy, and user control.

## Quick Start

### Console Interface
```bash
python start_console.py
```

### Web Interface  
```bash
python start_web.py
```
Then open http://localhost:7860 in your browser.

## Features
- 🔄 **Multi-Mode Operation**: Assistant, Companion, Roleplay, DM, Storyteller
- 🏠 **Local First**: Runs entirely on your hardware
- 🧠 **Memory System**: Short-term context + long-term learning
- ⚙️ **Configurable**: Adjust personality, safety, and behavior
- 🌐 **Web Interface**: Modern, responsive UI
- 💾 **Data Control**: All conversations and data stay local

## AI Modes

### Assistant Mode (Default)
Professional, helpful responses focused on information and task completion.

### Companion Mode  
Casual, friendly conversations with personality and empathy.

### Roleplay Mode
Creative character interactions and immersive scenarios.

### Dungeon Master Mode
Interactive storytelling with game mechanics and world-building.

### Storyteller Mode
Narrative-focused creative writing and collaborative stories.

## Configuration

Edit `alice_config.yaml` to customize:
- AI model selection
- Response parameters (temperature, length)
- Safety levels
- Memory settings
- Interface preferences

## Model Selection

### Lightweight (Pi 4B, 4-8GB RAM)
- `gpt2` - 117M parameters
- `distilgpt2` - 82M parameters
- `microsoft/DialoGPT-small` - 117M parameters

### Medium (8-16GB RAM)
- `microsoft/DialoGPT-medium` - 345M parameters  
- `EleutherAI/gpt-neo-125m` - 125M parameters
- `EleutherAI/gpt-neo-1.3B` - 1.3B parameters

### Large (16GB+ RAM, GPU recommended)
- `EleutherAI/gpt-neo-2.7B` - 2.7B parameters
- `mistralai/Mistral-7B-v0.1` - 7B parameters
- `meta-llama/Llama-2-7b-chat-hf` - 7B parameters

## System Commands

Type these in any interface:
- `/help` - Show available commands
- `/mode <mode_name>` - Switch AI mode
- `/status` - Show system status
- `/memory` - View recent memory
- `/config` - Show configuration
- `/save` - Save current settings

## File Structure
```
alice/
├── alice_core.py           # Core system
├── alice_web_interface.py  # Web UI
├── start_console.py        # Console launcher
├── start_web.py           # Web launcher
├── alice_config.yaml      # Configuration
├── data/                  # Databases and logs
├── models/               # Downloaded models
├── personas/             # Custom personalities
└── exports/              # Conversation exports
```

## Hardware Requirements

### Minimum (Pi 4B)
- 4GB RAM
- 16GB storage
- ARM64 or x86_64 CPU

### Recommended (Desktop)
- 8GB+ RAM  
- 50GB+ storage
- Multi-core CPU
- Optional: CUDA GPU (8GB+ VRAM)

## Privacy & Security
- All processing happens locally
- No data sent to external servers
- Conversation history stored locally
- Full user control over data retention

## Troubleshooting

### Model Loading Issues
- Reduce model size for your hardware
- Check available RAM/GPU memory
- Try CPU-only models first

### Performance Issues  
- Lower temperature/max_tokens
- Reduce context length
- Close other applications

### Web Interface Not Loading
- Check port 7860 is available
- Try different port: `python start_web.py --port 8080`
- Check firewall settings

## Support & Development
- Configuration help: Check alice_config.yaml
- Custom personas: Edit personas/custom_personas.json  
- Logs: Check logs/ directory for debugging
- Database: SQLite files in data/ directory

Enjoy your AI companion! 🤖
"""
        
        with open(self.base_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        print("✅ Documentation created")
    
    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        if not self.check_python_version():
            return False
        
        self.create_directory_structure()
        
        # Ask user about installation preferences
        print("\n🔧 Installation Options:")
        gpu_support = input("Enable GPU support? (Y/n): ").lower() != 'n'
        dev_mode = input("Install development packages? (y/N): ").lower().startswith('y')
        
        self.install_dependencies(gpu_support, dev_mode)
        self.create_default_config()
        self.create_startup_scripts()
        self.detect_hardware()
        self.create_documentation()
        
        print("\n" + "="*60)
        print("🎉 ALICE SETUP COMPLETE!")
        print("="*60)
        print("\n🚀 Quick Start:")
        print("   Console: python start_console.py")
        print("   Web UI:  python start_web.py")
        print("\n📚 Read README.md for detailed instructions")
        print("⚙️  Edit alice_config.yaml to customize settings")
        print("\n🤖 Welcome to ALICE - your local AI companion!")
        
        return True

def main():
    """Main setup entry point"""
    setup = ALICESetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automated setup with defaults
        print("Running automated setup...")
        setup.run_setup()
    else:
        # Interactive setup
        print("Starting interactive setup...")
        confirm = input("This will set up ALICE in the current directory. Continue? (y/N): ")
        if confirm.lower().startswith('y'):
            setup.run_setup()
        else:
            print("Setup cancelled.")

if __name__ == "__main__":
    main()