# 🤖 Project ALICE
### Artificial Learning Intelligent Conversational Entity

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)](https://github.com/)

A privacy-focused, locally-hosted AI companion system with multiple personalities that scales from Raspberry Pi to high-end gaming PCs. ALICE offers different interaction modes while keeping all your conversations and data completely local.


### 🎭 Multiple AI Personalities
- **Assistant Mode**: Professional, helpful responses for productivity
- **Companion Mode**: Casual, friendly conversations with empathy  
- **Roleplay Mode**: Creative character interactions and scenarios
- **Dungeon Master Mode**: Interactive storytelling with game mechanics
- **Storyteller Mode**: Narrative-focused creative writing

### 🧠 Intelligent Memory System
- **Short-term memory**: Maintains conversation context
- **Long-term memory**: Learns and remembers facts about you
- **Cross-session continuity**: Remembers you between conversations
- **Export/import**: Take your ALICE with you when upgrading hardware

### 🏠 Privacy-First Design
- **Completely local**: No data sent to external servers
- **Your hardware**: Runs on everything from Pi 4B to gaming PCs
- **Open source**: Full transparency, modify as needed
- **No tracking**: Conversations stay on your device

### 🎮 Resource Management
- **Gaming mode**: Temporarily free GPU/RAM for games
- **Hardware detection**: Automatically selects appropriate AI models
- **Scalable performance**: Same system works on Pi 4B or RTX 4090

### 🌐 Universal Access
- **Web interface**: Modern, responsive UI accessible from any device
- **Mobile friendly**: Bookmark and use like an app on phones/tablets
- **Multi-user**: Family members can each have conversations
- **Network access**: Use ALICE from anywhere on your local network

## 🚀 Quick Start

### One-Line Install
```bash
git clone https://github.com/BarbarossaKad/Project-ALICE.git
cd Project-ALICE
python alice_setup.py
```

### Basic Usage
```bash
# Console interface
python alice_core.py

### Console Interface
```bash
python start_console.py

## 📋 Requirements

### Minimum (Raspberry Pi 4B)
- 4GB RAM
- Python 3.8+
- 16GB storage
- Internet for initial model download

### Recommended (Desktop/Gaming PC)
- 8GB+ RAM
- Modern GPU with 6GB+ VRAM (optional but recommended)
- 50GB+ storage for larger models
- Multi-core CPU

### Supported Platforms
- 🐧 **Linux** (Ubuntu, Debian, Pi OS, etc.)
- 🪟 **Windows** (10/11)
- 🍎 **macOS** (Intel/Apple Silicon)
- 🥧 **Raspberry Pi** (4B with 4GB+ RAM)

## 🎯 Supported AI Models

| Hardware | Recommended Models | Response Time |
|----------|-------------------|---------------|
| Pi 4B (4GB) | GPT-2, DistilGPT-2 | 15-30s |
| Pi 4B (8GB) | DialoGPT-Small | 10-20s |
| Desktop (8GB) | DialoGPT-Medium | 5-15s |
| Gaming PC (16GB+) | Mistral-7B, Llama-2-7B | 1-5s |

ALICE automatically detects your hardware and recommends optimal models.

## 🛠️ Installation

### Automatic Setup (Recommended)
```bash
git clone https://github.com/BarbarossaKad/Project-ALICE.git
cd Project-ALICE
python alice_setup.py
```

The setup script will:
- Detect your hardware capabilities
- Install appropriate dependencies
- Download recommended AI model
- Create configuration files
- Set up directory structure

### Manual Installation
```bash
# Clone repository
git clone https://github.com/BarbarossaKad/Project-ALICE.git
cd Project-ALICE

# Create virtual environment
python -m venv alice_env
source alice_env/bin/activate  # Linux/Mac
# alice_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run setup
python alice_setup.py
```

### Docker Installation
```bash
docker-compose up -d
# Access at http://localhost:7860
```

## 💬 Usage Examples

### Console Commands
```bash
# Switch personality modes
/mode companion
/mode storyteller
/mode dungeon_master

# System management  
/gaming          # Free resources for gaming
/resume          # Resume after gaming
/memory          # View conversation history
/status          # System information
/help            # Full command list
```

### Web Interface
1. Start web interface: `python alice_web_interface.py`
2. Open browser to `http://localhost:7860`
3. Chat with ALICE using the modern UI
4. Switch modes, view memory, export conversations

### Mobile Access
1. Find your computer's IP address
2. Bookmark `http://192.168.1.xxx:7860` on your phone
3. Add to home screen for app-like experience

## 🔧 Configuration

### Basic Configuration
Edit `alice_config.yaml`:
```yaml
current_mode: companion
model_name: "microsoft/DialoGPT-medium"
temperature: 0.7
max_tokens: 200
safety_level: moderate
```

### Custom Personalities
Create custom personas in `personas/custom_personas.json`:
```json
{
  "teacher": {
    "name": "ALICE Teacher",
    "personality": "Educational, patient, encouraging",
    "style": "Clear explanations with examples",
    "restrictions": ["Keep content age-appropriate", "Focus on learning"]
  }
}
```

### Advanced Model Configuration
The model manager automatically optimizes settings based on your hardware, but you can override:
```python
# For high-end GPUs
config = {
    "model_name": "mistralai/Mistral-7B-Instruct-v0.1",
    "load_in_8bit": True,
    "device_map": "auto"
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Core System    │    │  Model Manager  │
│   (Gradio UI)   │◄──►│   (alice_core)   │◄──►│   (AI Models)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │  Memory System   │
                       │   (SQLite DB)    │
                       └──────────────────┘
```

- **Core System**: Main ALICE logic, personality management
- **Memory System**: Conversation storage and user learning  
- **Model Manager**: AI model loading, optimization, scaling
- **Web Interface**: Modern UI accessible from any device
- **Persona System**: Switchable AI personalities and behaviors

## 📚 Documentation

- [**Installation Guide**](docs/INSTALLATION.md) - Detailed setup instructions
- [**API Reference**](docs/API.md) - Technical documentation  
- [**Contributing**](CONTRIBUTING.md) - How to contribute to the project
- [**FAQ**](docs/FAQ.md) - Common questions and troubleshooting

## 🤝 Contributing

Contributions are welcome! Whether you're:
- 🐛 Reporting bugs
- 💡 Suggesting features  
- 📖 Improving documentation
- 🔧 Adding new personalities
- ⚡ Optimizing performance

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📊 Project Stats

- **Languages**: Python, JavaScript, HTML/CSS
- **AI Framework**: Hugging Face Transformers, PyTorch
- **UI Framework**: Gradio
- **Database**: SQLite
- **Supported Models**: 15+ pre-configured AI models
- **Platforms**: Cross-platform (Linux, Windows, macOS, Pi OS)

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Voice input/output support
- [ ] Plugin system for custom extensions
- [ ] Multi-language support
- [ ] Advanced memory search and organization
- [ ] Integration with external APIs (optional)

### Future Ideas
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced roleplay scenarios
- [ ] Educational mode for learning
- [ ] Home automation integration
- [ ] Multi-user conversation rooms

## 🏆 Recognition

This project was developed with assistance from AI collaborators:
- **Claude (Anthropic)**: Primary development assistance, system architecture, and technical implementation
- **ChatGPT (OpenAI)**: Initial concept development, technical specifications, and documentation support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Commercial use** - Use ALICE in commercial projects
- ✅ **Modification** - Adapt and change the code as needed  
- ✅ **Distribution** - Share with others
- ✅ **Private use** - Use for personal projects
- ⚠️ **Attribution required** - Credit the original project

## 🙏 Acknowledgments

- **Hugging Face** - For the transformers library and model ecosystem
- **Gradio** - For making beautiful web interfaces simple
- **PyTorch** - For the underlying AI framework
- **The open-source community** - For inspiring privacy-focused AI development
- **Teachers and educators** - Who inspired the educational focus and accessibility

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BarbarossaKad/Project-ALICE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BarbarossaKad/Project-ALICE/discussions)
- **Wiki**: [Project Wiki](https://github.com/BarbarossaKad/Project-ALICE/wiki)

## ⭐ Star History

If you find ALICE helpful, please consider giving it a star! ⭐
