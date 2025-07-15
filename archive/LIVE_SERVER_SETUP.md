# 🚀 วิธีการรัน Football Chatbot ผ่าน Live Server

## 📋 ขั้นตอนการตั้งค่า

### 1️⃣ **รัน Backend API (จำเป็น)**
```bash
# เปิด Terminal ใน VS Code
cd "c:\Users\work\Desktop\งาน\chatbot"
python app.py
```

### 2️⃣ **รัน Frontend ผ่าน Live Server**
1. คลิกขวาที่ไฟล์ `index-live.html` 
2. เลือก "Open with Live Server"
3. หรือกด `Alt + L + O`

## 🌐 URLs ที่ใช้งาน

### Frontend (Live Server)
- **หน้าแรก**: `http://127.0.0.1:5500/index-live.html`
- **หน้าแชท**: `http://127.0.0.1:5500/chat-live.html`

### Backend (Flask API)
- **API Server**: `http://localhost:5000`
- **Chat Endpoint**: `http://localhost:5000/chat`

## 📁 ไฟล์สำหรับ Live Server

```
chatbot/
├── index-live.html          # 🏠 หน้าแรก (รันผ่าน Live Server)
├── chat-live.html           # 💬 หน้าแชท (รันผ่าน Live Server)
├── static/
│   ├── css/
│   │   ├── index.css        # สไตล์หน้าแรก
│   │   └── chat.css         # สไตล์หน้าแชท
│   └── js/
│       └── chat-live.js     # Logic แชท (รองรับ CORS)
└── app.py                   # Backend API (ต้องรันแยก)
```

## ⚙️ คุณสมบัติพิเศษ

### ✅ **Auto Backend Detection**
- ตรวจสอบสถานะ Backend อัตโนมัติ
- แสดงสถานะ Online/Offline
- แจ้งเตือนเมื่อ Backend ไม่พร้อม

### 🔄 **CORS Support**
- รองรับ Cross-Origin Requests
- เชื่อมต่อระหว่าง Live Server และ Flask API

### 🎨 **Real-time Status**
- 🟢 ONLINE = Backend พร้อมใช้งาน
- 🔴 OFFLINE = Backend ไม่พร้อม

## 🐛 การแก้ปัญหา

### ปัญหา: ส่งข้อความไม่ได้
**วิธีแก้:**
1. ตรวจสอบว่ารัน `python app.py` แล้วหรือไม่
2. ดูให้แน่ใจว่า Backend รันที่ port 5000
3. ตรวจสอบ Console ใน Browser

### ปัญหา: CORS Error
**วิธีแก้:**
1. ตรวจสอบว่ามี `flask-cors` ติดตั้งแล้ว
2. ดูการตั้งค่า CORS ใน `app.py`

### ปัญหา: Live Server ไม่เปิด
**วิธีแก้:**
1. ติดตั้ง Live Server Extension
2. คลิกขวาที่ไฟล์ HTML
3. เลือก "Open with Live Server"

## 🎯 ข้อดีของ Live Server

- ✅ **Hot Reload** - แก้ไข CSS/JS เห็นผลทันที
- ✅ **ไม่ต้อง Flask** - รัน Frontend แยกได้
- ✅ **Easy Development** - พัฒนา Frontend ง่าย
- ✅ **Real URL** - มี URL ที่ใช้แชร์ได้
- ✅ **Mobile Testing** - ทดสอบบนมือถือได้
