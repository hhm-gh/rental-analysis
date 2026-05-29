# Rental Analysis

A single-page Streamlit app that models the financial trade-off between **selling a home** vs. **renting it out**, projected year-by-year over a configurable horizon.

Live app: https://rental-analysis-229545692350.us-central1.run.app

## What it does

Runs a month-by-month simulation of two parallel scenarios:

- **Sell** — net proceeds (home value − mortgage balance − closing costs) are invested and compound at a configurable return rate
- **Rent** — house appreciates, mortgage amortizes, and monthly net cash flow (rent − mortgage − operating costs) is reinvested separately at its own return rate

Outputs a three-panel chart comparing net worth, the rent advantage over time, and a summary inputs table. Results can be downloaded as CSV or PNG.

## Stack

- Python 3, Streamlit, matplotlib
- Single-file app (`rent_vs_sell.py`) — no database, no backend

## Running locally

```bash
# Using the included venv
.venv/bin/streamlit run rent_vs_sell.py
# App opens at http://localhost:8501
```

Or with Docker:

```bash
docker build -t rental-analysis .
docker run -p 8501:8501 rental-analysis
```

## Key inputs (all adjustable in the sidebar)

| Input | Description |
|---|---|
| Home value | Current market value |
| Mortgage balance + rate | Remaining loan balance and interest rate |
| Monthly rent | Expected rental income |
| Operating costs | Insurance, taxes, maintenance, vacancy, etc. |
| Appreciation rate | Expected annual home price growth |
| Investment return | Return on proceeds if sold |
| Cash flow return | Reinvestment rate on net rental cash flows |
| Projection years | How far out to model |

## Modelling notes

- All rates compound monthly
- Accumulated cash flows (positive or negative) are tracked as a separate pool — not folded into equity
- The sign of the rent advantage flips depending on cash flow return rate: negative cash flows compound against the rent scenario at higher rates

## Deployment (Google Cloud Run)

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis .
gcloud run deploy rental-analysis \
  --image us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis \
  --platform managed --region us-central1 --allow-unauthenticated --port 8501
```

## Code quality

No static analysis or type checking is configured (no mypy, ruff, or similar). The codebase is a single-file exploratory tool.
