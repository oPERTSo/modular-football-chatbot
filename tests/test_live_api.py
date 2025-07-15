#!/usr/bin/env python3
"""
Test live API endpoint for topscorer to catch debug output
"""
import requests
import json
import time

def test_live_topscorer_api():
    """Test the live API endpoint for topscorer"""
    url = "http://localhost:5000/api/chat"
    
    # Test messages that should trigger topscorer
    test_messages = [
        "ดาวซัลโวพรีเมียร์ลีก",
        "topscorer premier league",
        "ดาวซัลโว premier league",
        "topscorer epl",
        "ดาวซัลโว อังกฤษ"
    ]
    
    print("Testing live API endpoint for topscorer...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        print("-" * 30)
        
        try:
            # Make API request
            response = requests.post(url, json={"message": message}, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # Check if it's an error response
                    if "response" in data:
                        if "ขออภัย" in data["response"] or "ไม่สามารถดึงข้อมูล" in data["response"]:
                            print("❌ ERROR: Got error response from API")
                        else:
                            print("✅ SUCCESS: Got valid response")
                    else:
                        print("⚠️  WARNING: Unexpected response format")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response: {response.text}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("Live API test completed!")

if __name__ == "__main__":
    test_live_topscorer_api()
