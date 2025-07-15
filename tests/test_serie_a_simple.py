#!/usr/bin/env python3
"""
Simple test to get Serie A standings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_serie_a_standings():
    print("=== Testing Serie A Standings ===")
    
    # Initialize the chatbot
    chatbot = ThaiFootballAnalysisChatbot()
    
    # Test Serie A standings query
    message = "ตารางลีกเซเรียอา"
    print(f"Query: {message}")
    
    try:
        response = chatbot.chat(message)
        print(f"Response type: {type(response)}")
        
        if isinstance(response, str):
            if '<table' in response.lower():
                print("✅ SUCCESS: HTML table generated")
                # Save HTML to file for viewing
                with open('serie_a_standings.html', 'w', encoding='utf-8') as f:
                    f.write(response)
                print("📄 Saved to serie_a_standings.html")
                
                # Show first 500 characters
                print("\n--- Preview ---")
                print(response[:500])
                print("...")
                
            else:
                print("❌ FAILED: No HTML table generated")
                print(f"Response: {response}")
        else:
            print(f"❌ FAILED: Unexpected response type: {type(response)}")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serie_a_standings()
