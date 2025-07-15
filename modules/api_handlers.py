"""
API Handlers สำหรับ Flask Routes
จัดการทุก endpoint ของ chatbot
"""

from flask import request, jsonify
from typing import Any, Dict


class APIHandlers:
    """คลาสสำหรับจัดการ API endpoints ทั้งหมด"""
    
    def __init__(self, chatbot):
        """
        Args:
            chatbot: instance ของ ThaiFootballBot
        """
        self.chatbot = chatbot
    
    def chat_endpoint(self) -> Dict[str, Any]:
        """
        Handle POST /chat endpoint
        
        Returns:
            JSON response with chat result or error
        """
        try:
            data = request.json
            print(f"🔍 Chat endpoint received data: {data}")
            
            user_message = data.get('prompt', '') or data.get('message', '')
            print(f"🔍 Extracted message: '{user_message}'")
            
            if not user_message:
                return jsonify({"error": "กรุณาป้อนข้อความ"}), 400
            
            # ใช้ chatbot object
            print(f"🤖 Calling chatbot.analyze_message() with message: '{user_message}'")
            result = self.chatbot.analyze_message(user_message)
            print(f"🤖 Chatbot returned: {type(result)}, length: {len(result) if result else 0}")
            
            return jsonify({
                "response": result,
                "message": result,
                "success": True
            })
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"เกิดข้อผิดพลาด: {str(e)}",
                "success": False
            }), 500
    
    def standings_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/standings endpoint
        
        Returns:
            JSON response with standings table
        """
        league = request.args.get('league', 'พรีเมียร์ลีก')
        
        try:
            league_id = self.chatbot.extract_league_id(league)
            result = self.chatbot.get_standings_table(league_id, 2024)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def topscorers_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/topscorers endpoint
        
        Returns:
            JSON response with top scorers
        """
        league = request.args.get('league', 'พรีเมียร์ลีก')
        
        try:
            league_id = self.chatbot.extract_league_id(league)
            result = self.chatbot.get_topscorers(league_id, 2024)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def team_form_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/team-form endpoint
        
        Returns:
            JSON response with team form
        """
        team = request.args.get('team', '')
        
        if not team:
            return jsonify({"error": "กรุณาระบุชื่อทีม เช่น ?team=แมนยู"}), 400
        
        try:
            result = self.chatbot.get_last_fixtures(team, count=5)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def compare_teams_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/compare-teams endpoint
        
        Returns:
            JSON response with team comparison
        """
        team1 = request.args.get('team1', '')
        team2 = request.args.get('team2', '')
        
        if not team1 or not team2:
            return jsonify({"error": "กรุณาระบุทีม 2 ทีม เช่น ?team1=แมนยู&team2=ลิเวอร์พูล"}), 400
        
        try:
            result = self.chatbot.compare_teams_form(team1, team2, count=5)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def last_results_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/last-results endpoint
        
        Returns:
            JSON response with last results
        """
        try:
            fixtures = self.chatbot.get_today_fixtures()
            if fixtures:
                return jsonify({"results": fixtures})
            else:
                return jsonify({"results": ["ไม่มีผลบอลล่าสุด"]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def news_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/news endpoint
        
        Returns:
            JSON response with news (latest or by keyword)
        """
        keyword = request.args.get('keyword', '')
        
        try:
            if keyword:
                result = self.chatbot.get_news_by_keyword(keyword)
            else:
                result = self.chatbot.get_latest_news_from_data()
            
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def latest_news_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/news/latest endpoint
        
        Returns:
            JSON response with latest news
        """
        try:
            result = self.chatbot.get_latest_news_from_data()
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def search_news_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/news/search endpoint
        
        Returns:
            JSON response with search results
        """
        keyword = request.args.get('q', '')
        
        if not keyword:
            return jsonify({"error": "กรุณาระบุคำค้นหา เช่น ?q=แมนยู"}), 400
        
        try:
            result = self.chatbot.get_news_by_keyword(keyword)
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def today_fixtures_endpoint(self) -> Dict[str, Any]:
        """
        Handle GET /api/fixtures/today endpoint
        
        Returns:
            JSON response with today's fixtures
        """
        try:
            result = self.chatbot.get_today_fixtures()
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
