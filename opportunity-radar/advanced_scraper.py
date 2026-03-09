import urllib.request
import json
import sqlite3
import time
import subprocess
import random

def fetch_github_issues():
    count = 0
    queries = [
        '"feature request" is:issue state:open',
        '"wish there was a tool" is:issue state:open',
        '"is there a way to automate" is:issue state:open'
    ]
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    headers = {'User-Agent': 'OpportunityRadar/1.0', 'Accept': 'application/vnd.github.v3+json'}
    
    for q in queries:
        try:
            url = f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&sort=created&order=desc&per_page=10"
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            
            for item in data.get('items', []):
                title = item.get('title', '')
                body = item.get('body', '') or ''
                text = f"{title}\n{body}"
                url = item.get('html_url', '')
                if len(text.strip()) > 30:
                    c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (url, text[:5000]))
                    count += 1
        except Exception as e:
            print(f"GitHub Error for query '{q}': {e}")
            
    conn.commit()
    conn.close()
    return count

def fetch_hn():
    count = 0
    try:
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json")
        resp = urllib.request.urlopen(req, timeout=10)
        story_ids = json.loads(resp.read())[:15]
        conn = sqlite3.connect('radar.db')
        c = conn.cursor()
        for sid in story_ids:
            try:
                item_req = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                item_resp = urllib.request.urlopen(item_req, timeout=5)
                item = json.loads(item_resp.read())
                if not item: continue
                title = item.get('title', '')
                text = item.get('text', '')
                content = f"{title}\n{text}"
                url = f"https://news.ycombinator.com/item?id={sid}"
                if len(content.strip()) > 20:
                    c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (url, content))
                    count += 1
            except Exception as e:
                pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"HN Error: {e}")
    return count

def run_pipeline():
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running detection & clustering pipeline...")
        subprocess.run(["python3", "pipeline.py"])
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    for _ in range(6): # remaining cycles
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Advanced Scan (GitHub, HN)...")
        c_gh = fetch_github_issues()
        c_hn = fetch_hn()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraped {c_gh} GitHub issues and {c_hn} HN posts.")
        run_pipeline()
        time.sleep(1800)
