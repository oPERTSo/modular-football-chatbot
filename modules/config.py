import os
from dotenv import load_dotenv


# โหลด environment variables
print('DEBUG: Loading .env ...')
load_dotenv()
print('DEBUG: OPENAI_API_KEY from os.environ:', os.environ.get('OPENAI_API_KEY'))
print('DEBUG: OPENAI_API_KEY from os.getenv:', os.getenv('OPENAI_API_KEY'))

class Config:
    """คลาสสำหรับจัดการ configuration"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
    SPORTSDB_API_KEY = os.getenv("sportsdb_api_key")
    
    # API URLs
    FOOTBALL_API_BASE_URL = "https://v3.football.api-sports.io"
    
    # การตั้งค่าอื่นๆ
    MAX_TOKENS = 3500
    MAX_NEWS_ITEMS = 10
    DEFAULT_LEAGUE = "พรีเมียร์ลีก"
    
    @classmethod
    def validate_keys(cls):
        """ตรวจสอบ API Keys"""
        missing_keys = []
        
        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not cls.API_FOOTBALL_KEY:
            missing_keys.append("API_FOOTBALL_KEY")
            
        return missing_keys
    
    @classmethod
    def print_status(cls):
        """แสดงสถานะ API Keys"""
        print("🔑 ตรวจสอบ API Keys:")
        print(f"OPENAI_API_KEY: {'✅ มี' if cls.OPENAI_API_KEY else '❌ ไม่มี'}")
        print(f"API_FOOTBALL_KEY: {'✅ มี' if cls.API_FOOTBALL_KEY else '❌ ไม่มี'}")
        print(f"sportsdb_api_key: {'✅ มี' if cls.SPORTSDB_API_KEY else '❌ ไม่มี'}")

def get_api_keys():
    """ดึง API Keys ทั้งหมด"""
    return {
        'openai_key': Config.OPENAI_API_KEY,
        'api_football_key': Config.API_FOOTBALL_KEY,
        'sportsdb_key': Config.SPORTSDB_API_KEY
    }

def validate_api_keys(api_keys=None):
    """ตรวจสอบความถูกต้องของ API Keys"""
    if api_keys is None:
        api_keys = get_api_keys()
    
    # ตรวจสอบ keys ที่จำเป็น
    required_keys = ['openai_key', 'api_football_key']
    
    for key in required_keys:
        if not api_keys.get(key):
            print(f"❌ {key} ไม่พบหรือไม่ถูกต้อง")
            return False
    
    return True
