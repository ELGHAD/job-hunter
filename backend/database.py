"""
Job Hunter - Database Module
Handles PostgreSQL storage and retrieval of job listings
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    source TEXT,
    url TEXT UNIQUE,
    description TEXT,
    salary TEXT,
    posted_at TEXT,
    work_type TEXT,
    relevance_score INTEGER DEFAULT 0,
    keywords_matched JSONB DEFAULT '[]',
    search_query TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_relevance ON jobs(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_search_query ON jobs(search_query);
"""


class JobDatabase:
    def __init__(self, connection_string: str):
        self.conn_str = connection_string
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(self.conn_str)
        self.conn.autocommit = True

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def setup_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def save_jobs(self, jobs: list[dict], search_query: str) -> int:
        """Insert jobs, skip duplicates by URL. Returns count inserted."""
        if not jobs:
            return 0

        rows = []
        for j in jobs:
            rows.append((
                j.get("title", ""),
                j.get("company", ""),
                j.get("location", ""),
                j.get("source", ""),
                j.get("url", ""),
                j.get("description", ""),
                j.get("salary", ""),
                j.get("posted_at", ""),
                j.get("work_type", ""),
                j.get("relevance_score", 0),
                json.dumps(j.get("keywords_matched", [])),
                search_query,
                j.get("scraped_at", datetime.utcnow().isoformat()),
            ))

        insert_sql = """
            INSERT INTO jobs 
                (title, company, location, source, url, description, salary,
                 posted_at, work_type, relevance_score, keywords_matched, search_query, scraped_at)
            VALUES %s
            ON CONFLICT (url) DO UPDATE SET
                relevance_score = EXCLUDED.relevance_score,
                keywords_matched = EXCLUDED.keywords_matched,
                search_query = EXCLUDED.search_query,
                scraped_at = EXCLUDED.scraped_at
        """

        with self.conn.cursor() as cur:
            execute_values(cur, insert_sql, rows)
            return cur.rowcount

    def get_jobs(self, query: str = None, source: str = None,
                 limit: int = 100, offset: int = 0) -> list[dict]:
        """Retrieve jobs with optional filters."""
        conditions = []
        params = []

        if query:
            conditions.append("(search_query ILIKE %s OR title ILIKE %s OR description ILIKE %s)")
            like = f"%{query}%"
            params.extend([like, like, like])

        if source and source != "all":
            conditions.append("source ILIKE %s")
            params.append(f"%{source}%")

        where = "WHERE " + " AND ".join(conditions) if conditions else ""

        sql = f"""
            SELECT * FROM jobs
            {where}
            ORDER BY relevance_score DESC, scraped_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def get_stats(self) -> dict:
        """Return summary stats for dashboard."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT source) as total_sources,
                    COUNT(DISTINCT company) as total_companies,
                    COUNT(DISTINCT search_query) as total_searches
                FROM jobs
            """)
            stats = dict(cur.fetchone())

            cur.execute("""
                SELECT source, COUNT(*) as count
                FROM jobs
                GROUP BY source
                ORDER BY count DESC
                LIMIT 10
            """)
            stats["by_source"] = [dict(r) for r in cur.fetchall()]

            return stats

    def delete_old_jobs(self, days: int = 30):
        """Clean up jobs older than N days."""
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM jobs WHERE scraped_at < NOW() - INTERVAL '%s days'",
                (days,)
            )
            return cur.rowcount