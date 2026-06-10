"""
Job Hunter - Scraper Module
Uses SerpAPI to search jobs across multiple platforms for Morocco
"""
import os
import re
import time
from datetime import datetime
from serpapi import GoogleSearch

# Job sources to search across
JOB_SITES = [
    "linkedin.com",
    "bayt.com",
    "rekrute.com",
    "emploi.ma",
    "marocannonces.com",
    "indeed.com",
    "glassdoor.com",
    "monster.com",
]

def build_queries(keywords: str, location: str = "Morocco") -> list[dict]:
    """Build multiple search queries targeting Moroccan job boards."""
    queries = []

    # Generic Google Jobs search
    queries.append({
        "engine": "google_jobs",
        "q": keywords,
        "location": location,
        "hl": "en",
        "gl": "ma",
    })

    # Site-specific searches via Google
    priority_sites = ["linkedin.com", "bayt.com", "rekrute.com", "emploi.ma"]
    for site in priority_sites:
        queries.append({
            "engine": "google",
            "q": f'site:{site} "{keywords}" job Morocco',
            "num": 10,
            "gl": "ma",
            "hl": "en",
        })

    return queries


def search_jobs(api_key: str, keywords: str, location: str = "Morocco") -> list[dict]:
    """Run all queries and return merged, deduplicated job results."""
    all_jobs = []
    seen_urls = set()

    queries = build_queries(keywords, location)

    for query in queries:
        try:
            params = {**query, "api_key": api_key}
            search = GoogleSearch(params)
            results = search.get_dict()

            if query["engine"] == "google_jobs":
                jobs = results.get("jobs_results", [])
                for job in jobs:
                    url = job.get("share_link", job.get("job_id", ""))
                    if url not in seen_urls:
                        seen_urls.add(url)
                        all_jobs.append(_normalize_google_job(job, keywords))

            elif query["engine"] == "google":
                organic = results.get("organic_results", [])
                for r in organic:
                    url = r.get("link", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        job = _normalize_organic_result(r, keywords, query["q"])
                        if job:
                            all_jobs.append(job)

            time.sleep(0.3)  # Respect rate limits

        except Exception as e:
            print(f"[WARN] Query failed: {e}")
            continue

    return rank_jobs(all_jobs, keywords)


def _normalize_google_job(job: dict, keywords: str) -> dict:
    """Normalize a Google Jobs API result."""
    extensions = job.get("detected_extensions", {})
    highlights = job.get("job_highlights", [])
    description = " ".join(
        item for h in highlights for item in h.get("items", [])
    )

    source = job.get("via", "Unknown").replace("via ", "")
    posted = extensions.get("posted_at", "")
    salary = extensions.get("salary", extensions.get("salary_range", ""))
    work_type = extensions.get("work_from_home", False)

    # Get the real direct URL, not the Google redirect
    url = _extract_direct_url(job)

    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": job.get("location", "Morocco"),
        "source": source,
        "url": url,
        "description": description[:500] if description else "",
        "salary": salary,
        "posted_at": posted,
        "work_type": "Remote" if work_type else extensions.get("schedule_type", "On-site"),
        "relevance_score": 0,
        "keywords_matched": [],
        "scraped_at": datetime.utcnow().isoformat(),
    }


def _extract_direct_url(job: dict) -> str:
    """Extract the real job URL instead of Google redirect."""
    # 1. Check apply_options first — these are direct links
    apply_options = job.get("apply_options", [])
    if apply_options:
        # Prefer known job sites over Google
        priority = ["linkedin", "bayt", "rekrute", "emploi", "indeed", "glassdoor", "monster"]
        for preferred in priority:
            for option in apply_options:
                link = option.get("link", "")
                if preferred in link.lower():
                    return link
        # Fall back to first apply option
        first = apply_options[0].get("link", "")
        if first:
            return first

    # 2. Try related_links
    for related in job.get("related_links", []):
        link = related.get("link", "")
        if link and "google.com" not in link:
            return link

    # 3. Last resort — Google share link
    return job.get("share_link", "")


def _normalize_organic_result(result: dict, keywords: str, query: str) -> dict | None:
    """Normalize a Google organic search result into a job dict."""
    title = result.get("title", "")
    snippet = result.get("snippet", "")
    url = result.get("link", "")

    # Filter: only keep if it looks like a job posting
    job_keywords = ["job", "emploi", "poste", "recrutement", "offre", "career", "hiring"]
    combined = (title + snippet).lower()
    if not any(kw in combined for kw in job_keywords):
        return None

    # Detect source from URL
    source = "Unknown"
    for site in JOB_SITES:
        if site in url:
            source = site.replace(".com", "").replace(".ma", "").title()
            break

    return {
        "title": title,
        "company": _extract_company(snippet, result),
        "location": "Morocco",
        "source": source,
        "url": url,
        "description": snippet[:500],
        "salary": "",
        "posted_at": result.get("date", ""),
        "work_type": "Unknown",
        "relevance_score": 0,
        "keywords_matched": [],
        "scraped_at": datetime.utcnow().isoformat(),
    }


def _extract_company(snippet: str, result: dict) -> str:
    """Try to extract company name from snippet."""
    rich = result.get("rich_snippet", {})
    bottom = rich.get("bottom", {})
    detected = bottom.get("detected_extensions", {})
    if "company" in detected:
        return detected["company"]
    # Fallback: use domain name
    url = result.get("link", "")
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return match.group(1).split(".")[0].title() if match else ""


def rank_jobs(jobs: list[dict], keywords: str) -> list[dict]:
    """Score and sort jobs by relevance to the input keywords."""
    kw_list = [k.strip().lower() for k in re.split(r"[,\s]+", keywords) if k.strip()]

    priority_sources = {"linkedin": 3, "bayt": 3, "rekrute": 2, "emploi": 2, "indeed": 1}

    for job in jobs:
        score = 0
        matched = []
        text = f"{job['title']} {job['description']} {job['company']}".lower()

        for kw in kw_list:
            if kw in text:
                matched.append(kw)
                # Title match worth more
                if kw in job["title"].lower():
                    score += 3
                else:
                    score += 1

        # Bonus for known quality sources
        source_lower = job["source"].lower()
        for src, bonus in priority_sources.items():
            if src in source_lower:
                score += bonus
                break

        # Bonus for salary info
        if job.get("salary"):
            score += 2

        # Recency bonus
        posted = job.get("posted_at", "").lower()
        if "today" in posted or "hour" in posted or "1 day" in posted:
            score += 3
        elif "week" in posted and "1 week" in posted:
            score += 1

        job["relevance_score"] = score
        job["keywords_matched"] = matched

    return sorted(jobs, key=lambda x: x["relevance_score"], reverse=True)