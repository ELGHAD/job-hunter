# Job Hunter — Smart Job Search Aggregator

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-REST%20API-000000?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SerpAPI-Job%20Discovery-4285F4" alt="SerpAPI" />
  <img src="https://img.shields.io/badge/Frontend-HTML%20%2F%20JavaScript-E34F26?logo=html5&logoColor=white" alt="HTML and JavaScript" />
  <img src="https://img.shields.io/badge/Export-Excel-217346?logo=microsoftexcel&logoColor=white" alt="Excel Export" />
  <img src="https://img.shields.io/badge/License-Not%20specified-lightgrey" alt="License not specified" />
</p>

## Overview

**Job Hunter** is a job search aggregation platform designed to simplify the process of discovering, evaluating, and tracking employment opportunities.

Instead of manually searching across multiple job boards, users can submit a single search query and collect relevant opportunities through SerpAPI-powered search workflows. The application processes the results, removes duplicates, ranks opportunities using a relevance-scoring system, and stores search data for later review.

Built with Python, Flask, and PostgreSQL, the project combines external API integration, data processing, REST API development, database persistence, and structured Excel reporting in one practical application.

It is particularly relevant to job seekers exploring opportunities in Morocco and international markets.

## Key Features

- **Unified Job Discovery:** Collect job listings through a centralized search workflow using SerpAPI.
- **Multi-Source Search:** Combine Google Jobs results with targeted searches for additional job platforms.
- **Relevance Scoring:** Rank opportunities using keyword matches, title relevance, source information, salary availability, and posting freshness.
- **Automatic Deduplication:** Reduce duplicate listings returned by overlapping searches.
- **Persistent Job Data:** Store job listings and related search information in PostgreSQL.
- **Excel Reporting:** Export formatted `.xlsx` reports with clickable links, relevance indicators, and summary statistics.
- **Search History:** Retrieve previous searches and review stored opportunities.
- **REST API:** Expose endpoints for search, export, history, and statistics.
- **Lightweight Web Interface:** Provide a simple HTML and JavaScript interface without a heavy frontend framework.
- **Automation Potential:** Support scheduled searches through external scheduling tools such as cron, when configured.

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Backend | Python, Flask | Application logic and REST API |
| Job discovery | SerpAPI | Retrieve search and job listing results |
| Data processing | Python | Normalize, deduplicate, and rank results |
| Database | PostgreSQL | Persist job listings and search data |
| Excel export | openpyxl, if used by the implementation | Generate formatted spreadsheets |
| Frontend | HTML5, JavaScript, CSS | Search interface and results presentation |
| Configuration | Environment variables | Separate credentials and configuration from source code |

## Architecture

The application separates job discovery, processing, persistence, reporting, and presentation into distinct responsibilities.

```text
                  User
                   |
                   v
            Web Interface
                   |
                   v
             Flask REST API
                   |
                   v
            Search Workflow
                   |
                   v
              SerpAPI
                   |
                   v
       Normalize and Deduplicate
                   |
                   v
          Relevance Scoring
             /          \
            v            v
     PostgreSQL       Excel Export
            |
            v
      Search History
```

This structure makes the main processing steps easier to understand and provides a foundation for future enhancements.

## How the Relevance Scoring Works

A search engine can return many results that are not equally useful to a candidate. Job Hunter adds a ranking step to help users prioritize opportunities.

The described scoring logic considers:

- **Title matching:** Whether the requested skills or keywords appear in the job title.
- **Description matching:** Whether relevant keywords appear in the job description.
- **Source information:** A source-related contribution to the ranking.
- **Salary availability:** Whether salary information is provided.
- **Posting freshness:** How recently the opportunity was published, when the necessary data is available.

The resulting score helps users prioritize listings rather than treating every search result as equally relevant.

The score is a heuristic ranking, not a guarantee that a job is a good fit or that the listing is still available.

## Data Management

Job listings are stored in a structured PostgreSQL table.

The documented data model includes fields such as:

| Field | Description |
|---|---|
| `title` | Job title |
| `company` | Hiring company |
| `location` | Job location |
| `source` | Source associated with the listing |
| `url` | Link to the original opportunity |
| `description` | Available job description |
| `salary` | Salary information, when available |
| `posted_at` | Publication date, when available |
| `work_type` | Work arrangement, when available |
| `relevance_score` | Calculated relevance score |
| `keywords_matched` | Matching search terms |
| `search_query` | Associated search query |
| `scraped_at` | Time the result was collected |

This structure supports search history, result analysis, and subsequent reporting.

## REST API

The application exposes the following documented endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/search` | Search for job opportunities |
| `POST` | `/api/export/excel` | Export results to Excel |
| `GET` | `/api/history` | Retrieve search history |
| `GET` | `/api/stats` | Retrieve database statistics |
| `GET` | `/health` | Check service health |

Request formats, response schemas, and error handling depend on the implementation in the repository.

## Excel Export

Job Hunter turns collected listings into a structured spreadsheet that can be used outside the application.

The documented export features include:

- Clickable links to original job listings.
- Visual indicators based on relevance scores.
- Summary statistics grouped by source.
- Totals and search-related metadata.

This allows users to review, compare, and organize opportunities without remaining inside the web interface.

## Getting Started

### Prerequisites

- Python 3.x
- pip
- A SerpAPI API key
- PostgreSQL for persistent database storage, if enabled by the configuration

### 1. Clone the Repository

```bash
git clone https://github.com/ELGHAD/job-hunter.git
cd job-hunter
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
```

Activate it before installing dependencies.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux or macOS:**

```bash
source .venv/bin/activate
```

Then install the requirements.

### 3. Configure Environment Variables

Copy the example configuration:

```bash
cp .env.example .env
```

On Windows, you can copy the file using:

```powershell
Copy-Item .env.example .env
```

Configure the required values in `.env`, using the names expected by the application. For example:

```dotenv
SERPAPI_KEY=your_serpapi_api_key
DATABASE_URL=your_postgresql_connection_string
```

These are example variable names; verify the repository's configuration before using them.

Never commit your real API key or database credentials.

### 4. Configure PostgreSQL

If PostgreSQL persistence is enabled, create the database:

```sql
CREATE DATABASE jobhunter;
```

Set the database connection string in your environment configuration. Initialize the schema according to the application's database implementation.

### 5. Start the Backend

From the repository root:

```bash
cd backend
python app.py
```

The documented local address is:

```text
http://localhost:5050
```

Use the host and port configured in the application if they differ.

### 6. Open the Frontend

From the repository root, serve the frontend directory:

```bash
python -m http.server 3000 --directory frontend
```

Open the following address in your browser:

```text
http://localhost:3000
```

If the frontend and backend use different ports, ensure that the frontend is configured to call the correct API address and that cross-origin requests are handled appropriately.

## Project Structure

```text
job-hunter/
├── backend/
│   ├── app.py
│   ├── scraper.py
│   ├── database.py
│   └── excel_export.py
├── frontend/
│   └── index.html
├── exports/
├── .env.example
├── requirements.txt
└── README.md
```

The structure shown above reflects the documented project layout. Generated exports and other runtime files may vary depending on configuration.

## Security and Reliability

The project uses environment-based configuration to separate API credentials from application code and separates major responsibilities into distinct modules.

For a more production-ready deployment, the following areas deserve attention:

- Validate search inputs and limit query sizes.
- Handle external API errors, timeouts, and rate limits.
- Add tests for scoring, deduplication, and API responses.
- Protect sensitive endpoints if user-specific data or administrative operations are introduced.
- Use database constraints and appropriate indexes.
- Avoid exposing credentials or internal error details in API responses.
- Respect the terms and access policies of external job platforms and data providers.
- Keep dependencies updated and document deployment configuration.

## Potential Improvements

Future iterations could introduce:

- Saved searches and configurable job alerts.
- Filters for location, work arrangement, seniority, and salary.
- More transparent, configurable relevance scoring.
- A dedicated dashboard for tracking shortlisted opportunities.
- User accounts and personalized search preferences.
- Automated integration and unit tests.
- Docker-based deployment and continuous integration.
- A deployment-ready configuration with monitoring and structured logging.

These are possible extensions rather than claims about current functionality.

## Author

**ELGHAD**

- GitHub: https://github.com/ELGHAD
- Repository: https://github.com/ELGHAD/job-hunter

