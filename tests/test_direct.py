#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def main():
    """ทดสอบ topscorer โดยตรง"""
    
    print("🧪 Direct Topscorer Test")
    print("=" * 50)
    
    try:
        # สร้าง chatbot
        print("🤖 Creating chatbot...")
        bot = ThaiFootballAnalysisChatbot()
        
        # ทดสอบ queries
        test_queries = [
            "ดาวซัลโวพรีเมียร์ลีก",
            "topscorer premier league",
            "ดาวซัลโวลาลีกา",
            "ดาวซัลโว บุนเดสลีกา"
        ]
        
        for query in test_queries:
            print(f"\n🎯 Testing: '{query}'")
            print("-" * 30)
            
            try:
                response = bot.chat(query)
                
                # ตรวจสอบผลลัพธ์
                if response:
                    print(f"✅ Response Length: {len(response)}")
                    
                    if "<table" in response:
                        print("📊 Contains HTML table")
                        print("✅ Success!")
                    elif "ขออภัย" in response:
                        print("❌ Contains error message")
                        print(f"Error: {response[:200]}...")
                    else:
                        print("📝 Text response")
                        print(f"Response: {response[:200]}...")
                        
                else:
                    print("❌ No response")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Failed to create chatbot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
