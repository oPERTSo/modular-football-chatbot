#!/usr/bin/env python3
"""
Test Serie A standings via API
"""

import requests
import json

def test_serie_a_api():
    print("=== Testing Serie A Standings via API ===")
    
    url = 'http://localhost:5000/api/chat'
    
    # Test different Serie A queries
    test_queries = [
        "ตารางลีกเซเรียอา",
        "ตารางเซเรียอา", 
        "Serie A standings",
        "ตารางอิตาลี",
        "ตารางซีรี่ย์เอ"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")
        
        try:
            response = requests.post(url, 
                                   json={'message': query},
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                if 'response' in data:
                    content = data['response']
                    print(f"Response type: {type(content)}")
                    print(f"Response length: {len(content)}")
                    
                    if '<table' in content.lower():
                        print("✅ SUCCESS: HTML table generated")
                        
                        # Save to file for viewing
                        filename = f"serie_a_{query.replace(' ', '_')}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"📄 Saved to {filename}")
                        
                        # Show preview
                        print("\n--- Preview ---")
                        print(content[:300])
                        print("...")
                        
                    else:
                        print("❌ No HTML table found")
                        print(f"Content preview: {content[:200]}")
                        
                else:
                    print("❌ No 'response' key in data")
                    print(f"Data: {data}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_serie_a_api()
