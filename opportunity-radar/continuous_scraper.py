import urllib.request
import json
import sqlite3
import time
import os
import subprocess

def fetch_hn():
    try:
        # Fetch Top Stories from Hacker News
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json")
        resp = urllib.request.urlopen(req)
        story_ids = json.loads(resp.read())[:30] # Top 30 stories
        
        conn = sqlite3.connect('radar.db')
        c = conn.cursor()
        count = 0
        
        for sid in story_ids:
            try:
                item_req = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                item_resp = urllib.request.urlopen(item_req)
                item = json.loads(item_resp.read())
                
                if not item: continue
                
                title = item.get('title', '')
                text = item.get('text', '')
                content = f"{title}\n{text}"
                
                if len(content.strip()) > 10:
                    c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (f"hackernews/{sid}", content))
                    count += 1
            except Exception as e:
                pass
        
        conn.commit()
        conn.close()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraped {count} items from Hacker News.")
    except Exception as e:
        print(f"HN Error: {e}")

def run_pipeline():
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running detection & clustering pipeline...")
        subprocess.run(["python3", "pipeline.py"])
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    print("Starting continuous Opportunity Radar scraper...")
    # Run every 30 minutes for 3.5 hours (7 iterations)
    for _ in range(7):
        fetch_hn()
        run_pipeline()
        time.sleep(1800) # Sleep for 30 minutes
