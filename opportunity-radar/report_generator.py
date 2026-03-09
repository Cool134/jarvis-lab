import sqlite3

conn = sqlite3.connect('radar.db')
c = conn.cursor()

raw_data_count = c.execute('SELECT COUNT(*) FROM raw_data').fetchone()[0]
complaints_count = c.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]
opportunities_count = c.execute('SELECT COUNT(*) FROM opportunities').fetchone()[0]

print(f'Total Raw Data Scraped: {raw_data_count}')
print(f'Total Complaints Identified: {complaints_count}')
print(f'Total Startup Opportunities Generated: {opportunities_count}')

print('\n--- Top 5 Startup Opportunities (Ranked by AI Score) ---')
opps = c.execute('SELECT idea, business_model, customers, monetization, score FROM opportunities ORDER BY score DESC LIMIT 5').fetchall()

if not opps:
    print("No opportunities found yet. The AI is still processing the backlog or faced issues.")
else:
    for i, opp in enumerate(opps):
        print(f'\n{i+1}. Idea: {opp[0]}')
        print(f'   Business Model: {opp[1]}')
        print(f'   Target Customers: {opp[2]}')
        print(f'   Monetization: {opp[3]}')
        print(f'   Score: {opp[4]}/100')

conn.close()
