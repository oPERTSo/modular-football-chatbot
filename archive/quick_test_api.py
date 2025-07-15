#!/usr/bin/env python3
"""
Quick test of API Football topscorers endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.config import get_api_keys
from modules.football_api import FootballAPI

def test_api_direct():
    """Test API Football directly"""
    try:
        print("🔧 Testing API Football directly...")
        
        # Get API keys
        api_keys = get_api_keys()
        if not api_keys.get('api_football_key'):
            print("❌ No API Football key found")
            return
            
        print(f"✅ API Football key: {api_keys['api_football_key'][:10]}...")
        
        # Create API instance
        api = FootballAPI(api_keys['api_football_key'])
        
        # Test different leagues
        leagues = [
            (39, "Premier League"),
            (140, "La Liga"),
            (78, "Bundesliga"),
            (135, "Serie A"),
            (61, "Ligue 1")
        ]
        
        for league_id, league_name in leagues:
            print(f"\n📋 Testing {league_name} (ID: {league_id})")
            print("-" * 40)
            
            try:
                result = api.get_topscorers(league_id, 2024)
                
                if result:
                    print(f"✅ Success: {type(result)}")
                    if isinstance(result, dict):
                        print(f"✅ Keys: {list(result.keys())}")
                        if "response" in result:
                            if result["response"]:
                                print(f"✅ Players found: {len(result['response'])}")
                                # Show first player
                                first_player = result["response"][0]
                                player_name = first_player.get("player", {}).get("name", "Unknown")
                                goals = first_player.get("statistics", [{}])[0].get("goals", {}).get("total", 0)
                                print(f"✅ Top scorer: {player_name} ({goals} goals)")
                            else:
                                print("⚠️  No players in response")
                        else:
                            print("⚠️  No 'response' key in result")
                    else:
                        print(f"⚠️  Result is not a dict: {result}")
                else:
                    print("❌ No result returned")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
            print()
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_direct()
