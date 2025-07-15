#!/usr/bin/env python3
"""
ทดสอบการทำงานของระบบข่าวและการดึงข้อมูลจากโฟลเดอร์ data
"""

from modules.thai_football_bot import ThaiFootballAnalysisChatbot
from modules.config import get_api_keys

def test_news_data():
    """ทดสอบการดึงข้อมูลข่าวจากโฟลเดอร์ data"""
    print("🔧 เริ่มต้นทดสอบระบบข่าว...")
    
    try:
        # ใช้ API keys
        api_keys = get_api_keys()
        
        # สร้าง chatbot
        print("🤖 สร้าง chatbot...")
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            reference_folder='data'
        )
        
        print(f"📁 จำนวนไฟล์ข้อมูลทั้งหมด: {len(chatbot.reference_data)}")
        print(f"📰 จำนวนไฟล์ข่าว: {len(chatbot.news_manager.get_all_files())}")
        
        # ตรวจสอบ path ของโฟลเดอร์ data
        print(f"📂 path ของ data folder: {chatbot.news_manager.data_folder}")
        print(f"📂 data folder มีอยู่จริง: {chatbot.news_manager.data_folder.exists()}")
        
        # ทดสอบดึงข่าวล่าสุด
        print("\n=== ทดสอบข่าวล่าสุด ===")
        latest_news = chatbot.news_manager.get_latest_news(3)
        print(f"ได้ข่าว {len(latest_news)} ข่าว:")
        for i, news in enumerate(latest_news, 1):
            print(f"  {i}. {news['title'][:60]}...")
            print(f"     ไฟล์: {news['filename']}")
        
        # ทดสอบค้นหาข่าวแมนยู
        print("\n=== ทดสอบค้นหาข่าวแมนยู ===")
        man_utd_news = chatbot.news_manager.search_news_by_keyword('แมนยู', 3)
        print(f"ได้ข่าว {len(man_utd_news)} ข่าว:")
        for i, news in enumerate(man_utd_news, 1):
            print(f"  {i}. {news['title'][:60]}...")
            print(f"     ไฟล์: {news['filename']}")
        
        # ทดสอบการสร้าง HTML
        print("\n=== ทดสอบการสร้าง HTML ===")
        html_result = chatbot.get_latest_news_from_data()
        print(f"HTML ขนาด: {len(html_result)} ตัวอักษร")
        print(f"เป็น HTML: {'<!DOCTYPE html>' in html_result}")
        print(f"มี news-item: {'news-item' in html_result}")
        print(f"มี news-container: {'news-container' in html_result}")
        
        # ทดสอบฟังก์ชัน chat
        print("\n=== ทดสอบฟังก์ชัน chat ===")
        chat_result = chatbot.chat('ข่าวฟุตบอลล่าสุด')
        print(f"Chat result ขนาด: {len(chat_result)} ตัวอักษร")
        print(f"เป็น HTML: {'<!DOCTYPE html>' in chat_result}")
        
        # แสดงตัวอย่าง HTML
        if '<!DOCTYPE html>' in chat_result:
            print("\n=== ตัวอย่าง HTML (100 ตัวอักษรแรก) ===")
            print(chat_result[:200] + "...")
        
        print("\n✅ ทดสอบสำเร็จ!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_news_data()
