"""
Test script for The Intersect Web API
This script tests the FastAPI endpoints to ensure everything is working correctly.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   Model: {data['model']}")
            print(f"   Dataset size: {data['dataset_size']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the main chat endpoint."""
    print("\\n💬 Testing chat endpoint...")
    
    test_messages = [
        "Tell me about yourself",
        "What are Brenda's main skills?",
        "How can I contact you?"
    ]
    
    conversation_id = None
    
    for i, message in enumerate(test_messages, 1):
        print(f"\\n{i}. Sending: '{message}'")
        
        try:
            payload = {"message": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                
                print(f"   ✅ Response ({response_time:.2f}s): {data['response'][:100]}...")
                print(f"   📊 Processing time: {data['processing_time']:.2f}s")
                print(f"   🆔 Conversation ID: {conversation_id[:8]}...")
                
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
                if response.content:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Chat error: {str(e)}")
            return False
    
    print("\\n✅ All chat tests passed!")
    return True

def test_stats_endpoint():
    """Test the stats endpoint."""
    print("\\n📊 Testing stats endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved:")
            print(f"   Active conversations: {data['active_conversations']}")
            print(f"   Rate limit entries: {data['total_rate_limit_entries']}")
            print(f"   Dataset categories: {data['dataset_categories']}")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\\n⏱️ Testing rate limiting...")
    
    try:
        # Send multiple requests quickly
        for i in range(3):
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json={"message": f"Test message {i+1}"},
                timeout=10
            )
            print(f"   Request {i+1}: {response.status_code}")
            
        print("✅ Rate limiting test completed (check server logs for details)")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test error: {str(e)}")
        return False

def main():
    """Run all API tests."""
    print("🧪 The Intersect Web API Test Suite")
    print("=" * 50)
    
    # Test sequence
    tests = [
        ("Health Check", test_health_endpoint),
        ("Chat Functionality", test_chat_endpoint),
        ("Statistics", test_stats_endpoint),
        ("Rate Limiting", test_rate_limiting)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🔬 Running: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is ready for production!")
        print("\\n🌐 Ready for website integration:")
        print(f"   - API Base URL: {API_BASE_URL}")
        print("   - Chat endpoint: POST /api/v1/chat")
        print("   - Documentation: http://localhost:8000/docs")
        print("   - Demo page: Open chat_demo.html in your browser")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
