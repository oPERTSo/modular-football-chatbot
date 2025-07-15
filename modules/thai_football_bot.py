from pathlib import Path
import tiktoken
from typing import List, Dict
import re
from rapidfuzz import process, fuzz
from .football_api import FootballAPI
from .news_manager import NewsManager
from .config import Config


class ThaiFootballAnalysisChatbot:
    def get_league_name_from_message(self, user_message: str) -> str:
        """ดึงชื่อลีกจากข้อความ (รองรับไทย/อังกฤษ)"""
        msg = user_message.lower().strip()
        league_keywords = {
            'พรีเมียร์ลีก': 'พรีเมียร์ลีก', 'premier league': 'พรีเมียร์ลีก', 'epl': 'พรีเมียร์ลีก',
            'ลาลีกา': 'ลาลีกา', 'ลาลิกา': 'ลาลีกา', 'la liga': 'ลาลีกา',
            'บุนเดสลีกา': 'บุนเดสลีกา', 'bundesliga': 'บุนเดสลีกา',
            'เซเรีย อา': 'เซเรีย อา', 'serie a': 'เซเรีย อา',
            'ลีกเอิง': 'ลีกเอิง', 'ligue 1': 'ลีกเอิง',
            'ไทยลีก': 'ไทยลีก', 'thai league': 'ไทยลีก',
            'เจลีก': 'เจลีก', 'j league': 'เจลีก',
        }
        for key, name in league_keywords.items():
            if key in msg:
                return name
        return 'พรีเมียร์ลีก'  # Default
    import requests
    import json
    def ask_openai_fallback(self, user_message: str) -> str:
        """ใช้ OpenAI API ตอบคำถามทั่วไปเมื่อไม่มีข้อมูลในระบบ (รองรับ openai>=1.0.0)"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
                max_tokens=800,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"[OpenAI fallback error]: {e}")
            return "ขออภัย ระบบไม่สามารถตอบคำถามนี้ได้ในขณะนี้ (OpenAI API error)"
    def get_team_squad_html(self, team_name: str, season: int = 2024) -> str:
        """ดึงและแสดงรายชื่อนักเตะของทีมในรูปแบบ HTML"""
        team_id = self.get_team_id_by_name(team_name)
        if not team_id:
            return f"❌ ไม่พบ team_id สำหรับทีม '{team_name}' กรุณาระบุชื่อทีมให้ถูกต้อง (รองรับเฉพาะทีมยอดนิยม)"
        data = self.football_api.get_team_squad(team_id, season=season)
        if not data or 'response' not in data or not data['response']:
            return f"❌ ไม่พบข้อมูลรายชื่อนักเตะของทีม '{team_name}'"
        squad_info = data['response'][0] if data['response'] else None
        if not squad_info or 'players' not in squad_info:
            return f"❌ ไม่พบข้อมูลรายชื่อนักเตะของทีม '{team_name}'"
        players = squad_info['players']
        html = f"""
        <div class='team-squad-container'>
            <h3>👥 รายชื่อนักเตะ {team_name}</h3>
            <table class='squad-table'>
                <thead><tr><th>ชื่อ</th><th>ตำแหน่ง</th><th>อายุ</th><th>หมายเลข</th><th>สัญชาติ</th></tr></thead>
                <tbody>
        """
        for player in players:
            name = player.get('name', '-')
            position = player.get('position', '-')
            age = player.get('age', '-')
            number = player.get('number', '-')
            nationality = player.get('nationality', '-')
            html += f"<tr><td>{name}</td><td>{position}</td><td>{age}</td><td>{number}</td><td>{nationality}</td></tr>"
        html += """
                </tbody>
            </table>
            <p style='font-size:small;color:gray;'>*ข้อมูลจริงจาก API</p>
        </div>
        """
        return html
    def get_team_id_by_name(self, team_name: str) -> int:
        """แปลงชื่อทีม (ไทย/อังกฤษ/สะกดหลากหลาย) เป็น team_id สำหรับ API พร้อม fallback fuzzy match"""
        team_id_map = {
            # Premier League
            "แมนยู": 33, "แมนฯยูไนเต็ด": 33, "แมนฯยู": 33, "แมน u": 33, "man utd": 33, "man u": 33,
            "manchester united": 33, "manchester utd": 33, "man united": 33, "man utd fc": 33, "แมนยูไนเต็ด": 33, "แมนเชสเตอร์ ยูไนเต็ด": 33, "ปีศาจแดง": 33,
            "ลิเวอร์พูล": 40, "liverpool": 40, "หงส์แดง": 40, "ลิเวอร์": 40, "ลิเวอร์พลู": 40, "ลิpool": 40, "ลิpool": 40,
            "แมนซิตี้": 50, "แมนฯซิตี้": 50, "แมนซิ": 50, "man city": 50, "manchester city": 50, "เรือใบ": 50, "แมนเชสเตอร์ ซิตี้": 50, "city": 50,
            "อาร์เซนอล": 42, "arsenal": 42, "ปืนใหญ่": 42, "อาเซนอล": 42, "อาเซน่อล": 42, "ars": 42,
            "เชลซี": 49, "chelsea": 49, "สิงห์บลู": 49, "สิงห์บลูส์": 49, "เชลล์ซี": 49, "เชลซี เอฟซี": 49,
            "สเปอร์ส": 47, "tottenham": 47, "spurs": 47, "ไก่เดือยทอง": 47, "ท็อตแน่ม": 47, "ท็อตแน่ม ฮ็อทสเปอร์": 47,
            # La Liga
            "บาร์เซโลนา": 529, "บาร์ซ่า": 529, "barcelona": 529, "fc barcelona": 529, "บาร์เซโลน่า": 529, "บาร์ซา": 529, "บาซ่า": 529,
            "เรอัลมาดริด": 541, "real madrid": 541, "มาดริด": 541, "ราชันชุดขาว": 541, "เรอัล": 541, "เรอัล มาดริด": 541,
            "แอตเลติโก มาดริด": 530, "atletico madrid": 530, "แอตเลติโก": 530, "ตราหมี": 530,
            "เซบียา": 536, "sevilla": 536, "เซวิยา": 536,
            "บิลเบา": 531, "athletic bilbao": 531, "บิลเบา": 531,
            # Bundesliga
            "บาเยิร์น": 157, "bayern": 157, "bayern munich": 157, "บาเยิร์น มิวนิค": 157, "เสือใต้": 157, "บาเยิน": 157,
            "ดอร์ทมุนด์": 165, "dortmund": 165, "borussia dortmund": 165, "บีวีบี": 165, "ผึ้งเหลือง": 165,
            "ไลป์ซิก": 173, "rb leipzig": 173, "ไลป์ซิก": 173,
            "เลเวอร์คูเซ่น": 168, "bayer leverkusen": 168, "เลเวอร์คูเซ่น": 168,
            "แฟรงก์เฟิร์ต": 169, "eintracht frankfurt": 169, "แฟรงก์เฟิร์ต": 169,
            # Serie A
            "ยูเวนตุส": 496, "juventus": 496, "ม้าลาย": 496, "ยูเว่": 496,
            "อินเตอร์": 505, "inter": 505, "inter milan": 505, "อินเตอร์ มิลาน": 505, "งูใหญ่": 505,
            "มิลาน": 489, "ac milan": 489, "เอซีมิลาน": 489, "ปีศาจแดงดำ": 489,
            "นาโปลี": 492, "napoli": 492, "นาโปลี": 492,
            "โรม่า": 497, "roma": 497, "as roma": 497, "หมาป่ากรุงโรม": 497,
            # Ligue 1
            "เปแอสเช": 85, "psg": 85, "paris sg": 85, "paris saint-germain": 85, "ปารีส": 85, "ปารีสแซงต์แชร์กแมง": 85,
            "มาร์กเซย": 81, "marseille": 81, "โอลิมปิก มาร์กเซย": 81, "om": 81,
            "ลียง": 80, "lyon": 80, "โอแอล": 80,
            "โมนาโก": 91, "monaco": 91, "โมนาโก": 91,
            "ลีล": 79, "lille": 79, "ลีล": 79,
        }
        name = team_name.strip().lower()
        if name in team_id_map:
            return team_id_map[name]
        # Fuzzy match fallback (ใช้ rapidfuzz)
        choices = list(team_id_map.keys())
        match, score, idx = process.extractOne(name, choices, scorer=fuzz.ratio)
        if score >= 80:
            return team_id_map[match]
        return None

    def get_team_real_form(self, team_name: str, last: int = 5) -> str:
        """ดึงผลแข่ง 5 นัดล่าสุดของทีมจาก API และแสดงผลจริง"""
        team_id = self.get_team_id_by_name(team_name)
        if not team_id:
            return f"❌ ไม่พบ team_id สำหรับทีม '{team_name}' กรุณาระบุชื่อทีมให้ถูกต้อง (รองรับเฉพาะทีมยอดนิยม)"
        data = self.football_api.get_team_fixtures(team_id, last=last)
        if not data or 'response' not in data or not data['response']:
            return f"❌ ไม่พบข้อมูลผลการแข่งขันจริงของทีม '{team_name}'"
        fixtures = data['response']
        html = f"""
        <div class='team-form-container'>
            <h3>📅 ผลการแข่งขัน {last} นัดหลังสุด: {team_name}</h3>
            <table class='real-form-table'>
                <thead><tr><th>วันที่</th><th>คู่แข่ง</th><th>ผล</th><th>สกอร์</th></tr></thead>
                <tbody>
        """
        for fixture in fixtures:
            try:
                date = fixture['fixture']['date'][:10]
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                goals_home = fixture['goals']['home']
                goals_away = fixture['goals']['away']
                is_home = (home.lower() == team_name.lower())
                opponent = away if is_home else home
                score = f"{goals_home}-{goals_away}" if is_home else f"{goals_away}-{goals_home}"
                # Determine result
                if goals_home == goals_away:
                    result = "เสมอ"
                elif (is_home and goals_home > goals_away) or (not is_home and goals_away > goals_home):
                    result = "ชนะ"
                else:
                    result = "แพ้"
                html += f"<tr><td>{date}</td><td>{opponent}</td><td>{result}</td><td>{score}</td></tr>"
            except Exception as e:
                html += f"<tr><td colspan='4'>⚠️ ข้อมูลไม่สมบูรณ์: {e}</td></tr>"
        html += """
                </tbody>
            </table>
            <p style='font-size:small;color:gray;'>*ข้อมูลจริงจาก API</p>
        </div>
        """
        return html
    def compare_teams_form(self, team1_name: str, team2_name: str, count: int = 5) -> str:
        """เปรียบเทียบฟอร์ม 5 นัดหลังสุดของ 2 ทีม (5 ลีกใหญ่ยุโรป) ด้วยข้อมูลจริงจาก API"""
        # Map Thai/EN team names
        team1_id = self.get_team_id_by_name(team1_name)
        team2_id = self.get_team_id_by_name(team2_name)
        if not team1_id or not team2_id:
            return f"ขออภัย ไม่พบข้อมูลทีม '{team1_name}' หรือ '{team2_name}' ใน 5 ลีกใหญ่ยุโรป"

        # ดึงข้อมูลฟอร์ม 5 นัดหลังสุดจาก API-Football
        data1 = self.football_api.get_team_fixtures(team1_id, last=count)
        data2 = self.football_api.get_team_fixtures(team2_id, last=count)
        def parse_form(data, team_id):
            if not data or 'response' not in data or not data['response']:
                return None
            wins = draws = losses = goals_for = goals_against = 0
            form = []
            for fixture in data['response']:
                home = fixture['teams']['home']['id']
                away = fixture['teams']['away']['id']
                goals_h = fixture['goals']['home']
                goals_a = fixture['goals']['away']
                is_home = (home == team_id)
                gf = goals_h if is_home else goals_a
                ga = goals_a if is_home else goals_h
                goals_for += gf
                goals_against += ga
                if goals_h == goals_a:
                    draws += 1
                    form.append('D')
                elif (is_home and goals_h > goals_a) or (not is_home and goals_a > goals_h):
                    wins += 1
                    form.append('W')
                else:
                    losses += 1
                    form.append('L')
            return {
                'wins': wins, 'draws': draws, 'losses': losses,
                'goals_for': goals_for, 'goals_against': goals_against,
                'form': '-'.join(form)
            }
        team1_form = parse_form(data1, team1_id)
        team2_form = parse_form(data2, team2_id)
        if not team1_form or not team2_form:
            return f"ขออภัยครับ ไม่สามารถดึงข้อมูลฟอร์มของทีมได้ กรุณาลองใหม่อีกครั้ง"
        # Build HTML comparison table
        comparison = f"""
<div class='team-comparison'>
    <h3>เปรียบเทียบฟอร์ม {count} นัดหลังสุด</h3>
    <table class='comparison-table'>
        <thead>
            <tr>
                <th>สถิติ</th>
                <th>{team1_name}</th>
                <th>{team2_name}</th>
            </tr>
        </thead>
        <tbody>
            <tr><td><b>ชนะ</b></td><td>{team1_form['wins']}</td><td>{team2_form['wins']}</td></tr>
            <tr><td><b>เสมอ</b></td><td>{team1_form['draws']}</td><td>{team2_form['draws']}</td></tr>
            <tr><td><b>แพ้</b></td><td>{team1_form['losses']}</td><td>{team2_form['losses']}</td></tr>
            <tr><td><b>ยิงประตู</b></td><td>{team1_form['goals_for']}</td><td>{team2_form['goals_for']}</td></tr>
            <tr><td><b>เสียประตู</b></td><td>{team1_form['goals_against']}</td><td>{team2_form['goals_against']}</td></tr>
            <tr><td><b>ผลต่างประตู</b></td><td>{team1_form['goals_for'] - team1_form['goals_against']:+d}</td><td>{team2_form['goals_for'] - team2_form['goals_against']:+d}</td></tr>
            <tr><td><b>ฟอร์ม</b></td><td>{team1_form['form']}</td><td>{team2_form['form']}</td></tr>
        </tbody>
    </table>
    <div class='summary'><h4>🏆 สรุป:</h4>"""
        # Analyze which team is better
        team1_points = team1_form['wins'] * 3 + team1_form['draws']
        team2_points = team2_form['wins'] * 3 + team2_form['draws']
        if team1_points > team2_points:
            comparison += f"<p>• <b>{team1_name}</b> มีฟอร์มดีกว่า (มากกว่า {team1_points - team2_points} แต้ม)</p>"
        elif team2_points > team1_points:
            comparison += f"<p>• <b>{team2_name}</b> มีฟอร์มดีกว่า (มากกว่า {team2_points - team1_points} แต้ม)</p>"
        else:
            comparison += f"<p>• ทั้งสองทีมมีฟอร์มเท่ากัน ({team1_points} แต้ม)</p>"
        # Compare goals scored
        if team1_form['goals_for'] > team2_form['goals_for']:
            comparison += f"<p>• <b>{team1_name}</b> ทำประตูได้มากกว่า ({team1_form['goals_for']} vs {team2_form['goals_for']})</p>"
        elif team2_form['goals_for'] > team1_form['goals_for']:
            comparison += f"<p>• <b>{team2_name}</b> ทำประตูได้มากกว่า ({team2_form['goals_for']} vs {team1_form['goals_for']})</p>"
        comparison += "</div></div>"
        return comparison
    def __init__(self, openai_api_key: str = None, api_football_key: str = None, reference_folder: str = "data", max_tokens: int = 3500):
        self.openai_api_key = openai_api_key or Config.OPENAI_API_KEY
        self.api_football_key = api_football_key or Config.API_FOOTBALL_KEY
        self.reference_folder = Path(reference_folder)
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.reference_data = self.load_reference_files()
        
        # Initialize API and News Manager
        self.football_api = FootballAPI(self.api_football_key)
        self.news_manager = NewsManager(reference_folder)
        
        # Team mappings
        self.thai_team_map = {
            # Premier League
            "แมนยู": "Manchester United",
            "แมนยูไนเต็ด": "Manchester United",
            "แมนเชสเตอร์ ยูไนเต็ด": "Manchester United",
            "ลิเวอร์พูล": "Liverpool",
            "หงส์แดง": "Liverpool",
            "แมนซิตี้": "Manchester City",
            "แมนเชสเตอร์ ซิตี้": "Manchester City",
            "เรือใบสีฟ้า": "Manchester City",
            "อาร์เซนอล": "Arsenal",
            "ปืนใหญ่": "Arsenal",
            "เชลซี": "Chelsea",
            "สิงห์บลูส์": "Chelsea",
            "สเปอร์ส": "Tottenham",
            "ท็อตแน่ม ฮ็อทสเปอร์": "Tottenham",
            "ไก่เดือยทอง": "Tottenham",
        }
        
        self.team_to_league = {
            # Premier League
            "Manchester United": 39, "แมนเชสเตอร์ ยูไนเต็ด": 39, "แมนยู": 39,
            "Liverpool": 39, "ลิเวอร์พูล": 39, "หงส์แดง": 39,
            "Arsenal": 39, "อาร์เซนอล": 39, "ปืนใหญ่": 39,
            "Chelsea": 39, "เชลซี": 39, "สิงห์บลูส์": 39,
            "Manchester City": 39, "แมนเชสเตอร์ ซิตี้": 39, "แมนซิตี้": 39,
            "Tottenham": 39, "สเปอร์ส": 39, "ท็อตแน่ม ฮ็อทสเปอร์": 39,
        }
    
    def load_reference_files(self) -> Dict[str, Dict]:
        """โหลดไฟล์อ้างอิง"""
        reference_data = {}
        if not self.reference_folder.exists():
            print(f"คำเตือน: ไม่พบโฟลเดอร์ข้อมูลอ้างอิง {self.reference_folder}")
            return reference_data
            
        txt_files = list(self.reference_folder.glob("*.txt"))
        print(f"กำลังโหลดไฟล์ข้อมูลฟุตบอล {len(txt_files)} ไฟล์...")
        
        for file_path in txt_files:
            try:
                content = None
                for encoding in ['utf-8', 'utf-8-sig', 'cp874', 'tis-620']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read().strip()
                            break
                    except UnicodeDecodeError:
                        continue
                        
                if content:
                    reference_data[file_path.stem] = {
                        'content': content,
                        'type': 'ข้อมูลฟุตบอลทั่วไป',
                        'filename': file_path.name,
                        'word_count': len(content.split())
                    }
                    print(f"โหลดแล้ว: {file_path.name}")
                    
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการโหลด {file_path}: {e}")
                
        print(f"โหลดไฟล์ข้อมูลฟุตบอลสำเร็จ {len(reference_data)} ไฟล์")
        return reference_data
    
    def extract_league_id(self, user_message: str) -> int:
        """แปลงชื่อลีกเป็น ID ด้วย Enhanced Fuzzy Matching พร้อมคำค้นหาที่หลากหลาย"""
        # ขยายรายการลีกและชื่อเล่น/ชื่อสามัญ - เพิ่มคำค้นหาใหม่
        league_map = {
            # Premier League - รองรับหลายรูปแบบ (รวมการพิมพ์ผิด)
            "พรีเมียร์ลีก": 39, "พรีเมีย": 39, "พรีเมียร์": 39, "พรีเมียลีก": 39,
            "พรีเมียลีค": 39, "พรีเมีย ลีก": 39, "พรีเมียร์ลีค": 39,
            "ปรีเมียลีก": 39, "ปรีเมีย": 39, "ปรีเมียลีก": 39, "ปรีเมีย": 39,
            "พรีเมียลีค": 39, "พรีเมีย ลีค": 39, "พรีเมียร์ลีค": 39,
            "ปรีเมีย": 39, "ปรีเมีย": 39, "ปรีเมียลีก": 39,
            "พรีเมียร์ลีคา": 39, "พรีเมียร์ลีคะ": 39, "พรีเมียร์ลีคำ": 39,
            "premier league": 39, "premier": 39, "epl": 39, "england": 39, 
            "อังกฤษ": 39, "อังกฤส": 39, "อังฤษ": 39, "english": 39,
            "ปรีเมีย": 39, "ปรีเมีย": 39, "ปรีเมียลีก": 39,
            "pl": 39, "england league": 39, "premier lg": 39,
            # เพิ่มคำค้นหาใหม่สำหรับ Premier League
            "แมนยู": 39, "แมนซิตี้": 39, "ลิเวอร์พูล": 39, "เชลซี": 39, "อาร์เซนอล": 39,
            "สเปอร์ส": 39, "นิวคาสเซิล": 39, "แมนเชสเตอร์": 39, "ลอนดอน": 39,
            "liverpool": 39, "manchester": 39, "arsenal": 39, "chelsea": 39,
            "tottenham": 39, "spurs": 39, "city": 39, "united": 39,
            "กัน": 39, "ฮาวก์": 39, "อีกิล": 39, "ฮาลันด์": 39, "ซาลาห์": 39,
            
            # Bundesliga - รองรับหลายรูปแบบ (รวมการพิมพ์ผิด)
            "บุนเดสลีกา": 78, "บุนเดส": 78, "บุนเดสลีก": 78, "บุนเดสลีกะ": 78,
            "บุนเดสลีค": 78, "บุนเดสลีกำ": 78, "บุนเดสลีกาา": 78,
            "บันเดสลีกา": 78, "บันเดส": 78, "บันเดสลีก": 78, "บันเดสลีกะ": 78,
            "บุนเดสลีคา": 78, "บุนเดสลีคะ": 78, "บุนเดสลีคำ": 78,
            "บันเดสลีคา": 78, "บันเดสลีคะ": 78, "บันเดสลีคำ": 78,
            "บุนเดสลีคาา": 78, "บุนเดสลีคะะ": 78, "บุนเดสลีคำำ": 78,
            "bundesliga": 78, "german": 78, "germany": 78, "เยอรมัน": 78, 
            "เยอรมนี": 78, "เยอรมันนี่": 78, "ยอร์มัน": 78, "เยอรมันนี": 78,
            "บันเดส": 78, "บันเดสลีก": 78, "บันเดสลีกา": 78,
            "bl": 78, "germany league": 78, "bundesliga 1": 78,
            # เพิ่มคำค้นหาใหม่สำหรับ Bundesliga
            "บาเยิร์น": 78, "ดอร์ทมุนด์": 78, "ไลป์ซิก": 78, "เลเวอร์คูเซ่น": 78,
            "บาย": 78, "บีวีบี": 78, "มิวนิค": 78, "ฮาลันด์": 78,
            "bayern": 78, "dortmund": 78, "leipzig": 78, "bayer": 78,
            "bvb": 78, "munich": 78, "leverkusen": 78, "borussia": 78,
            
            # La Liga - รองรับหลายรูปแบบ (รวมการพิมพ์ผิด)
            "ลาลิก้า": 140, "ลาลีกา": 140, "ลาลิกา": 140, "ลาลีก": 140,
            "ลาลีคา": 140, "ลาลิค": 140, "ลาลิคา": 140, "ลาลีค": 140,
            "ลาลิค": 140, "ลาลีค": 140, "ลาลิคา": 140, "ลาลีคา": 140,
            "ลาลิกา": 140, "ลาลีกา": 140, "ลาลิค": 140, "ลาลีค": 140,
            "ลาลิก": 140, "ลาลีก": 140, "ลาลิคะ": 140, "ลาลีคะ": 140,
            "ลาลิคำ": 140, "ลาลีคำ": 140, "ลาลิคาา": 140, "ลาลีคาา": 140,
            "laliga": 140, "la liga": 140, "spain": 140, "spanish": 140,
            "สเปน": 140, "สเปน": 140, "สเปนน์": 140, "สเปนิช": 140,
            "สเปนิส": 140, "สเปนส์": 140, "ลลีกา": 140,
            "ll": 140, "spain league": 140, "la liga santander": 140,
            # เพิ่มคำค้นหาใหม่สำหรับ La Liga
            "เรอัลมาดริด": 140, "บาร์เซโลนา": 140, "แอตเลติโก": 140, "เซบียา": 140,
            "เรอัล": 140, "บาร์ซ่า": 140, "บาร์ซา": 140, "เอเลา": 140,
            "มาดริด": 140, "บาร์เซโลน่า": 140, "เบติส": 140, "บิลเบา": 140,
            "real madrid": 140, "barcelona": 140, "atletico": 140, "sevilla": 140,
            "real": 140, "barca": 140, "atleti": 140, "madrid": 140,
            "messi": 140, "ronaldo": 140, "benzema": 140, "modric": 140,
            
            # Serie A - รองรับหลายรูปแบบ (รวมการพิมพ์ผิด)
            "เซเรีย อา": 135, "เซเรีย": 135, "เซเรียอา": 135, "เซเรียเอ": 135,
            "เซเรียะ": 135, "เซเรียา": 135, "เซเรีย เอ": 135, "เซเรีย อะ": 135,
            "ซีเรียอา": 135, "ซีเรีย": 135, "ซีเรียเอ": 135, "ซีเรียา": 135,
            "ซีเรีย อา": 135, "ซีเรีย เอ": 135, "ซีเรีย อะ": 135,
            "เซเรียอะ": 135, "เซเรียเอ": 135, "เซเรียอ": 135, "เซรีย": 135,
            "ซีเรีย": 135, "ซีเรียะ": 135, "ซีเรียอะ": 135, "ซีเรียอ": 135,
            "ซีรีย": 135, "เซรีย": 135, "ซีรีย อา": 135, "เซรีย อา": 135,
            "serie a": 135, "serie": 135, "italy": 135, "italian": 135,
            "อิตาลี": 135, "อิตาลี่": 135, "อิตาเลี่ยน": 135, "อิตาเลียน": 135,
            "อิตาเลียม": 135, "อิตาลี": 135, "เซเรีย เอ": 135,
            "sa": 135, "italy league": 135, "serie a tim": 135,
            # เพิ่มคำค้นหาใหม่สำหรับ Serie A
            "ยูเวนตุส": 135, "อินเตอร์": 135, "มิลาน": 135, "โรมา": 135,
            "ลาซิโอ": 135, "นาโปลี": 135, "ฟิออเรนตินา": 135, "อาตาลันตา": 135,
            "ยูเว": 135, "อินเตอร์มิลาน": 135, "เอซีมิลาน": 135, "โรม่า": 135,
            "juventus": 135, "inter": 135, "milan": 135, "roma": 135,
            "lazio": 135, "napoli": 135, "juve": 135, "ac milan": 135,
            "inter milan": 135, "fiorentina": 135, "atalanta": 135,
            
            # Ligue 1 - รองรับหลายรูปแบบ (รวมการพิมพ์ผิด)
            "ลีกเอิง": 61, "ลีก 1": 61, "ลีกวัน": 61, "ลีก1": 61,
            "ลีกเอิ้ง": 61, "ลีกเอิ่ง": 61, "ลีกหนึ่ง": 61, "ลีค 1": 61,
            "ลีกเอิ้ง": 61, "ลีกเอิ่ง": 61, "ลีกเอิ๋ง": 61, "ลีกเอิ๊ง": 61,
            "ลีกเอิงค์": 61, "ลีกเอิงก์": 61, "ลีกเอิงส์": 61,
            "ลีกฝรั่งเศส": 61, "ลีกฝรั่งเศษ": 61, "ลีกฝรั่งเศด": 61,
            "ลีค เอิง": 61, "ลีค 1": 61, "ลีค วัน": 61, "ลีค หนึ่ง": 61,
            "ligue 1": 61, "ligue": 61, "france": 61, "french": 61,
            "ฝรั่งเศส": 61, "ฝรั่งเศส": 61, "ฝรั่งเศษ": 61, "เฟรนช์": 61,
            "เฟรนซ์": 61, "ฝรั่งเศด": 61, "ฝรั่งเศท": 61, "ฝรั่งเศส": 61,
            "ฝรั่งเศษ": 61, "ฝรั่งเศศ": 61, "ฝรั่งเศท": 61,
            "l1": 61, "france league": 61, "ligue 1 uber eats": 61,
            # เพิ่มคำค้นหาใหม่สำหรับ Ligue 1
            "ปารีสแซงต์แชร์กแมง": 61, "ปีเอสจี": 61, "มาร์เซย": 61, "ลียง": 61,
            "โมนาโก": 61, "ลีล": 61, "ปารีส": 61, "แซงต์": 61,
            "psg": 61, "paris": 61, "marseille": 61, "lyon": 61,
            "monaco": 61, "lille": 61, "saint germain": 61, "om": 61,
            "mbappe": 61, "neymar": 61, "messi": 61, "paris sg": 61,
            
            # Champions League - เพิ่มเติม (รวมการพิมพ์ผิด)
            "แชมป์เปี้ยนส์ลีก": 2, "แชมป์เปี้ยนลีก": 2, "แชมเปี้ยนลีก": 2,
            "แชมป์เปี้ยนส์ลีค": 2, "แชมป์เปี้ยนลีค": 2, "แชมเปี้ยนลีค": 2,
            "แชมป์เปี้ยนส์ลีคา": 2, "แชมป์เปี้ยนลีคา": 2, "แชมเปี้ยนลีคา": 2,
            "แชมป์เปี้ยนส์ลีคะ": 2, "แชมป์เปี้ยนลีคะ": 2, "แชมเปี้ยนลีคะ": 2,
            "แชมป์เปี้ยนลีคำ": 2, "แชมเปี้ยนลีคำ": 2, "แชมป์เปี้ยนส์ลีคำ": 2,
            "แชมป์เปี้ยนส์ลีกา": 2, "แชมป์เปี้ยนลีกา": 2, "แชมเปี้ยนลีกา": 2,
            "แชมป์เปี้ยนลีกะ": 2, "แชมเปี้ยนลีกะ": 2, "แชมป์เปี้ยนส์ลีกะ": 2,
            "แชมป์เปี้ยนลีกำ": 2, "แชมเปี้ยนลีกำ": 2, "แชมป์เปี้ยนส์ลีกำ": 2,
            "champions league": 2, "ucl": 2, "champions": 2, "cl": 2,
            "แชมป์เปี้ยนส์": 2, "แชมป์เปี้ยน": 2, "แชมเปี้ยน": 2,
            "ยูซีแอล": 2, "ยูเอฟ่าแชมป์เปี้ยน": 2, "ยูซีเอล": 2, "ยูซีเอ": 2,
            "ยูฟ่า": 2, "ยูเอฟ่า": 2, "แชมเปี้ยนส์": 2, "แชมป์": 2,
            "ชปล": 2, "ชปลีก": 2, "ชล": 2, "ยูฟ่าชปล": 2, "ยูฟ่าชล": 2,
            
            # Europa League - เพิ่มเติม (รวมการพิมพ์ผิด)
            "ยูโรป้าลีก": 3, "ยูโรป้า": 3, "ยูโรปา": 3, "ยูโรป่า": 3,
            "ยูโรป้าลีค": 3, "ยูโรป้าลีคา": 3, "ยูโรป้าลีคะ": 3,
            "ยูโรป้าลีคำ": 3, "ยูโรป้าลีกา": 3, "ยูโรป้าลีกะ": 3,
            "ยูโรป้าลีกำ": 3, "ยูโรป้าลีกาา": 3, "ยูโรป้าลีคาา": 3,
            "ยูโรปาลีก": 3, "ยูโรปาลีค": 3, "ยูโรปาลีคา": 3,
            "ยูโรปาลีคะ": 3, "ยูโรปาลีคำ": 3, "ยูโรปาลีกา": 3,
            "ยูโรปาลีกะ": 3, "ยูโรปาลีกำ": 3, "ยูโรปาลีกาา": 3,
            "ยูโรป่าลีก": 3, "ยูโรป่าลีค": 3, "ยูโรป่าลีคา": 3,
            "ยูโรป่าลีคะ": 3, "ยูโรป่าลีคำ": 3, "ยูโรป่าลีกา": 3,
            "europa league": 3, "europa": 3, "uel": 3, "el": 3,
            "ยูโรปะ": 3, "ยูโรปาลีก": 3, "ยูโรป่าลีก": 3,
            "ยูโรป่าลีค": 3, "ยุโรป": 3, "ยูโรป": 3, "ยูโรปป": 3,
            "ยูโรป้": 3, "ยูโรป่": 3, "ยูโรป๋": 3, "ยูโรป๊": 3,
            
            # เพิ่มลีกอื่นๆ พร้อมการพิมพ์ผิด
            # Thai League
            "ไทยลีก": 253, "ไทย": 253, "ไทยลีค": 253, "ไทยลีกา": 253,
            "ไทยลีกะ": 253, "ไทยลีกำ": 253, "ไทยลีกาา": 253, "ไทยลีคา": 253,
            "ไทยลีคะ": 253, "ไทยลีคำ": 253, "ไทยลีคาา": 253, "ไทยลีกก": 253,
            "thai league": 253, "thailand": 253, "thai": 253, "tl": 253,
            "ลีกไทย": 253, "ลีคไทย": 253, "ลีกาไทย": 253, "ลีคาไทย": 253,
            "ลีกะไทย": 253, "ลีกำไทย": 253, "ลีกไทยลีก": 253,
            
            # J League (Japan)
            "เจลีก": 188, "เจลีค": 188, "เจลีกา": 188, "เจลีกะ": 188,
            "เจลีกำ": 188, "เจลีกาา": 188, "เจลีคา": 188, "เจลีคะ": 188,
            "เจลีคำ": 188, "เจลีคาา": 188, "เจลีคค": 188, "เจลีกก": 188,
            "ญี่ปุ่น": 188, "ญี่ปุ่นลีก": 188, "ญี่ปุ่นลีค": 188, "ญี่ปุ่นลีกา": 188,
            "ญี่ปุ่นลีกะ": 188, "ญี่ปุ่นลีกำ": 188, "ญี่ปุ่นลีกาา": 188,
            "ญี่ปุ่นลีคา": 188, "ญี่ปุ่นลีคะ": 188, "ญี่ปุ่นลีคำ": 188,
            "japan": 188, "j league": 188, "j1": 188, "j1 league": 188,
            "japanese": 188, "japan league": 188, "nippon": 188,
            "ลีกญี่ปุ่น": 188, "ลีคญี่ปุ่น": 188, "ลีกาญี่ปุ่น": 188,
            
            # K League (Korea)
            "เคลีก": 292, "เคลีค": 292, "เคลีกา": 292, "เคลีกะ": 292,
            "เคลีกำ": 292, "เคลีกาา": 292, "เคลีคา": 292, "เคลีคะ": 292,
            "เคลีคำ": 292, "เคลีคาา": 292, "เคลีคค": 292, "เคลีกก": 292,
            "เกาหลี": 292, "เกาหลีลีก": 292, "เกาหลีลีค": 292, "เกาหลีลีกา": 292,
            "เกาหลีลีกะ": 292, "เกาหลีลีกำ": 292, "เกาหลีลีกาา": 292,
            "เกาหลีลีคา": 292, "เกาหลีลีคะ": 292, "เกาหลีลีคำ": 292,
            "korea": 292, "k league": 292, "k1": 292, "k1 league": 292,
            "korean": 292, "korea league": 292, "south korea": 292,
            "ลีกเกาหลี": 292, "ลีคเกาหลี": 292, "ลีกาเกาหลี": 292,
            
            # Turkish Super League
            "ซุปเปอร์ลีก": 203, "ซุปเปอร์ลีค": 203, "ซุปเปอร์ลีกา": 203,
            "ซุปเปอร์ลีกะ": 203, "ซุปเปอร์ลีกำ": 203, "ซุปเปอร์ลีกาา": 203,
            "ซุปเปอร์ลีคา": 203, "ซุปเปอร์ลีคะ": 203, "ซุปเปอร์ลีคำ": 203,
            "ซุปเปอลีก": 203, "ซุปเปอลีค": 203, "ซุปเปอลีกา": 203,
            "ซุปเปอลีกะ": 203, "ซุปเปอลีกำ": 203, "ซุปเปอลีกาา": 203,
            "ซูปเปอร์ลีก": 203, "ซูปเปอร์ลีค": 203, "ซูปเปอร์ลีกา": 203,
            "ตุรกี": 203, "ตุรกีลีก": 203, "ตุรกีลีค": 203, "ตุรกีลีกา": 203,
            "ตุรกีลีกะ": 203, "ตุรกีลีกำ": 203, "ตุรกีลีกาา": 203,
            "turkey": 203, "turkish": 203, "super lig": 203, "super league": 203,
            "ลีกตุรกี": 203, "ลีคตุรกี": 203, "ลีกาตุรกี": 203,
            
            # Russian Premier League
            "พรีเมียร์ลีกรัสเซีย": 235, "พรีเมียร์ลีครัสเซีย": 235,
            "พรีเมียร์ลีการัสเซีย": 235, "พรีเมียร์ลีกะรัสเซีย": 235,
            "พรีเมียร์ลีกำรัสเซีย": 235, "พรีเมียร์ลีกาารัสเซีย": 235,
            "ปรีเมียลีกรัสเซีย": 235, "ปรีเมียลีครัสเซีย": 235,
            "ปรีเมียลีการัสเซีย": 235, "ปรีเมียลีกะรัสเซีย": 235,
            "รัสเซีย": 235, "รัสเซียลีก": 235, "รัสเซียลีค": 235,
            "รัสเซียลีกา": 235, "รัสเซียลีกะ": 235, "รัสเซียลีกำ": 235,
            "รัสเซียลีกาา": 235, "รัสเซียลีคา": 235, "รัสเซียลีคะ": 235,
            "russia": 235, "russian": 235, "rpl": 235, "russia league": 235,
            "ลีกรัสเซีย": 235, "ลีครัสเซีย": 235, "ลีการัสเซีย": 235,
            
            # Netherlands Eredivisie
            "เออร์ดิวิซี": 88, "เออร์ดิวิซี่": 88, "เออร์ดิวิซี้": 88,
            "เออร์ดิวิซีย์": 88, "เออร์ดิวิซีี": 88, "เออร์ดิวิซีา": 88,
            "เออร์ดิวิซีิ": 88, "เออร์ดิวิซีส": 88, "เออร์ดิวิซีค": 88,
            "เออดิวิซี": 88, "เออดิวิซี่": 88, "เออดิวิซี้": 88,
            "เออดิวิซีย์": 88, "เออดิวิซีี": 88, "เออดิวิซีา": 88,
            "เนเธอร์แลนด์": 88, "เนเธอร์แลนด์ลีก": 88, "เนเธอร์แลนด์ลีค": 88,
            "เนเธอร์แลนด์ลีกา": 88, "เนเธอร์แลนด์ลีกะ": 88, "เนเธอร์แลนด์ลีกำ": 88,
            "เนเธอร์แลนด์ลีกาา": 88, "เนเธอร์แลนด์ลีคา": 88, "เนเธอร์แลนด์ลีคะ": 88,
            "netherlands": 88, "dutch": 88, "eredivisie": 88, "holland": 88,
            "ลีกเนเธอร์แลนด์": 88, "ลีคเนเธอร์แลนด์": 88, "ลีกาเนเธอร์แลนด์": 88,
            
            # Belgium Jupiler Pro League
            "จูปิแลร์ลีก": 144, "จูปิแลร์ลีค": 144, "จูปิแลร์ลีกา": 144,
            "จูปิแลร์ลีกะ": 144, "จูปิแลร์ลีกำ": 144, "จูปิแลร์ลีกาา": 144,
            "จูปิแลร์ลีคา": 144, "จูปิแลร์ลีคะ": 144, "จูปิแลร์ลีคำ": 144,
            "จูปิแลลีก": 144, "จูปิแลลีค": 144, "จูปิแลลีกา": 144,
            "จูปิแลลีกะ": 144, "จูปิแลลีกำ": 144, "จูปิแลลีกาา": 144,
            "จูปิลาร์ลีก": 144, "จูปิลาร์ลีค": 144, "จูปิลาร์ลีกา": 144,
            "เบลเยี่ยม": 144, "เบลเยี่ยมลีก": 144, "เบลเยี่ยมลีค": 144,
            "เบลเยี่ยมลีกา": 144, "เบลเยี่ยมลีกะ": 144, "เบลเยี่ยมลีกำ": 144,
            "เบลเยี่ยมลีกาา": 144, "เบลเยี่ยมลีคา": 144, "เบลเยี่ยมลีคะ": 144,
            "belgium": 144, "belgian": 144, "jupiler": 144, "pro league": 144,
            "ลีกเบลเยี่ยม": 144, "ลีคเบลเยี่ยม": 144, "ลีกาเบลเยี่ยม": 144,
            
            # Portugal Primeira Liga
            "ไพร์เมียร์ลีก": 94, "ไพร์เมียร์ลีค": 94, "ไพร์เมียร์ลีกา": 94,
            "ไพร์เมียร์ลีกะ": 94, "ไพร์เมียร์ลีกำ": 94, "ไพร์เมียร์ลีกาา": 94,
            "ไพร์เมียร์ลีคา": 94, "ไพร์เมียร์ลีคะ": 94, "ไพร์เมียร์ลีคำ": 94,
            "ไพรเมียร์ลีก": 94, "ไพรเมียร์ลีค": 94, "ไพรเมียร์ลีกา": 94,
            "ไพรเมียร์ลีกะ": 94, "ไพรเมียร์ลีกำ": 94, "ไพรเมียร์ลีกาา": 94,
            "ไพรม์เมียร์ลีก": 94, "ไพรม์เมียร์ลีค": 94, "ไพรม์เมียร์ลีกา": 94,
            "โปรตุเกส": 94, "โปรตุเกสลีก": 94, "โปรตุเกสลีค": 94,
            "โปรตุเกสลีกา": 94, "โปรตุเกสลีกะ": 94, "โปรตุเกสลีกำ": 94,
            "โปรตุเกสลีกาา": 94, "โปรตุเกสลีคา": 94, "โปรตุเกสลีคะ": 94,
            "portugal": 94, "portuguese": 94, "primeira": 94, "primeira liga": 94,
            "ลีกโปรตุเกส": 94, "ลีคโปรตุเกส": 94, "ลีกาโปรตุเกส": 94,
            
            # Additional Popular Leagues พร้อมการพิมพ์ผิด
            # Brazilian Serie A
            "บราซิล": 71, "บราซิลลีก": 71, "บราซิลลีค": 71, "บราซิลลีกา": 71,
            "บราซิลลีกะ": 71, "บราซิลลีกำ": 71, "บราซิลลีกาา": 71,
            "บราซิลลีคา": 71, "บราซิลลีคะ": 71, "บราซิลลีคำ": 71,
            "บราซิลเซเรียอา": 71, "บราซิลเซเรียอะ": 71, "บราซิลเซเรียอ": 71,
            "บราซิลซีเรียอา": 71, "บราซิลซีเรียอะ": 71, "บราซิลซีเรียอ": 71,
            "brazil": 71, "brazilian": 71, "serie a brazil": 71, "campeonato brasileiro": 71,
            "ลีกบราซิล": 71, "ลีคบราซิล": 71, "ลีกาบราซิล": 71,
            
            # Argentine Primera Division
            "อาร์เจนตินา": 128, "อาร์เจนตินาลีก": 128, "อาร์เจนตินาลีค": 128,
            "อาร์เจนตินาลีกา": 128, "อาร์เจนตินาลีกะ": 128, "อาร์เจนตินาลีกำ": 128,
            "อาร์เจนตินาลีกาา": 128, "อาร์เจนตินาลีคา": 128, "อาร์เจนตินาลีคะ": 128,
            "อาร์เจนติน่า": 128, "อาร์เจนติน่าลีก": 128, "อาร์เจนติน่าลีค": 128,
            "อาร์เจนติน่าลีกา": 128, "อาร์เจนติน่าลีกะ": 128, "อาร์เจนติน่าลีกำ": 128,
            "argentina": 128, "argentine": 128, "primera division": 128, "liga argentina": 128,
            "ลีกอาร์เจนตินา": 128, "ลีคอาร์เจนตินา": 128, "ลีกาอาร์เจนตินา": 128,
            
            # MLS (Major League Soccer)
            "เอ็มแอลเอส": 253, "เอ็มแอลเอส": 253, "เอ็มแอลเอสส์": 253,
            "เอ็มแอลเอสซ์": 253, "เอ็มแอลเอสส": 253, "เอ็มแอลเอสท์": 253,
            "เอ็มแอลเอสด์": 253, "เอ็มแอลเอสค์": 253, "เอ็มแอลเอสก์": 253,
            "เอ็มแอลเอสลีก": 253, "เอ็มแอลเอสลีค": 253, "เอ็มแอลเอสลีกา": 253,
            "อเมริกา": 253, "อเมริกาลีก": 253, "อเมริกาลีค": 253,
            "อเมริกาลีกา": 253, "อเมริกาลีกะ": 253, "อเมริกาลีกำ": 253,
            "mls": 253, "major league soccer": 253, "usa": 253, "america": 253,
            "ลีกอเมริกา": 253, "ลีคอเมริกา": 253, "ลีกาอเมริกา": 253,
            
            # Saudi Pro League
            "ซาอุดิอาระเบีย": 307, "ซาอุดิอาระเบียลีก": 307, "ซาอุดิอาระเบียลีค": 307,
            "ซาอุดิอาระเบียลีกา": 307, "ซาอุดิอาระเบียลีกะ": 307, "ซาอุดิอาระเบียลีกำ": 307,
            "ซาอุดิอาระเบียลีกาา": 307, "ซาอุดิอาระเบียลีคา": 307, "ซาอุดิอาระเบียลีคะ": 307,
            "ซาอุดิ": 307, "ซาอุดิลีก": 307, "ซาอุดิลีค": 307,
            "ซาอุดิลีกา": 307, "ซาอุดิลีกะ": 307, "ซาอุดิลีกำ": 307,
            "ซาอุฯ": 307, "ซาอุฯลีก": 307, "ซาอุฯลีค": 307,
            "saudi": 307, "saudi arabia": 307, "pro league": 307, "spl": 307,
            "ลีกซาอุดิ": 307, "ลีคซาอุดิ": 307, "ลีกาซาอุดิ": 307,
            
            # Chinese Super League
            "จีน": 169, "จีนลีก": 169, "จีนลีค": 169, "จีนลีกา": 169,
            "จีนลีกะ": 169, "จีนลีกำ": 169, "จีนลีกาา": 169,
            "จีนลีคา": 169, "จีนลีคะ": 169, "จีนลีคำ": 169,
            "จีนซุปเปอร์ลีก": 169, "จีนซุปเปอร์ลีค": 169, "จีนซุปเปอร์ลีกา": 169,
            "จีนซุปเปอร์ลีกะ": 169, "จีนซุปเปอร์ลีกำ": 169, "จีนซุปเปอร์ลีกาา": 169,
            "china": 169, "chinese": 169, "super league": 169, "csl": 169,
            "ลีกจีน": 169, "ลีคจีน": 169, "ลีกาจีน": 169,
            
            # Indian Super League
            "อินเดีย": 323, "อินเดียลีก": 323, "อินเดียลีค": 323,
            "อินเดียลีกา": 323, "อินเดียลีกะ": 323, "อินเดียลีกำ": 323,
            "อินเดียลีกาา": 323, "อินเดียลีคา": 323, "อินเดียลีคะ": 323,
            "อินเดียซุปเปอร์ลีก": 323, "อินเดียซุปเปอร์ลีค": 323, "อินเดียซุปเปอร์ลีกา": 323,
            "อินเดียซุปเปอร์ลีกะ": 323, "อินเดียซุปเปอร์ลีกำ": 323, "อินเดียซุปเปอร์ลีกาา": 323,
            "india": 323, "indian": 323, "isl": 323, "indian super league": 323,
            "ลีกอินเดีย": 323, "ลีคอินเดีย": 323, "ลีกาอินเดีย": 323,
            
            # Australian A-League
            "ออสเตรเลีย": 188, "ออสเตรเลียลีก": 188, "ออสเตรเลียลีค": 188,
            "ออสเตรเลียลีกา": 188, "ออสเตรเลียลีกะ": 188, "ออสเตรเลียลีกำ": 188,
            "ออสเตรเลียลีกาา": 188, "ออสเตรเลียลีคา": 188, "ออสเตรเลียลีคะ": 188,
            "ออสเตรเลียเอลีก": 188, "ออสเตรเลียเอลีค": 188, "ออสเตรเลียเอลีกา": 188,
            "ออสเตรเลียเอลีกะ": 188, "ออสเตรเลียเอลีกำ": 188, "ออสเตรเลียเอลีกาา": 188,
            "australia": 188, "australian": 188, "a-league": 188, "aleague": 188,
            "ลีกออสเตรเลีย": 188, "ลีคออสเตรเลีย": 188, "ลีกาออสเตรเลีย": 188
        }
        
        msg = user_message.lower().strip()
        
        # Direct match check
        for key, league_id in league_map.items():
            if key in msg:
                return league_id
        
        # Fuzzy matching
        try:
            best, score, _ = process.extractOne(msg, league_map.keys(), scorer=fuzz.partial_ratio)
            if score >= 60:
                return league_map[best]
        except:
            pass
        
        # Default to Premier League
        return 39
    
    def get_today_fixtures(self) -> str:
        """ดึงโปรแกรมการแข่งขันวันนี้และแปลงเป็น HTML"""
        try:
            print("🔍 Getting today's fixtures...")
            
            data = self.football_api.get_today_fixtures()
            
            if not data or 'response' not in data or not data['response']:
                return "<div class='no-matches'>📅 ไม่มีการแข่งขันในวันนี้</div>"
            
            fixtures = data['response']
            print(f"✅ Found {len(fixtures)} fixtures for today")
            
            # สร้าง HTML
            html = f"""
            <div class="fixtures-container">
                <div class="fixtures-header">
                    <h3>📅 โปรแกรมการแข่งขันวันนี้</h3>
                    <p>{self._get_today_date()}</p>
                </div>
                <div class="fixtures-table">
                    <table>
                        <thead>
                            <tr>
                                <th>เวลา</th>
                                <th>ลีก</th>
                                <th>ทีมเหย้า</th>
                                <th>vs</th>
                                <th>ทีมเยือน</th>
                                <th>สถานะ</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for fixture in fixtures:
                try:
                    fixture_time = self._format_fixture_time(fixture['fixture']['date'])
                    league_name = fixture['league']['name']
                    home_team = fixture['teams']['home']['name']
                    away_team = fixture['teams']['away']['name']
                    status = self._get_fixture_status(fixture['fixture']['status'])
                    
                    # คะแนน (ถ้ามี)
                    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else ""
                    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else ""
                    
                    vs_text = "vs"
                    if home_score != "" and away_score != "":
                        vs_text = f"{home_score} - {away_score}"
                    
                    html += f"""
                        <tr>
                            <td class="time">{fixture_time}</td>
                            <td class="league">{league_name}</td>
                            <td class="home-team">{home_team}</td>
                            <td class="score">{vs_text}</td>
                            <td class="away-team">{away_team}</td>
                            <td class="status">{status}</td>
                        </tr>
                    """
                except Exception as e:
                    print(f"⚠️ Error processing fixture: {e}")
                    continue
            
            html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Error in get_today_fixtures: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงโปรแกรมการแข่งขัน: {str(e)}</div>"
    
    def _get_today_date(self) -> str:
        """ได้วันที่วันนี้"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y")
    
    def _format_fixture_time(self, date_str: str) -> str:
        """แปลงเวลาแมตช์"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%H:%M")
        except:
            return "TBD"
    
    def _get_fixture_status(self, status_data: dict) -> str:
        """แปลงสถานะแมตช์"""
        status_map = {
            'TBD': 'รอกำหนด',
            'NS': 'ยังไม่เริ่ม', 
            '1H': 'ครึ่งแรก',
            'HT': 'พักครึ่ง',
            '2H': 'ครึ่งหลัง',
            'ET': 'เวลาพิเศษ',
            'FT': 'จบแล้ว',
            'AET': 'จบในเวลาพิเศษ',
            'PEN': 'จุดโทษ',
            'SUSP': 'ถูกระงับ',
            'INT': 'ขัดจังหวะ',
            'CANC': 'ยกเลิก',
            'ABD': 'ยกเลิก',
            'AWD': 'ตัดสิน',
            'WO': 'ชนะโดยไม่ต้องแข่ง'
        }
        
        short_status = status_data.get('short', 'TBD')
        return status_map.get(short_status, short_status)
    
    def analyze_message(self, user_message: str) -> str:
        """วิเคราะห์ข้อความผู้ใช้และตอบกลับ"""
        try:
            msg = user_message.lower().strip()
            print(f"🔍 Analyzing message: '{msg}'")

            # ตรวจสอบคำขอรายชื่อนักเตะ เช่น "นักเตะ", "squad", "รายชื่อ", "player list", "รายชื่อนักเตะ"
            squad_keywords = ["นักเตะ", "squad", "รายชื่อ", "player list", "รายชื่อนักเตะ"]
            if any(keyword in msg for keyword in squad_keywords):
                teams = self._extract_teams_from_message(msg)
                if teams:
                    team = teams[0]
                    team_en = self.thai_team_map.get(team, team)
                    print(f"🔍 Detected: Squad request for {team} (mapped: {team_en})")
                    result = self.get_team_squad_html(team_en)
                    if result and not result.startswith("❌"):
                        return result
                    # fallback
                    return self.ask_openai_fallback(user_message)
                else:
                    return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอฟอร์มทีม 5 นัดหลังสุด เช่น "แมนยู 5 นัดหลังสุด", "ฟอร์มแมนยู", "recent form", "last 5 matches"
            form_keywords = ["5 นัดหลังสุด", "ฟอร์ม", "recent form", "last 5 matches", "ฟอร์มล่าสุด", "form ล่าสุด", "ฟอร์มทีม", "team form"]
            if any(keyword in msg for keyword in form_keywords):
                teams = self._extract_teams_from_message(msg)
                if teams:
                    team = teams[0]
                    team_en = self.thai_team_map.get(team, team)
                    print(f"🔍 Detected: Team form request for {team} (mapped: {team_en})")
                    result = self.get_team_real_form(team_en, last=5)
                    if result and not result.startswith("❌"):
                        return result
                    return self.ask_openai_fallback(user_message)
                else:
                    return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอทำนายผลบอลก่อน (ให้ความสำคัญสูงสุด)
            if any(keyword in msg for keyword in ['ทำนาย', 'predict', 'prediction', 'พยากรณ์', 'คาดการณ์', 'วิเคราะห์ผล']):
                print("🔍 Detected: Match prediction request")
                result = self.predict_match_result(msg)
                if result and not result.startswith("❌"):
                    return result
                return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอเปรียบเทียบทีม เช่น แมนยู vs ลิเวอร์พูล หรือ เปรียบเทียบ แมนยู กับ ลิเวอร์พูล
            if any(keyword in msg for keyword in ['เปรียบเทียบ', 'compare', 'vs', 'กับ']):
                teams = self._extract_teams_from_message(msg)
                if len(teams) == 2:
                    print(f"🔍 Detected: Compare teams request: {teams[0]} vs {teams[1]}")
                    result = self.compare_teams_form(teams[0], teams[1], count=5)
                    if result and not result.startswith("❌"):
                        return result
                    return self.ask_openai_fallback(user_message)
                else:
                    return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอผลบอล/โปรแกรมการแข่งขัน (ไม่รวม 'ข่าว' และ 'บอลวันนี้' เพื่อป้องกันชนกับ intent ข่าว)
            if any(keyword in msg for keyword in ['ผลบอล', 'โปรแกรม', 'แมตช์', 'แข่ง', 'fixture', 'match', 'game', 'ตารางแข่ง']) or (
                'บอลวันนี้' in msg and not any(news_kw in msg for news_kw in ['ข่าว', 'news', 'ข่าวสาร', 'อัพเดท', 'ข่าววันนี้'])):
                print("🔍 Detected: Fixtures/Results request")
                result = self.get_today_fixtures()
                if result and not result.startswith("❌"):
                    return result
                return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอตารางคะแนน
            if any(keyword in msg for keyword in [
                'ตารางคะแนน', 'ตาราง', 'standings', 'table',
                'อันดับ', 'อันดับที่', 'อันดับเท่าไหร่', 'อยู่อันดับ', 'อันดับที่เท่าไหร่', 'rank', 'ranking', 'position']):
                print("🔍 Detected: Standings request")
                league_id = self.extract_league_id(msg)
                league_name = self.get_league_name_from_message(msg)
                print(f"🔍 League detected: {league_name} (ID: {league_id})")
                result = self.get_standings_table(league_id)
                if result and not result.startswith("❌"):
                    return result
                return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอดาวซัลโว
            if any(keyword in msg for keyword in ['ดาวซัลโว', 'ดาวยิง', 'topscorer', 'top scorer', 'goalscorer']):
                print("🔍 Detected: Top scorers request")
                league_id = self.extract_league_id(msg)
                league_name = self.get_league_name_from_message(msg)
                print(f"🔍 League detected: {league_name} (ID: {league_id})")
                result = self.get_topscorers_table(league_id)
                if result and not result.startswith("❌"):
                    return result
                return self.ask_openai_fallback(user_message)

            # ตรวจสอบคำขอข่าวฟุตบอล (เฉพาะคำที่เกี่ยวกับข่าวโดยตรง ไม่รวม 'บอลวันนี้')
            if any(keyword in msg for keyword in ['ข่าว', 'news', 'ข่าวสาร', 'อัพเดท', 'ข่าววันนี้']):
                print("🔍 Detected: News request")
                result = self.news_manager.generate_news_response(msg)
                if result and not result.startswith("<div class='error'>") and 'ไม่พบ' not in result:
                    return result
                return self.ask_openai_fallback(user_message)

            # ถ้าเป็น keyword เดียว (เช่น "โรนัลโด้") หรือข้อความที่ไม่มีในระบบ ให้ใช้ OpenAI ตอบทันที
            if len(msg.split()) == 1:
                print("🔍 Detected: Single keyword, fallback to OpenAI")
                return self.ask_openai_fallback(user_message)

            # ถ้าไม่ใช่คำขอที่เฉพาะเจาะจง ให้ส่งไปยัง news manager
            print("🔍 Detected: General query, forwarding to news manager")
            result = self.news_manager.generate_news_response(msg)
            if result and not result.startswith("<div class='error'>") and 'ไม่พบ' not in result:
                return result
            return self.ask_openai_fallback(user_message)

        except Exception as e:
            print(f"❌ Error in analyze_message: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการวิเคราะห์ข้อความ: {str(e)}</div>"
    def get_standings_table(self, league_id: int, season: int = 2024) -> str:
        """ดึงตารางคะแนนและแปลงเป็น HTML"""
        try:
            print(f"🔍 Getting standings for league_id: {league_id}, season: {season}")
            
            data = self.football_api.get_standings(league_id, season)
            
            if not data or 'response' not in data or not data['response']:
                return f"<div class='error'>ไม่สามารถดึงข้อมูลตารางคะแนนได้ (League ID: {league_id})</div>"
            
            league_data = data['response'][0]
            league_name = league_data['league']['name']
            standings = league_data['league']['standings'][0]
            
            print(f"✅ Successfully retrieved standings for: {league_name}")
            
            # สร้าง HTML Table แบบสวยงาม
            html = f"""
            <div class="standings-container">
                <div class="standings-header">
                    <h3>🏆 ตารางคะแนน {league_name}</h3>
                    <p>ฤดูกาล {season}</p>
                </div>
                <div class="standings-table">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>ทีม</th>
                                <th>เล่น</th>
                                <th>ชนะ</th>
                                <th>เสมอ</th>
                                <th>แพ้</th>
                                <th>ได้</th>
                                <th>เสีย</th>
                                <th>ต่าง</th>
                                <th>คะแนน</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for team in standings:
                rank = team['rank']
                team_name = team['team']['name']
                team_logo = team['team']['logo']
                played = team['all']['played']
                wins = team['all']['win']
                draws = team['all']['draw']
                losses = team['all']['lose']
                goals_for = team['all']['goals']['for']
                goals_against = team['all']['goals']['against']
                goal_diff = goals_for - goals_against
                points = team['points']
                
                html += f"""
                            <tr>
                                <td style="text-align: center; font-weight: bold;">{rank}</td>
                                <td class="team-cell">
                                    <img src="{team_logo}" alt="{team_name}" class="team-logo" 
                                         onerror="console.log('Logo failed for {team_name}:', this.src); this.style.display='none';" 
                                         onload="console.log('Logo loaded for {team_name}:', this.src);">
                                    <span class="team-name">{team_name}</span>
                                </td>
                                <td>{played}</td>
                                <td>{wins}</td>
                                <td>{draws}</td>
                                <td>{losses}</td>
                                <td>{goals_for}</td>
                                <td>{goals_against}</td>
                                <td class="{'positive' if goal_diff > 0 else 'negative' if goal_diff < 0 else 'neutral'}">{goal_diff:+d}</td>
                                <td class="points-cell">{points}</td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Error in get_standings_table: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงตารางคะแนน: {str(e)}</div>"
    
    def get_topscorers_table(self, league_id: int, season: int = 2024) -> str:
        """ดึงข้อมูลดาวซัลโวและแปลงเป็น HTML"""
        try:
            print(f"🔍 Getting top scorers for league_id: {league_id}, season: {season}")
            
            data = self.football_api.get_topscorers(league_id, season)
            
            if not data or 'response' not in data or not data['response']:
                return f"<div class='error'>ไม่สามารถดึงข้อมูลดาวซัลโวได้ (League ID: {league_id})</div>"
            
            players = data['response']
            
            # สร้าง HTML Table
            html = f"""
            <div class="topscorers-container">
                <div class="topscorers-header">
                    <h3>⚽ ดาวซัลโว</h3>
                    <p>ฤดูกาล {season}</p>
                </div>
                <div class="topscorers-table">
                    <table>
                        <thead>
                            <tr>
                                <th>อันดับ</th>
                                <th>นักเตะ</th>
                                <th>ทีม</th>
                                <th>ประตู</th>
                                <th>แอสซิสต์</th>
                                <th>เล่น</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for index, player_data in enumerate(players[:20], 1):  # แสดงแค่ 20 อันดับแรก
                player = player_data['player']
                statistics = player_data['statistics'][0]
                
                name = player['name']
                team = statistics['team']['name']
                goals = statistics['goals']['total'] or 0
                assists = statistics['goals']['assists'] or 0
                appearances = statistics['games']['appearences'] or 0
                
                html += f"""
                            <tr>
                                <td>{index}</td>
                                <td class="player-name">{name}</td>
                                <td class="team-name">{team}</td>
                                <td class="goals">{goals}</td>
                                <td>{assists}</td>
                                <td>{appearances}</td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Error in get_topscorers_table: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงข้อมูลดาวซัลโว: {str(e)}</div>"
    
    def predict_match_result(self, user_message: str) -> str:
        """ทำนายผลการแข่งขัน"""
        try:
            print(f"🔮 Predicting match result for: '{user_message}'")
            
            # แยกชื่อทีมจากข้อความ
            teams = self._extract_teams_from_message(user_message)
            
            if len(teams) < 2:
                return self._get_upcoming_matches_prediction()
            
            team1, team2 = teams[0], teams[1]
            
            # ดึงข้อมูลฟอร์มทีม
            team1_form = self._get_team_recent_form(team1)
            team2_form = self._get_team_recent_form(team2)
            
            # วิเคราะห์และทำนาย
            prediction = self._analyze_and_predict(team1, team2, team1_form, team2_form)
            
            return prediction
            
        except Exception as e:
            print(f"❌ Error in predict_match_result: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการทำนายผล: {str(e)}</div>"
    
    def _extract_teams_from_message(self, message: str) -> List[str]:
        """แยกชื่อทีมจากข้อความ"""
        # รายการทีมยอดนิยมทุกลีก
        popular_teams = [
            # Bundesliga
            "บาเยิร์น", "bayern", "bayern munich", "บาเยิร์น มิวนิค", "เสือใต้", "บาเยิน",
            "ดอร์ทมุนด์", "borussia dortmund", "ผึ้งเหลือง", "บีวีบี",
            "ไลป์ซิก", "rb leipzig", "ไลป์ซิก",
            "เลเวอร์คูเซ่น", "bayer leverkusen", "เลเวอร์คูเซ่น",
            "แฟรงก์เฟิร์ต", "eintracht frankfurt", "แฟรงก์เฟิร์ต",

            # Serie A
            "ยูเวนตุส", "juventus", "ม้าลาย", "ยูเว่", "ม้าลายเก่าแก่",
            "มิลาน", "ac milan", "ปีศาจแดงดำ", "เอซีมิลาน",
            "อินเตอร์", "inter milan", "งูใหญ่", "อินเตอร์ มิลาน", "inter",
            "นาโปลี", "napoli", "ปาร์เทโนเป",
            "โรม่า", "roma", "as roma", "หมาป่ากรุงโรม",

            # Ligue 1
            "เปแอสเช", "psg", "paris sg", "paris saint-germain", "ปารีส", "ปารีสแซงต์แชร์กแมง",
            "มาร์กเซย", "marseille", "โอลิมปิก มาร์กเซย", "om",
            "ลียง", "lyon", "โอแอล",
            "โมนาโก", "monaco", "โมนาโก",
            "ลีล", "lille", "ลีล",
        ] + [
            # Premier League
            "แมนยู", "แมนฯยูไนเต็ด", "แมนฯยู", "แมน u", "man utd", "man u", "manchester united", "manchester utd", "man united", "man utd fc", "แมนยูไนเต็ด", "แมนเชสเตอร์ ยูไนเต็ด", "ปีศาจแดง", "united",
            "ลิเวอร์พูล", "liverpool", "หงส์แดง", "ลิเวอร์", "ลิเวอร์พลู", "ลิpool",
            "แมนซิตี้", "แมนฯซิตี้", "แมนซิ", "man city", "manchester city", "เรือใบ", "แมนเชสเตอร์ ซิตี้", "city",
            "อาร์เซนอล", "arsenal", "ปืนใหญ่", "อาเซนอล", "อาเซน่อล", "ars",
            "เชลซี", "chelsea", "สิงห์บลู", "สิงห์บลูส์", "เชลล์ซี", "เชลซี เอฟซี",
            "สเปอร์ส", "tottenham", "spurs", "ไก่เดือยทอง", "ท็อตแน่ม", "ท็อตแน่ม ฮ็อทสเปอร์",
            "นิวคาสเซิล", "newcastle", "นกแก้ว",
            "แอสตัน วิลลา", "aston villa", "วิลลา",
            "บรายท์ตัน", "brighton", "นกนางนวล",
            "เวสต์แฮม", "west ham", "ค้อนเหล็ก",

            # La Liga
            "เรอัลมาดริด", "real madrid", "ราชันชุดขาว", "มาดริด", "เรอัล", "เรอัล มาดริด",
            "บาร์เซโลนา", "barcelona", "บาร์ซ่า", "บาซ่า", "บาร์ซา", "บาร์เซโลน่า", "fc barcelona",
            "แอตเลติโก มาดริด", "atletico madrid", "แอตเลติโก",
            "เซบียา", "sevilla", "เซวิยา",
            "วาเลนเซีย", "valencia", "วาเลนเซีย",
            "บิลเบา", "athletic bilbao", "บิลเบา",
            "เรอัล โซเซียดาด", "real sociedad", "โซเซียดาด",
            "เบติส", "real betis", "เบติส",

            # Bundesliga
            "บาเยิร์น", "bayern", "bayern munich", "บาเยิร์น มิวนิค", "เสือใต้", "บาเยิน",
            "ดอร์ทมุนด์", "borussia dortmund", "ผึ้งเหลือง", "บีวีบี",
            "ไลป์ซิก", "rb leipzig", "ไลป์ซิก",
            "เลเวอร์คูเซ่น", "bayer leverkusen", "เลเวอร์คูเซ่น",
            "แฟรงก์เฟิร์ต", "eintracht frankfurt", "แฟรงก์เฟิร์ต",
            "โบรุสเซีย เมิ่นเชนกลาดบาค", "borussia monchengladbach", "โบรุสเซีย",
            "วูล์ฟสบวร์ก", "wolfsburg", "หมาป่า",
            "ชตุ๊ตการ์ท", "stuttgart", "ชตุ๊ตการ์ท",

            # Serie A
            "ยูเวนตุส", "juventus", "ม้าลาย", "ยูเว่", "ม้าลายเก่าแก่",
            "มิลาน", "ac milan", "ปีศาจแดงดำ", "เอซีมิลาน",
            "อินเตอร์", "inter milan", "งูใหญ่", "อินเตอร์ มิลาน", "inter",
            "นาโปลี", "napoli", "ปาร์เทโนเป",
            "โรมา", "as roma", "หมาป่ากรุงโรม",
            "ลาซิโอ", "lazio", "นกอินทรี",
            "อาตาลันตา", "atalanta", "อาตาลันตา",
            "ฟิออเรนตินา", "fiorentina", "ฟิออเรนตินา",

            # Ligue 1
            "เปแอสเช", "psg", "paris sg", "paris saint-germain", "ปารีส", "ปารีสแซงต์แชร์กแมง",
            "มาร์กเซย", "marseille", "โอลิมปิก มาร์กเซย", "om",
            "ลียง", "lyon", "โอแอล",
            "โมนาโก", "monaco", "โมนาโก",
            "ลีล", "lille", "ลีล",
            "นีซ", "nice", "นีซ",
            "รีมส์", "reims", "รีมส์",
            "เรนน์", "rennes", "เรนน์",

            # ทีมอื่นๆ ที่มีชื่อเสียง
            "อัล นาสเซอร์", "al nassr", "อัลนาสเซอร์",
            "อัล ฮิลาล", "al hilal", "อัลฮิลาล",
            "อินเตอร์ ไมอามี", "inter miami", "ไมอามี"
        ]
        
        message_lower = message.lower()
        found_teams = []
        # Exact match first
        for team in popular_teams:
            if team.lower() in message_lower:
                found_teams.append(team)
                if len(found_teams) >= 2:
                    break
        # Fuzzy match if not found
        if not found_teams:
            from rapidfuzz import process, fuzz
            best, score, _ = process.extractOne(message_lower, popular_teams, scorer=fuzz.partial_ratio)
            if score >= 70:
                found_teams.append(best)
        return found_teams[:2]
    
    def _get_team_recent_form(self, team_name: str) -> Dict:
        """ดึงฟอร์มล่าสุดของทีม (จำลอง)"""
        # ข้อมูลจำลองสำหรับการทำนาย - เพิ่มทีมให้ครบทุกลีก
        team_data = {
            # Premier League
            "แมนยู": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "form": "W-W-D-W-L"},
            "แมนซิตี้": {"wins": 4, "draws": 1, "losses": 0, "goals_for": 12, "goals_against": 2, "form": "W-W-W-D-W"},
            "ลิเวอร์พูล": {"wins": 4, "draws": 0, "losses": 1, "goals_for": 10, "goals_against": 3, "form": "W-W-L-W-W"},
            "เชลซี": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 4, "form": "W-D-L-W-D"},
            "อาร์เซนอล": {"wins": 3, "draws": 2, "losses": 0, "goals_for": 9, "goals_against": 3, "form": "W-D-W-W-D"},
            "สเปอร์ส": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 7, "goals_against": 6, "form": "L-W-D-W-L"},
            "นิวคาสเซิล": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 6, "goals_against": 3, "form": "W-W-W-D-L"},
            "แอสตัน วิลลา": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 5, "goals_against": 4, "form": "W-D-L-W-D"},
            "บรายท์ตัน": {"wins": 3, "draws": 0, "losses": 2, "goals_for": 7, "goals_against": 5, "form": "W-L-W-W-L"},
            "เวสต์แฮม": {"wins": 1, "draws": 3, "losses": 1, "goals_for": 4, "goals_against": 5, "form": "D-L-D-W-D"},
            
            # La Liga
            "เรอัลมาดริด": {"wins": 4, "draws": 1, "losses": 0, "goals_for": 11, "goals_against": 2, "form": "W-W-D-W-W"},
            "บาร์เซโลนา": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 9, "goals_against": 5, "form": "W-W-L-D-W"},
            "แอตเลติโก มาดริด": {"wins": 3, "draws": 2, "losses": 0, "goals_for": 7, "goals_against": 3, "form": "W-D-W-W-D"},
            "เซบียา": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 6, "form": "L-W-D-W-L"},
            "วาเลนเซีย": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 4, "form": "W-D-L-W-D"},
            "บิลเบา": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 4, "goals_against": 5, "form": "L-W-D-L-W"},
            "เรอัล โซเซียดาด": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "form": "W-W-D-L-W"},
            "เบติส": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 5, "form": "W-D-L-D-W"},
            
            # Bundesliga
            "บาเยิร์น": {"wins": 4, "draws": 0, "losses": 1, "goals_for": 12, "goals_against": 4, "form": "W-W-W-L-W"},
            "ดอร์ทมุนด์": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 9, "goals_against": 5, "form": "W-D-W-W-L"},
            "ไลป์ซิก": {"wins": 3, "draws": 2, "losses": 0, "goals_for": 8, "goals_against": 3, "form": "W-D-W-D-W"},
            "เลเวอร์คูเซ่น": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 7, "goals_against": 4, "form": "W-W-D-L-W"},
            "แฟรงก์เฟิร์ต": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 5, "form": "D-W-L-W-D"},
            "โบรุสเซีย": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 6, "form": "L-W-D-L-W"},
            "วูล์ฟสบวร์ก": {"wins": 1, "draws": 3, "losses": 1, "goals_for": 4, "goals_against": 4, "form": "D-L-D-W-D"},
            "ชตุ๊ตการ์ท": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 7, "form": "L-W-D-W-L"},
            
            # Serie A
            "ยูเวนตุส": {"wins": 3, "draws": 2, "losses": 0, "goals_for": 8, "goals_against": 3, "form": "W-D-W-W-D"},
            "มิลาน": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 7, "goals_against": 4, "form": "W-W-D-L-W"},
            "อินเตอร์": {"wins": 4, "draws": 1, "losses": 0, "goals_for": 10, "goals_against": 2, "form": "W-W-W-D-W"},
            "นาโปลี": {"wins": 3, "draws": 0, "losses": 2, "goals_for": 8, "goals_against": 6, "form": "W-L-W-W-L"},
            "โรมา": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 5, "form": "W-D-L-D-W"},
            "ลาซิโอ": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 6, "form": "L-W-D-W-L"},
            "อาตาลันตา": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 9, "goals_against": 5, "form": "W-W-D-L-W"},
            "ฟิออเรนตินา": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 4, "form": "W-D-L-W-D"},
            
            # Ligue 1
            "ปารีสแซงต์แชร์กแมง": {"wins": 4, "draws": 1, "losses": 0, "goals_for": 13, "goals_against": 3, "form": "W-W-W-D-W"},
            "มาร์เซย": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "form": "W-D-W-W-L"},
            "ลียง": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 5, "form": "W-D-L-D-W"},
            "โมนาโก": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 7, "goals_against": 4, "form": "W-W-D-L-W"},
            "ลีล": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 5, "goals_against": 6, "form": "L-W-D-W-L"},
            "นีซ": {"wins": 2, "draws": 2, "losses": 1, "goals_for": 5, "goals_against": 4, "form": "W-D-L-D-W"},
            "รีมส์": {"wins": 1, "draws": 3, "losses": 1, "goals_for": 4, "goals_against": 4, "form": "D-L-D-W-D"},
            "เรนน์": {"wins": 2, "draws": 1, "losses": 2, "goals_for": 6, "goals_against": 7, "form": "L-W-D-W-L"},
            
            # ทีมอื่นๆ
            "อัล นาสเซอร์": {"wins": 4, "draws": 0, "losses": 1, "goals_for": 11, "goals_against": 3, "form": "W-W-W-L-W"},
            "อัล ฮิลาล": {"wins": 5, "draws": 0, "losses": 0, "goals_for": 15, "goals_against": 1, "form": "W-W-W-W-W"},
            "อินเตอร์ ไมอามี": {"wins": 3, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "form": "W-W-D-L-W"}
        }
        
        # หาทีมที่ตรงกับชื่อที่ค้นหา
        for team_key, data in team_data.items():
            if team_key.lower() in team_name.lower() or team_name.lower() in team_key.lower():
                return data
        
        # ถ้าไม่เจอ ให้ข้อมูลเริ่มต้น
        return {"wins": 2, "draws": 2, "losses": 1, "goals_for": 6, "goals_against": 4, "form": "W-D-L-W-D"}
    
    def _analyze_and_predict(self, team1: str, team2: str, form1: Dict, form2: Dict) -> str:
        """วิเคราะห์และทำนายผล"""
        # คำนวณคะแนนฟอร์ม
        team1_points = form1["wins"] * 3 + form1["draws"] * 1
        team2_points = form2["wins"] * 3 + form2["draws"] * 1
        
        # คำนวณอัตราส่วนประตู
        team1_goal_ratio = form1["goals_for"] / max(form1["goals_against"], 1)
        team2_goal_ratio = form2["goals_for"] / max(form2["goals_against"], 1)
        
        # ทำนายผล
        if team1_points > team2_points + 3:
            prediction = f"{team1} ชนะ"
            confidence = "สูง"
            score_prediction = "2-0 หรือ 2-1"
        elif team2_points > team1_points + 3:
            prediction = f"{team2} ชนะ"
            confidence = "สูง"
            score_prediction = "0-2 หรือ 1-2"
        elif abs(team1_points - team2_points) <= 1:
            prediction = "เสมอ"
            confidence = "ปานกลาง"
            score_prediction = "1-1 หรือ 2-2"
        else:
            winner = team1 if team1_points > team2_points else team2
            prediction = f"{winner} ชนะ"
            confidence = "ปานกลาง"
            score_prediction = "1-0 หรือ 2-1"
        
        # สร้าง HTML การทำนาย
        html = f"""
        <div class="prediction-container">
            <div class="prediction-header">
                <h3>🔮 การทำนายผลการแข่งขัน</h3>
                <p>{team1} 🆚 {team2}</p>
            </div>
            
            <div class="prediction-result">
                <div class="main-prediction">
                    <h4>🎯 ผลทำนาย: <span class="prediction-text">{prediction}</span></h4>
                    <p class="confidence">ความมั่นใจ: {confidence}</p>
                    <p class="score-prediction">คะแนนที่คาดหวัง: {score_prediction}</p>
                </div>
            </div>
            
            <div class="team-analysis">
                <div class="team-stats">
                    <h5>📊 ฟอร์ม {team1}</h5>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">ชนะ:</span>
                            <span class="stat-value">{form1["wins"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">เสมอ:</span>
                            <span class="stat-value">{form1["draws"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">แพ้:</span>
                            <span class="stat-value">{form1["losses"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ประตูได้:</span>
                            <span class="stat-value">{form1["goals_for"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ประตูเสีย:</span>
                            <span class="stat-value">{form1["goals_against"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ฟอร์ม:</span>
                            <span class="stat-value">{form1["form"]}</span>
                        </div>
                    </div>
                </div>
                
                <div class="team-stats">
                    <h5>📊 ฟอร์ม {team2}</h5>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">ชนะ:</span>
                            <span class="stat-value">{form2["wins"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">เสมอ:</span>
                            <span class="stat-value">{form2["draws"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">แพ้:</span>
                            <span class="stat-value">{form2["losses"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ประตูได้:</span>
                            <span class="stat-value">{form2["goals_for"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ประตูเสีย:</span>
                            <span class="stat-value">{form2["goals_against"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">ฟอร์ม:</span>
                            <span class="stat-value">{form2["form"]}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="prediction-disclaimer">
                <p>⚠️ <strong>คำเตือน:</strong> การทำนายนี้อิงจากข้อมูลทางสถิติและไม่สามารถรับประกันความแม่นยำได้ 100%</p>
                <p>🎲 ฟุตบอลเป็นกีฬาที่มีความไม่แน่นอนสูง ผลการแข่งขันจริงอาจแตกต่างจากการทำนาย</p>
            </div>
        </div>
        """
        
        return html
    
    def _get_upcoming_matches_prediction(self) -> str:
        """แสดงการทำนายสำหรับแมตช์ที่กำลังจะมาถึงจากข้อมูลจริง"""
        try:
            # ดึงข้อมูลโปรแกรมการแข่งขันวันนี้จริงๆ
            data = self.football_api.get_today_fixtures()
            
            if not data or 'response' not in data or not data['response']:
                # ถ้าไม่มีแมตช์วันนี้ ให้แสดงแมตช์จำลอง
                return self._get_simulated_predictions()
            
            fixtures = data['response']
            print(f"✅ Found {len(fixtures)} real fixtures for prediction")
            
            html = """
            <div class="upcoming-predictions">
                <div class="prediction-header">
                    <h3>🔮 การทำนายแมตช์วันนี้</h3>
                    <p>ทำนายจากโปรแกรมฟุตบอลจริงวันนี้</p>
                </div>
                <div class="predictions-list">
            """
            
            predictions_made = 0
            max_predictions = 15  # จำกัดไม่เกิน 15 คู่
            
            for fixture in fixtures:
                if predictions_made >= max_predictions:
                    break
                    
                try:
                    # ดึงข้อมูลทีม
                    home_team = fixture['teams']['home']['name']
                    away_team = fixture['teams']['away']['name']
                    league_name = fixture['league']['name']
                    fixture_time = self._format_fixture_time(fixture['fixture']['date'])
                    status = fixture['fixture']['status']['short']
                    
                    # ทำนายเฉพาะแมตช์ที่ยังไม่เริ่ม
                    if status in ['TBD', 'NS']:
                        # ทำการทำนาย
                        prediction_result = self._predict_real_match(home_team, away_team, league_name)
                        
                        confidence_color = "🔥" if prediction_result['confidence'] == "สูง" else "⚡" if prediction_result['confidence'] == "ปานกลาง" else "💫"
                        
                        html += f"""
                            <div class="prediction-item">
                                <div class="match-info">
                                    <strong>{home_team} vs {away_team}</strong>
                                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                                        🏆 {league_name} | ⏰ {fixture_time}
                                    </div>
                                </div>
                                <div class="prediction-details">
                                    <span class="prediction-result">🎯 {prediction_result['prediction']}</span>
                                    <span class="prediction-score">⚽ {prediction_result['score']}</span>
                                    <span class="prediction-confidence">{confidence_color} {prediction_result['confidence']}</span>
                                </div>
                            </div>
                        """
                        predictions_made += 1
                        
                except Exception as e:
                    print(f"⚠️ Error processing fixture for prediction: {e}")
                    continue
            
            if predictions_made == 0:
                html += """
                    <div class="prediction-item">
                        <div class="match-info">
                            <strong>ไม่มีแมตช์ที่รอการแข่งขันในวันนี้</strong>
                        </div>
                        <div class="prediction-details">
                            <span class="prediction-result">🕐 กรุณาลองใหม่พรุ่งนี้</span>
                        </div>
                    </div>
                """
            
            html += f"""
                </div>
                <div class="prediction-note">
                    <p>📊 <strong>ทำนาย {predictions_made} คู่</strong> จากโปรแกรมการแข่งขันจริงวันนี้</p>
                    <p>💡 <strong>วิธีใช้:</strong> พิมพ์ "ทำนาย [ทีม1] vs [ทีม2]" เพื่อดูการทำนายแบบละเอียด</p>
                    <p>🔍 <strong>ตัวอย่าง:</strong> "ทำนาย{home_team if predictions_made > 0 else 'แมนยู'} vs {away_team if predictions_made > 0 else 'ลิเวอร์พูล'}"</p>
                    <p>⚠️ <strong>หมายเหตุ:</strong> การทำนายอิงจากสถิติและไม่รับประกันความแม่นยำ</p>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Error in _get_upcoming_matches_prediction: {str(e)}")
            return self._get_simulated_predictions()
    
    def _predict_real_match(self, home_team: str, away_team: str, league_name: str) -> Dict:
        """ทำนายผลแมตช์จากข้อมูลจริง"""
        try:
            # ดึงฟอร์มทีม (ใช้ชื่อทีมจริงจาก API)
            home_form = self._get_team_form_by_api_name(home_team)
            away_form = self._get_team_form_by_api_name(away_team)
            
            # คำนวณคะแนนฟอร์ม
            home_points = home_form["wins"] * 3 + home_form["draws"] * 1
            away_points = away_form["wins"] * 3 + away_form["draws"] * 1
            
            # คำนวณอัตราส่วนประตู
            home_goal_ratio = home_form["goals_for"] / max(home_form["goals_against"], 1)
            away_goal_ratio = away_form["goals_for"] / max(away_form["goals_against"], 1)
            
            # ปรับคะแนนตามลีก (ลีกดังมีการแข่งขันสูงกว่า)
            league_factor = self._get_league_competitiveness(league_name)
            
            # ปรับคะแนนสำหรับประโยชน์เจ้าบ้าน
            home_advantage = 0.3
            adjusted_home_points = home_points + home_advantage
            
            # ทำนายผล
            if adjusted_home_points > away_points + 2:
                prediction = f"{home_team} ชนะ"
                confidence = "สูง" if abs(adjusted_home_points - away_points) > 4 else "ปานกลาง"
                score_options = ["2-0", "2-1", "3-1"]
            elif away_points > adjusted_home_points + 2:
                prediction = f"{away_team} ชนะ"
                confidence = "สูง" if abs(away_points - adjusted_home_points) > 4 else "ปานกลาง"
                score_options = ["0-2", "1-2", "1-3"]
            elif abs(adjusted_home_points - away_points) <= 1:
                prediction = "เสมอ"
                confidence = "ปานกลาง"
                score_options = ["1-1", "0-0", "2-2"]
            else:
                winner = home_team if adjusted_home_points > away_points else away_team
                prediction = f"{winner} ชนะ"
                confidence = "ปานกลาง"
                score_options = ["1-0", "2-1"] if winner == home_team else ["0-1", "1-2"]
            
            # เลือกคะแนนโดยสุ่ม
            import random
            score_prediction = random.choice(score_options)
            
            return {
                "prediction": prediction,
                "score": score_prediction,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"⚠️ Error in _predict_real_match: {e}")
            return {
                "prediction": "เสมอ",
                "score": "1-1", 
                "confidence": "ต่ำ"
            }
    
    def _get_team_form_by_api_name(self, team_name: str) -> Dict:
        """ดึงฟอร์มทีมโดยใช้ชื่อจาก API"""
        # แมปชื่อทีมจาก API กับฐานข้อมูลของเรา
        team_mapping = {
            # Premier League
            "Manchester United": "แมนยู",
            "Manchester City": "แมนซิตี้", 
            "Liverpool": "ลิเวอร์พูล",
            "Chelsea": "เชลซี",
            "Arsenal": "อาร์เซนอล",
            "Tottenham": "สเปอร์ส",
            "Newcastle": "นิวคาสเซิล",
            "Aston Villa": "แอสตัน วิลลา",
            "Brighton": "บรายท์ตัน",
            "West Ham": "เวสต์แฮม",
            
            # La Liga
            "Real Madrid": "เรอัลมาดริด",
            "Barcelona": "บาร์เซโลนา",
            "Atletico Madrid": "แอตเลติโก มาดริด",
            "Sevilla": "เซบียา",
            "Valencia": "วาเลนเซีย",
            "Athletic Bilbao": "บิลเบา",
            "Real Sociedad": "เรอัล โซเซียดาด",
            "Real Betis": "เบติส",
            
            # Bundesliga
            "Bayern Munich": "บาเยิร์น",
            "Borussia Dortmund": "ดอร์ทมุนด์",
            "RB Leipzig": "ไลป์ซิก",
            "Bayer Leverkusen": "เลเวอร์คูเซ่น",
            "Eintracht Frankfurt": "แฟรงก์เฟิร์ต",
            "Borussia Monchengladbach": "โบรุสเซีย",
            "Wolfsburg": "วูล์ฟสบวร์ก",
            "Stuttgart": "ชตุ๊ตการ์ท",
            
            # Serie A
            "Juventus": "ยูเวนตุส",
            "AC Milan": "มิลาน",
            "Inter": "อินเตอร์",
            "Napoli": "นาโปลี",
            "AS Roma": "โรมา",
            "Lazio": "ลาซิโอ",
            "Atalanta": "อาตาลันตา",
            "Fiorentina": "ฟิออเรนตินา",
            
            # Ligue 1
            "Paris Saint Germain": "ปารีสแซงต์แชร์กแมง",
            "Marseille": "มาร์เซย",
            "Lyon": "ลียง",
            "Monaco": "โมนาโก",
            "Lille": "ลีล",
            "Nice": "นีซ",
            "Reims": "รีมส์",
            "Rennes": "เรนน์"
        }
        
        # หาชื่อทีมในฐานข้อมูล
        mapped_name = team_mapping.get(team_name, team_name)
        
        # ใช้ฟังก์ชันเดิมในการดึงข้อมูล
        return self._get_team_recent_form(mapped_name)
    
    def _get_league_competitiveness(self, league_name: str) -> float:
        """คำนวณระดับการแข่งขันของลีก"""
        premier_leagues = ["Premier League", "Championship", "League One"]
        top_leagues = ["La Liga", "Bundesliga", "Serie A", "Ligue 1"]
        
        if any(league in league_name for league in premier_leagues):
            return 1.2  # พรีเมียร์ลีกแข่งสูงสุด
        elif any(league in league_name for league in top_leagues):
            return 1.1  # ลีกดังอื่นๆ
        else:
            return 1.0  # ลีกทั่วไป
    
    def _get_simulated_predictions(self) -> str:
        """แสดงการทำนายจำลองเมื่อไม่มีแมตช์จริง"""
        upcoming_predictions = [
            # Premier League
            {"match": "แมนยู vs แมนซิตี้", "prediction": "แมนซิตี้ ชนะ", "score": "1-2", "confidence": "สูง"},
            {"match": "ลิเวอร์พูล vs เชลซี", "prediction": "ลิเวอร์พูล ชนะ", "score": "2-1", "confidence": "ปานกลาง"},
            {"match": "อาร์เซนอล vs สเปอร์ส", "prediction": "เสมอ", "score": "1-1", "confidence": "ปานกลาง"},
            {"match": "นิวคาสเซิล vs แอสตัน วิลลา", "prediction": "นิวคาสเซิล ชนะ", "score": "2-0", "confidence": "ปานกลาง"},
            {"match": "บรายท์ตัน vs เวสต์แฮม", "prediction": "บรายท์ตัน ชนะ", "score": "1-0", "confidence": "ปานกลาง"},
            
            # La Liga
            {"match": "เรอัลมาดริด vs บาร์เซโลนา", "prediction": "เรอัลมาดริด ชนะ", "score": "2-0", "confidence": "สูง"},
            {"match": "แอตเลติโก vs เซบียา", "prediction": "แอตเลติโก ชนะ", "score": "1-0", "confidence": "ปานกลาง"}
        ]
        
        html = """
        <div class="upcoming-predictions">
            <div class="prediction-header">
                <h3>🔮 การทำนายแมตช์ยอดนิยม</h3>
                <p>ไม่มีแมตช์วันนี้ - แสดงแมตช์ยอดนิยมแทน</p>
            </div>
            <div class="predictions-list">
        """
        
        for pred in upcoming_predictions:
            confidence_color = "🔥" if pred["confidence"] == "สูง" else "⚡" if pred["confidence"] == "ปานกลาง" else "💫"
            html += f"""
                <div class="prediction-item">
                    <div class="match-info">
                        <strong>{pred["match"]}</strong>
                    </div>
                    <div class="prediction-details">
                        <span class="prediction-result">🎯 {pred["prediction"]}</span>
                        <span class="prediction-score">⚽ {pred["score"]}</span>
                        <span class="prediction-confidence">{confidence_color} {pred["confidence"]}</span>
                    </div>
                </div>
            """
        
        html += """
            </div>
            <div class="prediction-note">
                <p>📊 <strong>แมตช์จำลอง</strong> เนื่องจากไม่มีการแข่งขันจริงวันนี้</p>
                <p>💡 <strong>วิธีใช้:</strong> พิมพ์ "ทำนาย [ทีม1] vs [ทีม2]" เพื่อดูการทำนายแบบละเอียด</p>
                <p>🔍 <strong>ตัวอย่าง:</strong> "ทำนายแมนยู vs ลิเวอร์พูล"</p>
            </div>
        </div>
        """
        
        return html
