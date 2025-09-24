# ALICE Web Interface using Gradio
# Run this file to launch the web interface

try:
    import gradio as gr
except ImportError:
    print("Gradio not installed. Install with: pip install gradio")
    exit(1)

import threading
import time
from datetime import datetime
from alice_core import ALICE, AIMode, AliceConfig

class ALICEWebInterface:
    """Web interface for ALICE using Gradio"""
    
    def __init__(self):
        self.alice = ALICE()
        self.alice.start()
        self.chat_history = []
        self.system_messages = []
        
    def chat_with_alice(self, message, history):
        """Handle chat messages from the web interface"""
        if not message.strip():
            return history, ""
        
        # Get response from ALICE
        response = self.alice.process_input(message)
        
        # Update history
        history.append([message, response])
        
        return history, ""
    
    def switch_mode(self, mode_name):
        """Switch ALICE mode from web interface"""
        try:
            new_mode = AIMode(mode_name.lower())
            result = self.alice.switch_mode(new_mode)
            self.system_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {result}")
            return result
        except ValueError:
            error_msg = f"Invalid mode: {mode_name}"
            self.system_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            return error_msg
    
    def get_system_status(self):
        """Get current system status"""
        status = f"""**ALICE System Status**

**Current Mode:** {self.alice.current_mode.value}
**Model:** {self.alice.config.model_name}
**Temperature:** {self.alice.config.temperature}
**Max Tokens:** {self.alice.config.max_tokens}
**Safety Level:** {self.alice.config.safety_level}
**Short-term Memory:** {len(self.alice.memory.short_term_memory)} entries
**Running:** {self.alice.is_running}

**Recent System Messages:**
"""
        
        for msg in self.system_messages[-10:]:  # Last 10 messages
            status += f"\n{msg}"
            
        return status
    
    def update_model_settings(self, temperature, max_tokens, model_name):
        """Update model configuration"""
        self.alice.config.temperature = temperature
        self.alice.config.max_tokens = max_tokens
        
        if model_name != self.alice.config.model_name:
            self.alice.config.model_name = model_name
            # Note: In production, you'd want to reload the model here
            self.system_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] Model changed to {model_name} (restart required)")
        
        self.alice.config.save()
        self.system_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] Settings updated")
        
        return "Settings updated successfully!"
    
    def get_memory_summary(self):
        """Get memory summary"""
        summary = "**Recent Conversations:**\n\n"
        
        for i, entry in enumerate(self.alice.memory.short_term_memory[-10:], 1):
            summary += f"**{i}.** [{entry['mode']}] {entry['timestamp'][:19]}\n"
            summary += f"**User:** {entry['user_input'][:100]}...\n"
            summary += f"**ALICE:** {entry['alice_response'][:100]}...\n\n"
        
        if not self.alice.memory.short_term_memory:
            summary = "No recent conversations in memory."
            
        return summary
    
    def clear_memory(self):
        """Clear short-term memory"""
        self.alice.memory.short_term_memory.clear()
        self.system_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] Short-term memory cleared")
        return "Short-term memory cleared!"
    
    def export_conversation(self):
        """Export conversation history"""
        if not self.chat_history:
            return "No conversation to export."
        
        export_text = f"ALICE Conversation Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"Mode: {self.alice.current_mode.value}\n"
        export_text += "=" * 60 + "\n\n"
        
        for user_msg, alice_msg in self.chat_history:
            export_text += f"USER: {user_msg}\n\n"
            export_text += f"ALICE: {alice_msg}\n\n"
            export_text += "-" * 40 + "\n\n"
        
        return export_text
    
    def create_interface(self):
        """Create the Gradio interface"""
        
        # Custom CSS for better styling
        css = """
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 10px;
        }
        .mode-indicator {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
        }
        """
        
        with gr.Blocks(css=css, title="ALICE - AI Companion System", theme=gr.themes.Soft()) as interface:
            
            # Header
            gr.Markdown("""
            # 🤖 ALICE - Artificial Learning Intelligent Conversational Entity
            ### Your Local AI Companion with Multiple Personalities
            """)
            
            # Main chat interface
            with gr.Tab("💬 Chat"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="Conversation with ALICE",
                            height=500,
                            bubble_full_width=False
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="Your message",
                                placeholder="Type your message here...",
                                lines=2,
                                scale=4
                            )
                            send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    with gr.Column(scale=1):
                        # Mode selection
                        gr.Markdown("### 🎭 AI Mode")
                        current_mode_display = gr.Textbox(
                            value=self.alice.current_mode.value.title(),
                            label="Current Mode",
                            interactive=False
                        )
                        
                        mode_selector = gr.Dropdown(
                            choices=["assistant", "companion", "roleplay", "dungeon_master", "storyteller"],
                            value=self.alice.current_mode.value,
                            label="Switch Mode"
                        )
                        
                        mode_switch_btn = gr.Button("Switch Mode", variant="secondary")
                        mode_status = gr.Textbox(label="Mode Status", lines=3, interactive=False)
                        
                        # Quick actions
                        gr.Markdown("### ⚡ Quick Actions")
                        clear_chat_btn = gr.Button("Clear Chat", variant="secondary")
                        export_btn = gr.Button("Export Conversation", variant="secondary")
            
            # Settings tab
            with gr.Tab("⚙️ Settings"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Model Configuration")
                        
                        temperature_slider = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            value=self.alice.config.temperature,
                            step=0.1,
                            label="Temperature (Creativity)"
                        )
                        
                        max_tokens_slider = gr.Slider(
                            minimum=50,
                            maximum=500,
                            value=self.alice.config.max_tokens,
                            step=10,
                            label="Max Tokens (Response Length)"
                        )
                        
                        model_name_input = gr.Textbox(
                            value=self.alice.config.model_name,
                            label="Model Name",
                            placeholder="e.g., gpt2, microsoft/DialoGPT-medium"
                        )
                        
                        safety_level = gr.Dropdown(
                            choices=["strict", "moderate", "relaxed"],
                            value=self.alice.config.safety_level,
                            label="Safety Level"
                        )
                        
                        save_settings_btn = gr.Button("Save Settings", variant="primary")
                        settings_status = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("### System Information")
                        system_status_display = gr.Textbox(
                            label="System Status",
                            lines=15,
                            interactive=False
                        )
                        refresh_status_btn = gr.Button("Refresh Status")
            
            # Memory tab
            with gr.Tab("🧠 Memory"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Memory Management")
                        memory_display = gr.Textbox(
                            label="Recent Memory",
                            lines=20,
                            interactive=False
                        )
                        
                        with gr.Row():
                            refresh_memory_btn = gr.Button("Refresh Memory")
                            clear_memory_btn = gr.Button("Clear Memory", variant="stop")
                        
                        memory_status = gr.Textbox(label="Memory Status", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("### User Facts")
                        gr.Markdown("*ALICE learns and remembers things about you over time*")
                        
                        user_facts_display = gr.Textbox(
                            label="What ALICE Knows About You",
                            lines=15,
                            interactive=False
                        )
                        
                        refresh_facts_btn = gr.Button("Refresh Facts")
            
            # Advanced tab
            with gr.Tab("🔧 Advanced"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Export & Import")
                        
                        export_conversation_btn = gr.Button("Export Full Conversation")
                        export_output = gr.Textbox(
                            label="Exported Conversation",
                            lines=10,
                            interactive=False
                        )
                        
                        gr.Markdown("### System Commands")
                        system_command_input = gr.Textbox(
                            label="System Command",
                            placeholder="Enter system command (e.g., /help, /status)"
                        )
                        execute_cmd_btn = gr.Button("Execute Command")
                        command_output = gr.Textbox(
                            label="Command Output",
                            lines=5,
                            interactive=False
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Model Management")
                        gr.Markdown("*Advanced model operations*")
                        
                        load_model_btn = gr.Button("Reload Model", variant="secondary")
                        unload_model_btn = gr.Button("Unload Model", variant="stop")
                        model_status = gr.Textbox(
                            label="Model Status",
                            lines=5,
                            interactive=False
                        )
                        
                        gr.Markdown("### Database Operations")
                        backup_db_btn = gr.Button("Backup Database")
                        clean_db_btn = gr.Button("Clean Old Data")
                        db_status = gr.Textbox(
                            label="Database Status",
                            lines=5,
                            interactive=False
                        )
            
            # Event handlers
            def send_message(message, history):
                return self.chat_with_alice(message, history)
            
            def switch_mode_handler(mode):
                result = self.switch_mode(mode)
                return result, mode.title()
            
            def clear_chat():
                self.chat_history.clear()
                return []
            
            def update_settings(temp, tokens, model, safety):
                return self.update_model_settings(temp, tokens, model)
            
            def refresh_status():
                return self.get_system_status()
            
            def refresh_memory():
                return self.get_memory_summary()
            
            def clear_memory_handler():
                return self.clear_memory()
            
            def export_conversation():
                return self.export_conversation()
            
            def execute_system_command(command):
                if command.strip():
                    return self.alice.process_input(command)
                return "Please enter a command."
            
            def reload_model():
                try:
                    self.alice.model.unload_model()
                    self.alice.model.load_model()
                    return "Model reloaded successfully!"
                except Exception as e:
                    return f"Error reloading model: {str(e)}"
            
            def unload_model():
                try:
                    self.alice.model.unload_model()
                    return "Model unloaded successfully!"
                except Exception as e:
                    return f"Error unloading model: {str(e)}"
            
            def get_user_facts():
                facts = self.alice.memory.get_user_facts()
                if not facts:
                    return "No user facts stored yet."
                
                facts_text = "**What ALICE has learned about you:**\n\n"
                for fact in facts:
                    facts_text += f"**{fact['category']}** - {fact['key']}: {fact['value']} (confidence: {fact['confidence']:.2f})\n"
                
                return facts_text
            
            # Wire up the events
            send_btn.click(
                send_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            msg_input.submit(
                send_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            mode_switch_btn.click(
                switch_mode_handler,
                inputs=[mode_selector],
                outputs=[mode_status, current_mode_display]
            )
            
            clear_chat_btn.click(
                clear_chat,
                outputs=[chatbot]
            )
            
            save_settings_btn.click(
                update_settings,
                inputs=[temperature_slider, max_tokens_slider, model_name_input, safety_level],
                outputs=[settings_status]
            )
            
            refresh_status_btn.click(
                refresh_status,
                outputs=[system_status_display]
            )
            
            refresh_memory_btn.click(
                refresh_memory,
                outputs=[memory_display]
            )
            
            clear_memory_btn.click(
                clear_memory_handler,
                outputs=[memory_status]
            )
            
            export_conversation_btn.click(
                export_conversation,
                outputs=[export_output]
            )
            
            execute_cmd_btn.click(
                execute_system_command,
                inputs=[system_command_input],
                outputs=[command_output]
            )
            
            load_model_btn.click(
                reload_model,
                outputs=[model_status]
            )
            
            unload_model_btn.click(
                unload_model,
                outputs=[model_status]
            )
            
            refresh_facts_btn.click(
                get_user_facts,
                outputs=[user_facts_display]
            )
            
            # Initialize displays
            interface.load(
                refresh_status,
                outputs=[system_status_display]
            )
            
            interface.load(
                refresh_memory,
                outputs=[memory_display]
            )
        
        return interface
    
    def launch(self, share=False, server_port=7860):
        """Launch the web interface"""
        interface = self.create_interface()
        
        print(f"""
🚀 ALICE Web Interface Starting...
📱 Access locally at: http://localhost:{server_port}
🌐 Share link: {"Enabled" if share else "Disabled"}

Current Mode: {self.alice.current_mode.value.title()}
Model: {self.alice.config.model_name}
""")
        
        interface.launch(
            share=share,
            server_port=server_port,
            server_name="0.0.0.0",
            show_error=True,
            quiet=False
        )

def main():
    """Main entry point for web interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ALICE Web Interface")
    parser.add_argument("--port", type=int, default=7860, help="Port to run the web interface")
    parser.add_argument("--share", action="store_true", help="Create public share link")
    parser.add_argument("--model", type=str, help="Override model name")
    
    args = parser.parse_args()
    
    # Create and launch interface
    web_interface = ALICEWebInterface()
    
    # Override model if specified
    if args.model:
        web_interface.alice.config.model_name = args.model
        web_interface.alice.model.unload_model()
        web_interface.alice.model.load_model()
    
    try:
        web_interface.launch(share=args.share, server_port=args.port)
    except KeyboardInterrupt:
        print("\n👋 Shutting down ALICE...")
        web_interface.alice.stop()
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        web_interface.alice.stop()

if __name__ == "__main__":
    main()