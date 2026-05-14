# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the script

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Run with CSV output + matplotlib plot
python3 rent_vs_sell.py

# CSV only (no plot window)
python3 rent_vs_sell.py --no-plot

# Or without activating the venv
.venv/bin/python3 rent_vs_sell.py
```

Outputs: `rent_vs_sell.csv` and `rent_vs_sell.png` (written to the project root).

## Dependencies

matplotlib is installed in `.venv/`. The stdlib (`csv`, `sys`) covers everything else. To add a package: `.venv/bin/pip install <package>`.

## Architecture

Single-file script (`rent_vs_sell.py`) with four sections:

**Inputs** — all scenario variables are module-level constants at the top of the file. This is the only section that needs editing for a new scenario.

**Mortgage helpers** — two pure functions: `calc_monthly_payment` (standard amortization formula) and `calc_remaining_balance` (closed-form balance after k payments).

**Core simulation** (`run_analysis`) — month-by-month loop over `PROJECTION_YEARS * 12` months. Tracks two parallel scenarios:
- *Sell*: net proceeds (`home_value − remaining_balance − closing_costs`) compound at `INVESTMENT_RETURN`
- *Rent*: house value appreciates, mortgage amortizes, net monthly cash flow (`rent − mortgage_pmt − operating_costs`) is reinvested at `CASHFLOW_RETURN` (a separate rate from `INVESTMENT_RETURN`). Cash flow automatically switches to `rent − operating_costs` once the mortgage is paid off.

Year-end snapshots are collected via `_row()`, which computes derived fields (`house_equity`, `rent_total_net_worth`, `advantage_rent_over_sell`).

**Output** — `write_csv` and `plot_analysis` consume the row list produced by `run_analysis`. The plot has three panels: net worth comparison (stacked area + lines), a bar chart of rent advantage by year, and a scenario inputs table.

## Key modelling decisions

- `rent_total_net_worth = house_equity + acc_cf` — accumulated cash flows are treated as a separate reinvested pool, not folded into equity.
- `advantage_rent_over_sell` sign depends heavily on `CASHFLOW_RETURN`: negative cash flows (rent < mortgage + ops) compound against the rent scenario at higher rates. At 0% cash flow return the losses accumulate linearly and house equity tends to dominate; at market rates the compounding deficit can flip the outcome.
- `INVESTMENT_RETURN` applies only to the sell scenario's invested proceeds. `CASHFLOW_RETURN` applies only to the accumulated rental cash flow pool (`acc_cf`).
- All rates compound monthly (`(1 + annual_rate)^(1/12) - 1`), not annually.
