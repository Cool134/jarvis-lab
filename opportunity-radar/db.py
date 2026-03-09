import sqlite3

def init_db():
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS raw_data (id INTEGER PRIMARY KEY, source TEXT, text TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY, raw_id INTEGER, problem TEXT, severity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clusters (id INTEGER PRIMARY KEY, theme TEXT, size INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS opportunities (id INTEGER PRIMARY KEY, cluster_id INTEGER, idea TEXT, business_model TEXT, customers TEXT, monetization TEXT, score INTEGER)''')
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
