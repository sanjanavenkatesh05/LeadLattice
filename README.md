# Lead Lattice - AI Lead Generation Agent

**Live Demo:** [https://leadlattice.streamlit.app/#prioritized-leads](https://leadlattice.streamlit.app/#prioritized-leads)

**Lead Lattice** is an autonomous AI agent that identifies, enriches, and ranks high-value leads for **3D In-Vitro Model** products. It scrapes scientific literature (PubMed) to find researchers actively working on relevant topics (DILI, Organ-on-chip) and scores them based on their likelihood to purchase.

## Features
*   **Real-Time Scraping**: Fetches recent publications from PubMed.
*   **Propensity Scoring**: Ranks leads (0-100) based on Role, Funding, Tech Stack, and Location.
*   **Dual Dashboard**: visualize leads in a premium **Next.js** app or a lightweight **Streamlit** dashboard.
*   **Scraping Resilience**: handling rate‑limits and request retries for robust data collection.
*   **Stratified Sampling**: Delivers a balanced list of top-tier and mid-tier candidates.

---

## Installation

### 1. Python Environment (Backend)
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Node.js Environment (Dashboard)
Install the frontend dependencies:
```bash
cd dashboard
npm install
cd ..
```

---

## Usage

### Step 1: Generate Leads
You have two modes of operation:

**Option A: Real Data (Recommended)**
Scrapes actual PubMed data, extracts emails/affiliations, and ranks candidates.
```bash
python -m agent.main_real
```
*Output: Generates `dashboard/public/leads_data.json` with ~500 balanced leads.*

**Option B: Mock Data (Testing)**
Generates synthetic data for quick UI testing.
```bash
python -m agent.main
```

### Step 2: View Dashboard (Next.js)
Launch the premium web interface:
```bash
cd dashboard
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** to view the table, sort by Probability, and export to CSV.

### Step 3: Streamlit App (Alternative)
Run the lightweight analytics dashboard:
```bash
streamlit run streamlit_app.py
```

---

## Scraping Mechanics

- **Pagination** – The PubMed API (`esearch.fcgi`) returns up to 20 000 IDs per request. We retrieve all IDs in a single call (using `retmax`) because our keyword list is bounded; for larger queries we would iteratively request subsequent pages via the `retstart` parameter.
- **Rate Limiting & Throttling** – All HTTP calls go through `HttpClient`, which inserts a random delay of **0.5‑1.5 s** before each request (`_rate_limit_delay`). This respects NCBI's recommendation of ≤3 requests‑per‑second.
- **Retry Logic** – `HttpClient` uses `urllib3.Retry` with **exponential back‑off** (factor 0.5) and retries up to **3 times** for transient status codes (429, 500‑504). Failed attempts are logged but do not abort the whole run.
- **Error Handling** – Missing fields (e.g., no email or affiliation) are safely omitted; the parser falls back to empty lists. XML parsing (`xml.etree.ElementTree`) is robust to malformed elements – any parsing exception skips that article and continues.
- **Structured Parsing** – Responses are JSON (`esearch`) for IDs and XML (`efetch`) for article details. We use `ElementTree` to extract `<ArticleTitle>`, `<Author>`, `<Affiliation>`, and `<PMID>` nodes, avoiding fragile regex string matches.

---

## Architecture / Data Flow Diagram
```mermaid
flowchart TD
    A[Keyword List] -->|Search| B[PubMed esearch API]
    B --> C[PMID List]
    C -->|Batch fetch| D[PubMed efetch (XML)]
    D --> E[Parse & Extract Lead Data]
    E --> F[Score & Rank (ProbabilityEngine)]
    F --> G[Dashboard JSON Output]
    G --> H{Dashboard UI}
    H -->|Next.js| I[Premium Web App]
    H -->|Streamlit| J[Lightweight UI]
```

---

## Scale & Performance Numbers
- **Typical Run**: ~500 leads are generated in **≈2 minutes** on a standard laptop (Intel i7, 16 GB RAM).
- **API Calls**: 1 `esearch` call + **≈20** `efetch` POST calls (chunks of 200 IDs) → **≈21** HTTP requests per run.
- **Concurrency**: Current implementation is **synchronous**; the `HttpClient` rate‑limit delay ensures we stay within NCBI guidelines. Future versions could adopt `asyncio`/`aiohttp` for parallel chunk fetching while still respecting the per‑second limit.

---

## Reliability / Failure Handling
- **PubMed Service Outage** – If the `esearch` or `efetch` endpoint returns a non‑retryable error, the scraper logs the issue and exits gracefully, leaving any previously fetched leads untouched.
- **Partial/Corrupt Records** – Articles missing titles, authors, or affiliations are skipped with a warning; the pipeline continues.
- **Network Timeouts** – Handled by the retry strategy; after maximum retries the request is aborted and the affected chunk is omitted.
- **Logging** – All errors and retry attempts are printed to stdout; in production you can redirect to a log file or monitoring system.

---

## Explicit Tech Stack Table
| Layer | Library / Tool | Purpose |
|---|---|---|
| **HTTP / Rate‑Limiting** | `requests` + `urllib3.Retry` | Robust HTTP client with retries & back‑off |
| **XML Parsing** | `xml.etree.ElementTree` | Parse PubMed efetch XML responses |
| **Data Modeling** | `pydantic` (via `Lead`, `Company` models) | Validation & easy JSON export |
| **Scoring** | Custom `ProbabilityEngine` (pure Python) | Rank leads by heuristic scores |
| **Dashboard** | **Next.js** (React) + **Vercel** | Premium UI |
|  | **Streamlit** | Lightweight analytics UI |
| **Packaging** | `python -m` entrypoints | CLI execution |
| **Continuous Integration** | GitHub Actions | Run tests on each push |

---

## Testing & Validation
- **Manual Spot‑Check** – Ran the scraper on **10 known researcher profiles** and verified that extracted emails and affiliations matched the PubMed records.
- **Unit Tests** – `tests/test_pubmed_scraper.py` validates pagination handling, XML parsing of a sample article, and proper fallback when affiliation data is missing.
- **Continuous Integration** – GitHub Actions run the test suite on every push to ensure future changes don’t break the scraping logic.

---

## Scoring Logic
The AI assigns points based on the following weighted signals (Max 100):

| Category | Criteria | Points |
| :--- | :--- | :--- |
| **Scientific Intent** | Published on **DILI**, **3D Culture**, **Organ-on-chip** | **+40** (Very High) |
| **Role Fit** | Title/Dept contains **Toxicology**, **Safety**, **Hepatic** | **+30** (High) |
| **Company Intent** | Recent **Series A/B** Funding | **+20** (High) |
| **Technographic** | Uses **In-Vitro** methods (+15) and Open to **NAMs** (+10) | **+25** (Medium) |
| **Location** | Located in a Biotech Hub (Boston, Basel, UK, etc.) | **+10** (Medium) |

*Leads with a score > 80 are marked as **Highest Priority**.*