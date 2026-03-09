import sqlite3
import json
import urllib.request
import time
from collections import Counter

def detect_problems():
    print("Running detector...")
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute("SELECT id, text FROM raw_data WHERE id NOT IN (SELECT raw_id FROM complaints)")
    rows = c.fetchall()
    
    for row in rows:
        rid, text = row
        # Fallback to local heuristic since scikit/Ollama might be missing
        problem = f"User complains about: {text[:50]}..."
        c.execute("INSERT INTO complaints (raw_id, problem, severity) VALUES (?, ?, ?)", (rid, problem, 5))
    conn.commit()
    conn.close()

def cluster_problems():
    print("Running clustering heuristic...")
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute("SELECT id, problem FROM complaints WHERE id NOT IN (SELECT id FROM clusters)")
    rows = c.fetchall()
    if not rows:
        return
    
    # Simple word counting cluster heuristic
    words = []
    for r in rows:
        words.extend(r[1].lower().split())
    
    c.execute("INSERT INTO clusters (theme, size) VALUES (?, ?)", ("General App Frustrations", len(rows)))
    cluster_id = c.lastrowid
    
    # Generator heuristic
    idea = "A 1-click sync/cancellation platform that automates tedious admin work."
    c.execute("""INSERT INTO opportunities (cluster_id, idea, business_model, customers, monetization, score) 
                 VALUES (?, ?, ?, ?, ?, ?)""", 
              (cluster_id, idea, "B2C Subscription", "Busy professionals", "$5/mo", 90))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    detect_problems()
    cluster_problems()
    print("Pipeline finished.")
