#!/usr/bin/env python3
"""
Test script for enhanced fuzzy matching - สำหรับทดสอบการพิมพ์ผิด
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_fuzzy_matching():
    print("=== Testing Enhanced Fuzzy Matching ===")
    
    # Initialize the chatbot
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test queries with typos and variations
    test_queries = [
        # Serie A variations
        "ตารางเซเรียอา",      # ถูกต้อง
        "ตารางซีเรียอา",      # พิมพ์ผิด: ซี แทน เซ
        "ตารางเซเรียอะ",      # พิมพ์ผิด: อะ แทน อา
        "ตารางซีเรียอะ",      # พิมพ์ผิด: ซี + อะ
        "ตารางเซรียอา",       # พิมพ์ผิด: ไม่มีเ
        "ตารางซีรียอา",       # พิมพ์ผิด: ซี + ไม่มีเ
        "ตารางเซเรียอ",       # พิมพ์ผิด: ไม่มีา
        "ตารางซีเรียอ",       # พิมพ์ผิด: ซี + ไม่มีา
        "ตารางเซรีย อา",      # พิมพ์ผิด: เซรีย แยก
        "ตารางซีรีย อา",      # พิมพ์ผิด: ซีรีย แยก
        
        # Premier League variations
        "ตารางพรีเมียร์ลีก",   # ถูกต้อง
        "ตารางปรีเมียร์ลีก",   # พิมพ์ผิด: ป แทน พ
        "ตารางพรีเมียลีก",     # พิมพ์ผิด: ไม่มีร์
        "ตารางปรีเมียลีก",     # พิมพ์ผิด: ป + ไม่มีร์
        "ตารางพรีเมียร์ลีค",   # พิมพ์ผิด: ค แทน ก
        "ตารางปรีเมียร์ลีค",   # พิมพ์ผิด: ป + ค
        
        # La Liga variations
        "ตารางลาลีกา",        # ถูกต้อง
        "ตารางลาลิกา",        # พิมพ์ผิด: ลิ แทน ลี
        "ตารางลาลีก",         # พิมพ์ผิด: ไม่มีา
        "ตารางลาลิก",         # พิมพ์ผิด: ลิ + ไม่มีา
        "ตารางลาลีคา",        # พิมพ์ผิด: ค แทน ก
        "ตารางลาลิคา",        # พิมพ์ผิด: ลิ + ค
        
        # Bundesliga variations
        "ตารางบุนเดสลีกา",    # ถูกต้อง
        "ตารางบันเดสลีกา",    # พิมพ์ผิด: บัน แทน บุน
        "ตารางบุนเดสลีค",     # พิมพ์ผิด: ค แทน กา
        "ตารางบันเดสลีค",     # พิมพ์ผิด: บัน + ค
        "ตารางบุนเดสลีคา",    # พิมพ์ผิด: คา แทน กา
        "ตารางบันเดสลีคา",    # พิมพ์ผิด: บัน + คา
    ]
    
    print("\n🔍 Testing various typos and variations...")
    
    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")
        
        try:
            # Test league detection
            league_id = chatbot.extract_league_id(query)
            
            # Map league IDs to names
            league_names = {
                39: "พรีเมียร์ลีก",
                140: "ลาลีกา", 
                78: "บุนเดสลีกา",
                135: "เซเรีย อา",
                61: "ลีกเอิง"
            }
            
            detected_league = league_names.get(league_id, f"Unknown (ID: {league_id})")
            
            # Test full chat response
            response = chatbot.chat(query)
            has_html_table = '<table' in response.lower()
            
            print(f"✅ Detected League: {detected_league}")
            print(f"✅ HTML Table Generated: {'Yes' if has_html_table else 'No'}")
            
            if has_html_table:
                print(f"📊 Response Preview: {response[:100]}...")
            else:
                print(f"📝 Text Response: {response[:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_specific_cases():
    print("\n=== Testing Specific Cases ===")
    
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test your specific examples
    specific_tests = [
        "เซเรียอา",
        "ซีเรียอา",
        "เซเรียอะ",
        "ซีเรียอะ",
        "เซรีย อา",
        "ซีรีย อา"
    ]
    
    for test in specific_tests:
        print(f"\n--- Testing specific case: '{test}' ---")
        
        try:
            league_id = chatbot.extract_league_id(test)
            if league_id == 135:
                print(f"✅ SUCCESS: Correctly identified as Serie A (ID: 135)")
            else:
                print(f"❌ FAILED: Identified as League ID {league_id}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_fuzzy_matching()
    test_specific_cases()
