"""
Job Hunter - Flask API Server
REST endpoints for the frontend
"""
import os
import sys
import ssl
import urllib3
import requests

# Fix SSL for corporate/work machines
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_original_request = requests.Session.request
def _patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)
requests.Session.request = _patched_request

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Add backend dir to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper import search_jobs
from excel_export import export_to_excel

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_ENABLED = False
db_instance = None

def _get_db():
    global db_instance, DB_ENABLED
    if DB_ENABLED and db_instance is not None:
        return db_instance
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            from database import JobDatabase
            db_instance = JobDatabase(db_url)
            db_instance.connect()
            db_instance.setup_schema()
            DB_ENABLED = True
            return db_instance
        except Exception as e:
            print(f"[DB] Could not connect: {e}")
    return None


@app.route("/api/search", methods=["POST"])
def search():
    data     = request.get_json()
    keywords = data.get("keywords", "").strip()
    location = data.get("location", "Morocco").strip()
    api_key  = data.get("api_key") or os.getenv("SERPAPI_KEY", "")

    if not keywords:
        return jsonify({"error": "keywords required"}), 400
    if not api_key:
        return jsonify({"error": "SerpAPI key required"}), 400

    try:
        jobs = search_jobs(api_key, keywords, location)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    db = _get_db()
    if db:
        try:
            db.save_jobs(jobs, keywords)
        except Exception as e:
            print(f"[DB] Save failed: {e}")

    return jsonify({
        "jobs": jobs,
        "total": len(jobs),
        "keywords": keywords,
        "location": location,
    })


@app.route("/api/export/excel", methods=["POST"])
def export_excel():
    data     = request.get_json()
    jobs     = data.get("jobs", [])
    keywords = data.get("keywords", "jobs")

    if not jobs:
        return jsonify({"error": "No jobs to export"}), 400

    exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    filepath = export_to_excel(jobs, keywords, exports_dir)

    return send_file(
        filepath,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=os.path.basename(filepath),
    )


@app.route("/api/history", methods=["GET"])
def history():
    db = _get_db()
    if not db:
        return jsonify({"error": "Database not configured", "jobs": []}), 200

    query  = request.args.get("q")
    source = request.args.get("source")
    limit  = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    try:
        jobs = db.get_jobs(query=query, source=source, limit=limit, offset=offset)
        return jsonify({"jobs": jobs, "total": len(jobs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    db = _get_db()
    if not db:
        return jsonify({"db_enabled": False})
    try:
        return jsonify({**db.get_stats(), "db_enabled": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "db": DB_ENABLED})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    print(f"\n🚀 Job Hunter API running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)