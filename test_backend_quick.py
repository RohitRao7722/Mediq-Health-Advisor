"""
Quick test to verify backend is working
"""

import requests
import json

def test_backend():
    print("🧪 Testing Backend API...")
    
    try:
        # Test health endpoint
        health_response = requests.get("http://localhost:5000/api/health")
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
            return
        
        # Test chat endpoint
        chat_data = {
            "message": "What are the symptoms of diabetes?",
            "sessionId": "test_session"
        }
        
        print("Sending test message...")
        chat_response = requests.post(
            "http://localhost:5000/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Chat response status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("✅ Chat API working!")
            print(f"Response length: {len(response_data.get('response', ''))}")
            print(f"Response preview: {response_data.get('response', '')[:200]}...")
        else:
            print("❌ Chat API failed")
            print(f"Error: {chat_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_backend()

