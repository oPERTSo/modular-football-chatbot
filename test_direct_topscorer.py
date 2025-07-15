#!/usr/bin/env python3
"""
Direct test of the topscorer function with debug output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.config import get_api_keys
from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_topscorer_direct():
    """Test the topscorer function directly"""
    try:
        print("🔧 กำลังเริ่มต้นระบบ...")
        
        # Load API keys
        api_keys = get_api_keys()
        if not api_keys.get('openai_key'):
            print("❌ ไม่พบ OpenAI API key")
            return
            
        # Initialize chatbot
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            reference_folder="data"
        )
        
        print("✅ ระบบเริ่มต้นสำเร็จ")
        
        # Test different topscorer queries
        test_queries = [
            "ดาวซัลโวพรีเมียร์ลีก",
            "topscorer premier league",
            "ดาวซัลโวลาลีกา",
            "topscorer laliga",
            "ดาวซัลโวบุนเดสลีกา"
        ]
        
        print("\n" + "="*50)
        print("TESTING TOPSCORER FUNCTION")
        print("="*50)
        
        for query in test_queries:
            print(f"\n🧪 Testing: '{query}'")
            print("-" * 30)
            
            # Test the chat function (which calls get_topscorers_table)
            try:
                result = chatbot.chat(query)
                print(f"✅ Result type: {type(result)}")
                print(f"✅ Result length: {len(result) if result else 0}")
                
                if result:
                    if "ขออภัย" in result or "ไม่สามารถดึงข้อมูล" in result:
                        print("❌ ERROR: Got error message")
                        print(f"Error message: {result}")
                    else:
                        print("✅ SUCCESS: Got valid result")
                        # Show first 200 characters
                        print(f"Preview: {result[:200]}...")
                else:
                    print("❌ ERROR: Got empty result")
                    
            except Exception as e:
                print(f"❌ Exception in chat: {e}")
                import traceback
                traceback.print_exc()
                
        print("\n" + "="*50)
        print("DIRECT TEST COMPLETED")
        print("="*50)
                
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topscorer_direct()
