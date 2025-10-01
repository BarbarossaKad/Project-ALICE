#!/usr/bin/env python3
"""
ALICE Pi-Optimized Version
Lightweight configuration for Raspberry Pi 4 with minimal memory footprint
"""

import json
import sqlite3
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum
import os
import yaml

# Simplified AI Modes for Pi
class AIMode(Enum):
    ASSISTANT = "assistant"
    COMPANION = "companion"

@dataclass
class AliceConfigPi:
    """Lightweight configuration for Pi"""
    current_mode: AIMode = AIMode.ASSISTANT
    max_context_length: int = 512  # Reduced for Pi
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 50  # Shorter responses
    model_name: str = "distilgpt2"
    memory_retention_days: int = 7  # Less history
    log_conversations: bool = True
    
    def save(self, path: str = "alice_config_pi.yaml"):
        with open(path, 'w') as f:
            yaml.dump(asdict(self), f)
    
    @classmethod
    def load(cls, path: str = "alice_config_pi.yaml"):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                # Convert mode string back to enum
                if 'current_mode' in data:
                    data['current_mode'] = AIMode(data['current_mode'])
                return cls(**data)
        return cls()

# Lightweight Memory Manager
class MemoryManagerPi:
    """Memory manager optimized for Pi - keeps minimal in-memory data"""
    
    def __init__(self, db_path: str = "alice_memory_pi.db"):
        self.db_path = db_path
        self.short_term_memory = []
        self.max_short_term = 5  # Only keep last 5 exchanges
        self._init_database()
        
    def _init_database(self):
        """Initialize minimal database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                mode TEXT,
                user_input TEXT,
                alice_response TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_to_short_term(self, user_input: str, alice_response: str, mode: AIMode):
        """Add to short-term memory with strict limit"""
        entry = {
            'user_input': user_input,
            'alice_response': alice_response,
            'mode': mode.value
        }
        
        self.short_term_memory.append(entry)
        
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)
    
    def save_to_long_term(self, user_input: str, alice_response: str, mode: AIMode):
        """Save to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (timestamp, mode, user_input, alice_response)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), mode.value, user_input, alice_response))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_conversations(self, days: int = 7):
        """Remove old conversations to save space"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM conversations 
            WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        conn.commit()
        conn.close()

# Simple Persona System
class PersonaManagerPi:
    """Minimal persona system for Pi"""
    
    def __init__(self):
        self.personas = {
            AIMode.ASSISTANT: {
                'greeting': "Hello! I'm ALICE (running on Raspberry Pi). How can I help?",
                'system_prompt': "You are a helpful AI assistant. Keep responses brief and focused."
            },
            AIMode.COMPANION: {
                'greeting': "Hey! ALICE here. What's on your mind?",
                'system_prompt': "You are a friendly conversational AI. Be casual and supportive."
            }
        }
    
    def get_system_prompt(self, mode: AIMode) -> str:
        return self.personas.get(mode, self.personas[AIMode.ASSISTANT])['system_prompt']
    
    def get_greeting(self, mode: AIMode) -> str:
        return self.personas.get(mode, self.personas[AIMode.ASSISTANT])['greeting']

# Pi Model Interface
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    class PiModel:
        """Optimized model interface for Raspberry Pi"""
        
        def __init__(self, config: AliceConfigPi):
            self.config = config
            self.tokenizer = None
            self.model = None
            
        def load_model(self):
            """Load model with Pi-specific optimizations"""
            print(f"Loading {self.config.model_name} on Raspberry Pi...")
            print("This may take 30-60 seconds...")
            
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
                
                # Load model in float32 (Pi doesn't have GPU)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                print("Model loaded successfully!")
                print("Note: Response generation will take 10-30 seconds on Pi hardware.")
                return True
                
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        
        def generate_response(self, prompt: str, system_prompt: str = "") -> str:
            """Generate response with Pi-optimized settings"""
            if not self.model or not self.tokenizer:
                return "Model not loaded."
            
            # Keep prompt short for Pi
            full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAI:"
            
            try:
                print("Generating response (this may take 10-30 seconds)...")
                
                inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
                
                # Generate with conservative settings
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_new_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        num_beams=1,  # No beam search on Pi
                        early_stopping=True
                    )
                
                full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = full_response[len(full_prompt):].strip()
                
                # Clean up
                for stop in ["\nHuman:", "\n\n\n"]:
                    if stop in response:
                        response = response.split(stop)[0]
                
                return response.strip() or "I'm not sure how to respond."
                
            except Exception as e:
                return f"Error: {str(e)}"
        
        def unload_model(self):
            """Free memory"""
            self.model = None
            self.tokenizer = None

except ImportError:
    print("Error: transformers or torch not installed")
    print("Install with: pip install transformers torch")
    exit(1)

# Main ALICE Pi System
class ALICEPi:
    """ALICE optimized for Raspberry Pi"""
    
    def __init__(self, config_path: str = "alice_config_pi.yaml"):
        self.config = AliceConfigPi.load(config_path)
        self.memory = MemoryManagerPi()
        self.persona_manager = PersonaManagerPi()
        self.model = PiModel(self.config)
        self.current_mode = self.config.current_mode
        self.is_running = False
        
        # Simple logging
        logging.basicConfig(
            filename='alice_pi.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger('ALICEPi')
    
    def start(self):
        """Start ALICE on Pi"""
        print("\n" + "="*50)
        print("ALICE - Raspberry Pi Edition")
        print("="*50)
        
        self.is_running = True
        
        if not self.model.load_model():
            print("Failed to load model. Exiting.")
            return False
        
        print("\n" + self.persona_manager.get_greeting(self.current_mode))
        print("\nCommands: /help /mode /quit")
        print("-"*50 + "\n")
        
        self.logger.info("ALICE Pi started")
        return True
    
    def stop(self):
        """Stop ALICE"""
        self.is_running = False
        self.model.unload_model()
        self.logger.info("ALICE Pi stopped")
    
    def switch_mode(self, new_mode: AIMode):
        """Switch modes"""
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self.config.current_mode = new_mode
            greeting = self.persona_manager.get_greeting(new_mode)
            self.logger.info(f"Switched to {new_mode.value}")
            return f"Switched to {new_mode.value} mode.\n{greeting}"
        return f"Already in {new_mode.value} mode."
    
    def process_input(self, user_input: str) -> str:
        """Process input"""
        if not self.is_running:
            return "System not running."
        
        # Handle commands
        if user_input.lower().startswith('/'):
            return self._handle_command(user_input)
        
        # Get system prompt
        system_prompt = self.persona_manager.get_system_prompt(self.current_mode)
        
        # Add minimal context
        context = ""
        if self.memory.short_term_memory:
            recent = self.memory.short_term_memory[-2:]  # Only last 2
            for entry in recent:
                context += f"Human: {entry['user_input']}\nAI: {entry['alice_response']}\n"
        
        full_prompt = context + user_input
        
        # Generate response
        response = self.model.generate_response(full_prompt, system_prompt)
        
        # Store in memory
        self.memory.add_to_short_term(user_input, response, self.current_mode)
        
        if self.config.log_conversations:
            self.memory.save_to_long_term(user_input, response, self.current_mode)
        
        return response
    
    def _handle_command(self, command: str) -> str:
        """Handle system commands"""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            return """Commands:
/help - Show this message
/mode <assistant|companion> - Switch mode
/status - System status
/memory - Recent conversations
/cleanup - Remove old conversations
/quit - Exit"""
        
        elif cmd.startswith('/mode '):
            mode_name = cmd.split(' ', 1)[1].strip()
            try:
                new_mode = AIMode(mode_name)
                return self.switch_mode(new_mode)
            except ValueError:
                return f"Unknown mode. Use: assistant or companion"
        
        elif cmd == '/status':
            import psutil
            cpu_temp = "N/A"
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    cpu_temp = f"{int(f.read()) / 1000:.1f}°C"
            except:
                pass
            
            return f"""Status:
Mode: {self.current_mode.value}
Model: {self.config.model_name}
Memory: {len(self.memory.short_term_memory)} recent
CPU Temp: {cpu_temp}
RAM: {psutil.virtual_memory().percent:.1f}% used"""
        
        elif cmd == '/memory':
            if self.memory.short_term_memory:
                output = "Recent:\n"
                for i, entry in enumerate(self.memory.short_term_memory, 1):
                    output += f"{i}. You: {entry['user_input'][:40]}...\n"
                return output
            return "No recent memory."
        
        elif cmd == '/cleanup':
            self.memory.cleanup_old_conversations(self.config.memory_retention_days)
            return f"Cleaned conversations older than {self.config.memory_retention_days} days."
        
        elif cmd == '/quit':
            self.stop()
            return "Goodbye!"
        
        else:
            return f"Unknown command. Type /help for options."

def console_interface_pi():
    """Console interface for Pi"""
    alice = ALICEPi()
    
    if not alice.start():
        return
    
    try:
        while alice.is_running:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                response = alice.process_input(user_input)
                print(f"\nALICE: {response}")
                
                if user_input.lower() in ['/quit', 'exit']:
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
    print("Starting ALICE on Raspberry Pi...")
    console_interface_pi()
