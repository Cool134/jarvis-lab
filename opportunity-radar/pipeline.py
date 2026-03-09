import sqlite3
import json
import subprocess
import time

def run_ai_batch():
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    
    while True:
        c.execute("SELECT id, text FROM raw_data WHERE id NOT IN (SELECT raw_id FROM complaints) LIMIT 10")
        rows = c.fetchall()
        if not rows:
            print("No new data to process.")
            break
            
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Processing batch of {len(rows)} complaints via Gemini API...")
        
        # Mark as processed
        for row in rows:
            c.execute("INSERT INTO complaints (raw_id, problem, severity) VALUES (?, ?, ?)", (row[0], "Batched", 5))
        conn.commit()
        
        # Build prompt
        complaints_text = "\n---\n".join([f"Complaint {r[0]}: {r[1][:1000]}" for r in rows])
        prompt = f"""You are a top-tier startup scout. Read these complaints scraped from GitHub and Hacker News:
{complaints_text}

Identify the 2 best B2B SaaS or startup opportunities hidden in these complaints.
Output ONLY a JSON array with this exact structure, no markdown formatting at all:
[
  {{
    "idea": "Brief name/concept",
    "business_model": "SaaS / Pay-per-use etc",
    "customers": "Who pays for this",
    "monetization": "How it makes money",
    "score": 95
  }}
]"""
        
        try:
            result = subprocess.run(
                ["openclaw", "agent", "--agent", "main", "--message", prompt, "--json", "--thinking", "off"],
                capture_output=True, text=True, timeout=120
            )
            
            response_json = json.loads(result.stdout)
            payloads = response_json.get("result", {}).get("payloads", [])
            if not payloads:
                continue
            
            ai_text = payloads[0].get("text", "[]")
            ai_text = ai_text.strip("```json").strip("```").strip()
                
            opportunities = json.loads(ai_text)
            
            for opp in opportunities:
                c.execute("""INSERT INTO opportunities (cluster_id, idea, business_model, customers, monetization, score) 
                             VALUES (?, ?, ?, ?, ?, ?)""", 
                          (0, opp.get("idea", "Unknown"), opp.get("business_model", "Unknown"), 
                           opp.get("customers", "Unknown"), opp.get("monetization", "Unknown"), opp.get("score", 50)))
                print(f"Generated Opportunity: {opp.get('idea')} (Score: {opp.get('score')})")
                
        except Exception as e:
            print(f"AI Batch Error: {e}")
            
        conn.commit()
        time.sleep(2) # rate limit protection

    conn.close()

if __name__ == "__main__":
    run_ai_batch()
