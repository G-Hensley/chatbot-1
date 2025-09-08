"""
Setup script for Ollama Portfolio Chatbot
This script helps you set up and test the chatbot with Ollama.
"""

import subprocess
import sys
import requests
import time

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Ollama command not found"
    except FileNotFoundError:
        return False, "Ollama not installed"

def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def pull_model(model_name="llama3.1"):
    """Pull the specified model."""
    print(f"📥 Pulling {model_name} model (this may take a while)...")
    try:
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Successfully pulled {model_name}"
        else:
            return False, f"Failed to pull {model_name}: {result.stderr}"
    except Exception as e:
        return False, f"Error pulling model: {str(e)}"

def start_ollama_service():
    """Start Ollama service."""
    print("🚀 Starting Ollama service...")
    try:
        # Try to start Ollama in the background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for service to start
        time.sleep(3)
        
        # Check if it's running
        if check_ollama_running():
            return True, "Ollama service started successfully"
        else:
            return False, "Failed to start Ollama service"
    except Exception as e:
        return False, f"Error starting service: {str(e)}"

def setup_ollama_chatbot():
    """Complete setup process for the chatbot."""
    
    print("🤖 Ollama Portfolio Chatbot Setup")
    print("=" * 40)
    
    # Step 1: Check if Ollama is installed
    print("1. Checking Ollama installation...")
    installed, version = check_ollama_installed()
    
    if not installed:
        print("❌ Ollama is not installed.")
        print("\\nTo install Ollama:")
        print("1. Visit: https://ollama.ai")
        print("2. Download and install for your OS")
        print("3. Run this setup script again")
        return False
    
    print(f"✅ Ollama installed: {version}")
    
    # Step 2: Check if service is running
    print("\\n2. Checking Ollama service...")
    if not check_ollama_running():
        print("🔄 Ollama service not running, attempting to start...")
        success, message = start_ollama_service()
        if not success:
            print(f"❌ {message}")
            print("\\nManual start: Run 'ollama serve' in another terminal")
            return False
        print(f"✅ {message}")
    else:
        print("✅ Ollama service is running")
    
    # Step 3: Check/pull model
    print("\\n3. Checking for llama3.1 model...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        
        if not any("llama3.1" in name for name in model_names):
            print("🔄 llama3.1 model not found, pulling...")
            success, message = pull_model("llama3.1")
            if not success:
                print(f"❌ {message}")
                print("\\nManual pull: Run 'ollama pull llama3.1'")
                return False
            print(f"✅ {message}")
        else:
            print("✅ llama3.1 model available")
    
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")
        return False
    
    print("\\n🎉 Setup complete! You can now run the chatbot.")
    print("\\nTo start chatting:")
    print("python ollama_chatbot.py")
    
    return True

def test_chatbot():
    """Test the chatbot with a simple query."""
    print("\\n🧪 Testing chatbot...")
    
    try:
        from ollama_chatbot import OllamaPortfolioChatbot
        
        chatbot = OllamaPortfolioChatbot()
        connected, message = chatbot.check_ollama_connection()
        
        if connected:
            print("✅ Chatbot connection test passed")
            
            # Test with a simple question
            response = chatbot.chat_with_ollama("Tell me about yourself")
            print(f"\\n📝 Test Response: {response[:200]}...")
            
            return True
        else:
            print(f"❌ Connection test failed: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_chatbot()
    else:
        success = setup_ollama_chatbot()
        
        if success:
            print("\\n" + "="*40)
            user_input = input("Would you like to test the chatbot now? (y/n): ")
            if user_input.lower().startswith('y'):
                test_chatbot()
