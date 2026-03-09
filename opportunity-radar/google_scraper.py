import urllib.request
import json
import sqlite3
import time
import subprocess
import random

def scrape_reddit(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=15"
    # Randomize User-Agent to bypass 403 blocks occasionally
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    ]
    req = urllib.request.Request(url, headers={'User-Agent': random.choice(user_agents)})
    count = 0
    try:
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        conn = sqlite3.connect('radar.db')
        c = conn.cursor()
        for item in data['data']['children']:
            title = item['data'].get('title', '')
            selftext = item['data'].get('selftext', '')
            text = f"{title}\n{selftext}"
            if len(text.strip()) > 20:
                c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (f"reddit/r/{subreddit}", text))
                count += 1
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Reddit Error ({subreddit}): {e}")
    return count

def fetch_hn():
    count = 0
    try:
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json")
        resp = urllib.request.urlopen(req, timeout=10)
        story_ids = json.loads(resp.read())[:10]
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
                if len(content.strip()) > 20:
                    c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (f"hackernews/{sid}", content))
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
    for _ in range(7):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Scan...")
        c1 = scrape_reddit("SaaS")
        c2 = scrape_reddit("Entrepreneur")
        c3 = scrape_reddit("startups")
        c4 = fetch_hn()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraped {c1+c2+c3+c4} posts.")
        run_pipeline()
        time.sleep(1800) # 30 mins
