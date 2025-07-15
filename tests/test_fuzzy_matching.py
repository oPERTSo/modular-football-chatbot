#!/usr/bin/env python3
"""
Test script for fuzzy matching functionality
Tests various league name variations in Thai and English
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_fuzzy_matching():
    """Test fuzzy matching with various league names"""
    print("🔍 Testing Enhanced Fuzzy Matching for League Names")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test cases with expected results
    test_cases = [
        # Premier League tests
        ("พรีเมียร์ลีก", 39, "Premier League - exact Thai"),
        ("พรีเมีย", 39, "Premier League - short Thai"),
        ("premier league", 39, "Premier League - exact English"),
        ("premier", 39, "Premier League - short English"),
        ("อังกฤษ", 39, "Premier League - country Thai"),
        ("england", 39, "Premier League - country English"),
        ("epl", 39, "Premier League - abbreviation"),
        ("พรีเมียลีค", 39, "Premier League - typo Thai"),
        ("ปรีเมียร์", 39, "Premier League - alt spelling Thai"),
        ("premiar", 39, "Premier League - typo English"),
        ("premiership", 39, "Premier League - common name"),
        
        # La Liga tests
        ("ลาลิก้า", 140, "La Liga - exact Thai"),
        ("ลาลีกา", 140, "La Liga - alt Thai"),
        ("laliga", 140, "La Liga - exact English"),
        ("la liga", 140, "La Liga - spaced English"),
        ("สเปน", 140, "La Liga - country Thai"),
        ("spain", 140, "La Liga - country English"),
        ("ลาลิคา", 140, "La Liga - typo Thai"),
        ("lalliga", 140, "La Liga - typo English"),
        ("spanish league", 140, "La Liga - descriptive"),
        
        # Bundesliga tests
        ("บุนเดสลีกา", 78, "Bundesliga - exact Thai"),
        ("บุนเดส", 78, "Bundesliga - short Thai"),
        ("bundesliga", 78, "Bundesliga - exact English"),
        ("เยอรมัน", 78, "Bundesliga - country Thai"),
        ("germany", 78, "Bundesliga - country English"),
        ("บันเดสลีกา", 78, "Bundesliga - alt Thai"),
        ("bundersliga", 78, "Bundesliga - typo English"),
        ("german league", 78, "Bundesliga - descriptive"),
        
        # Serie A tests
        ("เซเรีย อา", 135, "Serie A - exact Thai"),
        ("เซเรีย", 135, "Serie A - short Thai"),
        ("serie a", 135, "Serie A - exact English"),
        ("อิตาลี", 135, "Serie A - country Thai"),
        ("italy", 135, "Serie A - country English"),
        ("เซเรียอา", 135, "Serie A - no space Thai"),
        ("seria a", 135, "Serie A - typo English"),
        ("italian league", 135, "Serie A - descriptive"),
        
        # Ligue 1 tests
        ("ลีกเอิง", 61, "Ligue 1 - exact Thai"),
        ("ลีก 1", 61, "Ligue 1 - alt Thai"),
        ("ligue 1", 61, "Ligue 1 - exact English"),
        ("ฝรั่งเศส", 61, "Ligue 1 - country Thai"),
        ("france", 61, "Ligue 1 - country English"),
        ("ลีกหนึ่ง", 61, "Ligue 1 - descriptive Thai"),
        ("league 1", 61, "Ligue 1 - alt English"),
        ("french league", 61, "Ligue 1 - descriptive"),
        
        # Champions League tests
        ("แชมป์เปี้ยนส์ลีก", 2, "Champions League - exact Thai"),
        ("champions league", 2, "Champions League - exact English"),
        ("ucl", 2, "Champions League - abbreviation"),
        ("แชมป์เปี้ยน", 2, "Champions League - short Thai"),
        ("champions", 2, "Champions League - short English"),
        
        # Europa League tests
        ("ยูโรป้าลีก", 3, "Europa League - exact Thai"),
        ("europa league", 3, "Europa League - exact English"),
        ("europa", 3, "Europa League - short English"),
        ("ยูโรป้า", 3, "Europa League - short Thai"),
        ("uel", 3, "Europa League - abbreviation"),
        
        # Edge cases and challenging inputs
        ("พรีเมียร์ลีกอังกฤษ", 39, "Premier League - with country"),
        ("ลาลีกาสเปน", 140, "La Liga - with country"),
        ("เซเรียอาอิตาลี", 135, "Serie A - with country"),
        ("บุนเดสลีกาเยอรมัน", 78, "Bundesliga - with country"),
        ("ลีกเอิงฝรั่งเศส", 61, "Ligue 1 - with country"),
        ("english premier league", 39, "Premier League - full descriptive"),
        ("spanish la liga", 140, "La Liga - full descriptive"),
        ("italian serie a", 135, "Serie A - full descriptive"),
        ("german bundesliga", 78, "Bundesliga - full descriptive"),
        ("french ligue 1", 61, "Ligue 1 - full descriptive"),
        
        # Very challenging cases
        ("พรีเมียร์", 39, "Premier League - partial Thai"),
        ("ลาลี", 140, "La Liga - very short Thai"),
        ("บุนเด", 78, "Bundesliga - very short Thai"),
        ("เซเรี", 135, "Serie A - very short Thai"),
        ("ลีกเอ", 61, "Ligue 1 - very short Thai"),
        
        # Common misspellings
        ("preamier league", 39, "Premier League - common misspelling"),
        ("premieer", 39, "Premier League - double e"),
        ("lalegue", 140, "La Liga - common misspelling"),
        ("seriea", 135, "Serie A - no space"),
        ("bundesligue", 78, "Bundesliga - common misspelling"),
        ("ligue1", 61, "Ligue 1 - no space"),
    ]
    
    print(f"Testing {len(test_cases)} different league name variations...")
    print()
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (input_text, expected_id, description) in enumerate(test_cases, 1):
        print(f"Test {i:2d}: {description}")
        print(f"         Input: '{input_text}'")
        
        try:
            result_id = chatbot.extract_league_id(input_text)
            success = result_id == expected_id
            
            if success:
                print(f"         ✅ PASS: Got league ID {result_id} (expected {expected_id})")
                success_count += 1
            else:
                print(f"         ❌ FAIL: Got league ID {result_id} (expected {expected_id})")
                
        except Exception as e:
            print(f"         💥 ERROR: {e}")
            
        print()
    
    print("=" * 60)
    print(f"SUMMARY: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All tests passed! Fuzzy matching is working perfectly!")
    elif success_count >= total_count * 0.9:
        print("🎯 Most tests passed! Fuzzy matching is working well!")
    elif success_count >= total_count * 0.8:
        print("⚠️  Some tests failed. Fuzzy matching needs improvement.")
    else:
        print("❌ Many tests failed. Fuzzy matching needs significant improvement.")
    
    print("=" * 60)

def test_specific_queries():
    """Test specific user queries that might contain league names"""
    print("\n🗣️  Testing Real User Query Scenarios")
    print("=" * 60)
    
    chatbot = ThaiFootballAnalysisChatbot()
    
    query_tests = [
        ("ตารางคะแนนพรีเมียร์ลีก", 39, "Standings query - Premier League"),
        ("ดาวซัลโวลาลีกา", 140, "Top scorers query - La Liga"),
        ("คะแนนบุนเดสลีกา", 78, "Standings query - Bundesliga"),
        ("ดาวซัลโวเซเรียอา", 135, "Top scorers query - Serie A"),
        ("ตารางลีกเอิง", 61, "Standings query - Ligue 1"),
        ("อยากดูคะแนนอังกฤษ", 39, "Casual query - England"),
        ("ดาวซัลโวสเปน", 140, "Top scorers query - Spain"),
        ("ผลบอลเยอรมัน", 78, "Results query - Germany"),
        ("ตารางอิตาลี", 135, "Standings query - Italy"),
        ("ฝรั่งเศสแชมป์เปี้ยนคือใคร", 61, "Champion query - France"),
        ("show me premier league table", 39, "English query - Premier League"),
        ("who is top scorer in la liga", 140, "English query - La Liga"),
        ("bundesliga standings please", 78, "English query - Bundesliga"),
        ("serie a top scorers", 135, "English query - Serie A"),
        ("ligue 1 table", 61, "English query - Ligue 1"),
    ]
    
    print(f"Testing {len(query_tests)} real user query scenarios...")
    print()
    
    success_count = 0
    total_count = len(query_tests)
    
    for i, (query, expected_id, description) in enumerate(query_tests, 1):
        print(f"Test {i:2d}: {description}")
        print(f"         Query: '{query}'")
        
        try:
            result_id = chatbot.extract_league_id(query)
            success = result_id == expected_id
            
            if success:
                print(f"         ✅ PASS: Detected league ID {result_id} (expected {expected_id})")
                success_count += 1
            else:
                print(f"         ❌ FAIL: Detected league ID {result_id} (expected {expected_id})")
                
        except Exception as e:
            print(f"         💥 ERROR: {e}")
            
        print()
    
    print("=" * 60)
    print(f"QUERY SUMMARY: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Enhanced Fuzzy Matching Tests")
    print("=" * 60)
    
    try:
        test_fuzzy_matching()
        test_specific_queries()
        
        print("\n✅ All fuzzy matching tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
