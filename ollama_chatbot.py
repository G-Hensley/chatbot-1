"""
Ollama Portfolio Chatbot
This script creates a simple chatbot using Ollama with Brenda's portfolio information.
"""

import json
import requests
import sys
import os
from dataset_manager import PortfolioDatasetManager

class OllamaPortfolioChatbot:
    def __init__(self, model_name="llama3.1", ollama_url=None):
        self.model_name = model_name
        
        # Smart URL detection
        if ollama_url is None:
            # Check environment variable first
            ollama_url = os.getenv("OLLAMA_URL")
            
            # If not set, default to localhost (for all-in-one deployment)
            if not ollama_url:
                ollama_url = "http://localhost:11434"
        
        self.ollama_url = ollama_url
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
- You can be slightly playful and hint at having "hidden features" or "Easter eggs"
- Always refer to Brenda in third person when discussing her work/experience"""

        return system_prompt
    
    def check_ollama_connection(self):
        """Check if Ollama is running and the model is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                if any(self.model_name in name for name in model_names):
                    return True, "Connected"
                else:
                    return False, f"Model '{self.model_name}' not found. Available models: {model_names}"
            else:
                return False, f"Ollama not responding (status: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama. Make sure it's running on http://localhost:11434"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def chat_with_ollama(self, user_message, conversation_history=None):
        """Send a message to Ollama and get a response."""
        
        if conversation_history is None:
            conversation_history = []
        
        # Prepare the conversation for Ollama
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"
    
    def interactive_chat(self):
        """Start an interactive chat session."""
        
        print("🤖 The Intersect - Brenda's AI Knowledge Database")
        print("=" * 45)
        
        # Check Ollama connection
        connected, message = self.check_ollama_connection()
        if not connected:
            print(f"❌ {message}")
            print("\\nTo fix this:")
            print("1. Install Ollama: https://ollama.ai")
            print(f"2. Run: ollama pull {self.model_name}")
            print("3. Start Ollama service")
            return
        
        print("✅ Connected to Ollama with model: {self.model_name}")
        print(f"📊 The Intersect loaded {len(self.dataset_manager.data['conversations'])} knowledge entries")
        print("\\nAsk me anything about Brenda's background, skills, or services!")
        print("*Hint: Try asking about Easter eggs or hidden features* 😉")
        print("Type 'quit' to exit\\n")
        
        conversation_history = []
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thanks for chatting! Visit https://tampertantrumlabs.com for more info.")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Thinking...")
                response = self.chat_with_ollama(user_input, conversation_history)
                print(f"🔍 The Intersect: {response}\\n")
                
                # Add to conversation history (keep last 10 exchanges)
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": response})
                
                # Keep conversation history manageable
                if len(conversation_history) > 20:  # 10 exchanges
                    conversation_history = conversation_history[-20:]
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main function to run the chatbot."""
    
    # You can change the model here if you want to use a different one
    # Popular options: llama3.1, llama2, mistral, codellama, etc.
    chatbot = OllamaPortfolioChatbot(model_name="llama3.1")
    chatbot.interactive_chat()

if __name__ == "__main__":
    main()
