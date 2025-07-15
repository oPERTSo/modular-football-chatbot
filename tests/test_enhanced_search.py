#!/usr/bin/env python3
"""
Test Enhanced League Search - ทดสอบการค้นหาลีกแบบใหม่
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_enhanced_league_search():
    """ทดสอบการค้นหาลีกแบบใหม่"""
    print("🔍 ENHANCED LEAGUE SEARCH TEST")
    print("=" * 60)
    
    # สร้าง bot instance (ไม่ต้องใช้ API keys สำหรับการทดสอบ fuzzy matching)
    bot = ThaiFootballAnalysisChatbot()
    
    # ทดสอบการค้นหาแบบต่างๆ
    test_cases = [
        # ===== Premier League =====
        ("ตารางคะแนนพรีเมียร์ลีก", "Premier League - พื้นฐาน"),
        ("ตารางคะแนนแมนยู", "Premier League - จากชื่อทีม"),
        ("ตารางคะแนนลิเวอร์พูล", "Premier League - จากชื่อทีม"),
        ("ตารางคะแนนอังกฤษ", "Premier League - จากประเทศ"),
        ("ตารางคะแนน epl", "Premier League - ตัวย่อ"),
        ("ตารางคะแนน premier", "Premier League - ภาษาอังกฤษ"),
        
        # ===== La Liga =====
        ("ตารางคะแนนลาลีกา", "La Liga - พื้นฐาน"),
        ("ตารางคะแนนเรอัลมาดริด", "La Liga - จากชื่อทีม"),
        ("ตารางคะแนนบาร์เซโลนา", "La Liga - จากชื่อทีม"),
        ("ตารางคะแนนสเปน", "La Liga - จากประเทศ"),
        ("ตารางคะแนน laliga", "La Liga - ภาษาอังกฤษ"),
        
        # ===== Bundesliga =====
        ("ตารางคะแนนบุนเดสลีกา", "Bundesliga - พื้นฐาน"),
        ("ตารางคะแนนบาเยิร์น", "Bundesliga - จากชื่อทีม"),
        ("ตารางคะแนนดอร์ทมุนด์", "Bundesliga - จากชื่อทีม"),
        ("ตารางคะแนนเยอรมัน", "Bundesliga - จากประเทศ"),
        ("ตารางคะแนน bundesliga", "Bundesliga - ภาษาอังกฤษ"),
        
        # ===== Serie A =====
        ("ตารางคะแนนเซเรีย อา", "Serie A - พื้นฐาน"),
        ("ตารางคะแนนยูเวนตุส", "Serie A - จากชื่อทีม"),
        ("ตารางคะแนนมิลาน", "Serie A - จากชื่อทีม"),
        ("ตารางคะแนนอิตาลี", "Serie A - จากประเทศ"),
        ("ตารางคะแนน serie a", "Serie A - ภาษาอังกฤษ"),
        
        # ===== Ligue 1 =====
        ("ตารางคะแนนลีกเอิง", "Ligue 1 - พื้นฐาน"),
        ("ตารางคะแนนปีเอสจี", "Ligue 1 - จากชื่อทีม"),
        ("ตารางคะแนนปารีส", "Ligue 1 - จากชื่อทีม"),
        ("ตารางคะแนนฝรั่งเศส", "Ligue 1 - จากประเทศ"),
        ("ตารางคะแนน ligue 1", "Ligue 1 - ภาษาอังกฤษ"),
        
        # ===== ลีกอื่นๆ =====
        ("ตารางคะแนนไทยลีก", "Thai League"),
        ("ตารางคะแนนเจลีก", "J League"),
        ("ตารางคะแนนญี่ปุ่น", "J League - จากประเทศ"),
        
        # ===== ทดสอบคำผิด =====
        ("ตารางคะแนน premiership", "Premier League - คำคล้าย"),
        ("ตารางคะแนน la liga", "La Liga - มีช่องว่าง"),
        ("ตารางคะแนน บาร์ซ่า", "La Liga - ชื่อเล่น"),
        ("ตารางคะแนน แมนซิตี้", "Premier League - ชื่อเล่น"),
        ("ตารางคะแนน อินเตอร์", "Serie A - ชื่อย่อ"),
    ]
    
    print(f"📊 ทดสอบ {len(test_cases)} กรณี...")
    print()
    
    success_count = 0
    
    for i, (query, expected_description) in enumerate(test_cases, 1):
        print(f"{i:2d}. {query}")
        print(f"    Expected: {expected_description}")
        
        try:
            # ทดสอบการ extract league
            league_id = bot.extract_league_id(query)
            league_name = bot.get_league_name_from_message(query)
            
            print(f"    Result: {league_name} (ID: {league_id})")
            
            # ตรวจสอบว่าถูกต้องหรือไม่
            if any(keyword in expected_description for keyword in ["Premier", "พรีเมียร์"]) and league_id == 39:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["La Liga", "ลาลีกา"]) and league_id == 140:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["Bundesliga", "บุนเดสลีกา"]) and league_id == 78:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["Serie A", "เซเรีย"]) and league_id == 135:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["Ligue 1", "ลีกเอิง"]) and league_id == 61:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["Thai", "ไทย"]) and league_id == 253:
                print("    ✅ PASS")
                success_count += 1
            elif any(keyword in expected_description for keyword in ["J League", "เจลีก"]) and league_id == 188:
                print("    ✅ PASS")
                success_count += 1
            else:
                print("    ⚠️  PARTIAL/FAIL")
                
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            
        print()
    
    print("=" * 60)
    print(f"🎯 ผลสรุป: {success_count}/{len(test_cases)} ผ่าน ({success_count/len(test_cases)*100:.1f}%)")
    print()
    
    # แสดงตัวอย่างการใช้งาน
    print("💡 ตัวอย่างการใช้งานจริง:")
    print("   - 'ตารางคะแนนแมนยู' → พรีเมียร์ลีก")
    print("   - 'ตารางคะแนนบาร์เซโลนา' → ลาลีกา")
    print("   - 'ตารางคะแนนบาเยิร์น' → บุนเดสลีกา")
    print("   - 'ตารางคะแนนยูเวนตุส' → เซเรีย อา")
    print("   - 'ตารางคะแนนปีเอสจี' → ลีกเอิง")
    print()
    print("🚀 Enhanced League Search พร้อมใช้งาน!")

if __name__ == "__main__":
    test_enhanced_league_search()
