
import requests
from bs4 import BeautifulSoup
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin


def get_valid_filename(title):
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    filename = filename.replace(' ', '_')
    return filename[:100] + '.txt'


def create_data_directory():
    if not os.path.exists('data'):
        os.makedirs('data')

def scrape_news_links(base_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/football/news-' in href:
                full_url = urljoin(base_url, href)
                article_links.append(full_url)
        return list(set(article_links))
    except Exception as e:
        print(f"Error scraping main page: {e}")
        return []

def scrape_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Untitled"
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            'div.content-detail'
        ]
        content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element.get_text(separator='\n', strip=True)
                break
        if not content:
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        # ดึงวันที่จากข่าว
        date_tag = soup.find('div', class_='date')
        date_str = date_tag.get_text(strip=True) if date_tag else None
        return title_text, content, date_str
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
        return None, None, None

def save_article_to_file(title, content, url):
    try:
        filename = get_valid_filename(title)
        filepath = os.path.join('data', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {filepath}")
    except Exception as e:
        print(f"Error saving file for '{title}': {e}")

def main():
    base_url = "https://www.thsport.live/sport-news/football/"
    # max_news removed: process all articles for the latest date
    print("Creating data directory...")
    create_data_directory()
    all_article_links = []
    for page in range(1, 2):
        if page == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}page-{page}/"
        print(f"Scraping page {page}: {page_url}")
        page_links = scrape_news_links(page_url)
        if not page_links:
            print(f"No links found on page {page}, stopping pagination")
            break
        all_article_links.extend(page_links)
        time.sleep(1)
    article_links = list(set(all_article_links))
    print("Scraping news links...")
    if not article_links:
        print("No article links found. Please check the website structure.")
        return
    print(f"Found {len(article_links)} article links")
    # หา date ล่าสุดจากข่าวในหน้าแรก
    latest_date = None
    date_list = []
    print("ตรวจสอบวันที่ข่าวล่าสุดในหน้าแรก...")
    for url in article_links:
        _, _, date_str = scrape_article_content(url)
        if date_str:
            date_list.append(date_str)
    if date_list:
        # ใช้วันที่ที่พบมากที่สุด (ข่าวใหม่สุดมักจะมีหลายข่าวในวันเดียวกัน)
        from collections import Counter
        latest_date = Counter(date_list).most_common(1)[0][0]
        print(f"จะดึงเฉพาะข่าววันที่: {latest_date}")
    else:
        print("ไม่พบวันที่ข่าวในหน้าแรก จะดึงทุกข่าว")

    for i, url in enumerate(article_links, 1):
        print(f"Processing article {i}/{len(article_links)}: {url}")
        title, content, date_str = scrape_article_content(url)
        # เฉพาะข่าวที่ตรงกับวันที่ล่าสุด
        if latest_date and date_str and date_str != latest_date:
            print(f"ข้ามข่าว (ไม่ใช่วันที่ล่าสุด): {date_str}")
            continue
        if title and content:
            save_article_to_file(title, content, url)
        else:
            print(f"Failed to extract content from {url}")
        time.sleep(1)
    print("Scraping completed!")

if __name__ == "__main__":
    main()
