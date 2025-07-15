import subprocess
import sys
import time

try:
    print("🚀 กำลังเริ่มต้น Modular Football Chatbot...")
    process = subprocess.Popen([sys.executable, "app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
    
    # รอ 10 วินาที
    time.sleep(10)
    
    # ตรวจสอบว่า process ยังทำงานอยู่ไหม
    if process.poll() is None:
        print("✅ แอปเริ่มต้นสำเร็จ! กำลังรันอยู่...")
        print("📡 แอปพร้อมใช้งานที่ http://localhost:5000")
        
        # หยุด process
        process.terminate()
        process.wait()
        print("⏹️ หยุดการทดสอบแล้ว")
    else:
        # อ่าน error ถ้ามี
        stdout, stderr = process.communicate()
        print("❌ แอปไม่สามารถเริ่มต้นได้")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
            
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
