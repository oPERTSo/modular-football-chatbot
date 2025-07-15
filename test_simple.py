#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """ทดสอบการ import modules"""
    try:
        from modules.thai_football_bot import ThaiFootballAnalysisChatbot
        print("✅ Successfully imported ThaiFootballAnalysisChatbot")
        return True
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False

def test_chatbot():
    """ทดสอบการสร้าง chatbot"""
    try:
        from modules.thai_football_bot import ThaiFootballAnalysisChatbot
        bot = ThaiFootballAnalysisChatbot()
        print("✅ Successfully created chatbot")
        return bot
    except Exception as e:
        print(f"❌ Failed to create chatbot: {e}")
        return None

def test_topscorer_query(bot):
    """ทดสอบคำสั่ง topscorer"""
    try:
        query = "ดาวซัลโวพรีเมียร์ลีก"
        response = bot.chat(query)
        
        if response:
            print(f"✅ Got response: {len(response)} characters")
            if "<table" in response:
                print("✅ Contains HTML table")
                return True
            elif "ขออภัย" in response:
                print("❌ Contains error message")
                return False
            else:
                print("📝 Text response")
                return True
        else:
            print("❌ No response")
            return False
            
    except Exception as e:
        print(f"❌ Error in topscorer query: {e}")
        return False

def main():
    print("🧪 Simple Test")
    print("=" * 30)
    
    # Test 1: Import
    print("1. Testing import...")
    if not test_import():
        return
    
    # Test 2: Create chatbot
    print("\n2. Testing chatbot creation...")
    bot = test_chatbot()
    if not bot:
        return
    
    # Test 3: Test topscorer
    print("\n3. Testing topscorer query...")
    success = test_topscorer_query(bot)
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()
