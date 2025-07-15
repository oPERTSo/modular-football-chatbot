#!/usr/bin/env python3
"""
สคริปต์ทดสอบ News Manager และ Chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.config import get_api_keys
from modules.news_manager import NewsManager
from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_news_manager():
    """ทดสอบ News Manager"""
    print("🧪 ทดสอบ News Manager...")
    
    news_manager = NewsManager("data")
    
    # ทดสอบการโหลดไฟล์
    all_files = news_manager.get_all_files()
    print(f"📁 พบไฟล์ข่าว: {len(all_files)} ไฟล์")
    
    if all_files:
        print("📋 ไฟล์ข่าวล่าสุด 3 ไฟล์:")
        for i, file_path in enumerate(all_files[:3]):
            print(f"  {i+1}. {file_path.name}")
    
    # ทดสอบข่าวล่าสุด
    latest_news = news_manager.get_latest_news(3)
    print(f"📰 ข่าวล่าสุด: {len(latest_news)} ข่าว")
    
    # ทดสอบการสร้าง HTML
    if latest_news:
        html = news_manager.create_news_html(latest_news, "ทดสอบข่าว")
        print(f"📄 HTML Length: {len(html)} characters")
        print("✅ News Manager ทำงานได้ปกติ")
    else:
        print("❌ ไม่พบข่าวในระบบ")
    
    return len(all_files) > 0

def test_chatbot():
    """ทดสอบ Chatbot"""
    print("\n🤖 ทดสอบ Chatbot...")
    
    try:
        api_keys = get_api_keys()
        print(f"🔑 API Keys: OpenAI={bool(api_keys.get('openai_key'))}")
        
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            reference_folder="data"
        )
        
        print("✅ Chatbot เริ่มต้นสำเร็จ")
        
        # ทดสอบคำขอข่าว
        print("\n📰 ทดสอบคำขอข่าว...")
        response = chatbot.chat("ข่าวบอลวันนี้", "")
        print(f"Response length: {len(response)} characters")
        
        if len(response) > 100:
            print("✅ Chatbot ตอบข่าวได้")
            print(f"Preview: {response[:200]}...")
        else:
            print("❌ Chatbot ตอบข่าวไม่ได้")
            print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chatbot Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("="*50)
    print("🧪 CHATBOT NEWS TEST")
    print("="*50)
    
    # ทดสอบ News Manager
    news_ok = test_news_manager()
    
    # ทดสอบ Chatbot
    chatbot_ok = test_chatbot()
    
    print("\n" + "="*50)
    print("📊 สรุปผลการทดสอบ:")
    print(f"📁 News Manager: {'✅ OK' if news_ok else '❌ FAIL'}")
    print(f"🤖 Chatbot: {'✅ OK' if chatbot_ok else '❌ FAIL'}")
    print("="*50)
    
    if news_ok and chatbot_ok:
        print("🎉 ระบบพร้อมใช้งาน!")
    else:
        print("⚠️ ระบบมีปัญหา กรุณาตรวจสอบ")

if __name__ == "__main__":
    main()
