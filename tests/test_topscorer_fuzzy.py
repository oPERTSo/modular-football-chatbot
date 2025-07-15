#!/usr/bin/env python3
"""
Test script specifically for topscorer functionality with fuzzy matching
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_topscorer_fuzzy_matching():
    """Test topscorer queries with fuzzy matching"""
    print("⚽ Testing Topscorer Queries with Fuzzy Matching")
    print("=" * 60)
    
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test various topscorer queries with different league name formats
    test_queries = [
        ("ดาวซัลโวพรีเมียร์ลีก", "Premier League topscorer - exact Thai"),
        ("ดาวซัลโวพรีเมีย", "Premier League topscorer - short Thai"),
        ("top scorers premier league", "Premier League topscorer - English"),
        ("ดาวซัลโวอังกฤษ", "Premier League topscorer - country Thai"),
        ("ดาวซัลโวลาลีกา", "La Liga topscorer - exact Thai"),
        ("ดาวซัลโวลาลิกา", "La Liga topscorer - typo Thai"),
        ("top scorers la liga", "La Liga topscorer - English"),
        ("ดาวซัลโวสเปน", "La Liga topscorer - country Thai"),
        ("ดาวซัลโวบุนเดสลีกา", "Bundesliga topscorer - exact Thai"),
        ("ดาวซัลโวบุนเดส", "Bundesliga topscorer - short Thai"),
        ("top scorers bundesliga", "Bundesliga topscorer - English"),
        ("ดาวซัลโวเยอรมัน", "Bundesliga topscorer - country Thai"),
        ("ดาวซัลโวเซเรียอา", "Serie A topscorer - exact Thai"),
        ("ดาวซัลโวเซเรีย", "Serie A topscorer - short Thai"),
        ("top scorers serie a", "Serie A topscorer - English"),
        ("ดาวซัลโวอิตาลี", "Serie A topscorer - country Thai"),
        ("ดาวซัลโวลีกเอิง", "Ligue 1 topscorer - exact Thai"),
        ("ดาวซัลโวลีก 1", "Ligue 1 topscorer - alt Thai"),
        ("top scorers ligue 1", "Ligue 1 topscorer - English"),
        ("ดาวซัลโวฝรั่งเศส", "Ligue 1 topscorer - country Thai"),
        
        # Mixed language queries
        ("ดาวซัลโว premier league", "Mixed - Thai + English"),
        ("top scorers ลาลีกา", "Mixed - English + Thai"),
        ("ดาวซัลโว bundesliga", "Mixed - Thai + English"),
        ("top scorers เซเรีย", "Mixed - English + Thai"),
        
        # Very casual queries
        ("ใครยิงได้มากที่สุดพรีเมียร์", "Who scored most - Premier League"),
        ("ใครยิงเก่งที่สุดลาลีกา", "Who scored best - La Liga"),
        ("ใครทำประตูเยอะที่สุดบุนเดส", "Who scored most - Bundesliga"),
        ("ใครเจ๋งที่สุดเซเรียอา", "Who is best - Serie A"),
        ("ใครเก่งที่สุดลีกเอิง", "Who is best - Ligue 1"),
        
        # Questions with typos
        ("ดาวซัลโวพรีเมียลีค", "Topscorer - Premier League typo"),
        ("ดาวซัลโวลาลิค", "Topscorer - La Liga typo"),
        ("ดาวซัลโวบันเดส", "Topscorer - Bundesliga typo"),
        ("ดาวซัลโวเซเรียะ", "Topscorer - Serie A typo"),
        ("ดาวซัลโวลีคเอิง", "Topscorer - Ligue 1 typo"),
    ]
    
    print(f"Testing {len(test_queries)} topscorer queries...")
    print()
    
    success_count = 0
    total_count = len(test_queries)
    
    for i, (query, description) in enumerate(test_queries, 1):
        print(f"Test {i:2d}: {description}")
        print(f"         Query: '{query}'")
        
        try:
            # Test if the query contains topscorer-related keywords
            topscorer_keywords = ["ดาวซัลโว", "top scorer", "top scorers", "ยิง", "ประตู", "เจ๋ง", "เก่ง"]
            contains_topscorer = any(keyword in query.lower() for keyword in topscorer_keywords)
            
            if contains_topscorer:
                # Extract league name from query
                league_id = chatbot.extract_league_id(query)
                league_names = {
                    39: "พรีเมียร์ลีก",
                    140: "ลาลีกา", 
                    78: "บุนเดสลีกา",
                    135: "เซเรีย อา",
                    61: "ลีกเอิง",
                }
                
                detected_league = league_names.get(league_id, "Unknown")
                print(f"         🎯 Detected league: {detected_league} (ID: {league_id})")
                
                # Test the topscorer function
                result = chatbot.get_topscorers_table(query)
                
                if result and "ไม่พบข้อมูล" not in result and "ขออภัย" not in result:
                    print(f"         ✅ PASS: Successfully got topscorer data")
                    success_count += 1
                else:
                    print(f"         ⚠️  PARTIAL: Query processed but no data returned")
                    print(f"         Result: {result[:100]}...")
                    success_count += 0.5  # Partial success
                    
            else:
                print(f"         ❌ FAIL: Query doesn't contain topscorer keywords")
                
        except Exception as e:
            print(f"         💥 ERROR: {e}")
            
        print()
    
    print("=" * 60)
    print(f"TOPSCORER SUMMARY: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    print("=" * 60)

def test_league_detection_accuracy():
    """Test how accurately we can detect leagues from various inputs"""
    print("\n🎯 Testing League Detection Accuracy")
    print("=" * 60)
    
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test cases with expected league IDs
    test_cases = [
        # Clear cases
        ("พรีเมียร์ลีก", 39, "Premier League"),
        ("ลาลีกา", 140, "La Liga"),
        ("บุนเดสลีกา", 78, "Bundesliga"),
        ("เซเรีย อา", 135, "Serie A"),
        ("ลีกเอิง", 61, "Ligue 1"),
        
        # Country names
        ("อังกฤษ", 39, "England -> Premier League"),
        ("สเปน", 140, "Spain -> La Liga"),
        ("เยอรมัน", 78, "Germany -> Bundesliga"),
        ("อิตาลี", 135, "Italy -> Serie A"),
        ("ฝรั่งเศส", 61, "France -> Ligue 1"),
        
        # English names
        ("premier league", 39, "Premier League English"),
        ("la liga", 140, "La Liga English"),
        ("bundesliga", 78, "Bundesliga English"),
        ("serie a", 135, "Serie A English"),
        ("ligue 1", 61, "Ligue 1 English"),
        
        # Abbreviations
        ("epl", 39, "EPL -> Premier League"),
        ("pl", 39, "PL -> Premier League"),
        ("ll", 140, "LL -> La Liga"),
        ("bl", 78, "BL -> Bundesliga"),
        ("sa", 135, "SA -> Serie A"),
        ("l1", 61, "L1 -> Ligue 1"),
        
        # Mixed with other words
        ("ตารางคะแนนพรีเมียร์ลีก", 39, "Standings Premier League"),
        ("ดาวซัลโวลาลีกา", 140, "Topscorer La Liga"),
        ("ผลบอลบุนเดสลีกา", 78, "Results Bundesliga"),
        ("ข่าวเซเรียอา", 135, "News Serie A"),
        ("แชมป์ลีกเอิง", 61, "Champion Ligue 1"),
        
        # Challenging cases
        ("พรีเมียร์ลีกอังกฤษ", 39, "Premier League England"),
        ("ลาลีกาสเปน", 140, "La Liga Spain"),
        ("บุนเดสลีกาเยอรมัน", 78, "Bundesliga Germany"),
        ("เซเรียอาอิตาลี", 135, "Serie A Italy"),
        ("ลีกเอิงฝรั่งเศส", 61, "Ligue 1 France"),
    ]
    
    print(f"Testing {len(test_cases)} league detection cases...")
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
                print(f"         ✅ PASS: Detected league ID {result_id}")
                success_count += 1
            else:
                print(f"         ❌ FAIL: Got {result_id}, expected {expected_id}")
                
        except Exception as e:
            print(f"         💥 ERROR: {e}")
            
        print()
    
    print("=" * 60)
    print(f"DETECTION SUMMARY: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Topscorer Fuzzy Matching Tests")
    print("=" * 60)
    
    try:
        test_league_detection_accuracy()
        test_topscorer_fuzzy_matching()
        
        print("\n✅ All topscorer fuzzy matching tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
