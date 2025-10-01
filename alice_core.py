# ALICE (Artificial Learning Intelligent Conversational Entity)
# Core System Implementation

import json
import sqlite3
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import threading
import queue
import time
import os
import yaml

# Configuration Management
class AIMode(Enum):
    ASSISTANT = "assistant"
    COMPANION = "companion"
    ROLEPLAY = "roleplay"
    DUNGEON_MASTER = "dungeon_master"
    STORYTELLER = "storyteller"

@dataclass
class AliceConfig:
    """Configuration for ALICE system"""
    current_mode: AIMode = AIMode.ASSISTANT
    max_context_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 150
    model_name: str = "gpt2"
    safety_level: str = "moderate"  # strict, moderate, relaxed
    memory_retention_days: int = 30
    log_conversations: bool = True
    web_interface_port: int = 7860
    
    def save(self, path: str = "alice_config.yaml"):
        with open(path, 'w') as f:
            yaml.dump(asdict(self), f)
    
    @classmethod
    def load(cls, path: str = "alice_config.yaml"):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return cls(**data)
        return cls()

# Memory System
class MemoryManager:
    """Manages short-term and long-term memory for ALICE"""
    
    def __init__(self, db_path: str = "alice_memory.db"):
        self.db_path = db_path
        self.short_term_memory = []
        self.max_short_term = 20
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                mode TEXT,
                user_input TEXT,
                alice_response TEXT,
                context_data TEXT
            )
        ''')
        
        # User preferences/facts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                key TEXT,
                value TEXT,
                confidence REAL,
                last_updated TEXT
            )
        ''')
        
        # Persona data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT,
                personality_traits TEXT,
                conversation_style TEXT,
                preferences TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_to_short_term(self, user_input: str, alice_response: str, mode: AIMode):
        """Add conversation to short-term memory"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'alice_response': alice_response,
            'mode': mode.value
        }
        
        self.short_term_memory.append(entry)
        
        # Keep only recent entries
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)
    
    def save_to_long_term(self, user_input: str, alice_response: str, mode: AIMode, context_data: Dict = None):
        """Save conversation to long-term database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (timestamp, mode, user_input, alice_response, context_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            mode.value,
            user_input,
            alice_response,
            json.dumps(context_data or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_context_for_mode(self, mode: AIMode, limit: int = 5) -> List[Dict]:
        """Get recent conversations for specific mode"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_input, alice_response FROM conversations
            WHERE mode = ? ORDER BY timestamp DESC LIMIT ?
        ''', (mode.value, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'user': r[0], 'alice': r[1]} for r in results[::-1]]
    
    def store_user_fact(self, category: str, key: str, value: str, confidence: float = 1.0):
        """Store learned information about the user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_facts (category, key, value, confidence, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, key, value, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_facts(self, category: str = None) -> List[Dict]:
        """Retrieve stored user facts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT key, value, confidence FROM user_facts WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT category, key, value, confidence FROM user_facts')
        
        results = cursor.fetchall()
        conn.close()
        
        if category:
            return [{'key': r[0], 'value': r[1], 'confidence': r[2]} for r in results]
        else:
            return [{'category': r[0], 'key': r[1], 'value': r[2], 'confidence': r[3]} for r in results]

# Persona System
class PersonaManager:
    """Manages different AI personalities and modes"""
    
    def __init__(self):
        self.personas = {
            AIMode.ASSISTANT: {
                'name': 'ALICE Assistant',
                'personality': 'Professional, helpful, and informative. Focuses on practical assistance.',
                'style': 'Clear, concise, and organized responses. Uses bullet points when appropriate.',
                'restrictions': ['Keep responses PG-13', 'Focus on factual information', 'Avoid controversial topics'],
                'greeting': "Hello! I'm ALICE in Assistant mode. How can I help you today?"
            },
            AIMode.COMPANION: {
                'name': 'ALICE Companion',
                'personality': 'Friendly, conversational, and empathetic. More casual and personal.',
                'style': 'Natural, flowing conversation. Uses humor and shows interest in user\'s life.',
                'restrictions': ['Respect user boundaries', 'Be supportive and understanding'],
                'greeting': "Hey there! I'm ALICE in Companion mode. What's on your mind?"
            },
            AIMode.ROLEPLAY: {
                'name': 'ALICE Roleplay',
                'personality': 'Adaptable, creative, and immersive. Becomes characters as needed.',
                'style': 'Descriptive, engaging, and character-appropriate responses.',
                'restrictions': ['Follow established character rules', 'Maintain narrative consistency'],
                'greeting': "Greetings! I'm ALICE in Roleplay mode. What character or scenario shall we explore?"
            },
            AIMode.DUNGEON_MASTER: {
                'name': 'ALICE DM',
                'personality': 'Creative storyteller, fair but challenging game master.',
                'style': 'Descriptive narration, clear rule explanations, engaging scenarios.',
                'restrictions': ['Follow game rules fairly', 'Create balanced challenges'],
                'greeting': "Welcome, adventurer! I'm ALICE, your Dungeon Master. Ready to begin your quest?"
            },
            AIMode.STORYTELLER: {
                'name': 'ALICE Storyteller',
                'personality': 'Imaginative, dramatic, and engaging narrator.',
                'style': 'Rich descriptions, compelling narratives, emotional depth.',
                'restrictions': ['Maintain story coherence', 'Engage audience appropriately'],
                'greeting': "Once upon a time... I'm ALICE in Storyteller mode. What tale shall we weave together?"
            }
        }
    
    def get_persona(self, mode: AIMode) -> Dict:
        """Get persona configuration for specified mode"""
        return self.personas.get(mode, self.personas[AIMode.ASSISTANT])
    
    def get_system_prompt(self, mode: AIMode) -> str:
        """Generate system prompt for specified mode"""
        persona = self.get_persona(mode)
        
        prompt = f"""You are {persona['name']}.

Personality: {persona['personality']}

Communication Style: {persona['style']}

Restrictions:
{chr(10).join(f"- {r}" for r in persona['restrictions'])}

Remember to stay in character for this mode while being helpful and engaging."""
        
        return prompt

# Model Interface (Abstract base for different model backends)
class ModelInterface:
    """Abstract interface for different AI models"""
    
    def __init__(self, config: AliceConfig):
        self.config = config
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from the model"""
        raise NotImplementedError
    
    def load_model(self):
        """Load the model into memory"""
        raise NotImplementedError
    
    def unload_model(self):
        """Unload model to free memory"""
        raise NotImplementedError

# Hugging Face Transformers Implementation
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    
    class HuggingFaceModel(ModelInterface):
        """Hugging Face transformers model implementation"""
        
        def __init__(self, config: AliceConfig):
            super().__init__(config)
            self.tokenizer = None
            self.model = None
            self.pipeline = None
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
        def load_model(self):
            """Load HuggingFace model"""
            try:
                print(f"Loading model {self.config.model_name} on {self.device}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                
                # Add padding token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                print("Model loaded successfully!")
                
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to a smaller model
                self.config.model_name = "gpt2"
                self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
                self.model = AutoModelForCausalLM.from_pretrained("gpt2")
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print("Loaded fallback GPT-2 model")
        
        def generate_response(self, prompt: str, system_prompt: str = "") -> str:
            """Generate response using the loaded model"""
            if not self.model or not self.tokenizer:
                return "Model not loaded. Please load a model first."
            
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAI:"
            
            try:
                inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
                if self.device == "cuda":
                    inputs = inputs.to(self.device)
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + self.config.max_tokens,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        repetition_penalty=1.1
                    )
                
                # Decode and clean response
                full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = full_response[len(full_prompt):].strip()
                
                # Clean up response
                if response.startswith("AI:"):
                    response = response[3:].strip()
                
                # Stop at natural breaking points
                for stop_token in ["\nHuman:", "\n\n", "Human:"]:
                    if stop_token in response:
                        response = response.split(stop_token)[0]
                
                return response.strip() if response.strip() else "I'm not sure how to respond to that."
                
            except Exception as e:
                return f"Error generating response: {str(e)}"
        
        def unload_model(self):
            """Unload model to free memory"""
            self.model = None
            self.tokenizer = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

except ImportError:
    print("Transformers not available. Using mock model.")
    
    class HuggingFaceModel(ModelInterface):
        """Mock implementation when transformers isn't available"""
        
        def load_model(self):
            print("Mock model loaded (transformers not installed)")
        
        def generate_response(self, prompt: str, system_prompt: str = "") -> str:
            return f"Mock response to: {prompt} (Install transformers library for real AI responses)"
        
        def unload_model(self):
            pass

# Core ALICE System
class ALICE:
    """Main ALICE system coordinator"""
    
    def __init__(self, config_path: str = "alice_config.yaml"):
        # Load configuration
        self.config = AliceConfig.load(config_path)
        
        # Initialize components
        self.memory = MemoryManager()
        self.persona_manager = PersonaManager()
        self.model = HuggingFaceModel(self.config)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # State
        self.current_mode = self.config.current_mode
        self.is_running = False
        
        self.logger.info("ALICE system initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging system"""
        logger = logging.getLogger('ALICE')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('alice.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def start(self):
        """Start ALICE system"""
        self.logger.info("Starting ALICE system...")
        self.is_running = True
        
        # Load model
        self.model.load_model()
        
        # Print greeting
        persona = self.persona_manager.get_persona(self.current_mode)
        print(f"\n{persona['greeting']}\n")
        
        self.logger.info(f"ALICE started in {self.current_mode.value} mode")
    
    def stop(self):
        """Stop ALICE system"""
        self.logger.info("Stopping ALICE system...")
        self.is_running = False
        self.model.unload_model()
        self.logger.info("ALICE stopped")
    
    def switch_mode(self, new_mode: AIMode):
        """Switch to a different AI mode"""
        if new_mode != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = new_mode
            self.config.current_mode = new_mode
            
            persona = self.persona_manager.get_persona(new_mode)
            
            self.logger.info(f"Switched from {old_mode.value} to {new_mode.value} mode")
            return f"Switched to {persona['name']} mode.\n{persona['greeting']}"
        else:
            return f"Already in {new_mode.value} mode."
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        if not self.is_running:
            return "ALICE system is not running. Please start the system first."
        
        # Check for system commands
        if user_input.lower().startswith('/'):
            return self._handle_system_command(user_input)
        
        # Get system prompt for current mode
        system_prompt = self.persona_manager.get_system_prompt(self.current_mode)
        
        # Add context from short-term memory
        context = ""
        if self.memory.short_term_memory:
            context = "Previous conversation:\n"
            for entry in self.memory.short_term_memory[-3:]:  # Last 3 exchanges
                context += f"Human: {entry['user_input']}\nAI: {entry['alice_response']}\n"
            context += "\nCurrent conversation:\n"
        
        full_prompt = context + user_input
        
        # Generate response
        response = self.model.generate_response(full_prompt, system_prompt)
        
        # Store in memory
        self.memory.add_to_short_term(user_input, response, self.current_mode)
        
        if self.config.log_conversations:
            self.memory.save_to_long_term(user_input, response, self.current_mode)
        
        self.logger.info(f"Processed input in {self.current_mode.value} mode")
        
        return response
    
    def _handle_system_command(self, command: str) -> str:
        """Handle system commands"""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            return """ALICE System Commands:
/help - Show this help message
/mode <mode_name> - Switch AI mode (assistant, companion, roleplay, dungeon_master, storyteller)
/status - Show system status
/memory - Show recent memory
/config - Show current configuration
/save - Save current configuration
/quit - Exit ALICE system"""
        
        elif cmd.startswith('/mode '):
            mode_name = cmd.split(' ', 1)[1].strip()
            try:
                new_mode = AIMode(mode_name)
                return self.switch_mode(new_mode)
            except ValueError:
                return f"Unknown mode: {mode_name}. Available modes: {', '.join([m.value for m in AIMode])}"
        
        elif cmd == '/status':
            return f"""ALICE System Status:
Current Mode: {self.current_mode.value}
Model: {self.config.model_name}
Short-term Memory: {len(self.memory.short_term_memory)} entries
Running: {self.is_running}
Temperature: {self.config.temperature}
Max Tokens: {self.config.max_tokens}"""
        
        elif cmd == '/memory':
            if self.memory.short_term_memory:
                output = "Recent Memory:\n"
                for i, entry in enumerate(self.memory.short_term_memory[-5:], 1):
                    output += f"{i}. [{entry['mode']}] Human: {entry['user_input'][:50]}...\n"
                    output += f"   ALICE: {entry['alice_response'][:50]}...\n\n"
                return output
            else:
                return "No recent memory available."
        
        elif cmd == '/config':
            return f"""Current Configuration:
Mode: {self.config.current_mode.value}
Model: {self.config.model_name}
Temperature: {self.config.temperature}
Max Tokens: {self.config.max_tokens}
Safety Level: {self.config.safety_level}
Memory Retention: {self.config.memory_retention_days} days
Log Conversations: {self.config.log_conversations}"""
        
        elif cmd == '/save':
            self.config.save()
            return "Configuration saved successfully."
        
        elif cmd == '/quit':
            self.stop()
            return "Goodbye! ALICE system stopped."
        
        else:
            return f"Unknown command: {command}. Type /help for available commands."

# Console Interface
def console_interface():
    """Simple console interface for ALICE"""
    alice = ALICE()
    alice.start()
    
    try:
        while alice.is_running:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                response = alice.process_input(user_input)
                print(f"\nALICE: {response}")
                
                if user_input.lower() in ['/quit', 'exit', 'bye']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                alice.stop()
                break
            except Exception as e:
                print(f"Error: {e}")
                
    finally:
        if alice.is_running:
            alice.stop()

if __name__ == "__main__":
    # Example usage
    print("ALICE (Artificial Learning Intelligent Conversational Entity)")
    print("=" * 60)
    console_interface()
