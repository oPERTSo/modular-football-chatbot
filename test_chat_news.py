#!/usr/bin/env python3
"""
ทดสอบการทำงานของระบบข่าวในแชท
"""

from modules.thai_football_bot import ThaiFootballAnalysisChatbot
from modules.config import get_api_keys

def test_news_system():
    print("🔧 กำลังเริ่มต้นทดสอบระบบข่าว...")
    
    try:
        # ใช้ API keys
        api_keys = get_api_keys()
        
        # สร้าง chatbot
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            reference_folder='data'
        )
        
        print(f"📁 จำนวนไฟล์ข้อมูล: {len(chatbot.reference_data)}")
        print(f"📰 จำนวนไฟล์ข่าว: {len(chatbot.news_manager.get_all_files())}")
        
        # ทดสอบข่าวล่าสุด
        print("\n=== ทดสอบข่าวล่าสุด ===")
        news_result = chatbot.get_latest_news_from_data()
        print(f"ผลลัพธ์: {news_result[:300]}...")
        
        # ทดสอบข่าวคีย์เวิร์ด
        print("\n=== ทดสอบข่าวคีย์เวิร์ด ===")
        keyword_result = chatbot.get_news_by_keyword('แมนยู')
        print(f"ผลลัพธ์: {keyword_result[:300]}...")
        
        # ทดสอบการตอบคำถามข่าว
        print("\n=== ทดสอบการตอบคำถามข่าว ===")
        chat_result = chatbot.chat('ข่าวฟุตบอลล่าสุด')
        print(f"ผลลัพธ์: {chat_result[:300]}...")
        
        # ทดสอบการตอบคำถามข่าวเฉพาะทีม
        print("\n=== ทดสอบข่าวเฉพาะทีม ===")
        team_news_result = chatbot.chat('ข่าวแมนยู')
        print(f"ผลลัพธ์: {team_news_result[:300]}...")
        
        print("\n✅ ทดสอบสำเร็จ!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_system()
