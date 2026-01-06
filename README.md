# Lead Lattice - AI Lead Generation Agent

**Live Demo:** [https://leadlattice.streamlit.app/#prioritized-leads](https://leadlattice.streamlit.app/#prioritized-leads)

**Lead Lattice** is an autonomous AI agent that identifies, enriches, and ranks high-value leads for **3D In-Vitro Model** products. It scrapes scientific literature (PubMed) to find researchers actively working on relevant topics (DILI, Organ-on-chip) and scores them based on their likelihood to purchase.

## Features
*   **Real-Time Scraping**: Fetches recent publications from PubMed.
*   **Propensity Scoring**: Ranks leads (0-100) based on Role, Funding, Tech Stack, and Location.
*   **Dual Dashboard**: visualize leads in a premium **Next.js** app or a lightweight **Streamlit** dashboard.
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