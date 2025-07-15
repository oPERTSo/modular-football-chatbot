"""
Test modular imports
"""

print("🔧 ทดสอบ imports...")

try:
    from modules.config import get_api_keys, validate_api_keys
    print("✅ Config imported")
except Exception as e:
    print(f"❌ Config error: {e}")

try:
    from modules.thai_football_bot import ThaiFootballAnalysisChatbot
    print("✅ ThaiFootballAnalysisChatbot imported")
except Exception as e:
    print(f"❌ ThaiFootballAnalysisChatbot error: {e}")

try:
    from modules.api_handlers import APIHandlers
    print("✅ APIHandlers imported")
except Exception as e:
    print(f"❌ APIHandlers error: {e}")

print("\n🔑 ทดสอบ API Keys...")
try:
    api_keys = get_api_keys()
    print(f"OpenAI Key: {'✅ มี' if api_keys['openai_key'] else '❌ ไม่มี'}")
    print(f"Football API Key: {'✅ มี' if api_keys['api_football_key'] else '❌ ไม่มี'}")
    
    if validate_api_keys(api_keys):
        print("✅ API Keys พร้อมใช้งาน")
    else:
        print("❌ API Keys ไม่ครบ")
        
except Exception as e:
    print(f"❌ Error checking API keys: {e}")

print("\n🤖 ทดสอบสร้าง Chatbot...")
try:
    api_keys = get_api_keys()
    chatbot = ThaiFootballAnalysisChatbot(
        openai_api_key=api_keys['openai_key'],
        reference_folder="data"
    )
    print("✅ Chatbot สร้างสำเร็จ")
    
    # ทดสอบสร้าง API Handlers
    api_handlers = APIHandlers(chatbot)
    print("✅ API Handlers สร้างสำเร็จ")
    
except Exception as e:
    print(f"❌ Error creating chatbot: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 การทดสอบเสร็จสิ้น!")
