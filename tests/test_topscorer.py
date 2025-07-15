#!/usr/bin/env python3
"""
Test Topscorer Function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot
from modules.config import get_api_keys

def test_topscorer():
    print("🧪 Testing Topscorer Function")
    print("=" * 50)
    
    try:
        # Initialize
        print("🔧 Initializing...")
        api_keys = get_api_keys()
        
        bot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            api_football_key=api_keys['api_football_key'],
            reference_folder='data'
        )
        
        print("✅ Bot initialized successfully")
        
        # Test different league queries
        test_queries = [
            "พรีเมียร์ลีก",
            "ลาลีกา", 
            "บุนเดสลีกา",
            "เซเรียอา",
            "ลีกเอิง"
        ]
        
        for query in test_queries:
            print(f"\n🎯 Testing: '{query}'")
            print("-" * 30)
            
            # Test league extraction
            league_id = bot.extract_league_id(query)
            print(f"   League ID detected: {league_id}")
            
            # Test topscorer function
            result = bot.get_topscorers_table(query)
            
            if result:
                print(f"   ✅ Result length: {len(result)} characters")
                print(f"   📝 First 100 chars: {result[:100]}...")
                
                # Check if it's HTML
                if "<table" in result:
                    print("   📊 HTML table detected")
                elif "ไม่พบข้อมูล" in result:
                    print("   ⚠️  No data found")
                elif "ขออภัย" in result:
                    print("   ❌ Error occurred")
                else:
                    print("   ❓ Unknown format")
            else:
                print("   ❌ No result returned")
        
        # Test the chat analyze function with topscorer queries
        print(f"\n🗣️ Testing Chat Integration")
        print("-" * 30)
        
        chat_queries = [
            "ดาวซัลโวพรีเมียร์ลีก",
            "topscorer la liga",
            "ดาวซัลโวลาลีกา"
        ]
        
        for query in chat_queries:
            print(f"\n   Query: '{query}'")
            response = bot.chat(query)
            
            if response:
                print(f"   ✅ Response length: {len(response)} characters") 
                if "<table" in response:
                    print("   📊 HTML table in response")
                elif "ไม่พบข้อมูล" in response:
                    print("   ⚠️  No data message")
                else:
                    print("   📝 Text response")
            else:
                print("   ❌ No response")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topscorer()
