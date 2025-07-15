import os
import shutil

# ไฟล์ที่ต้องการลบ
files_to_delete = [
    'API-Football.py',
    'app_backup.py', 
    'app_modular.py',
    'fetch_dooball66k.py',
    'fetch_thsport.py',
    'football_chatbot.py',
    'index.html',
    'OpenAI.py',
    'SportsDB.py',
    'standings_fetcher.py',
    'test_keys.py',
    'test_modules.py',
    'test_news.py',
    'test_run.py',
    'MODULAR_SUMMARY.md'
]

# โฟลเดอร์ที่ต้องการลบ
dirs_to_delete = ['__MACOSX', '__pycache__']

print("🗑️ กำลังลบไฟล์ที่ไม่ต้องการ...")

# ลบไฟล์
for file in files_to_delete:
    try:
        if os.path.exists(file):
            os.remove(file)
            print(f'✅ ลบไฟล์ {file} สำเร็จ')
        else:
            print(f'⚠️ ไม่พบไฟล์ {file}')
    except Exception as e:
        print(f'❌ ไม่สามารถลบไฟล์ {file}: {e}')

# ลบโฟลเดอร์
for dir_name in dirs_to_delete:
    try:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f'✅ ลบโฟลเดอร์ {dir_name} สำเร็จ')
        else:
            print(f'⚠️ ไม่พบโฟลเดอร์ {dir_name}')
    except Exception as e:
        print(f'❌ ไม่สามารถลบโฟลเดอร์ {dir_name}: {e}')

print('🎉 เสร็จสิ้น!')
