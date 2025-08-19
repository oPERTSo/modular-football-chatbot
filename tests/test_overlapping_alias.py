import os
import sys

# Ensure project root is on path for tests
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.thai_football_bot import ThaiFootballAnalysisChatbot


def test_overlapping_alias_extraction():
    bot = ThaiFootballAnalysisChatbot()
    message = "ทำนายผลแมนซิตี้กับสเปอร์"
    teams = bot._extract_teams_from_message(message)
    # Expect canonical Thai display names, no short-alias duplicates
    assert teams == ["แมนซิตี้", "สเปอร์ส"]
