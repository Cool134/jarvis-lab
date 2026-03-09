from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
import uvicorn
import os

app = FastAPI()
os.makedirs("templates", exist_ok=True)

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Opportunity Radar</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <h1 class="text-3xl font-bold mb-6">Opportunity Radar</h1>
    <div class="grid grid-cols-1 gap-6">
        {% for opp in opportunities %}
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-2">{{ opp.idea }}</h2>
            <p><strong>Business Model:</strong> {{ opp.model }}</p>
            <p><strong>Target Customers:</strong> {{ opp.customers }}</p>
            <p><strong>Monetization:</strong> {{ opp.monetization }}</p>
            <p><strong>Score:</strong> {{ opp.score }}/100</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""
with open("templates/index.html", "w") as f:
    f.write(html_content)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = sqlite3.connect('radar.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT idea, business_model as model, customers, monetization, score FROM opportunities")
    rows = c.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "opportunities": rows})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
