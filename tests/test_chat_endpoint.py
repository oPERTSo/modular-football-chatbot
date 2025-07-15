#!/usr/bin/env python3
"""
ทดสอบการทำงานของ /chat endpoint โดยตรง
"""

import requests
import json

def test_chat_endpoint():
    """ทดสอบ /chat endpoint"""
    url = "http://localhost:5000/chat"
    
    # ทดสอบการถามข่าว
    test_cases = [
        "ข่าวฟุตบอลล่าสุด",
        "ข่าวแมนยู", 
        "ข่าวบอลวันนี้",
        "ตารางคะแนน พรีเมียร์ลีก",
        "ดาวซัลโว พรีเมียร์ลีก",
        "ดาวซัลโวพรีเมียร์ลีก",
        "topscorer premier league"
    ]
    
    for prompt in test_cases:
        print(f"\n=== ทดสอบ: {prompt} ===")
        
        try:
            response = requests.post(url, 
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("response", data.get("message", "ไม่มีผลลัพธ์"))
                
                if "<!DOCTYPE html>" in result:
                    print("✅ ได้ HTML Response")
                    print(f"ขนาด: {len(result)} ตัวอักษร")
                    # แสดงเฉพาะส่วนหัวของ HTML
                    lines = result.split('\n')
                    for i, line in enumerate(lines[:10]):
                        print(f"  {i+1}: {line}")
                    if len(lines) > 10:
                        print(f"  ... และอีก {len(lines)-10} บรรทัด")
                else:
                    print("✅ ได้ Text Response")
                    print(f"ผลลัพธ์: {result[:200]}...")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("🔧 ทดสอบ Chat Endpoint...")
    print("📡 ตรวจสอบ http://localhost:5000...")
    test_chat_endpoint()
