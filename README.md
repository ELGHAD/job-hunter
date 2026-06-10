# 🇲🇦 Job Hunter Morocco

A job aggregator that searches **LinkedIn, Bayt, Rekrute, Emploi.ma, Indeed, Glassdoor** and more — all from one place. Results are ranked by relevance to your skills, exported to Excel, and stored in PostgreSQL.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env and add your SERPAPI_KEY
```

Get your **free SerpAPI key** at [serpapi.com](https://serpapi.com) — free plan gives 100 searches/month.

### 3. Set up PostgreSQL (optional but recommended)
```sql
CREATE DATABASE jobhunter;
```
Then update `DATABASE_URL` in your `.env` file. The app auto-creates tables on first run.



### 4. Start the backend
```bash
cd backend
python app.py
```
Backend runs at `http://localhost:5050`

### 5. Open the frontend
Open `frontend/index.html` in your browser directly, or serve it:
```bash
# With Python
python -m http.server 3000 --directory frontend
# Then visit http://localhost:3000
```

---

## 📁 Project Structure
```
job_hunter/
├── backend/
│   ├── app.py            # Flask API server
│   ├── scraper.py        # SerpAPI job searching + ranking
│   ├── database.py       # PostgreSQL storage
│   └── excel_export.py   # Formatted .xlsx export
├── frontend/
│   └── index.html        # Single-page UI
├── exports/              # Generated Excel files
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔍 How It Works

1. You enter skills/technologies (e.g. `React Node.js`)
2. The scraper builds **multiple SerpAPI queries**:
   - Google Jobs API (hits LinkedIn, Glassdoor, Indeed natively)
   - Targeted `site:bayt.com`, `site:rekrute.com`, `site:emploi.ma` queries
3. Results are **deduplicated** and **ranked** by:
   - Keyword match in title (+3) vs description (+1)
   - Source quality bonus (LinkedIn/Bayt: +3, Rekrute/Emploi.ma: +2)
   - Salary info present (+2)
   - Recency (today/hour: +3, this week: +1)
4. Saved to **PostgreSQL** for history
5. Exportable to **formatted Excel** with color-coded relevance

---

## 🌐 Supported Sites
| Site | Method |
|------|--------|
| LinkedIn | Google Jobs API |
| Bayt.com | Google Jobs + site: search |
| Rekrute.com | site: search |
| Emploi.ma | site: search |
| Indeed | Google Jobs API |
| Glassdoor | Google Jobs API |
| Monster | Google Jobs API |

---

## 📊 Excel Export
The exported `.xlsx` includes:
- **Job Listings sheet**: clickable Apply links, color-coded relevance scores, salary, work type
- **Summary sheet**: stats by source, totals, search metadata

---

## 🗄️ Database Schema
```sql
jobs (id, title, company, location, source, url, description,
      salary, posted_at, work_type, relevance_score,
      keywords_matched, search_query, scraped_at)
```

---

## 🔑 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Search jobs |
| POST | `/api/export/excel` | Download Excel |
| GET  | `/api/history` | Past searches from DB |
| GET  | `/api/stats` | DB statistics |
| GET  | `/health` | Health check |

---

## 💡 Tips
- Use comma-separated skills for broader search: `Python, Django, REST API`
- The relevance **score badge** on each card (0–15+) tells you how well it matches
- Green border = high match (≥7), good to apply first
- Set up a cron job to auto-search daily and build a DB of opportunities