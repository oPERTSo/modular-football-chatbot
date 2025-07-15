#!/usr/bin/env python3
"""
Quick test for fuzzy matching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def quick_test():
    print("=== Quick Fuzzy Matching Test ===")
    
    bot = ThaiFootballAnalysisChatbot()
    
    # Test cases
    tests = [
        ("เซเรียอา", 135),   # ถูกต้อง
        ("ซีเรียอา", 135),   # พิมพ์ผิด
        ("เซเรียอะ", 135),   # พิมพ์ผิด
        ("ซีเรียอะ", 135),   # พิมพ์ผิด
    ]
    
    for test_input, expected_id in tests:
        try:
            print(f"\nTesting: '{test_input}'")
            result_id = bot.extract_league_id(test_input)
            
            if result_id == expected_id:
                print(f"✅ SUCCESS: {test_input} -> Serie A (ID: {result_id})")
            else:
                print(f"❌ FAILED: {test_input} -> ID: {result_id} (expected: {expected_id})")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    quick_test()
