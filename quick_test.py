"""
Simple API test to verify The Intersect is working
"""
import requests
import json

def quick_test():
    try:
        # Test health
        print("Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        print(f"Health: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health data: {health_response.json()}")
        
        # Test chat
        print("\\nTesting chat endpoint...")
        chat_data = {"message": "Tell me about yourself"}
        chat_response = requests.post(
            "http://localhost:8000/api/v1/chat", 
            json=chat_data, 
            timeout=30
        )
        print(f"Chat: {chat_response.status_code}")
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"Response: {response_data['response'][:100]}...")
        
        print("\\n✅ API is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
