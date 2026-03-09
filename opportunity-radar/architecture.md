# Opportunity Radar - Architecture Plan

## Overview
Opportunity Radar is an autonomous pipeline that scrapes complaints from the web, processes them using a local LLM, clusters recurring issues, and generates actionable startup ideas presented on a web dashboard.

## Components
1. **Scraping Engine (`scraper.py`)**: 
   - Fetches data from Reddit (via JSON/PRAW) and App Stores.
   - Saves raw text to SQLite.
2. **Problem Detector (`detector.py`)**:
   - Polls SQLite for unprocessed text.
   - Calls Ollama (Local LLM) to classify if the text contains a valid "complaint" or "unsolved problem".
3. **Clustering Engine (`cluster.py`)**:
   - Uses TF-IDF and KMeans (or embeddings) to group similar complaints into macro-problems.
4. **Opportunity Generator (`generator.py`)**:
   - Passes clustered problems to Ollama.
   - Generates Startup Idea, Business Model, Target Customers, and Monetization.
   - Scores the opportunity based on cluster size and LLM severity analysis.
5. **Web Dashboard (`main.py` & `templates/`)**:
   - FastAPI backend serving a simple HTML/Tailwind dashboard.
   - Reads final opportunities from SQLite.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **Database:** SQLite (`radar.db`)
- **AI/LLM:** Ollama (local) via `requests`
- **NLP/Clustering:** `scikit-learn`
- **Frontend:** HTML, Jinja2, TailwindCSS (CDN)

## Database Schema (`schema.sql`)
- `raw_data` (id, source, text, timestamp)
- `complaints` (id, raw_id, extracted_problem, severity)
- `clusters` (id, theme, size)
- `opportunities` (id, cluster_id, idea, business_model, customers, monetization, score)
