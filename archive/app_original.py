import os
from openai import OpenAI
from pathlib import Path
import tiktoken
from typing import List, Dict
import re  # เพิ่มบรรทัดนี้
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# from football_chatbot import football_bp, last_results, compare_teams, player_stats, search_player

from rapidfuzz import process, fuzz
import requests
import datetime
import logging

# โหลด environment variables จากไฟล์ .env
load_dotenv()

# ทดสอบว่าโหลด API key ได้หรือไม่
print("🔑 ตรวจสอบ API Keys:")
print(f"OPENAI_API_KEY: {'✅ มี' if os.getenv('OPENAI_API_KEY') else '❌ ไม่มี'}")
print(f"API_FOOTBALL_KEY: {'✅ มี' if os.getenv('API_FOOTBALL_KEY') else '❌ ไม่มี'}")
print(f"sportsdb_api_key: {'✅ มี' if os.getenv('sportsdb_api_key') else '❌ ไม่มี'}")

app = Flask(__name__)
CORS(app)

def load_news_from_data():
    news_items = []
    news_dir = os.path.join(os.path.dirname(__file__), 'data')
    for fname in os.listdir(news_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(news_dir, fname), encoding='utf-8') as f:
                content = f.read().strip()
            title = fname.split('__')[0].replace('_', ' ')
            news_items.append({
                'title': title,
                'content': content
            })
    return news_items

# ...rest of your code...

class ThaiFootballAnalysisChatbot:
    def __init__(self, openai_api_key: str, reference_folder: str, max_tokens: int = 3500):
        self.openai_api_key = openai_api_key
        self.reference_folder = Path(reference_folder)
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.reference_data = self.load_reference_files()
        self.thai_football_keywords = {
            'match_prediction': [
                'ทำนาย', 'คาดการณ์', 'พยากรณ์', 'เต็ง', 'ราคาบอล', 'แทงบอล', 
                'ชนะ', 'แพ้', 'เสมอ', 'สกอร์', 'ผลการแข่งขัน', 'โอกาส'
            ],
            'team_analysis': [
                'ทีม', 'สโมสร', 'ทั้งทีม', 'แผนการเล่น', 'ยุทธวิธี', 'รูปแบบเล่น',
                'จุดแข็ง', 'จุดอ่อน', 'ฟอร์ม', 'ผลงาน', 'แนวทาง', 'การจัดวาง'
            ],
            'player_analysis': [
                'นักเตะ', 'ผู้เล่น', 'กองหน้า', 'กองกลาง', 'กองหลัง', 'ผู้รักษาประตู',
                'สถิติ', 'ประตู', 'แอสซิสต์', 'ทักษะ', 'ความสามารถ', 'การเล่น'
            ],
            'head_to_head': [
                'เจอกัน', 'ประวัติการเจอกัน', 'ผลงานในอดีต', 'สถิติการเจอกัน',
                'นัดก่อนหน้า', 'ประวัติศาสตร์', 'เก่าแก่'
            ],
            'injury_news': [
                'บาดเจ็บ', 'อาการ', 'ฟิตเนส', 'สุขภาพ', 'พร้อมเล่น', 'ไม่พร้อม',
                'แบน', 'ถูกใบเหลือง', 'ถูกใบแดง', 'ลงเล่น', 'ทีมตัวจริง'
            ],
            'form_analysis': [
                'ฟอร์ม', 'ล่าสุด', 'เมื่อเร็วๆนี้', 'ช่วงนี้', 'ปัจจุบัน', 'ต่อเนื่อง',
                'นัดล่าสุด', 'เกมที่แล้ว', 'ฤดูกาลนี้', 'สถานการณ์ปัจจุบัน'
            ]
        }
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
            "นิวคาสเซิล": "Newcastle",
            "นิวคาสเซิล ยูไนเต็ด": "Newcastle",
            "แอสตัน วิลล่า": "Aston Villa",
            "ไบรท์ตัน": "Brighton",
            "เวสต์แฮม": "West Ham",

            # La Liga
            "บาร์เซโลนา": "Barcelona",
            "บาร์เซโลน่า": "Barcelona",
            "บาร์ซ่า": "Barcelona",
            "เรอัล มาดริด": "Real Madrid",
            "ราชันชุดขาว": "Real Madrid",
            "แอตเลติโก มาดริด": "Atletico Madrid",
            "แอตฯ มาดริด": "Atletico Madrid",
            "เซบีญ่า": "Sevilla",
            "บียาร์เรอัล": "Villarreal",
            "บาเลนเซีย": "Valencia",

            # Bundesliga
            "บาเยิร์น": "Bayern Munich",
            "บาเยิร์น มิวนิค": "Bayern Munich",
            "เสือใต้": "Bayern Munich",
            "ดอร์ทมุนด์": "Borussia Dortmund",
            "โบรุสเซีย ดอร์ทมุนด์": "Borussia Dortmund",
            "เสือเหลือง": "Borussia Dortmund",
            "ไลป์ซิก": "RB Leipzig",
            "เลเวอร์คูเซ่น": "Bayer Leverkusen",
            "แฟรงค์เฟิร์ต": "Eintracht Frankfurt",

            # Serie A
            "ยูเวนตุส": "Juventus",
            "ม้าลาย": "Juventus",
            "อินเตอร์ มิลาน": "Inter",
            "อินเตอร์": "Inter",
            "เอซี มิลาน": "AC Milan",
            "มิลาน": "AC Milan",
            "โรม่า": "Roma",
            "นาโปลี": "Napoli",
            "ลาซิโอ": "Lazio",

            # Ligue 1
            "เปแอสเช": "Paris Saint Germain",
            "ปารีส แซงต์ แชร์กแมง": "Paris Saint Germain",
            "ปารีส": "Paris Saint Germain",
            "โอลิมปิก มาร์กเซย": "Marseille",
            "ลียง": "Lyon",
            "โมนาโก": "Monaco",
            "แรนส์": "Rennes",
        }
        self.team_to_league = {
            # Premier League
            "Manchester United": 39, "แมนเชสเตอร์ ยูไนเต็ด": 39, "แมนยู": 39, "แมนยูไนเต็ด": 39,
            "Liverpool": 39, "ลิเวอร์พูล": 39, "หงส์แดง": 39,
            "Arsenal": 39, "อาร์เซนอล": 39, "ปืนใหญ่": 39,
            "Chelsea": 39, "เชลซี": 39, "สิงห์บลูส์": 39,
            "Manchester City": 39, "แมนเชสเตอร์ ซิตี้": 39, "แมนซิตี้": 39, "เรือใบสีฟ้า": 39,
            "Tottenham": 39, "สเปอร์ส": 39, "ท็อตแน่ม ฮ็อทสเปอร์": 39, "ไก่เดือยทอง": 39,
            "Newcastle": 39, "นิวคาสเซิล": 39, "นิวคาสเซิล ยูไนเต็ด": 39,
            "Aston Villa": 39, "แอสตัน วิลล่า": 39,

            # La Liga
            "Barcelona": 140, "บาร์เซโลนา": 140, "บาร์เซโลน่า": 140, "บาร์ซ่า": 140,
            "Real Madrid": 140, "เรอัล มาดริด": 140, "ราชันชุดขาว": 140,
            "Atletico Madrid": 140, "แอตเลติโก มาดริด": 140, "แอตฯ มาดริด": 140,
            "Sevilla": 140, "เซบีญ่า": 140,
            "Villarreal": 140, "บียาร์เรอัล": 140,

            # Bundesliga
            "Bayern Munich": 78, "บาเยิร์น": 78, "บาเยิร์น มิวนิค": 78, "เสือใต้": 78,
            "Borussia Dortmund": 78, "ดอร์ทมุนด์": 78, "โบรุสเซีย ดอร์ทมุนด์": 78, "เสือเหลือง": 78,
            "RB Leipzig": 78, "ไลป์ซิก": 78,
            "Bayer Leverkusen": 78, "เลเวอร์คูเซ่น": 78,
            "Eintracht Frankfurt": 78, "แฟรงค์เฟิร์ต": 78,

            # Serie A
            "Juventus": 135, "ยูเวนตุส": 135, "ม้าลาย": 135,
            "Inter": 135, "อินเตอร์ มิลาน": 135, "อินเตอร์": 135,
            "AC Milan": 135, "เอซี มิลาน": 135, "มิลาน": 135,
            "Roma": 135, "โรม่า": 135,
            "Napoli": 135, "นาโปลี": 135,
            "Lazio": 135, "ลาซิโอ": 135,

            # Ligue 1
            "Paris Saint Germain": 61, "เปแอสเช": 61, "ปารีส แซงต์ แชร์กแมง": 61, "ปารีส": 61,
            "Marseille": 61, "โอลิมปิก มาร์กเซย": 61,
            "Lyon": 61, "ลียง": 61,
            "Monaco": 61, "โมนาโก": 61,
            "Rennes": 61, "แรนส์": 61,
        }

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_reference_files(self) -> Dict[str, Dict]:
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
                    file_type = self.categorize_thai_file(file_path.stem, content)
                    reference_data[file_path.stem] = {
                        'content': content,
                        'type': file_type,
                        'filename': file_path.name,
                        'word_count': len(content.split())
                    }
                    print(f"โหลดแล้ว: {file_path.name} ({file_type})")
                else:
                    print(f"ไม่สามารถอ่านไฟล์: {file_path.name}")
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการโหลด {file_path}: {e}")
        print(f"โหลดไฟล์ข้อมูลฟุตบอลสำเร็จ {len(reference_data)} ไฟล์")
        return reference_data

    def categorize_thai_file(self, filename: str, content: str) -> str:
        filename_lower = filename.lower()
        content_lower = content.lower()
        thai_team_keywords = ['ทีม', 'สโมสร', 'คลับ']
        thai_player_keywords = ['นักเตะ', 'ผู้เล่น', 'สถิติ', 'โปรไฟล์']
        thai_match_keywords = ['นัด', 'แมตช์', 'เกม', 'การแข่งขัน']
        thai_league_keywords = ['ลีก', 'ตาราง', 'อันดับ']
        thai_news_keywords = ['ข่าว', 'อัพเดท', 'บาดเจ็บ']
        if any(word in filename_lower for word in ['team', 'squad', 'club'] + thai_team_keywords):
            return 'ข้อมูลทีม'
        elif any(word in filename_lower for word in ['player', 'stats', 'profile'] + thai_player_keywords):
            return 'ข้อมูลนักเตะ'
        elif any(word in filename_lower for word in ['match', 'fixture', 'game'] + thai_match_keywords):
            return 'ข้อมูลการแข่งขัน'
        elif any(word in filename_lower for word in ['league', 'table', 'standing'] + thai_league_keywords):
            return 'ข้อมูลลีก'
        elif any(word in filename_lower for word in ['injury', 'news', 'update'] + thai_news_keywords):
            return 'ข่าวสาร'
        if any(word in content_lower for word in ['แผนการเล่น', 'ยุทธวิธี', 'รูปแบบ']):
            return 'วิเคราะห์ยุทธวิธี'
        elif any(word in content_lower for word in ['ประตู', 'แอสซิสต์', 'สถิติ']):
            return 'สถิตินักเตะ'
        elif any(word in content_lower for word in ['ทำนาย', 'คาดการณ์', 'เต็ง']):
            return 'ทำนายผลการแข่งขัน'
        return 'ข้อมูลฟุตบอลทั่วไป'

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def detect_thai_query_type(self, query: str) -> str:
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in self.thai_football_keywords['match_prediction']):
            return 'ทำนายการแข่งขัน'
        elif any(keyword in query_lower for keyword in self.thai_football_keywords['player_analysis']):
            return 'วิเคราะห์นักเตะ'
        elif any(keyword in query_lower for keyword in self.thai_football_keywords['team_analysis']):
            return 'วิเคราะห์ทีม'
        elif any(keyword in query_lower for keyword in self.thai_football_keywords['head_to_head']):
            return 'สถิติการเจอกัน'
        elif any(keyword in query_lower for keyword in self.thai_football_keywords['injury_news']):
            return 'ข่าวทีม'
        elif any(keyword in query_lower for keyword in self.thai_football_keywords['form_analysis']):
            return 'วิเคราะห์ฟอร์ม'
        elif "ตารางคะแนน" in query_lower or "อันดับ" in query_lower:
            return "standings"
        elif "โปรแกรม" in query_lower or "นัดถัดไป" in query_lower:
            return "next_fixture"
        elif "เปรียบเทียบ" in query_lower:
            return "compare"
        elif "ผลล่าสุด" in query_lower or "ผลเมื่อคืน" in query_lower:
            return "latest_result"
        return 'ทั่วไป'

    def extract_league_id(self, user_message: str) -> int:
        league_map = {
            "พรีเมียร์ลีก": 39, "premier league": 39, "england": 39, "อังกฤษ": 39,
            "บุนเดสลีกา": 78, "bundesliga": 78, "เยอรมัน": 78, "germany": 78,
            "ลาลิก้า": 140, "ลาลีกา": 140, "ลา ลีกา": 140, "ลา-ลีกา": 140, "laliga": 140, "la liga": 140, "สเปน": 140, "spain": 140,
            "เซเรีย อา": 135, "serie a": 135, "อิตาลี": 135, "italy": 135,
            "ลีกเอิง": 61, "ligue 1": 61, "ฝรั่งเศส": 61, "france": 61,
        }
        msg = user_message.lower()
        best, score, _ = process.extractOne(msg, league_map.keys(), scorer=fuzz.partial_ratio)
        if score > 75:
            return league_map[best]
        return 39  # default Premier League

    def extract_team_id(self, user_message: str) -> int:
        return None

    def search_relevant_thai_content(self, query: str, query_type: str, top_k: int = 4) -> List[Dict]:
        query_lower = query.lower()
        relevant_content = []
        thai_entities = re.findall(r'[\u0E00-\u0E7F]+(?:\s+[\u0E00-\u0E7F]+)*', query)
        english_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
        all_entities = thai_entities + english_entities
        for filename, file_data in self.reference_data.items():
            content = file_data['content']
            content_lower = content.lower()
            file_type = file_data['type'
            ]
            score = 0
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_lower)
            score += matches
            entity_matches = sum(1 for entity in all_entities if entity.lower() in content_lower)
            score += entity_matches * 4
            type_bonus = 0
            type_mapping = {
                'ทำนายการแข่งขัน': ['ทำนายผลการแข่งขัน', 'ข้อมูลการแข่งขัน', 'ข้อมูลทีม'],
                'วิเคราะห์นักเตะ': ['ข้อมูลนักเตะ', 'สถิตินักเตะ'],
                'วิเคราะห์ทีม': ['ข้อมูลทีม', 'วิเคราะห์ยุทธวิธี'],
                'สถิติการเจอกัน': ['ข้อมูลการแข่งขัน', 'ข้อมูลทีม'],
                'ข่าวทีม': ['ข่าวสาร', 'ข้อมูลทีม'],
                'วิเคราะห์ฟอร์ม': ['ข้อมูลทีม', 'ข้อมูลการแข่งขัน']
            }
            if query_type in type_mapping and file_type in type_mapping[query_type]:
                type_bonus = 6
            score += type_bonus
            if query_type in ['ทำนายการแข่งขัน', 'วิเคราะห์นักเตะ', 'วิเคราะห์ทีม', 'สถิติการเจอกัน', 'ข่าวทีม', 'วิเคราะห์ฟอร์ม']:
                thai_keyword_map = {
                    'ทำนายการแข่งขัน': 'match_prediction',
                    'วิเคราะห์นักเตะ': 'player_analysis', 
                    'วิเคราะห์ทีม': 'team_analysis',
                    'สถิติการเจอกัน': 'head_to_head',
                    'ข่าวทีม': 'injury_news',
                    'วิเคราะห์ฟอร์ม': 'form_analysis'
                }
                keyword_category = thai_keyword_map.get(query_type)
                if keyword_category and keyword_category in self.thai_football_keywords:
                    thai_matches = sum(1 for keyword in self.thai_football_keywords[keyword_category] 
                                     if keyword in content.lower())
                    score += thai_matches * 3
            if score > 0:
                relevant_content.append({
                    'filename': filename,
                    'content': content,
                    'type': file_type,
                    'score': score,
                    'matches': matches
                })
        relevant_content.sort(key=lambda x: x['score'], reverse=True)
        return relevant_content[:top_k]

    def build_thai_context(self, query: str, query_type: str) -> str:
        relevant_items = self.search_relevant_thai_content(query, query_type)
        context_parts = []
        total_tokens = 0
        for item in relevant_items:
            content = item['content']
            file_type = item['type']
            filename = item['filename']
            content_tokens = self.count_tokens(content)
            formatted_content = f"[{file_type} - {filename}]\n{content}"
            formatted_tokens = self.count_tokens(formatted_content)
            if total_tokens + formatted_tokens > self.max_tokens:
                remaining_tokens = self.max_tokens - total_tokens - 100
                if remaining_tokens > 150:
                    truncated = self.encoding.decode(
                        self.encoding.encode(content)[:remaining_tokens]
                    )
                    context_parts.append(f"[{file_type} - {filename}]\n{truncated}...")
                break
            else:
                context_parts.append(formatted_content)
                total_tokens += formatted_tokens
        return "\n\n" + "="*50 + "\n\n".join(context_parts)

    def get_last_fixtures(self, team_name: str, count: int = 5):
        # แปลงชื่อไทยเป็นอังกฤษถ้ามี
        team_en = self.thai_team_map.get(team_name, team_name)
        
        # ขยาย mapping ให้ครอบคลุมทุกทีมในระบบ
        team_name_to_id = {
            # Premier League
            "Manchester United": 33, "แมนเชสเตอร์ ยูไนเต็ด": 33, "แมนยู": 33, "แมนยูไนเต็ด": 33,
            "Liverpool": 40, "ลิเวอร์พูล": 40, "หงส์แดง": 40,
            "Arsenal": 42, "อาร์เซนอล": 42, "ปืนใหญ่": 42,
            "Chelsea": 49, "เชลซี": 49, "สิงห์บลูส์": 49,
            "Manchester City": 50, "แมนเชสเตอร์ ซิตี้": 50, "แมนซิตี้": 50, "เรือใบสีฟ้า": 50,
            "Tottenham": 47, "สเปอร์ส": 47, "ท็อตแน่ม ฮ็อทสเปอร์": 47, "ไก่เดือยทอง": 47,
            "Newcastle": 34, "นิวคาสเซิล": 34, "นิวคาสเซิล ยูไนเต็ด": 34,
            "Aston Villa": 66, "แอสตัน วิลล่า": 66,
            "Brighton": 51, "ไบรท์ตัน": 51,
            "West Ham": 48, "เวสต์แฮม": 48,
            
            # La Liga
            "Barcelona": 529, "บาร์เซโลนา": 529, "บาร์เซโลน่า": 529, "บาร์ซ่า": 529,
            "Real Madrid": 541, "เรอัล มาดริด": 541, "ราชันชุดขาว": 541,
            "Atletico Madrid": 530, "แอตเลติโก มาดริด": 530, "แอตฯ มาดริด": 530,
            "Sevilla": 536, "เซบีญ่า": 536,
            "Villarreal": 533, "บียาร์เรอัล": 533,
            "Valencia": 532, "บาเลนเซีย": 532,
            
            # Bundesliga
            "Bayern Munich": 157, "บาเยิร์น": 157, "บาเยิร์น มิวนิค": 157, "เสือใต้": 157,
            "Borussia Dortmund": 165, "ดอร์ทมุนด์": 165, "โบรุสเซีย ดอร์ทมุนด์": 165, "เสือเหลือง": 165,
            "RB Leipzig": 173, "ไลป์ซิก": 173,
            "Bayer Leverkusen": 168, "เลเวอร์คูเซ่น": 168,
            "Eintracht Frankfurt": 169, "แฟรงค์เฟิร์ต": 169,
            
            # Serie A
            "Juventus": 496, "ยูเวนตุส": 496, "ม้าลาย": 496,
            "Inter": 505, "อินเตอร์ มิลาน": 505, "อินเตอร์": 505,
            "AC Milan": 489, "เอซี มิลาน": 489, "มิลาน": 489,
            "Roma": 497, "โรม่า": 497,
            "Napoli": 492, "นาโปลี": 492,
            "Lazio": 487, "ลาซิโอ": 487,
            
            # Ligue 1
            "Paris Saint Germain": 85, "เปแอสเช": 85, "ปารีส แซงต์ แชร์กแมง": 85, "ปารีส": 85,
            "Marseille": 81, "โอลิมปิก มาร์กเซย": 81,
            "Lyon": 80, "ลียง": 80,
            "Monaco": 91, "โมนาโก": 91,
            "Rennes": 94, "แรนส์": 94,
        }
        
        # รองรับทั้งชื่ออังกฤษและไทย
        team_id = team_name_to_id.get(team_name) or team_name_to_id.get(team_en)
        
        if not team_id:
            return f"ขออภัยครับ ยังไม่รองรับทีม '{team_name}' ในระบบ กรุณาลองทีมอื่น\n\n📋 ทีมที่รองรับ:\n• พรีเมียร์ลีก: แมนยู, ลิเวอร์พูล, อาร์เซนอล, เชลซี, แมนซิตี้, สเปอร์ส\n• ลาลีกา: บาร์ซ่า, เรอัล มาดริด, แอตเลติโก\n• บุนเดสลีกา: บาเยิร์น, ดอร์ทมุนด์\n• เซเรีย อา: ยูเวนตุส, อินเตอร์, มิลาน\n• ลีกเอิง: ปารีส แซงต์ แชร์กแมง"
        
        api_key = os.getenv("API_FOOTBALL_KEY")
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last={count}"
        headers = {"x-apisports-key": api_key}
        try:
            self.logger.info(f"Fetching fixtures for {team_name}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["response"]:
                    results = []
                    for fixture in data["response"]:
                        date = fixture["fixture"]["date"][:10]
                        home = fixture["teams"]["home"]["name"]
                        away = fixture["teams"]["away"]["name"]
                        goals_home = fixture["goals"]["home"]
                        goals_away = fixture["goals"]["away"]
                        status = fixture["fixture"]["status"]["short"]
                        results.append(f"{date}: {home} {goals_home} - {goals_away} {away} ({status})")
                    return f"ฟอร์ม 5 นัดหลังสุดของ {team_en}:\n" + "\n".join(results)
                else:
                    return f"ขออภัยครับ ไม่พบข้อมูลฟอร์ม 5 นัดหลังสุดของ {team_name} อาจเป็นเพราะทีมยังไม่ได้เล่นครบ 5 นัด หรือข้อมูลยังไม่อัปเดต"
            else:
                return f"เกิดข้อผิดพลาดในการดึงข้อมูลฟอร์ม 5 นัดหลังสุดของ {team_name} ครับ กรุณาลองใหม่อีกครั้ง"
        except requests.exceptions.Timeout:
            return f"เชื่อมต่อ API ช้าเกินไป กรุณาลองใหม่อีกครั้ง"
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return f"เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง"

    def compare_teams_form(self, team1_name: str, team2_name: str, count: int = 5):
        """เปรียบเทียบฟอร์ม 5 นัดหลังสุดของ 2 ทีม"""
        # แปลงชื่อไทยเป็นอังกฤษถ้ามี
        team1_en = self.thai_team_map.get(team1_name, team1_name)
        team2_en = self.thai_team_map.get(team2_name, team2_name)
        
        # mapping ทีมใหม่ที่ครอบคลุมทุกลีก
        team_name_to_id = {
            # Premier League
            "Manchester United": 33, "แมนเชสเตอร์ ยูไนเต็ด": 33, "แมนยู": 33, "แมนยูไนเต็ด": 33,
            "Liverpool": 40, "ลิเวอร์พูล": 40, "หงส์แดง": 40,
            "Arsenal": 42, "อาร์เซนอล": 42, "ปืนใหญ่": 42,
            "Chelsea": 49, "เชลซี": 49, "สิงห์บลูส์": 49,
            "Manchester City": 50, "แมนเชสเตอร์ ซิตี้": 50, "แมนซิตี้": 50, "เรือใบสีฟ้า": 50,
            "Tottenham": 47, "สเปอร์ส": 47, "ท็อตแน่ม ฮ็อทสเปอร์": 47, "ไก่เดือยทอง": 47,
            "Newcastle": 34, "นิวคาสเซิล": 34, "นิวคาสเซิล ยูไนเต็ด": 34,
            "Aston Villa": 66, "แอสตัน วิลล่า": 66,
            "Brighton": 51, "ไบรท์ตัน": 51,
            "West Ham": 48, "เวสต์แฮม": 48,
            
            # La Liga
            "Barcelona": 529, "บาร์เซโลนา": 529, "บาร์เซโลน่า": 529, "บาร์ซ่า": 529,
            "Real Madrid": 541, "เรอัล มาดริด": 541, "ราชันชุดขาว": 541,
            "Atletico Madrid": 530, "แอตเลติโก มาดริด": 530, "แอตฯ มาดริด": 530,
            "Sevilla": 536, "เซบีญ่า": 536,
            "Villarreal": 533, "บียาร์เรอัล": 533,
            "Valencia": 532, "บาเลนเซีย": 532,
            
            # Bundesliga
            "Bayern Munich": 157, "บาเยิร์น": 157, "บาเยิร์น มิวนิค": 157, "เสือใต้": 157,
            "Borussia Dortmund": 165, "ดอร์ทมุนด์": 165, "โบรุสเซีย ดอร์ทมุนด์": 165, "เสือเหลือง": 165,
            "RB Leipzig": 173, "ไลป์ซิก": 173,
            "Bayer Leverkusen": 168, "เลเวอร์คูเซ่น": 168,
            "Eintracht Frankfurt": 169, "แฟรงค์เฟิร์ต": 169,
            
            # Serie A
            "Juventus": 496, "ยูเวนตุส": 496, "ม้าลาย": 496,
            "Inter": 505, "อินเตอร์ มิลาน": 505, "อินเตอร์": 505,
            "AC Milan": 489, "เอซี มิลาน": 489, "มิลาน": 489,
            "Roma": 497, "โรม่า": 497,
            "Napoli": 492, "นาโปลี": 492,
            "Lazio": 487, "ลาซิโอ": 487,
            
            # Ligue 1
            "Paris Saint Germain": 85, "เปแอสเช": 85, "ปารีส แซงต์ แชร์กแมง": 85, "ปารีส": 85,
            "Marseille": 81, "โอลิมปิก มาร์กเซย": 81,
            "Lyon": 80, "ลียง": 80,
            "Monaco": 91, "โมนาโก": 91,
            "Rennes": 94, "แรนส์": 94,
        }
        
        # หา team_id ของทั้ง 2 ทีม
        team1_id = team_name_to_id.get(team1_name) or team_name_to_id.get(team1_en)
        team2_id = team_name_to_id.get(team2_name) or team_name_to_id.get(team2_en)
        
        if not team1_id or not team2_id:
            missing_teams = []
            if not team1_id:
                missing_teams.append(team1_name)
            if not team2_id:
                missing_teams.append(team2_name)
            return f"ขออภัยครับ ยังไม่รองรับทีม: {', '.join(missing_teams)} กรุณาลองทีมอื่น"
        
        # ดึงข้อมูลฟอร์มทั้ง 2 ทีม
        api_key = os.getenv("API_FOOTBALL_KEY")
        
        def get_team_form(team_id, team_name):
            url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last={count}"
            headers = {"x-apisports-key": api_key}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data["response"]:
                    results = []
                    wins, draws, losses = 0, 0, 0
                    goals_for, goals_against = 0, 0
                    
                    for fixture in data["response"]:
                        date = fixture["fixture"]["date"][:10]
                        home = fixture["teams"]["home"]["name"]
                        away = fixture["teams"]["away"]["name"]
                        goals_home = fixture["goals"]["home"]
                        goals_away = fixture["goals"]["away"]
                        
                        # คำนวณผลแพ้ชนะ
                        if home == team_name or fixture["teams"]["home"]["id"] == team_id:
                            # ทีมเล่นเป็นเจ้าบ้าน
                            goals_for += goals_home if goals_home else 0
                            goals_against += goals_away if goals_away else 0
                            if goals_home and goals_away is not None:
                                if goals_home > goals_away:
                                    wins += 1
                                    result = "ชนะ"
                                elif goals_home < goals_away:
                                    losses += 1
                                    result = "แพ้"
                                else:
                                    draws += 1
                                    result = "เสมอ"
                            else:
                                result = "ยังไม่แข่ง"
                        else:
                            # ทีมเล่นเป็นทีมเยือน
                            goals_for += goals_away if goals_away else 0
                            goals_against += goals_home if goals_home else 0
                            if goals_home is not None and goals_away:
                                if goals_away > goals_home:
                                    wins += 1
                                    result = "ชนะ"
                                elif goals_away < goals_home:
                                    losses += 1
                                    result = "แพ้"
                                else:
                                    draws += 1
                                    result = "เสมอ"
                            else:
                                result = "ยังไม่แข่ง"
                        
                        results.append(f"{date}: {home} {goals_home}-{goals_away} {away} ({result})")
                    
                    return {
                        'matches': results,
                        'wins': wins,
                        'draws': draws,
                        'losses': losses,
                        'goals_for': goals_for,
                        'goals_against': goals_against,
                        'points': wins * 3 + draws
                    }
                else:
                    return None
            else:
                return None
        
        # ดึงข้อมูลทั้ง 2 ทีม
        team1_form = get_team_form(team1_id, team1_en)
        team2_form = get_team_form(team2_id, team2_en)
        
        if not team1_form or not team2_form:
            return f"ขออภัยครับ ไม่สามารถดึงข้อมูลฟอร์มของทีมได้ กรุณาลองใหม่อีกครั้ง"
        
        # สร้างตารางเปรียบเทียบแบบ HTML
        comparison = f"""
<div class="team-comparison">
    <h3>🔥 เปรียบเทียบฟอร์ม {count} นัดหลังสุด</h3>
    
    <table class="comparison-table">
        <thead>
            <tr>
                <th>สถิติ</th>
                <th>{team1_en}</th>
                <th>{team2_en}</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>ชนะ</b></td>
                <td>{team1_form['wins']}</td>
                <td>{team2_form['wins']}</td>
            </tr>
            <tr>
                <td><b>เสมอ</b></td>
                <td>{team1_form['draws']}</td>
                <td>{team2_form['draws']}</td>
            </tr>
            <tr>
                <td><b>แพ้</b></td>
                <td>{team1_form['losses']}</td>
                <td>{team2_form['losses']}</td>
            </tr>
            <tr>
                <td><b>คะแนน</b></td>
                <td>{team1_form['points']} แต้ม</td>
                <td>{team2_form['points']} แต้ม</td>
            </tr>
            <tr>
                <td><b>ได้ประตู</b></td>
                <td>{team1_form['goals_for']}</td>
                <td>{team2_form['goals_for']}</td>
            </tr>
            <tr>
                <td><b>เสียประตู</b></td>
                <td>{team1_form['goals_against']}</td>
                <td>{team2_form['goals_against']}</td>
            </tr>
            <tr>
                <td><b>ผลต่างประตู</b></td>
                <td>{team1_form['goals_for'] - team1_form['goals_against']:+d}</td>
                <td>{team2_form['goals_for'] - team2_form['goals_against']:+d}</td>
            </tr>
        </tbody>
    </table>
    
    <div class="summary">
        <h4>🏆 สรุป:</h4>"""
    
        # วิเคราะห์ผล
        if team1_form['points'] > team2_form['points']:
            comparison += f"<p>• <b>{team1_en}</b> มีฟอร์มดีกว่า (มากกว่า {team1_form['points'] - team2_form['points']} แต้ม)</p>"
        elif team2_form['points'] > team1_form['points']:
            comparison += f"<p>• <b>{team2_en}</b> มีฟอร์มดีกว่า (มากกว่า {team2_form['points'] - team1_form['points']} แต้ม)</p>"
        else:
            comparison += f"<p>• ทั้งสองทีมมีฟอร์มเท่ากัน ({team1_form['points']} แต้ม)</p>"
        
        # เปรียบเทียบการทำประตู
        if team1_form['goals_for'] > team2_form['goals_for']:
            comparison += f"<p>• <b>{team1_en}</b> ทำประตูได้มากกว่า ({team1_form['goals_for']} vs {team2_form['goals_for']})</p>"
        elif team2_form['goals_for'] > team1_form['goals_for']:
            comparison += f"<p>• <b>{team2_en}</b> ทำประตูได้มากกว่า ({team2_form['goals_for']} vs {team1_form['goals_for']})</p>"
        
        comparison += "</div></div>"
        
        return comparison

    def chat(self, user_message: str, page_data: str) -> str:
        query_type = self.detect_thai_query_type(user_message)
        api_result = None

        # ตรวจสอบคำขอตารางคะแนน
        if "ตารางคะแนน" in user_message or "อันดับ" in user_message:
            # ดึงชื่อลีกจากข้อความ
            league_name = "พรีเมียร์ลีก"  # default
            
            if any(x in user_message.lower() for x in ["ลาลีกา", "ลาลิก้า", "ลา ลีกา", "สเปน", "spain"]):
                league_name = "ลาลีกา"
            elif any(x in user_message.lower() for x in ["บุนเดสลีกา", "เยอรมัน", "germany"]):
                league_name = "บุนเดสลีกา"
            elif any(x in user_message.lower() for x in ["เซเรีย อา", "serie a", "อิตาลี", "italy"]):
                league_name = "เซเรีย อา"
            elif any(x in user_message.lower() for x in ["ลีกเอิง", "ligue 1", "ฝรั่งเศส", "france"]):
                league_name = "ลีกเอิง"
            
            return self.get_standings_table(league_name)

        # ถ้าถามเฉพาะอันดับทีม
        if "อันดับ" in user_message and not "ตารางคะแนน" in user_message:
            # รวมชื่อทีมทั้งหมด (ไทย/อังกฤษ)
            all_team_names = list(self.team_to_league.keys())
            try:
                best_team, score, _ = process.extractOne(user_message, all_team_names, scorer=fuzz.partial_ratio)
                if score > 70:
                    league_id = self.team_to_league[best_team]
                    # ดึงตารางคะแนนเพื่อหาอันดับทีม
                    league_names = {39: "พรีเมียร์ลีก", 140: "ลาลีกา", 78: "บุนเดสลีกา", 135: "เซเรีย อา", 61: "ลีกเอิง"}
                    league_name = league_names.get(league_id, "พรีเมียร์ลีก")
                    
                    # ใช้ฟังก์ชันตารางคะแนนใหม่
                    standings_html = self.get_standings_table(league_name)
                    
                    # ถ้าเป็น HTML แสดงว่าสำเร็จ
                    if "standings-container" in standings_html:
                        return standings_html
                    else:
                        return f"ขออภัยครับ ไม่พบข้อมูลอันดับของ {best_team} ในขณะนี้"
                else:
                    return "กรุณาระบุชื่อทีมที่ต้องการทราบอันดับให้ชัดเจนขึ้น"
            except Exception as e:
                return f"เกิดข้อผิดพลาดในการค้นหาอันดับทีม กรุณาลองใหม่อีกครั้ง"

        # ตรวจสอบคำขอข่าว
        if any(keyword in user_message.lower() for keyword in ["ข่าว", "news", "อัพเดท", "ข่าวสาร", "ล่าสุด"]):
            # ค้นหาคีย์เวิร์ด
            team_keywords = []
            for team_name in self.thai_team_map.keys():
                if team_name in user_message:
                    team_keywords.append(team_name)
            
            if team_keywords:
                # ค้นหาข่าวตามทีม
                return self.get_news_by_keyword(team_keywords[0])
            else:
                # ข่าวทั่วไป
                return self.get_latest_news_from_data()

        # ตรวจสอบคำขอฟอร์มทีม
        if any(keyword in user_message.lower() for keyword in ["ฟอร์ม", "form", "5 นัด", "นัดหลัง"]):
            # ค้นหาชื่อทีมในข้อความ
            all_team_names = list(self.team_to_league.keys())
            try:
                best_team, score, _ = process.extractOne(user_message, all_team_names, scorer=fuzz.partial_ratio)
                if score > 70:
                    return self.get_last_fixtures(best_team, count=5)
                else:
                    return "กรุณาระบุชื่อทีมที่ต้องการทราบฟอร์มให้ชัดเจนขึ้น"
            except Exception as e:
                return f"เกิดข้อผิดพลาดในการค้นหาฟอร์มทีม กรุณาลองใหม่อีกครั้ง"

        # ตรวจสอบคำขอเปรียบเทียบทีม
        if any(keyword in user_message.lower() for keyword in ["เปรียบเทียบ", "compare", "vs", "กับ"]):
            # หาชื่อทีมใน message
            teams_found = []
            for team_name in self.thai_team_map.keys():
                if team_name in user_message:
                    teams_found.append(team_name)
            
            # หาชื่อทีมอังกฤษ
            for team_name in self.thai_team_map.values():
                if team_name.lower() in user_message.lower():
                    teams_found.append(team_name)
            
            if len(teams_found) >= 2:
                return self.compare_teams_form(teams_found[0], teams_found[1], count=5)
            else:
                return "กรุณาระบุชื่อทีม 2 ทีมที่ต้องการเปรียบเทียบ เช่น 'เปรียบเทียบ แมนยู vs ลิเวอร์พูล'"

        # ตรวจสอบคำขอดาวซัลโว
        if any(keyword in user_message.lower() for keyword in ["ดาวซัลโว", "topscorer", "top scorer", "นักเตะทำประตูสูงสุด"]):
            # ดึงชื่อลีกจากข้อความ
            league_name = "พรีเมียร์ลีก"  # default
            
            if any(x in user_message.lower() for x in ["ลาลีกา", "ลาลิก้า", "ลา ลีกา", "สเปน", "spain"]):
                league_name = "ลาลีกา"
            elif any(x in user_message.lower() for x in ["บุนเดสลีกา", "เยอรมัน", "germany"]):
                league_name = "บุนเดสลีกา"
            elif any(x in user_message.lower() for x in ["เซเรีย อา", "serie a", "อิตาลี", "italy"]):
                league_name = "เซเรีย อา"
            elif any(x in user_message.lower() for x in ["ลีกเอิง", "ligue 1", "ฝรั่งเศส", "france"]):
                league_name = "ลีกเอิง"
            
            league_id = self.extract_league_id(league_name)
            return self.get_topscorers(league_id, 2024)

        # ตรวจสอบคำขอโปรแกรมบอล
        if any(keyword in user_message.lower() for keyword in ["โปรแกรม", "fixture", "นัดถัดไป", "แข่งวันนี้"]):
            return self.get_today_fixtures()

        # ถ้าไม่ตรงเงื่อนไขใดๆ ใช้ OpenAI
        try:
            # สร้าง context จากข้อมูลที่มี
            context = self.build_thai_context(user_message, query_type)
            
            # ใช้ OpenAI Client ใหม่
            client = OpenAI(api_key=self.openai_api_key)
            
            messages = [
                {"role": "system", "content": f"""คุณคือผู้เชี่ยวชาญด้านฟุตบอลที่สามารถตอบคำถามเป็นภาษาไทยได้
                
ข้อมูลที่มี: {context}

กรุณาตอบคำถามเป็นภาษาไทย โดยอิงจากข้อมูลที่ให้มา และเพิ่มเติมด้วยความรู้ทั่วไปเกี่ยวกับฟุตบอล
หากไม่มีข้อมูลที่เกี่ยวข้อง ให้บอกว่าไม่มีข้อมูลและแนะนำให้ถามคำถามอื่น"""},
                {"role": "user", "content": user_message}
            ]
            
            # เรียก OpenAI API ใหม่
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"

    def get_topscorers(self, league_id: int, season: int):
        """ดึงข้อมูลดาวซัลโว"""
        try:
            api_key = os.getenv("API_FOOTBALL_KEY")
            if not api_key:
                api_key = "1530104cc4e15e74372196bf79eeac9e"
            
            url = f"https://v3.football.api-sports.io/players/topscorers"
            params = {
                "league": league_id,
                "season": season
            }
            headers = {"x-apisports-key": api_key}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["response"]:
                    html_content = """
                    <div class="topscorers-container">
                        <h2>⚽ ดาวซัลโว</h2>
                        <table class="topscorers-table">
                            <thead>
                                <tr>
                                    <th>อันดับ</th>
                                    <th>ชื่อ</th>
                                    <th>ทีม</th>
                                    <th>ประตู</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    for i, player_data in enumerate(data["response"][:10]):
                        player = player_data["player"]
                        team = player_data["statistics"][0]["team"]
                        goals = player_data["statistics"][0]["goals"]["total"]
                        
                        html_content += f"""
                        <tr>
                            <td>{i+1}</td>
                            <td>{player["name"]}</td>
                            <td>{team["name"]}</td>
                            <td>{goals}</td>
                        </tr>
                        """
                    
                    html_content += """
                            </tbody>
                        </table>
                    </div>
                    """
                    
                    return html_content
                else:
                    return "ไม่พบข้อมูลดาวซัลโว"
            else:
                return f"เกิดข้อผิดพลาดในการดึงข้อมูล (Status: {response.status_code})"
                
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"
    
    def get_today_fixtures(self):
        """ดึงข้อมูลโปรแกรมบอลวันนี้"""
        try:
            api_key = os.getenv("API_FOOTBALL_KEY")
            if not api_key:
                api_key = "1530104cc4e15e74372196bf79eeac9e"
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            url = f"https://v3.football.api-sports.io/fixtures"
            params = {
                "date": today,
                "timezone": "Asia/Bangkok"
            }
            headers = {"x-apisports-key": api_key}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["response"]:
                    fixtures = []
                    for fixture in data["response"][:10]:
                        time = fixture["fixture"]["date"][11:16]
                        home = fixture["teams"]["home"]["name"]
                        away = fixture["teams"]["away"]["name"]
                        league = fixture["league"]["name"]
                        
                        fixtures.append(f"{time} - {home} vs {away} ({league})")
                    
                    return f"⚽ โปรแกรมบอลวันนี้:\n" + "\n".join(fixtures)
                else:
                    return "ไม่มีแมตช์วันนี้"
            else:
                return f"เกิดข้อผิดพลาดในการดึงข้อมูล"
                
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"

    def get_latest_news_from_data(self):
        """ดึงข่าวล่าสุดจากไฟล์ในโฟลเดอร์ data แบบการ์ด HTML สวยงาม"""
        try:
            news_folder = Path("data")
            if not news_folder.exists():
                return "ไม่พบโฟลเดอร์ข้อมูลข่าว"
            
            # ดึงไฟล์ทั้งหมดในโฟลเดอร์ data
            news_files = []
            for file_path in news_folder.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    mod_time = file_path.stat().st_mtime
                    import datetime
                    mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
                    
                    # แปลงชื่อไฟล์เป็นหัวข้อข่าว
                    title = file_path.stem
                    if "__" in title:
                        title = title.split("__")[0]
                    title = title.replace("_", " ")
                    
                    news_files.append({
                        'title': title,
                        'content': content,
                        'modified': mod_time,
                        'date': mod_date,
                        'filename': file_path.name
                    })
                except Exception as e:
                    continue
            
            if not news_files:
                return "ไม่พบไฟล์ข่าวในโฟลเดอร์ data"
            
            # เรียงลำดับตามวันที่แก้ไขล่าสุด
            news_files.sort(key=lambda x: x['modified'], reverse=True)
            
            # สร้าง HTML การ์ดข่าวสวยงาม
            html_content = f"""
            <div class="news-container">
                <div class="news-header">
                    <h2>📰 ข่าวฟุตบอลล่าสุด</h2>
                    <p class="news-subtitle">ข่าวล่าสุดจาก thsport.live</p>
                </div>
                
                <div class="news-grid">
            """
            
            # แสดงข่าว 5 ข่าวล่าสุด
            for i, news in enumerate(news_files[:5]):
                # ตัดเนื้อหาให้เหมาะสม
                content_preview = news['content']
                if len(content_preview) > 300:
                    content_preview = content_preview[:300] + "..."
                
                # แทนที่ line breaks ด้วย <br>
                content_preview = content_preview.replace('\n', '<br>')
                
                # Escape quotes เพื่อใช้ใน JavaScript
                content_escaped = news['content'].replace('"', '&quot;').replace("'", "&#39;").replace('\n', '\\n')
                
                html_content += f"""
                <div class="news-card">
                    <div class="news-card-header">
                        <div class="news-number">ข่าวที่ {i+1}</div>
                        <div class="news-date">📅 {news['date']}</div>
                    </div>
                    
                    <div class="news-title">
                        <h3>🔥 {news['title']}</h3>
                    </div>
                    
                    <div class="news-content">
                        {content_preview}
                    </div>
                    
                    <div class="news-footer">
                        <span class="news-source">📁 {news['filename']}</span>
                        <button class="read-more-btn" onclick="showFullNews('{news['filename']}', '{content_escaped}')">
                            อ่านเพิ่มเติม →
                        </button>
                    </div>
                </div>
                """
            
            html_content += f"""
                </div>
                
                <div class="news-summary">
                    <div class="summary-stats">
                        <span class="stat-item">📊 แสดง {min(5, len(news_files))} จาก {len(news_files)} ข่าว</span>
                        <span class="stat-item">🔄 อัพเดทล่าสุด: {news_files[0]['date'] if news_files else 'ไม่มีข้อมูล'}</span>
                        <span class="stat-item">📱 ข้อมูลจาก thsport.live</span>
                    </div>
                </div>
            </div>
            
            <style>
                .news-container {{
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                
                .news-header {{
                    text-align: center;
                    margin-bottom: 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }}
                
                .news-header h2 {{
                    margin: 0;
                    font-size: 2.2em;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                
                .news-subtitle {{
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                
                .news-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                
                .news-card {{
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    overflow: hidden;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    border: 1px solid #e0e0e0;
                }}
                
                .news-card:hover {{
                    transform: translateY(-8px);
                    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                }}
                
                .news-card-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .news-number {{
                    background: rgba(255,255,255,0.2);
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: bold;
                }}
                
                .news-date {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                
                .news-title {{
                    padding: 20px 20px 15px 20px;
                }}
                
                .news-title h3 {{
                    margin: 0;
                    color: #333;
                    font-size: 1.3em;
                    line-height: 1.4;
                }}
                
                .news-content {{
                    padding: 0 20px 20px 20px;
                    color: #666;
                    line-height: 1.6;
                    font-size: 0.95em;
                }}
                
                .news-content mark {{
                    background: #FFD700;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                
                .news-footer {{
                    padding: 15px 20px 20px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid #f0f0f0;
                }}
                
                .news-source {{
                    color: #888;
                    font-size: 0.85em;
                }}
                
                .read-more-btn {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 0.85em;
                    transition: transform 0.2s ease;
                }}
                
                .read-more-btn:hover {{
                    transform: scale(1.05);
                }}
                
                .news-summary {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #667eea;
                }}
                
                .summary-stats {{
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 15px;
                }}
                
                .stat-item {{
                    color: #666;
                    font-size: 0.9em;
                    font-weight: 500;
                }}
                
                @media (max-width: 768px) {{
                    .news-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .summary-stats {{
                        flex-direction: column;
                        text-align: center;
                    }}
                }}
            </style>
            
            <script>
                function showFullNews(filename, content) {{
                    const modal = document.createElement('div');
                    modal.style.cssText = `
                        position: fixed;
                        top: 0; left: 0; right: 0; bottom: 0;
                        background: rgba(0,0,0,0.8);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 1000;
                    `;
                    
                    const modalContent = document.createElement('div');
                    modalContent.style.cssText = `
                        background: white;
                        padding: 30px;
                        border-radius: 15px;
                        max-width: 80%;
                        max-height: 80%;
                        overflow-y: auto;
                        position: relative;
                    `;
                    
                    modalContent.innerHTML = `
                        <button onclick="this.parentElement.parentElement.remove()" 
                                style="position: absolute; top: 10px; right: 15px; 
                                       background: none; border: none; font-size: 20px; 
                                       cursor: pointer;">✕</button>
                        <h3>📄 ${{filename}}</h3>
                        <div style="line-height: 1.6; white-space: pre-wrap;">${{content}}</div>
                    `;
                    
                    modal.appendChild(modalContent);
                    document.body.appendChild(modal);
                    
                    modal.addEventListener('click', function(e) {{
                        if (e.target === modal) {{
                            modal.remove();
                        }}
                    }});
                }}
            </script>
            """
            
            return html_content
            
        except Exception as e:
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงข่าว: {str(e)}</div>"

    def get_news_by_keyword(self, keyword: str):
        """ค้นหาข่าวตามคีย์เวิร์ด"""
        try:
            news_folder = Path("data")
            if not news_folder.exists():
                return "ไม่พบโฟลเดอร์ข้อมูลข่าว"
            
            # ดึงไฟล์ทั้งหมดในโฟลเดอร์ data
            matching_files = []
            for file_path in news_folder.glob("*.txt"):
                try:
                    # ตรวจสอบชื่อไฟล์
                    if keyword.lower() in file_path.stem.lower():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        mod_time = file_path.stat().st_mtime
                        import datetime
                        mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
                        
                        # แปลงชื่อไฟล์เป็นหัวข้อข่าว
                        title = file_path.stem
                        if "__" in title:
                            title = title.split("__")[0]
                        title = title.replace("_", " ")
                        
                        matching_files.append({
                            'title': title,
                            'content': content,
                            'modified': mod_time,
                            'date': mod_date,
                            'filename': file_path.name
                        })
                        continue
                    
                    # ตรวจสอบเนื้อหาไฟล์
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    if keyword.lower() in content.lower():
                        mod_time = file_path.stat().st_mtime
                        import datetime
                        mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
                        
                        # แปลงชื่อไฟล์เป็นหัวข้อข่าว
                        title = file_path.stem
                        if "__" in title:
                            title = title.split("__")[0]
                        title = title.replace("_", " ")
                        
                        matching_files.append({
                            'title': title,
                            'content': content,
                            'modified': mod_time,
                            'date': mod_date,
                            'filename': file_path.name
                        })
                        
                except Exception as e:
                    continue
            
            if not matching_files:
                return f"ไม่พบข่าวที่เกี่ยวข้องกับ '{keyword}'"
            
            # เรียงลำดับตามวันที่แก้ไขล่าสุด
            matching_files.sort(key=lambda x: x['modified'], reverse=True)
            
            # สร้าง HTML cards
            cards_html = ""
            for i, news in enumerate(matching_files[:10]):
                content_preview = news['content']
                if len(content_preview) > 300:
                    content_preview = content_preview[:300] + "..."
                
                content_preview = content_preview.replace('\n', '<br>')
                content_preview = content_preview.replace(keyword, f"<mark>{keyword}</mark>")
                content_escaped = news['content'].replace('"', '&quot;').replace("'", "&#39;").replace('\n', '\\n')
                
                cards_html += f"""
                <div class="news-card">
                    <div class="news-card-header">
                        <div class="news-number">ข่าวที่ {i+1}</div>
                        <div class="news-date">📅 {news['date']}</div>
                    </div>
                    <div class="news-title">
                        <h3>🔥 {news['title']}</h3>
                    </div>
                    <div class="news-content">
                        {content_preview}
                    </div>
                    <div class="news-footer">
                        <span class="news-source">📁 {news['filename']}</span>
                        <button class="read-more-btn" onclick="showFullNews('{news['filename']}', '{content_escaped}')">
                            อ่านเพิ่มเติม →
                        </button>
                    </div>
                </div>
                """
            
            # แยก CSS ออกมา
            css_styles = """
            <style>
                .news-container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                
                .news-header {
                    text-align: center;
                    margin-bottom: 30px;
                    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }
                
                .news-header h2 {
                    margin: 0;
                    font-size: 2.2em;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                
                .news-subtitle {
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                }
                
                .news-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }
                
                .news-card {
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    overflow: hidden;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    border: 1px solid #e0e0e0;
                }
                
                .news-card:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                }
                
                .news-card-header {
                    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                    color: white;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .news-number {
                    background: rgba(255,255,255,0.2);
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: bold;
                }
                
                .news-date {
                    font-size: 0.9em;
                    opacity: 0.9;
                }
                
                .news-title {
                    padding: 20px 20px 15px 20px;
                }
                
                .news-title h3 {
                    margin: 0;
                    color: #333;
                    font-size: 1.3em;
                    line-height: 1.4;
                }
                
                .news-content {
                    padding: 0 20px 20px 20px;
                    color: #666;
                    line-height: 1.6;
                    font-size: 0.95em;
                }
                
                .news-content mark {
                    background: #FFD700;
                    padding: 2px 4px;
                    border-radius: 3px;
                }
                
                .news-footer {
                    padding: 15px 20px 20px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid #f0f0f0;
                }
                
                .news-source {
                    color: #888;
                    font-size: 0.85em;
                }
                
                .read-more-btn {
                    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 0.85em;
                    transition: transform 0.2s ease;
                }
                
                .read-more-btn:hover {
                    transform: scale(1.05);
                }
                
                .news-summary {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #FF6B6B;
                }
                
                .summary-stats {
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 15px;
                }
                
                .stat-item {
                    color: #666;
                    font-size: 0.9em;
                    font-weight: 500;
                }
                
                @media (max-width: 768px) {
                    .news-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .summary-stats {
                        flex-direction: column;
                        text-align: center;
                    }
                }
            </style>
            
            <script>
                function showFullNews(filename, content) {
                    const modal = document.createElement('div');
                    modal.style.cssText = `
                        position: fixed;
                        top: 0; left: 0; right: 0; bottom: 0;
                        background: rgba(0,0,0,0.8);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 1000;
                    `;
                    
                    const modalContent = document.createElement('div');
                    modalContent.style.cssText = `
                        background: white;
                        padding: 30px;
                        border-radius: 15px;
                        max-width: 80%;
                        max-height: 80%;
                        overflow-y: auto;
                        position: relative;
                    `;
                    
                    modalContent.innerHTML = `
                        <button onclick="this.parentElement.parentElement.remove()" 
                                style="position: absolute; top: 10px; right: 15px; 
                                       background: none; border: none; font-size: 20px; 
                                       cursor: pointer;">✕</button>
                        <h3>📄 ${{filename}}</h3>
                        <div style="line-height: 1.6; white-space: pre-wrap;">${{content}}</div>
                    `;
                    
                    modal.appendChild(modalContent);
                    document.body.appendChild(modal);
                    
                    modal.addEventListener('click', function(e) {
                        if (e.target === modal) {
                            modal.remove();
                        }
                    });
                }
            </script>
            """
            
            # รวมทุกอย่างเข้าด้วยกัน
            html_content = f"""
            <div class="news-container">
                <div class="news-header">
                    <h2>🔍 ข่าวเกี่ยวกับ "{keyword}"</h2>
                    <p class="news-subtitle">พบ {len(matching_files)} ข่าวที่เกี่ยวข้อง</p>
                </div>
                
                <div class="news-grid">
                    {cards_html}
                </div>
                
                <div class="news-summary">
                    <div class="summary-stats">
                        <span class="stat-item">🔍 คำค้นหา: "{keyword}"</span>
                        <span class="stat-item">📊 พบ {len(matching_files)} ข่าว</span>
                        <span class="stat-item">📱 ข้อมูลจาก thsport.live</span>
                    </div>
                </div>
            </div>
            
            {css_styles}
            """
            
            return html_content
            
        except Exception as e:
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงข่าว: {str(e)}</div>"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('prompt', '')
        
        if not user_message:
            return jsonify({"error": "กรุณาส่งข้อความมาด้วย"}), 400
        
        # ใช้ chatbot object ที่สร้างไว้
        result = chatbot.chat(user_message, "")
        
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/standings')
def api_standings():
    """API สำหรับดูตารางคะแนน"""
    league = request.args.get('league', 'พรีเมียร์ลีก')
    
    try:
        result = chatbot.get_standings_table(league)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/topscorers')
def api_topscorers():
    """API สำหรับดูดาวซัลโว"""
    league = request.args.get('league', 'พรีเมียร์ลีก')
    
    try:
        league_id = chatbot.extract_league_id(league)
        result = chatbot.get_topscorers(league_id, 2024)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/team-form')
def api_team_form():
    """API สำหรับดูฟอร์มทีม"""
    team = request.args.get('team', '')
    
    if not team:
        return jsonify({"error": "กรุณาระบุชื่อทีม เช่น ?team=แมนยู"}), 400
    
    try:
        result = chatbot.get_last_fixtures(team, count=5)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare-teams')
def api_compare_teams():
    """API สำหรับเปรียบเทียบทีม"""
    team1 = request.args.get('team1', '')
    team2 = request.args.get('team2', '')
    
    if not team1 or not team2:
        return jsonify({"error": "กรุณาระบุทีม 2 ทีม เช่น ?team1=แมนยู&team2=ลิเวอร์พูล"}), 400
    
    try:
        result = chatbot.compare_teams_form(team1, team2, count=5)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/last-results')
def api_last_results():
    """API สำหรับดูผลบอลล่าสุด"""
    try:
        fixtures = chatbot.get_today_fixtures()
        if fixtures:
            return jsonify({"results": fixtures})
        else:
            return jsonify({"results": ["ไม่มีผลบอลล่าสุด"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news')
def api_news():
    """API สำหรับดูข่าวฟุตบอล"""
    keyword = request.args.get('keyword', '')
    
    try:
        if keyword:
            result = chatbot.get_news_by_keyword(keyword)
        else:
            result = chatbot.get_latest_news_from_data()
        
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news/latest')
def api_latest_news():
    """API สำหรับดูข่าวล่าสุด"""
    try:
        result = chatbot.get_latest_news_from_data()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news/search')
def api_search_news():
    """API สำหรับค้นหาข่าว"""
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify({"error": "กรุณาระบุคำค้นหา เช่น ?q=แมนยู"}), 400
    
    try:
        result = chatbot.get_news_by_keyword(keyword)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚽ ฟุตบอล Chatbot</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .api-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .api-card {
                background: rgba(255,255,255,0.15);
                border-radius: 15px;
                padding: 20px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .api-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 10px;
            }
            .post { background: #28a745; }
            .get { background: #17a2b8; }
            .endpoint {
                font-family: 'Courier New', monospace;
                color: #ffd700;
                word-break: break-all;
                margin: 8px 0;
            }
            .description {
                color: #e0e0e0;
                font-size: 0.9em;
                margin-top: 10px;
            }
            .examples {
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }
            .example-item {
                margin: 8px 0;
                padding: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                border-left: 4px solid #ffd700;
            }
            .status {
                background: rgba(40, 167, 69, 0.2);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border: 1px solid rgba(40, 167, 69, 0.3);
            }
            .status h4 {
                color: #28a745;
                margin-top: 0;
            }
            .emoji {
                font-size: 1.2em;
                margin-right: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚽ ฟุตบอล Chatbot API</h1>
            <div class="subtitle">
                🚀 ระบบ AI วิเคราะห์ฟุตบอล พร้อมข่าวล่าสุดจาก thsport.live
            </div>
            
            <div class="api-grid">
                <div class="api-card">
                    <span class="method post">POST</span>
                    <div class="endpoint">/chat</div>
                    <div class="description">
                        <span class="emoji">💬</span>
                        Chat กับ AI ฟุตบอลอัจฉริยะ<br>
                        <small>Body: {"prompt": "ข่าวบอลวันนี้"}</small>
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/news/latest</div>
                    <div class="description">
                        <span class="emoji">📰</span>
                        ข่าวฟุตบอลล่าสุด (การ์ดสวยงาม)
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/news/search?q=แมนยู</div>
                    <div class="description">
                        <span class="emoji">🔍</span>
                        ค้นหาข่าวตามทีม/คีย์เวิร์ด
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/standings?league=พรีเมียร์ลีก</div>
                    <div class="description">
                        <span class="emoji">🏆</span>
                        ตารางคะแนนแบบ Real-time
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/topscorers?league=พรีเมียร์ลีก</div>
                    <div class="description">
                        <span class="emoji">⚽</span>
                        ดาวซัลโวประจำลีก
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/team-form?team=แมนยู</div>
                    <div class="description">
                        <span class="emoji">📊</span>
                        ฟอร์ม 5 นัดหลังสุดของทีม
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/compare-teams?team1=แมนยู&team2=ลิเวอร์พูล</div>
                    <div class="description">
                        <span class="emoji">🔥</span>
                        เปรียบเทียบฟอร์ม 2 ทีม
                    </div>
                </div>
                
                <div class="api-card">
                    <span class="method get">GET</span>
                    <div class="endpoint">/api/last-results</div>
                    <div class="description">
                        <span class="emoji">📈</span>
                        ผลบอลล่าสุด/วันนี้
                    </div>
                </div>
            </div>
            
            <h3>🔥 ตัวอย่างการใช้งาน:</h3>
            <div class="examples">
                <div class="example-item">
                    <b>ถาม:</b> "ดาวซัลโว พรีเมียร์ลีก" <br>
                    <b>ตอบ:</b> จะได้ข้อมูลดาวซัลโวจาก API จริง
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "ตารางคะแนน ลาลีกา" <br>
                    <b>ตอบ:</b> จะได้ตารางคะแนนจาก API
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "ฟอร์ม 5 นัด แมนยู" <br>
                    <b>ตอบ:</b> จะได้ผลงาน 5 นัดล่าสุดของแมนยู
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "เปรียบเทียบ แมนยู vs ลิเวอร์พูล" <br>
                    <b>ตอบ:</b> จะได้การเปรียบเทียบฟอร์ม 2 ทีม
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "อันดับ แมนซิตี้" <br>
                    <b>ตอบ:</b> จะได้อันดับปัจจุบันของแมนซิตี้
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "โปรแกรมบอลวันนี้" <br>
                    <b>ตอบ:</b> จะได้รายการแข่งขันวันนี้
                </div>
                <div class="example-item">
                    <b>ถาม:</b> "ข่าวบอลวันนี้" <br>
                    <b>ตอบ:</b> จะได้ข่าวล่าสุดจากไฟล์ data
                </div>
            </div>
            
            <div class="status">
                <h4>✅ สถานะระบบ:</h4>
                <p>• API-Football: ใช้งานได้ (มี API Key)</p>
                <p>• OpenAI: ใช้งานได้ (มี API Key)</p>
                <p>• ข้อมูลอ้างอิง: โหลดแล้ว</p>
                <p>• ระบบ Chat: พร้อมใช้งาน</p>
                <p>• ข่าวฟุตบอล: ดึงจากไฟล์ data</p>
            </div>
    </body>
    </html>
    """

def main():
    global chatbot
    try:
        print("🔧 กำลังเริ่มต้นระบบ...")
        
        # ทดสอบ API Keys
        print("🔑 ตรวจสอบ API Keys:")
        openai_key = os.getenv("OPENAI_API_KEY")
        football_key = os.getenv("API_FOOTBALL_KEY")
        
        if not openai_key:
            print("❌ OPENAI_API_KEY ไม่พบ")
            return
        if not football_key:
            print("❌ API_FOOTBALL_KEY ไม่พบ")
            return
            
        print("✅ API Keys พร้อมใช้งาน")
        
        # สร้าง chatbot object
        chatbot = ThaiFootballAnalysisChatbot(
            openai_api_key=openai_key,
            reference_folder="data"
        )
        
        if not chatbot.reference_data:
            print("⚠️ ไม่พบข้อมูลอ้างอิง แต่ไม่เป็นไร ผมยังพร้อมคุยฟุตบอลกับคุณ!")
        else:
            categories = {}
            for data in chatbot.reference_data.values():
                cat = data['type']
                categories[cat] = categories.get(cat, 0) + 1
            print("📋 ข้อมูลที่ผมมี:")
            for category, count in categories.items():
                print(f"  - {category}: {count} ไฟล์")
        
        print("🚀 เซิร์ฟเวอร์กำลังเริ่มต้น...")
        print("📡 URL: http://localhost:5000")
        print("🔴 กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์")
        
        # รันเซิร์ฟเวอร์
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n⏹️ หยุดเซิร์ฟเวอร์แล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

# ประกาศตัวแปร global
chatbot = None

if __name__ == "__main__":
    main()