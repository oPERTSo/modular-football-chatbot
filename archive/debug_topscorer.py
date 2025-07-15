#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_topscorer_directly():
    """ทดสอบ get_topscorers_table โดยตรงเพื่อดู error"""
    
    print("🧪 Testing get_topscorers_table directly")
    print("=" * 50)
    
    try:
        # สร้าง chatbot
        print("🤖 Creating chatbot...")
        bot = ThaiFootballAnalysisChatbot()
        print("✅ Chatbot created successfully")
        
        # ทดสอบ get_topscorers_table โดยตรง
        print("\n🎯 Testing get_topscorers_table...")
        result = bot.get_topscorers_table("พรีเมียร์ลีก")
        
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result) if result else 'None'}")
        
        if result:
            if "ขออภัย" in result:
                print("❌ Error message returned")
                print(f"Error: {result}")
            elif "<table" in result:
                print("✅ HTML table returned")
                print("Success!")
            else:
                print("📝 Other content returned")
                print(f"Content preview: {result[:200]}...")
        else:
            print("❌ No result returned")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

def test_extract_league_id():
    """ทดสอบ extract_league_id"""
    print("\n🔍 Testing extract_league_id...")
    
    try:
        bot = ThaiFootballAnalysisChatbot()
        
        test_queries = [
            "พรีเมียร์ลีก",
            "ดาวซัลโวพรีเมียร์ลีก", 
            "premier league"
        ]
        
        for query in test_queries:
            league_id = bot.extract_league_id(query)
            print(f"'{query}' -> League ID: {league_id}")
            
    except Exception as e:
        print(f"❌ Error in extract_league_id: {e}")

def test_football_api():
    """ทดสอบ FootballAPI โดยตรง"""
    print("\n🏈 Testing FootballAPI directly...")
    
    try:
        from modules.football_api import FootballAPI
        from modules.config import Config
        
        api = FootballAPI(Config.API_FOOTBALL_KEY)
        
        print("📡 Calling get_topscorers API...")
        result = api.get_topscorers(39, 2024)  # Premier League
        
        if result:
            print("✅ API call successful")
            print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict) and "response" in result:
                print(f"Response count: {len(result['response'])}")
            else:
                print("❌ No 'response' field in API result")
        else:
            print("❌ API call failed - no result")
            
    except Exception as e:
        print(f"❌ Error in API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extract_league_id()
    test_football_api()
    test_topscorer_directly()
