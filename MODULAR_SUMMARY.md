# 🏆 Modular Football Chatbot Architecture

ได้ทำการแยกฟังก์ชันออกเป็น modules แล้วเสร็จสิ้น ✅

## 📁 โครงสร้างไฟล์ใหม่

```
chatbot/
├── modules/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # จัดการ API Keys และการตั้งค่า
│   ├── football_api.py          # จัดการ API Football ทั้งหมด
│   ├── news_manager.py          # จัดการข่าวและการค้นหา
│   ├── thai_football_bot.py     # Logic หลักของ Chatbot
│   └── api_handlers.py          # จัดการ Flask routes
├── app.py                       # Main application (ใช้ modules ใหม่)
├── app_original.py              # ไฟล์เดิม (สำรองไว้)
└── data/                        # ข้อมูลข่าว
```

## 🧩 รายละเอียด Modules

### 1. `modules/config.py`
- จัดการ API Keys (OpenAI, API Football)
- ฟังก์ชัน `get_api_keys()` และ `validate_api_keys()`
- การตั้งค่าต่างๆ เช่น MAX_TOKENS, DEFAULT_LEAGUE

### 2. `modules/football_api.py` 
- คลาส `FootballAPI` สำหรับเรียก API
- ฟังก์ชัน `get_standings()`, `get_topscorers()`, `get_fixtures()`
- จัดการ league mapping และ team mapping

### 3. `modules/news_manager.py`
- คลาส `NewsManager` สำหรับจัดการข่าว
- ฟังก์ชัน `get_latest_news()`, `search_news()`, `render_news_html()`
- การจัดการไฟล์ข่าวในโฟลเดอร์ data

### 4. `modules/thai_football_bot.py`
- คลาส `ThaiFootballAnalysisChatbot` หลัก
- ฟังก์ชัน `chat()`, `detect_query_type()`, `build_context()`
- การผสานงาน OpenAI API กับข้อมูลฟุตบอล

### 5. `modules/api_handlers.py`
- คลาส `APIHandlers` สำหรับจัดการ Flask routes
- ฟังก์ชัน endpoint ทั้งหมด เช่น `chat_endpoint()`, `news_endpoint()`

## 🚀 การใช้งาน

### การรันแอป:
```bash
cd "c:\Users\work\Desktop\งาน\chatbot"
python app.py
```

### การทดสอบ modules:
```bash
python test_modules.py
```

## 🎯 ประโยชน์ที่ได้รับ

1. **โค้ดเป็นระบบ**: แต่ละ module มีหน้าที่ชัดเจน
2. **ง่ายต่อการแก้ไข**: แก้ไขแต่ละฟีเจอร์ได้อย่างอิสระ
3. **ทดสอบง่าย**: สามารถทดสอบแต่ละ module แยกกันได้
4. **ขยายตัวได้**: เพิ่มฟีเจอร์ใหม่ได้ง่าย
5. **รักษาง่าย**: โค้ดอ่านเข้าใจได้ง่ายกว่าเดิม

## 🔧 API Endpoints ที่พร้อมใช้งาน

- `POST /chat` - Chat กับ AI
- `GET /api/news/latest` - ข่าวล่าสุด
- `GET /api/news/search?q=แมนยู` - ค้นหาข่าว
- `GET /api/standings?league=พรีเมียร์ลีก` - ตารางคะแนน
- `GET /api/topscorers?league=พรีเมียร์ลีก` - ดาวซัลโว
- `GET /api/team-form?team=แมนยู` - ฟอร์มทีม
- `GET /api/compare-teams?team1=แมนยู&team2=ลิเวอร์พูล` - เปรียบเทียบ
- `GET /api/last-results` - ผลบอลล่าสุด

## ✅ สถานะ

- [x] แยก config และ API keys
- [x] แยก Football API logic  
- [x] แยก News management
- [x] แยก main chatbot logic
- [x] แยก Flask routes handlers
- [x] อัปเดต main app ให้ใช้ modules
- [x] ทดสอบการทำงานของทุก modules
- [x] ระบบพร้อมใช้งาน

🎉 **การแยก modules เสร็จสมบูรณ์แล้ว!**
