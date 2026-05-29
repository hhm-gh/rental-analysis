# Rental Analysis

A web app deployed on **Google Cloud Run** that models the financial trade-off between **selling a home** vs. **renting it out**, projected year-by-year over a configurable horizon.

**Live app: https://rental-analysis-229545692350.us-central1.run.app**

## What it does

Runs a month-by-month simulation of two parallel scenarios:

- **Sell** — net proceeds (home value − mortgage balance − closing costs) are invested and compound at a configurable return rate
- **Rent** — house appreciates, mortgage amortizes, and monthly net cash flow (rent − mortgage − operating costs) is reinvested separately at its own return rate

Outputs a three-panel chart comparing net worth, the rent advantage over time, and a summary inputs table. Results can be downloaded as CSV or PNG.

## Stack

- Python 3, Streamlit, matplotlib — containerized with Docker
- Hosted on Google Cloud Run (project: `rental-analysis-2026`, region: `us-central1`)
- Single-file app (`rent_vs_sell.py`) — no database, no backend

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

## Redeploying after code changes

```bash
./deploy.sh
```

## Running locally

```bash
# With Docker
docker build -t rental-analysis .
docker run -p 8501:8501 rental-analysis
# App opens at http://localhost:8501

# Or with the included venv
.venv/bin/streamlit run rent_vs_sell.py
```
