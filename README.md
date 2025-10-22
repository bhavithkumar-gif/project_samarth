# Project Samarth — Prototype Q&A (Streamlit)

## What this prototype does
Implements one core intent:
- Compare average annual rainfall between two states for last N years and list top M crops by production in each state across the same years.
Outputs include numerical results and per-claim citation (the CSV filename used).

## Setup
1. Create a venv and install requirements:
   python -m venv venv
   source venv/bin/activate   (on Windows: venv\\Scripts\\activate)
   pip install -r requirements.txt

2. (Optional) Discover & download live datasets:
   python discover_and_download.py
   This will try to fetch crop production and rainfall CSVs into `data/`. If that fails, the app will fall back to `sample_outputs/`.

3. Run the Streamlit app:
   streamlit run app.py

## Demo / Loom recording tip
- Use `sample_outputs/` CSVs for a stable demo.
- Pre-type the inputs in the sidebar (State X/Y, N, M).
- Click "Run" and show the results and CSV download button.

## Datasets referenced
- District-wise season-wise crop production statistics (data.gov.in). :contentReference[oaicite:2]{index=2}
- Rainfall (IMD) — monthwise & subdivision rainfall (data.gov.in). :contentReference[oaicite:3]{index=3}
