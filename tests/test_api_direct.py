#!/usr/bin/env python3
"""
Test API Football key and topscorers endpoint directly
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test API Football key directly"""
    api_key = os.getenv("API_FOOTBALL_KEY")
    
    if not api_key:
        print("❌ No API_FOOTBALL_KEY found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test with a simple API call
    url = "https://v3.football.api-sports.io/status"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "v3.football.api-sports.io"
    }
    
    try:
        print("🔍 Testing API status endpoint...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_topscorers_direct():
    """Test topscorers endpoint directly"""
    api_key = os.getenv("API_FOOTBALL_KEY")
    
    if not api_key:
        print("❌ No API key")
        return
    
    # Test Premier League topscorers
    url = "https://v3.football.api-sports.io/players/topscorers"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "v3.football.api-sports.io"
    }
    
    # Test different seasons
    seasons = [2024, 2023]
    league_id = 39  # Premier League
    
    for season in seasons:
        print(f"\n🔍 Testing Premier League topscorers for season {season}...")
        
        params = {
            "league": league_id,
            "season": season
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success for season {season}")
                print(f"Response keys: {list(data.keys())}")
                
                if "response" in data:
                    players = data["response"]
                    print(f"Players found: {len(players)}")
                    
                    if players:
                        print("Top 3 players:")
                        for i, player in enumerate(players[:3], 1):
                            name = player.get("player", {}).get("name", "Unknown")
                            goals = player.get("statistics", [{}])[0].get("goals", {}).get("total", 0)
                            team = player.get("statistics", [{}])[0].get("team", {}).get("name", "Unknown")
                            print(f"  {i}. {name} ({team}) - {goals} goals")
                    else:
                        print("  No players found")
                
                if "errors" in data and data["errors"]:
                    print(f"API Errors: {data['errors']}")
                    
                break  # If successful, no need to try other seasons
                
            elif response.status_code == 429:
                print(f"❌ Rate limit exceeded")
                print(f"Response: {response.text}")
            elif response.status_code == 403:
                print(f"❌ Forbidden - API key issue?")
                print(f"Response: {response.text}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    print("🧪 DIRECT API FOOTBALL TEST")
    print("=" * 50)
    
    # Test API key first
    if test_api_key():
        print("\n" + "=" * 50)
        # Test topscorers endpoint
        test_topscorers_direct()
    else:
        print("❌ API key test failed - skipping topscorers test")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    main()
