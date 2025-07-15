from pathlib import Path
import datetime
from typing import List, Dict
import re

class NewsManager:
    """คลาสสำหรับจัดการข่าว"""
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = Path(data_folder)
    
    def get_all_files(self) -> List[Path]:
        """ดึงรายชื่อไฟล์ทั้งหมดใน data folder"""
        try:
            if not self.data_folder.exists():
                return []
            return list(self.data_folder.glob("*.txt"))
        except Exception:
            return []
    
    def get_latest_news(self, limit: int = 5) -> List[Dict]:
        """ดึงข่าวล่าสุด"""
        try:
            if not self.data_folder.exists():
                return []
            
            news_files = []
            for file_path in self.data_folder.glob("*.txt"):
                try:
                    content = self.safe_read_file(file_path)
                    if not content:
                        continue
                    
                    mod_time = file_path.stat().st_mtime
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
                except Exception:
                    continue
            
            # เรียงลำดับตามวันที่แก้ไขล่าสุด
            news_files.sort(key=lambda x: x['modified'], reverse=True)
            return news_files[:limit]
            
        except Exception:
            return []
    
    def search_news_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """ค้นหาข่าวตามคีย์เวิร์ด"""
        try:
            if not self.data_folder.exists():
                return []
            
            matching_files = []
            for file_path in self.data_folder.glob("*.txt"):
                try:
                    # ตรวจสอบชื่อไฟล์
                    if keyword.lower() in file_path.stem.lower():
                        content = self.safe_read_file(file_path)
                        if not content:
                            continue
                        
                        mod_time = file_path.stat().st_mtime
                        mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
                        
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
                    content = self.safe_read_file(file_path)
                    if not content:
                        continue
                    
                    if keyword.lower() in content.lower():
                        mod_time = file_path.stat().st_mtime
                        mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
                        
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
                        
                except Exception:
                    continue
            
            # เรียงลำดับตามวันที่แก้ไขล่าสุด
            matching_files.sort(key=lambda x: x['modified'], reverse=True)
            return matching_files[:limit]
            
        except Exception:
            return []
    
    def create_news_html(self, news_list: List[Dict], title: str = "ข่าวฟุตบอล", keyword: str = None) -> str:
        """สร้าง HTML สำหรับแสดงข่าว"""
        if not news_list:
            return "<div class='no-results'>ไม่พบข่าว</div>"
        
        # สร้าง HTML cards
        cards_html = ""
        for i, news in enumerate(news_list):
            # ทำความสะอาดข้อมูลก่อนแสดง
            content_preview = self.clean_text(news['content'])
            content_full = self.clean_text(news['content']).replace('\n', '<br>')
            
            # สร้าง preview (300 ตัวอักษรแรก)
            if len(content_preview) > 300:
                content_preview = content_preview[:300] + "..."
                show_read_more = True
            else:
                show_read_more = False
            
            content_preview = content_preview.replace('\n', '<br>')
            
            # Highlight keyword ถ้ามี
            if keyword:
                clean_keyword = self.clean_text(keyword)
                content_preview = content_preview.replace(clean_keyword, f"<mark>{clean_keyword}</mark>")
                content_full = content_full.replace(clean_keyword, f"<mark>{clean_keyword}</mark>")
            
            # ทำความสะอาดชื่อเรื่องและชื่อไฟล์
            news_title = self.clean_text(news['title']).replace('"', '&quot;').replace("'", "&#39;")
            news_filename = self.clean_text(news['filename']).replace('"', '&quot;').replace("'", "&#39;")
            
            # สร้าง unique ID สำหรับแต่ละข่าว
            news_id = f"news_{i+1}"
            
            cards_html += f'''
            <div class="news-card">
                <div class="news-card-header">
                    <div class="news-number">ข่าวที่ {i+1}</div>
                    <div class="news-date">📅 {news['date']}</div>
                </div>
                
                <div class="news-title">
                    <h3>🔥 {news_title}</h3>
                </div>
                
                <div class="news-content">
                    <div class="content-preview">
                        {content_preview if show_read_more else content_full}
                    </div>
                    {f'<details class="news-details"><summary style="display: none;"></summary><div class="content-full">{content_full}</div></details>' if show_read_more else ''}
                </div>
                
                <div class="news-footer">
                    <span class="news-source">📁 {news_filename}</span>
                    {f'<div class="read-more-btn" onclick="this.closest(\'.news-card\').querySelector(\'.news-details\').toggleAttribute(\'open\'); this.textContent = this.closest(\'.news-card\').querySelector(\'.news-details\').hasAttribute(\'open\') ? \'← ซ่อนรายละเอียด\' : \'อ่านเพิ่มเติม →\';">อ่านเพิ่มเติม →</div>' if show_read_more else ''}
                </div>
            </div>
            '''
        
        # สร้าง HTML fragment สำหรับ chat 
        html_content = f'''
<style>
    .news-container {{ max-width: 1200px; margin: 20px auto; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    .news-header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); color: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
    .news-header h2 {{ margin: 0; font-size: 2.2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
    .news-subtitle {{ margin: 10px 0 0 0; font-size: 1.1em; opacity: 0.9; }}
    .news-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; margin-bottom: 30px; }}
    .news-card {{ background: white; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.3s ease, box-shadow 0.3s ease; border: 1px solid #e0e0e0; }}
    .news-card:hover {{ transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }}
    .news-card-header {{ background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }}
    .news-number {{ background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }}
    .news-date {{ font-size: 0.9em; opacity: 0.9; }}
    .news-title {{ padding: 20px 20px 15px 20px; }}
    .news-title h3 {{ margin: 0; color: #333; font-size: 1.3em; line-height: 1.4; }}
    .news-content {{ padding: 0 20px 20px 20px; color: #666; line-height: 1.6; font-size: 0.95em; }}
    .news-content mark {{ background: #FFD700; padding: 2px 4px; border-radius: 3px; }}
    
    /* Details/Summary Styling */
    .news-details {{ margin: 0; }}
    .news-details summary {{ display: none; }}
    .content-preview {{ }}
    .content-full {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0; animation: fadeIn 0.3s ease; display: none; }}
    .news-details[open] .content-full {{ display: block; }}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .news-footer {{ padding: 15px 20px 20px 20px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f0f0f0; }}
    .news-source {{ color: #888; font-size: 0.85em; }}
    
    /* Read More Button Styling */
    .read-more-btn {{ 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white; 
        padding: 8px 16px; 
        border-radius: 20px; 
        font-size: 0.85em; 
        font-weight: 500;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        user-select: none;
    }}
    .read-more-btn:hover {{ 
        transform: scale(1.05); 
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    
    .news-summary {{ background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #FF6B6B; text-align: center; }}
    .summary-stats {{ display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px; }}
    .stat-item {{ color: #666; font-size: 0.9em; font-weight: 500; }}
    .no-results {{ color: #e74c3c; text-align: center; padding: 20px; background: #f8d7da; border-radius: 10px; margin: 20px auto; max-width: 600px; }}
    @media (max-width: 768px) {{ .news-grid {{ grid-template-columns: 1fr; }} .summary-stats {{ flex-direction: column; text-align: center; }} }}
</style>

<div class="news-container">
    <div class="news-header">
        <h2>📰 {title}</h2>
        <p class="news-subtitle">{f'พบ {len(news_list)} ข่าวที่เกี่ยวข้อง' if keyword else 'ข่าวล่าสุดจาก thsport.live'}</p>
    </div>
    
    <div class="news-grid">
        {cards_html}
    </div>
    
    <div class="news-summary">
        <div class="summary-stats">
            <span class="stat-item">📊 จำนวนข่าว: {len(news_list)} ข่าว</span>
            <span class="stat-item">📱 ข้อมูลจาก thsport.live</span>
            <span class="stat-item">🕐 อัปเดตล่าสุด: {news_list[0]['date'] if news_list else ''}</span>
        </div>
    </div>
</div>'''
        
        return html_content
    
    def generate_news_response(self, user_message: str) -> str:
        """สร้างการตอบกลับข่าวตามข้อความของผู้ใช้"""
        try:
            msg = user_message.lower().strip()
            
            # ตรวจสอบว่าผู้ใช้ค้นหาข่าวเฉพาะเจาะจง
            if any(keyword in msg for keyword in ['ข่าว', 'news', 'ข่าวสาร', 'อัพเดท', 'บอลวันนี้', 'ข่าววันนี้']):
                # หาคำค้นหา
                keywords = []
                search_terms = ['แมนยู', 'ลิเวอร์พูล', 'แมนซิตี้', 'เชลซี', 'อาร์เซนอล', 'สเปอร์ส', 'เรอัลมาดริด', 'บาร์เซโลนา', 'พรีเมียร์ลีก', 'ลาลิกา', 'บุนเดสลีกา', 'เซเรียอา', 'ลีกเอิง']
                
                for term in search_terms:
                    if term in msg:
                        keywords.append(term)
                
                if keywords:
                    # ค้นหาข่าวตาม keyword แรกที่พบ
                    news_list = self.search_news_by_keyword(keywords[0], limit=10)
                    return self.create_news_html(news_list, f"ข่าว{keywords[0]}", keywords[0])
                else:
                    # แสดงข่าวล่าสุด
                    news_list = self.get_latest_news(limit=10)
                    return self.create_news_html(news_list, "ข่าวฟุตบอลล่าสุด")
            
            # ถ้าไม่ใช่คำขอข่าว ให้แสดงข่าวทั่วไป
            news_list = self.get_latest_news(limit=5)
            return self.create_news_html(news_list, "ข่าวฟุตบอล")
            
        except Exception as e:
            print(f"❌ Error in generate_news_response: {str(e)}")
            return f"<div class='error'>เกิดข้อผิดพลาดในการดึงข่าว: {str(e)}</div>"
    
    def clean_text(self, text: str) -> str:
        """ทำความสะอาดข้อความและลบ surrogate characters"""
        try:
            # ลบ surrogate characters
            text = re.sub(r'[\ud800-\udfff]', '', text)
            
            # แทนที่ emoji ที่อาจมีปัญหาด้วยข้อความ
            text = re.sub(r'[\U0001f600-\U0001f64f]', '😊', text)  # emoticons
            text = re.sub(r'[\U0001f300-\U0001f5ff]', '⚽', text)  # symbols & pictographs
            text = re.sub(r'[\U0001f680-\U0001f6ff]', '🚀', text)  # transport & map
            text = re.sub(r'[\U0001f1e0-\U0001f1ff]', '🏳️', text)  # flags
            
            # ทำความสะอาดช่องว่างเพิ่มเติม
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            print(f"Warning: Error cleaning text: {e}")
            # ถ้าทำความสะอาดไม่ได้ ให้ใช้วิธีแบบง่าย
            return ''.join(char for char in text if ord(char) < 65536)
    
    def safe_read_file(self, file_path: Path) -> str:
        """อ่านไฟล์อย่างปลอดภัยโดยจัดการ encoding และ surrogate characters"""
        encodings = ['utf-8', 'utf-8-sig', 'cp874', 'tis-620', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read().strip()
                    # ทำความสะอาดข้อความ
                    content = self.clean_text(content)
                    return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                print(f"Error reading file {file_path} with {encoding}: {e}")
                continue
        
        # ถ้าอ่านไม่ได้ทุกวิธี ให้อ่านแบบ binary แล้วแปลง
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # ลองแปลงเป็น string โดยข้าม error
                content = content.decode('utf-8', errors='ignore')
                content = self.clean_text(content)
                return content
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return ""
