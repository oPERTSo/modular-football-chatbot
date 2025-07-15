#!/usr/bin/env python3
"""
Test script to get Serie A standings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballBot
from modules.config import Config

def test_serie_a():
    print("Testing Serie A standings...")
    
    # Initialize the bot
    bot = ThaiFootballBot()
    
    # Test different Serie A queries
    test_messages = [
        "ตารางลีกเซเรียอา",
        "ตารางลีกอิตาลี", 
        "Serie A standings",
        "ตารางเซเรียอา",
        "ตารางซีรี่ย์เอ"
    ]
    
    for message in test_messages:
        print(f"\n--- Testing: '{message}' ---")
        try:
            response = bot.process_message(message)
            print(f"Response type: {type(response)}")
            if isinstance(response, str):
                # Check if it's HTML
                if '<table' in response or '<div' in response:
                    print("✓ HTML response generated")
                    # Show first 200 chars
                    print(f"Preview: {response[:200]}...")
                else:
                    print(f"Text response: {response}")
            else:
                print(f"Response: {response}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test direct API call
    print("\n--- Testing direct API call ---")
    try:
        from modules.football_api import FootballAPI
        api = FootballAPI()
        standings = api.get_standings('SA')  # Serie A
        print(f"Direct API call result: {standings is not None}")
        if standings:
            print(f"Number of teams: {len(standings.get('response', [{}])[0].get('league', {}).get('standings', [[]])[0])}")
    except Exception as e:
        print(f"Direct API error: {e}")

if __name__ == "__main__":
    test_serie_a()
