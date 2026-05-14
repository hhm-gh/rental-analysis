All scenario inputs are Streamlit sidebar widgets at the top of `rent_vs_sell.py` (after the imports). This is the only section that needs editing for a new scenario.

To run: `.venv/bin/streamlit run rent_vs_sell.py` (opens at http://localhost:8501).
On every render, `rent_vs_sell.png` is written/overwritten on disk. CSV and PNG are also available via in-browser download buttons.

Key input widgets:
- `HOME_VALUE`, `ORIGINAL_PRINCIPAL`, `ANNUAL_RATE`, `TERM_YEARS`, `YEARS_PAID`
- `MONTHLY_RENT`, `INVESTMENT_RETURN`, `CASHFLOW_RETURN`, `APPRECIATION_RATE`
- `ANNUAL_PROPERTY_TAX`, `ANNUAL_INSURANCE`, `ANNUAL_MAINTENANCE`
- `CLOSING_COST_PCT`, `PROJECTION_YEARS`

CSV columns: `year`, `sell_investment_value`, `rent_house_value`, `rent_mortgage_balance`, `rent_house_equity`, `rent_accumulated_cf`, `rent_total_net_worth`, `rent_monthly_net_cf`, `advantage_rent_over_sell`.

The plot has 3 panels: net worth comparison (top-left), rent advantage bars (bottom-left), inputs table (right). `build_figure()` produces the matplotlib figure.
