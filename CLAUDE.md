# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
# Start the Streamlit web app (opens in browser at http://localhost:8501)
.venv/bin/streamlit run rent_vs_sell.py
```

All inputs are sidebar widgets — adjusting any value re-runs the analysis and redraws the chart instantly. A "Download CSV" button exports the results.

## Dependencies

streamlit and matplotlib are installed in `.venv/`. The stdlib (`csv`, `io`) covers everything else. To add a package: `.venv/bin/pip install <package>`.

## Architecture

Single-file script (`rent_vs_sell.py`) with four sections:

**Inputs** — all scenario variables are Streamlit sidebar widgets at the top of the file. Adjusting any widget triggers an immediate re-run.

**Mortgage helpers** — two pure functions: `calc_monthly_payment` (standard amortization formula) and `calc_remaining_balance` (closed-form balance after k payments).

**Core simulation** (`run_analysis`) — month-by-month loop over `PROJECTION_YEARS * 12` months. Tracks two parallel scenarios:
- *Sell*: net proceeds (`home_value − remaining_balance − closing_costs`) compound at `INVESTMENT_RETURN`
- *Rent*: house value appreciates, mortgage amortizes, net monthly cash flow (`rent − mortgage_pmt − operating_costs`) is reinvested at `CASHFLOW_RETURN` (a separate rate from `INVESTMENT_RETURN`). Cash flow automatically switches to `rent − operating_costs` once the mortgage is paid off.

Year-end snapshots are collected via `_row()`, which computes derived fields (`house_equity`, `rent_total_net_worth`, `advantage_rent_over_sell`).

**Output** — `build_figure(rows)` produces a matplotlib figure (three panels: net worth comparison, rent advantage bars, inputs table) rendered via `st.pyplot()`. PNG written to disk on every render. CSV and PNG download buttons at the bottom.

## Key modelling decisions

- `rent_total_net_worth = house_equity + acc_cf` — accumulated cash flows are treated as a separate reinvested pool, not folded into equity.
- `advantage_rent_over_sell` sign depends heavily on `CASHFLOW_RETURN`: negative cash flows (rent < mortgage + ops) compound against the rent scenario at higher rates. At 0% cash flow return the losses accumulate linearly and house equity tends to dominate; at market rates the compounding deficit can flip the outcome.
- `INVESTMENT_RETURN` applies only to the sell scenario's invested proceeds. `CASHFLOW_RETURN` applies only to the accumulated rental cash flow pool (`acc_cf`).
- All rates compound monthly (`(1 + annual_rate)^(1/12) - 1`), not annually.

## Deployment

**Docker (local):**
```bash
docker build -t rental-analysis .
docker run -p 8501:8501 rental-analysis
# App available at http://localhost:8501
```

**Google Cloud Run (live):**
- URL: https://rental-analysis-229545692350.us-central1.run.app
- Project: `rental-analysis-2026`, Region: `us-central1`
- To redeploy after code changes:
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis .
gcloud run deploy rental-analysis --image us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis --platform managed --region us-central1 --allow-unauthenticated --port 8501
```
