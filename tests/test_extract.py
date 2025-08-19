import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.thai_football_bot import ThaiFootballAnalysisChatbot

bot = ThaiFootballAnalysisChatbot()

tests = [
    "ทำนาย สเปอร์ส กับ แมนยู",
    "ทำนาย แมนยู vs สเปอร์ส",
    "ทำนาย tottenham vs man utd",
    "สเปอร์ และ แมนยู ทำนายผล",
    "ทำนาย spurs กับ man u",
    "ทำนาย ลิเวอร์พูล กับ แมนยู",
    "ทำนายผล ลิเวอร์พูล กับ แมนยู"
]

for t in tests:
    teams = bot._extract_teams_from_message(t)
    print(f"Input: {t}\n -> Extracted: {teams}\n")
