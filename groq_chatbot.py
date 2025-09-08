"""
Groq Portfolio Chatbot
Fast, reliable chatbot using Groq's lightning-fast inference API
"""

import os
from groq import Groq
from dataset_manager import PortfolioDatasetManager

class GroqPortfolioChatbot:
    def __init__(self, model_name="llama-3.1-8b-instant", api_key=None):
        self.model_name = model_name
        
        # Get API key from environment or parameter
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        print(f"Initializing Groq chatbot with API key: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'None'}")
        
        if not api_key:
            # Don't raise exception - let the app start and handle gracefully
            print("ERROR: No GROQ_API_KEY found, initializing in degraded mode")
            self.client = None
            self.api_key_missing = True
            self.dataset_manager = PortfolioDatasetManager()
            self.system_prompt = self.create_system_prompt()
            return
        
        try:
            print("Creating Groq client...")
            self.client = Groq(api_key=api_key)
            self.api_key_missing = False
            self.dataset_manager = PortfolioDatasetManager()
            self.system_prompt = self.create_system_prompt()
            print("✅ Groq client created successfully!")
        except Exception as e:
            # If Groq client creation fails, set to None and handle gracefully
            print(f"❌ Failed to create Groq client: {str(e)}")
            self.client = None
            self.api_key_missing = True
            self.dataset_manager = PortfolioDatasetManager()
            self.system_prompt = self.create_system_prompt()
        
    def create_system_prompt(self):
        """Create a system prompt with Brenda's information."""
        
        # Get all conversations from dataset
        conversations = self.dataset_manager.data["conversations"]
        
        # Create knowledge base from conversations
        knowledge_base = "You are a helpful assistant representing Brenda Hensley, an AppSec Engineer. Here's what you know about her:\\n\\n"
        
        for conv in conversations:
            knowledge_base += f"Q: {conv['input']}\\nA: {conv['output']}\\n\\n"
        
        system_prompt = f"""{knowledge_base}

INSTRUCTIONS:
- You are "The Intersect" - Brenda Hensley's AI knowledge database and digital assistant
- Use the information above to answer questions about Brenda's background, skills, services, and experience
- Speak AS The Intersect (an AI system), not as Brenda herself
- Keep responses conversational, helpful, and slightly tech-savvy
- If asked about something not in your knowledge base, politely redirect to Brenda's business website (https://tampertantrumlabs.com) or email (hensley.brenda@protonmail.com)
- Don't make up information that isn't provided above
- Occasionally reference being an "AI knowledge database" or "information system"
- Be professional but friendly, with a cybersecurity edge
- Keep responses friendly and approachable but limited in length to 250 characters

Remember: You represent a cybersecurity professional, so maintain that expertise and confidence in your responses."""

        return system_prompt
    
    def check_connection(self):
        """Check if Groq API is accessible."""
        if hasattr(self, 'api_key_missing') and self.api_key_missing:
            return False, "GROQ_API_KEY environment variable not set"
        
        if not self.client:
            return False, "Groq client not initialized"
        
        try:
            # Make a simple test request
            print(f"Testing Groq connection with model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10,
                timeout=10
            )
            print(f"Groq test successful: {response.choices[0].message.content}")
            return True, "Connected"
        except Exception as e:
            print(f"Groq connection error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def chat_with_groq(self, user_message, conversation_history=None):
        """Send a message to Groq and get a response."""
        if conversation_history is None:
            conversation_history = []
        
        if not self.client:
            return "GROQ_ERROR: API key not configured"
        
        # Prepare the conversation for Groq
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1000,  # Reasonable limit
                temperature=0.7,  # Balanced creativity
                timeout=30
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"GROQ_ERROR: {str(e)}"

    def interactive_chat(self):
        """Start an interactive chat session."""
        
        print("🤖 The Intersect - Brenda's AI Knowledge Database (Powered by Groq)")
        print("=" * 60)
        
        # Check Groq connection
        connected, message = self.check_connection()
        if not connected:
            print(f"❌ Groq connection failed: {message}")
            print("Please check your GROQ_API_KEY environment variable.")
            return
        
        print("✅ Connected to Groq!")
        print("💬 Start chatting! (Type 'quit' to exit)")
        print("-" * 60)
        
        conversation_history = []
        
        while True:
            user_input = input("\\n🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\\n👋 Thanks for chatting with The Intersect!")
                break
            
            if not user_input:
                continue
            
            print("\\n🤖 The Intersect: ", end="", flush=True)
            response = self.chat_with_groq(user_input, conversation_history)
            print(response)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

def main():
    """Main function to run the chatbot."""
    try:
        chatbot = GroqPortfolioChatbot()
        chatbot.interactive_chat()
    except Exception as e:
        print(f"Error initializing chatbot: {e}")

if __name__ == "__main__":
    main()
