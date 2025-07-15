import requests
import json
import logging
from typing import Dict, Optional
from .config import Config

class FootballAPI:
    def get_team_squad(self, team_id: int, season: int = 2024) -> Optional[Dict]:
        """ดึงข้อมูลรายชื่อนักเตะของทีม"""
        try:
            url = f"{self.base_url}/players/squads"
            params = {"team": team_id, "season": season}
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API Error: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching team squad: {e}")
            return None
    """คลาสสำหรับเรียก Football API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.API_FOOTBALL_KEY
        self.base_url = Config.FOOTBALL_API_BASE_URL
        self.headers = {"x-apisports-key": self.api_key}
        self.logger = logging.getLogger(__name__)
    
    def get_standings(self, league_id: int, season: int = 2024) -> Optional[Dict]:
        """ดึงตารางคะแนน"""
        try:
            url = f"{self.base_url}/standings"
            params = {"league": league_id, "season": season}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API Error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching standings: {e}")
            return None
    
    def get_topscorers(self, league_id: int, season: int = 2024) -> Optional[Dict]:
        """ดึงข้อมูลดาวซัลโว"""
        try:
            url = f"{self.base_url}/players/topscorers"
            params = {"league": league_id, "season": season}
            
            print(f"🔍 API call: {url}")
            print(f"🔍 Params: {params}")
            print(f"🔍 Headers: {self.headers}")
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            print(f"🔍 Response status: {response.status_code}")
            print(f"🔍 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"🔍 Response data type: {type(data)}")
                    print(f"🔍 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict):
                        print(f"🔍 Errors field: {data.get('errors', 'No errors field')}")
                        print(f"🔍 Results field: {data.get('results', 'No results field')}")
                        
                        if "response" in data:
                            response_data = data["response"]
                            print(f"🔍 Response items count: {len(response_data) if response_data else 0}")
                            
                            if response_data and len(response_data) > 0:
                                first_player = response_data[0]
                                print(f"🔍 First player structure: {type(first_player)}")
                                if isinstance(first_player, dict):
                                    print(f"🔍 First player keys: {list(first_player.keys())}")
                                    if "player" in first_player:
                                        print(f"🔍 First player name: {first_player['player'].get('name', 'No name')}")
                                print(f"🔍 Sample data: {str(first_player)[:200]}...")
                        else:
                            print(f"🔍 No 'response' key in data")
                    
                    return data
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"❌ Raw response: {response.text[:500]}...")
                    return None
                    
            elif response.status_code == 429:
                print(f"❌ Rate limit exceeded (429)")
                print(f"❌ Response: {response.text}")
                return None
            elif response.status_code == 403:
                print(f"❌ Forbidden (403) - API key issue?")
                print(f"❌ Response: {response.text}")
                return None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"❌ Error response: {response.text}")
                self.logger.error(f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error")
            return None
        except Exception as e:
            print(f"❌ Exception in get_topscorers: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Error fetching topscorers: {e}")
            return None
    
    def get_team_fixtures(self, team_id: int, last: int = 5) -> Optional[Dict]:
        """ดึงผลการแข่งขันของทีม"""
        try:
            url = f"{self.base_url}/fixtures"
            params = {"team": team_id, "last": last}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API Error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching fixtures: {e}")
            return None
    
    def get_today_fixtures(self) -> Optional[Dict]:
        """ดึงข้อมูลแมตช์วันนี้"""
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/fixtures"
            params = {"date": today, "timezone": "Asia/Bangkok"}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API Error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching today fixtures: {e}")
            return None
