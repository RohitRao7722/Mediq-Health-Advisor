"""
Debug the actual response structure
"""

import requests
import json

def debug_response():
    print("🔍 Debugging Response Structure...")
    
    chat_data = {
        "message": "What are the symptoms of diabetes?",
        "sessionId": "test_session"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Response Structure:")
            print(f"Keys: {list(data.keys())}")
            print(f"Response field exists: {'response' in data}")
            print(f"Response type: {type(data.get('response'))}")
            print(f"Response length: {len(data.get('response', ''))}")
            print(f"Sources field exists: {'sources' in data}")
            print(f"Sources type: {type(data.get('sources'))}")
            print(f"Sources length: {len(data.get('sources', []))}")
            
            print("\n📝 Full Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_response()

