#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

def test_topscorer_api():
    """ทดสอบ API โดยตรงเพื่อหาสาเหตุที่ chat UI ไม่ทำงาน"""
    
    print("🧪 Testing Topscorer API")
    print("=" * 50)
    
    # Test data
    test_queries = [
        "ดาวซัลโวพรีเมียร์ลีก",
        "topscorer premier league",
        "ดาวซัลโวลาลีกา",
        "ดาวซัลโว บุนเดสลีกา",
        "ดาวซัลโวเซเรียอา"
    ]
    
    base_url = "http://localhost:5000"
    
    for query in test_queries:
        print(f"\n🎯 Testing: '{query}'")
        print("-" * 30)
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/chat",
                json={"prompt": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response Keys: {list(data.keys())}")
                    
                    # Check response field
                    if 'response' in data:
                        response_text = data['response']
                        print(f"Response Length: {len(response_text)}")
                        
                        # Check for success indicators
                        if "<table" in response_text:
                            print("✅ Contains HTML table")
                        elif "ขออภัย" in response_text:
                            print("❌ Contains error message")
                            print(f"Error: {response_text[:200]}...")
                        else:
                            print("📝 Contains text response")
                            
                    else:
                        print("❌ No 'response' field found")
                        
                    # Check message field
                    if 'message' in data:
                        print(f"Message field present: {len(data['message'])} chars")
                        
                except json.JSONDecodeError:
                    print("❌ Invalid JSON response")
                    print(f"Raw response: {response.text[:500]}...")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Flask server not running?")
            return False
        except requests.exceptions.Timeout:
            print("❌ Request Timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    return True

def test_server_health():
    """ทดสอบสถานะเซิร์ฟเวอร์"""
    print("\n🏥 Testing Server Health")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/", timeout=10)
        print(f"✅ Server is running - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return False

def main():
    """Main testing function"""
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    # Test server health first
    if not test_server_health():
        print("❌ Server is not running. Please start the Flask app first.")
        sys.exit(1)
    
    # Test topscorer API
    test_topscorer_api()
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete")

if __name__ == "__main__":
    main()
