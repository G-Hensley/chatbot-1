"""
Test script for the Ollama Portfolio Chatbot
This script runs several test questions to validate the chatbot responses.
"""

from ollama_chatbot import OllamaPortfolioChatbot

def test_chatbot_responses():
    """Test the chatbot with various questions."""
    
    print("🧪 Testing Brenda's Portfolio Chatbot")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = OllamaPortfolioChatbot()
    
    # Check connection
    connected, message = chatbot.check_ollama_connection()
    if not connected:
        print(f"❌ Connection failed: {message}")
        return
    
    print(f"✅ Connected to Ollama")
    print(f"📊 Dataset loaded with {len(chatbot.dataset_manager.data['conversations'])} conversations\\n")
    
    # Test questions
    test_questions = [
        "Tell me about yourself",
        "What are your main skills?",
        "How did you get into cybersecurity?",
        "What certifications do you have?",
        "How do you balance being a mom and working in tech?",
        "What services do you offer?",
        "How can I contact you?",
        "What makes you different from other security consultants?",
        "Do you have any advice for career changers?"
    ]
    
    print("🤖 Testing Responses:")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\\n{i}. Question: {question}")
        print("   Thinking...")
        
        try:
            response = chatbot.chat_with_ollama(question)
            print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\\n" + "=" * 50)
    print("✅ Test completed!")
    print("\\nTo chat interactively, run: python ollama_chatbot.py")

if __name__ == "__main__":
    test_chatbot_responses()
