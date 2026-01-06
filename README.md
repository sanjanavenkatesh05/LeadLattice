# Lead Lattice - AI Lead Generation Agent

This system autonomously identifies, enriches, and ranks leads for 3D In-Vitro Model therapies.

## Project Structure
- `agent/`: Python-based Probability Engine & Data Generator.
- `dashboard/`: Next.js Web Application for visualization.

## Prerequisites
- Python 3.8+
- Node.js 18+

## Quick Start
### 1. Generate Leads (Agent)
The agent generates 500+ realistic mock leads and ranks them using the "Propensity to Buy" logic.

```bash
cd agent
python main.py
```
This outputs `leads_ranked.json` and automatically simulates the pipeline.

### 2. Run Dashboard
Launch the interface to explore the leads.

```bash
cd dashboard
npm install # If not already installed
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.