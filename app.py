"""
Modular Football Chatbot Application
ระบบ AI วิเคราะห์ฟุตบอลแบบ Modular ที่แยกฟังก์ชันการทำงานออกเป็นส่วนๆ
"""

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

# Import our modular components
from modules.config import get_api_keys, validate_api_keys

from modules.thai_football_bot import ThaiFootballAnalysisChatbot
from modules.api_handlers import APIHandlers

app = Flask(__name__)
CORS(app)

# Global chatbot instance
chatbot = None
api_handlers = None

def clean_text(text):
    import re
    # Remove surrogate characters
    text = re.sub(r'[\ud800-\udfff]', '', text)
    # Remove any remaining problematic unicode
    return ''.join(c for c in text if ord(c) < 0xD800 or ord(c) > 0xDFFF)
@app.route('/')
def index():
    """หน้าแรกพร้อมคู่มือการใช้งาน API"""
    return render_template('index.html')

# Route handlers using APIHandlers

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    result = api_handlers.chat_endpoint()
    if isinstance(result, str):
        return clean_text(result)
    return result

@app.route('/api/standings')
def api_standings():
    """ตารางคะแนน"""
    return api_handlers.standings_endpoint()

@app.route('/api/topscorers')
def api_topscorers():
    """ดาวซัลโว"""
    return api_handlers.topscorers_endpoint()

@app.route('/api/team-form')
def api_team_form():
    """ฟอร์มทีม"""
    return api_handlers.team_form_endpoint()

@app.route('/api/compare-teams')
def api_compare_teams():
    """เปรียบเทียบทีม"""
    return api_handlers.compare_teams_endpoint()

@app.route('/api/last-results')
def api_last_results():
    """ผลบอลล่าสุด"""
    return api_handlers.last_results_endpoint()


@app.route('/api/news')
def api_news():
    """ข่าวฟุตบอล"""
    result = api_handlers.news_endpoint()
    if isinstance(result, str):
        return clean_text(result)
    return result


@app.route('/api/news/latest')
def api_latest_news():
    """ข่าวล่าสุด"""
    result = api_handlers.latest_news_endpoint()
    if isinstance(result, str):
        return clean_text(result)
    return result


@app.route('/api/news/search')
def api_search_news():
    """ค้นหาข่าว"""
    result = api_handlers.search_news_endpoint()
    if isinstance(result, str):
        return clean_text(result)
    return result

@app.route('/api/fixtures/today')
def api_today_fixtures():
    """โปรแกรมการแข่งขันวันนี้"""
    return api_handlers.today_fixtures_endpoint()

@app.route('/chat-ui')
def chat_ui():
    """หน้าแชทแบบ ChatGPT สำหรับถามคำถามฟุตบอล"""
    return render_template('chat.html')

@app.route('/test-api.html')
def test_api():
    """หน้าทดสอบ API Response"""
    return send_from_directory('.', 'test-api.html')

@app.route('/test-topscorer.html')
def test_topscorer():
    """หน้าทดสอบ Topscorer API"""
    return send_from_directory('.', 'test-topscorer.html')

@app.route('/test-serie-a.html')
def test_serie_a():
    """หน้าทดสอบ Serie A API"""
    return send_from_directory('.', 'test_serie_a_manual.html')

@app.route('/test-fuzzy-ui.html')
def test_fuzzy_ui():
    """หน้าทดสอบ Enhanced Fuzzy Matching"""
    return send_from_directory('.', 'test_fuzzy_ui.html')

def initialize_app():
    """Initialize the application with modules"""
    global chatbot, api_handlers
    
    try:
        print("🔧 กำลังเริ่มต้นระบบ Modular Football Chatbot...")
        
        # Load and validate API keys
        print("🔑 ตรวจสอบ API Keys...")
        api_keys = get_api_keys()
        
        if not validate_api_keys(api_keys):
            print("❌ API Keys ไม่ครบ กรุณาตรวจสอบไฟล์ .env")
            return False
        
        print("✅ API Keys พร้อมใช้งาน")
        
        # Initialize chatbot
        print("🤖 กำลังเริ่มต้น ThaiFootballBot...")
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=api_keys['openai_key'],
            reference_folder="data"
        )
        
        # Initialize API handlers
        print("🔌 กำลังเริ่มต้น API Handlers...")
        api_handlers = APIHandlers(chatbot)
        
        print("🎯 ตรวจสอบข้อมูลอ้างอิง...")
        if not chatbot.news_manager.get_all_files():
            print("⚠️ ไม่พบข้อมูลอ้างอิง แต่ระบบยังใช้งานได้")
        else:
            news_count = len(chatbot.news_manager.get_all_files())
            print(f"📋 โหลดข้อมูลสำเร็จ: {news_count} ไฟล์ข่าว")
        
        print("🚀 ระบบพร้อมใช้งาน!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นระบบ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main application entry point"""
    try:
        # Initialize the application
        if not initialize_app():
            print("❌ ไม่สามารถเริ่มต้นระบบได้")
            return
        
        print("\n" + "="*60)
        print("🏆 MODULAR FOOTBALL CHATBOT")
        print("="*60)
        print("📡 หน้าแรก: http://localhost:5000")
        print("� หน้าแชท: http://localhost:5000/chat-ui")
        print("🔴 กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์")
        print("🧩 โครงสร้างแบบ Modular พร้อมใช้งาน")
        print("📁 Static Files: templates/, static/css/, static/js/")
        print("="*60)
        
        # Run the Flask application
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n⏹️ หยุดเซิร์ฟเวอร์แล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
