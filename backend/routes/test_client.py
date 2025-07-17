#!/usr/bin/env python3
"""
Test script to simulate client requests to the backend service
"""

import asyncio
import httpx
import json
import time
from typing import Optional, Dict, Any

class BackendServiceTester:
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
    
    async def test_streaming_chat(self, message: str, child_age: int = 5):
        """Test the streaming chat endpoint"""
        url = f"{self.base_url}/api/v1/chat/stream"
        
        payload = {
            "message": message,
            "child_age": child_age
        }
        
        print(f"🚀 Testing streaming chat...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Headers: {json.dumps(self.headers, indent=2)}")
        print("-" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start_time = time.time()
                
                async with client.stream("POST", url, json=payload, headers=self.headers) as response:
                    print(f"✅ Response Status: {response.status_code}")
                    print(f"📋 Response Headers: {dict(response.headers)}")
                    print("-" * 50)
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"❌ Error: {error_text.decode()}")
                        return
                    
                    print("📡 Streaming response:")
                    full_content = ""
                    chunk_count = 0
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            chunk_count += 1
                            elapsed = time.time() - start_time
                            
                            print(f"[{elapsed:.2f}s] Chunk {chunk_count}: {line}")
                            
                            # Parse SSE data
                            if line.startswith("data: "):
                                try:
                                    json_content = line[6:]  # Remove "data: " prefix
                                    data = json.loads(json_content)
                                    
                                    if data.get("type") == "content":
                                        full_content += data.get("content", "")
                                    elif data.get("type") == "complete":
                                        print(f"✅ Stream completed!")
                                        break
                                    elif data.get("type") == "error":
                                        print(f"❌ Stream error: {data.get('content', 'Unknown error')}")
                                        break
                                        
                                except json.JSONDecodeError as e:
                                    print(f"❌ JSON decode error: {e}")
                                    print(f"Raw line: {line}")
                    
                    total_time = time.time() - start_time
                    print("-" * 50)
                    print(f"📊 Summary:")
                    print(f"   Total chunks: {chunk_count}")
                    print(f"   Total time: {total_time:.2f}s")
                    print(f"   Full content length: {len(full_content)} chars")
                    print(f"   First 100 chars: {full_content[:100]}...")
                    
        except httpx.TimeoutException:
            print("❌ Request timed out")
        except httpx.NetworkError as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        url = f"{self.base_url}/health"  # Adjust if you have a different health endpoint
        
        print(f"🏥 Testing health check...")
        print(f"URL: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    async def test_with_curl_equivalent(self, message: str, child_age: int = 5):
        """Show equivalent curl command for manual testing"""
        url = f"{self.base_url}/api/v1/chat/stream"
        payload = {
            "message": message,
            "child_age": child_age
        }
        
        print(f"🐚 Equivalent curl command:")
        print(f"curl -X POST '{url}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -H 'Accept: text/event-stream' \\")
        if self.auth_token:
            print(f"  -H 'Authorization: Bearer {self.auth_token}' \\")
        print(f"  -d '{json.dumps(payload)}' \\")
        print(f"  --no-buffer")
        print("-" * 50)

async def main():
    # Configuration
    BACKEND_URL = "http://localhost:8000"  # Change this to your backend URL
    AUTH_TOKEN = ''  # Set this if you need authentication
    
    # Test parameters
    TEST_MESSAGE = "Bagaimana performa anak saya dalam konsep menabung dan berbagi?"
    CHILD_AGE = 10
    
    # Initialize tester
    tester = BackendServiceTester(BACKEND_URL, AUTH_TOKEN)
    
    print("🧪 Backend Service Stream Test")
    print("=" * 50)
    
    # Test 1: Health check (optional)
    # await tester.test_health_check()
    # print()
    
    # Test 2: Show curl equivalent
    await tester.test_with_curl_equivalent(TEST_MESSAGE, CHILD_AGE)
    print()
    
    # Test 3: Streaming chat
    await tester.test_streaming_chat(TEST_MESSAGE, CHILD_AGE)
    print()
    
    # Test 4: Test with different messages
    test_cases = [
        ("Bagaimana performa anak saya dalam 1 tahun terakhir (12 bulan)", 6),
    ]
    
    for message, age in test_cases:
        print(f"🧪 Testing: '{message}' (age: {age})")
        await tester.test_streaming_chat(message, age)
        print("\n" + "="*50 + "\n")
        await asyncio.sleep(1)  # Small delay between tests


class SimpleStreamTester:
    """Simplified tester for quick debugging"""
    
    @staticmethod
    async def quick_test(url: str, message: str = "Hello"):
        """Quick test function"""
        payload = {"message": message, "child_age": 5}
        
        print(f"Quick test: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.strip():
                                print(f"Received: {line}")
                                if "complete" in line:
                                    break
                    else:
                        error = await response.aread()
                        print(f"Error: {error.decode()}")
                        
        except Exception as e:
            print(f"Exception: {e}")


if __name__ == "__main__":
    # Run the main test
    asyncio.run(main())