import sqlite3

mock_data = [
    ("reddit", "I hate how hard it is to sync my calendar with my wife's. We keep double booking."),
    ("app_store", "This budgeting app is so complex. I just want something that links to my bank and categorizes automatically without 50 steps."),
    ("forum", "Why is it impossible to find a reliable local plumber? Every site is just lead gen spam."),
    ("reddit", "Managing subscriptions is a nightmare. I just realized I paid for a gym for 3 months without going because cancelling is so hard."),
    ("app_store", "The UI on this CRM is from 2005. Tracking customer emails takes 10 clicks when it should take 1."),
]

conn = sqlite3.connect('radar.db')
c = conn.cursor()
for source, text in mock_data:
    c.execute("INSERT INTO raw_data (source, text) VALUES (?, ?)", (source, text))
conn.commit()
conn.close()
print("Seeded mock data for pipeline testing.")
