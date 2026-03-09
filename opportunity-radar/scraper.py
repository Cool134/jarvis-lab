import urllib.request
import json
import sqlite3

def scrape_reddit(subreddit="Entrepreneur"):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=15"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OpportunityRadar/1.0'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        conn = sqlite3.connect('radar.db')
        c = conn.cursor()
        count = 0
        for item in data['data']['children']:
            title = item['data'].get('title', '')
            selftext = item['data'].get('selftext', '')
            text = f"{title}\n{selftext}"
            c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (f"reddit/r/{subreddit}", text))
            count += 1
        conn.commit()
        conn.close()
        print(f"Scraped {count} items from r/{subreddit}.")
    except Exception as e:
        print(f"Scraping error: {e}")

if __name__ == "__main__":
    scrape_reddit("smallbusiness")
    scrape_reddit("Entrepreneur")
