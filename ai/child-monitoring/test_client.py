import requests
import json
import time

def test_streaming_chat():
    """Test the streaming chat endpoint"""
    
    url = "http://localhost:8001/chat/stream"
    
    payload = {
        "message": "Bagaimana performa anak saya dalam konsep berbagi dan kerja keras?",
        "child_age": 8,
        "session_id": "session_123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing streaming chat endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the request with streaming enabled
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            stream=True,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connection successful! Streaming response:")
            print("-" * 50)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_json = decoded_line[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_json)
                            if data.get('type') == 'content':
                                print(data['content'], end='', flush=True)
                            elif data.get('type') == 'complete':
                                print("\n" + "-" * 50)
                                print("✅ Streaming completed!")
                                break
                            elif data.get('type') == 'error':
                                print(f"\n❌ Error: {data['content']}")
                                break
                        except json.JSONDecodeError:
                            print(f"⚠️ Could not parse JSON: {data_json}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the server is running on http://localhost:8001")
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_non_streaming_chat():
    """Test the non-streaming chat endpoint"""
    
    url = "http://localhost:8001/chat"
    
    payload = {
        "message": "Berikan tips untuk mengajarkan anak tentang uang",
        "child_age": 10,
        "session_id": "session_456"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\n🚀 Testing non-streaming chat endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print("-" * 50)
            print(f"Response: {result['response']}")
            print(f"Session ID: {result.get('session_id')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the server is running on http://localhost:8001")
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_check():
    """Test the health check endpoint"""
    
    url = "http://localhost:8001/health"
    
    print("\n🚀 Testing health check endpoint...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check successful!")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the server is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_system_status():
    """Test the system status endpoint"""
    
    url = "http://localhost:8001/system/status"
    
    print("\n🚀 Testing system status endpoint...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ System status retrieved!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ System status failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the server is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Child Financial Literacy Chatbot API")
    print("=" * 60)
    
    # Test all endpoints
    test_health_check()
    test_system_status()
    test_streaming_chat()
    # test_non_streaming_chat()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")