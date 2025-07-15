#!/usr/bin/env python
# -*- coding: utf-8 -*-

from modules.news_manager import NewsManager
from modules.thai_football_bot import ThaiFootballAnalysisChatbot

def test_news_system():
    # Test News Manager
    print("Testing News Manager...")
    nm = NewsManager('data')
    all_files = nm.get_all_files()
    print(f'News Manager loaded: {len(all_files)} files')
    
    # Test generate_news_response directly
    print("\nTesting news generation directly...")
    news_html = nm.generate_news_response("ข่าวล่าสุด")
    print(f"Generated HTML length: {len(news_html)}")
    print(f"HTML preview: {news_html[:300]}...")
    
    # Test chatbot news response
    print("\nTesting chatbot news response...")
    bot = ThaiFootballAnalysisChatbot()
    response = bot.analyze_message('ข่าวล่าสุด')
    print(f'Bot response length: {len(response)}')
    print(f'Bot response preview: {response[:300]}...')
    
    # Test specific news search
    print("\nTesting specific news search...")
    specific_news = nm.generate_news_response("เวียร์ตซ์")
    print(f"Specific news length: {len(specific_news)}")
    print(f"Specific news preview: {specific_news[:300]}...")

if __name__ == "__main__":
    test_news_system()
