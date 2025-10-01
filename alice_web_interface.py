#!/usr/bin/env python3
"""
ALICE Web Interface using Gradio
Simple browser-based UI for interacting with ALICE
"""

import gradio as gr
from alice_core import ALICE, AIMode
import time

# Initialize ALICE instance
alice = None

def initialize_alice():
    """Initialize ALICE system"""
    global alice
    if alice is None:
        alice = ALICE()
        alice.start()
    return "ALICE initialized and ready!"

def chat(message, history):
    """Process chat message"""
    global alice
    
    if alice is None or not alice.is_running:
        return "ALICE is not running. Please initialize first."
    
    # Process the message
    response = alice.process_input(message)
    
    return response

def switch_mode(mode_name):
    """Switch AI mode"""
    global alice
    
    if alice is None:
        return "ALICE not initialized"
    
    try:
        mode = AIMode(mode_name.lower())
        result = alice.switch_mode(mode)
        return result
    except ValueError:
        return f"Invalid mode: {mode_name}"

def get_status():
    """Get system status"""
    global alice
    
    if alice is None:
        return "ALICE not initialized"
    
    return alice.process_input("/status")

def get_memory():
    """Get recent memory"""
    global alice
    
    if alice is None:
        return "ALICE not initialized"
    
    return alice.process_input("/memory")

def shutdown_alice():
    """Shutdown ALICE"""
    global alice
    
    if alice:
        alice.stop()
        return "ALICE stopped. Refresh page to restart."
    return "ALICE not running"

# Create Gradio interface
with gr.Blocks(title="ALICE - Local AI Companion", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # ALICE - Artificial Learning Intelligent Conversational Entity
    ### Your Local AI Companion
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Main chat interface
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_copy_button=True
            )
            
            msg = gr.Textbox(
                label="Your message",
                placeholder="Type your message here... (or use /help for commands)",
                lines=2
            )
            
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")
            
            gr.Markdown("""
            **Commands:** `/help` `/status` `/memory` `/mode <name>` `/quit`
            
            **Note:** Response generation takes 5-15 seconds on CPU
            """)
        
        with gr.Column(scale=1):
            # Control panel
            gr.Markdown("## Control Panel")
            
            init_btn = gr.Button("Initialize ALICE", variant="primary")
            init_output = gr.Textbox(label="Status", lines=2)
            
            gr.Markdown("### Quick Actions")
            
            mode_dropdown = gr.Dropdown(
                choices=["assistant", "companion", "roleplay", "dungeon_master", "storyteller"],
                value="assistant",
                label="AI Mode"
            )
            mode_btn = gr.Button("Switch Mode")
            mode_output = gr.Textbox(label="Mode Status", lines=2)
            
            status_btn = gr.Button("System Status")
            status_output = gr.Textbox(label="Status Info", lines=8)
            
            memory_btn = gr.Button("View Memory")
            memory_output = gr.Textbox(label="Recent Memory", lines=8)
            
            shutdown_btn = gr.Button("Shutdown ALICE", variant="stop")
            shutdown_output = gr.Textbox(label="Shutdown Status", lines=2)
            
            gr.Markdown("""
            ---
            ### Hardware Info
            Running on CPU with DialoGPT-medium
            
            Expect 5-15 second response times
            """)
    
    # Event handlers
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history
        
        # Add user message to history
        chat_history.append([message, None])
        
        # Get bot response
        bot_response = chat(message, chat_history)
        
        # Update history with bot response
        chat_history[-1][1] = bot_response
        
        return "", chat_history
    
    # Button clicks
    send_btn.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    clear_btn.click(
        lambda: None,
        outputs=[chatbot]
    )
    
    init_btn.click(
        initialize_alice,
        outputs=[init_output]
    )
    
    mode_btn.click(
        switch_mode,
        inputs=[mode_dropdown],
        outputs=[mode_output]
    )
    
    status_btn.click(
        get_status,
        outputs=[status_output]
    )
    
    memory_btn.click(
        get_memory,
        outputs=[memory_output]
    )
    
    shutdown_btn.click(
        shutdown_alice,
        outputs=[shutdown_output]
    )

def main():
    """Launch the web interface"""
    print("Starting ALICE Web Interface...")
    print("This will open in your browser automatically.")
    print("If not, navigate to: http://localhost:7860")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True to create public link
        inbrowser=True
    )

if __name__ == "__main__":
    main()
