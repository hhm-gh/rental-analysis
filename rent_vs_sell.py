#!/usr/bin/env python3
"""
Rent vs. Sell: net worth projection.

Compares:
  SELL — sell the house, pay off the mortgage, invest net proceeds
  RENT — keep the house, rent it out, reinvest net monthly cash flows

Edit the INPUT section, then run:
    python3 rent_vs_sell.py            # produce CSV + plot
    python3 rent_vs_sell.py --no-plot  # CSV only
"""

import csv
import sys


# ── Inputs ────────────────────────────────────────────────────────────────────

HOME_VALUE           = 500_000   # Current market value ($)
ORIGINAL_PRINCIPAL   = 400_000   # Original loan amount ($)
ANNUAL_RATE          = 0.04      # Mortgage annual interest rate (e.g. 0.065 = 6.5%)
TERM_YEARS           = 30        # Original mortgage term (years)
YEARS_PAID           = 5         # Number of years payments have already been made
MONTHLY_RENT         = 3_000     # Gross monthly rent collected ($)
INVESTMENT_RETURN    = 0.07      # Annual return on invested proceeds (e.g. 0.07 = 7%)
CASHFLOW_RETURN      = 0.00      # Annual return on reinvested rental cash flows
APPRECIATION_RATE    = 0.02      # Annual home price appreciation rate
ANNUAL_PROPERTY_TAX  = 6_000     # Annual property tax ($)
ANNUAL_INSURANCE     = 1_500     # Annual homeowner's insurance ($)
ANNUAL_MAINTENANCE   = 2_000     # Annual maintenance / capex ($)
# ANNUAL_PROPERTY_TAX  = 0     # Annual property tax ($)
# ANNUAL_INSURANCE     = 0     # Annual homeowner's insurance ($)
# ANNUAL_MAINTENANCE   = 0     # Annual maintenance / capex ($)
CLOSING_COST_PCT     = 0.0      # Seller closing costs as % of sale price
PROJECTION_YEARS     = 30

OUTPUT_CSV  = "rent_vs_sell.csv"
OUTPUT_PLOT = "rent_vs_sell.png"


# ── Mortgage helpers ──────────────────────────────────────────────────────────

def calc_monthly_payment(principal: float, annual_rate: float, term_years: int) -> float:
    r = annual_rate / 12
    n = term_years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def calc_remaining_balance(
    principal: float, annual_rate: float, term_years: int, months_paid: int
) -> float:
    r = annual_rate / 12
    n = term_years * 12
    if months_paid >= n:
        return 0.0
    return principal * ((1 + r) ** n - (1 + r) ** months_paid) / ((1 + r) ** n - 1)


# ── Core simulation ───────────────────────────────────────────────────────────

def run_analysis():
    r_monthly    = ANNUAL_RATE / 12
    inv_monthly  = (1 + INVESTMENT_RETURN) ** (1 / 12) - 1
    cf_monthly   = (1 + CASHFLOW_RETURN) ** (1 / 12) - 1
    app_monthly  = (1 + APPRECIATION_RATE) ** (1 / 12) - 1
    monthly_ops  = (ANNUAL_PROPERTY_TAX + ANNUAL_INSURANCE + ANNUAL_MAINTENANCE) / 12
    mortgage_pmt = calc_monthly_payment(ORIGINAL_PRINCIPAL, ANNUAL_RATE, TERM_YEARS)

    months_paid_0 = YEARS_PAID * 12
    balance_0     = calc_remaining_balance(ORIGINAL_PRINCIPAL, ANNUAL_RATE, TERM_YEARS, months_paid_0)
    closing_costs = HOME_VALUE * CLOSING_COST_PCT
    net_proceeds  = HOME_VALUE - balance_0 - closing_costs

    rows = []

    # Year-0 snapshot (the moment of decision)
    initial_monthly_cf = MONTHLY_RENT - mortgage_pmt - monthly_ops
    rows.append(_row(0, net_proceeds, HOME_VALUE, balance_0, 0.0, initial_monthly_cf))

    sell_inv      = net_proceeds
    house_value   = HOME_VALUE
    mort_balance  = balance_0
    acc_cf        = 0.0
    last_cf       = initial_monthly_cf

    for month in range(1, PROJECTION_YEARS * 12 + 1):
        # Sell scenario: portfolio compounds monthly
        sell_inv *= (1 + inv_monthly)

        # House appreciates
        house_value *= (1 + app_monthly)

        # Amortize mortgage
        if mort_balance > 0.01:
            interest     = mort_balance * r_monthly
            principal_pd = mortgage_pmt - interest
            mort_balance = max(0.0, mort_balance - principal_pd)
            monthly_cf   = MONTHLY_RENT - mortgage_pmt - monthly_ops
        else:
            mort_balance = 0.0
            monthly_cf   = MONTHLY_RENT - monthly_ops  # mortgage gone

        # Reinvest net cash flow (positive or negative)
        acc_cf = acc_cf * (1 + cf_monthly) + monthly_cf
        last_cf = monthly_cf

        if month % 12 == 0:
            rows.append(_row(month // 12, sell_inv, house_value, mort_balance, acc_cf, last_cf))

    return rows


def _row(year, sell_inv, house_value, mort_balance, acc_cf, monthly_cf):
    house_equity   = house_value - mort_balance
    rent_net_worth = house_equity + acc_cf
    return {
        "year":                     year,
        "sell_investment_value":    round(sell_inv),
        "rent_house_value":         round(house_value),
        "rent_mortgage_balance":    round(mort_balance),
        "rent_house_equity":        round(house_equity),
        "rent_accumulated_cf":      round(acc_cf),
        "rent_total_net_worth":     round(rent_net_worth),
        "rent_monthly_net_cf":      round(monthly_cf),
        "advantage_rent_over_sell": round(rent_net_worth - sell_inv),
    }


# ── Output ────────────────────────────────────────────────────────────────────

FIELDNAMES = [
    "year",
    "sell_investment_value",
    "rent_house_value",
    "rent_mortgage_balance",
    "rent_house_equity",
    "rent_accumulated_cf",
    "rent_total_net_worth",
    "rent_monthly_net_cf",
    "advantage_rent_over_sell",
]


def write_csv(rows):
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV  → {OUTPUT_CSV}")


def plot_analysis(rows):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    years        = [r["year"] for r in rows]
    sell_vals    = [r["sell_investment_value"] / 1_000 for r in rows]
    rent_nw      = [r["rent_total_net_worth"] / 1_000 for r in rows]
    house_eq     = [r["rent_house_equity"] / 1_000 for r in rows]
    acc_cf       = [r["rent_accumulated_cf"] / 1_000 for r in rows]
    advantage    = [r["advantage_rent_over_sell"] / 1_000 for r in rows]

    fig = plt.figure(figsize=(15, 10))
    gs  = GridSpec(2, 2, figure=fig, width_ratios=[2.5, 1], hspace=0.35, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[:, 1])

    # ── Top panel: net worth comparison ──
    ax1.stackplot(
        years, house_eq, acc_cf,
        labels=["House Equity (rent)", "Accumulated Cash Flow (rent)"],
        alpha=0.3, colors=["darkorange", "gold"],
    )
    ax1.plot(years, sell_vals, label="Sell & Invest", linewidth=2.5, color="steelblue")
    ax1.plot(years, rent_nw,   label="Rent Out (total net worth)", linewidth=2.5,
             color="darkorange", linestyle="--")
    ax1.set_ylabel("Net Worth ($000s)")
    ax1.set_title("Rent vs. Sell: Net Worth Projection")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # ── Bottom panel: rent advantage ──
    bar_colors = ["green" if a >= 0 else "red" for a in advantage]
    ax2.bar(years, advantage, color=bar_colors, alpha=0.7, width=0.8)
    ax2.axhline(0, color="black", linewidth=0.9)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Rent Advantage ($000s)")
    ax2.set_title("Rent Net Worth − Sell Net Worth  (green = rent wins)")
    ax2.grid(True, alpha=0.3)

    # ── Right panel: scenario inputs ──
    ax3.axis("off")
    ax3.set_title("Scenario Inputs", fontweight="bold", pad=10)

    mortgage_pmt = calc_monthly_payment(ORIGINAL_PRINCIPAL, ANNUAL_RATE, TERM_YEARS)

    table_data = [
        ["Home Value",          f"${HOME_VALUE:,.0f}"],
        ["Original Principal",  f"${ORIGINAL_PRINCIPAL:,.0f}"],
        ["Mortgage Rate",       f"{ANNUAL_RATE*100:.2f}%"],
        ["Term",                f"{TERM_YEARS} yrs"],
        ["Years Paid",          f"{YEARS_PAID}"],
        ["Monthly Payment",     f"${mortgage_pmt:,.0f}"],
        ["Monthly Rent",        f"${MONTHLY_RENT:,.0f}"],
        ["Investment Return",   f"{INVESTMENT_RETURN*100:.1f}%"],
        ["Cash Flow Return",    f"{CASHFLOW_RETURN*100:.1f}%"],
        ["Appreciation Rate",   f"{APPRECIATION_RATE*100:.1f}%"],
        ["Property Tax",        f"${ANNUAL_PROPERTY_TAX:,.0f}/yr"],
        ["Insurance",           f"${ANNUAL_INSURANCE:,.0f}/yr"],
        ["Maintenance",         f"${ANNUAL_MAINTENANCE:,.0f}/yr"],
        ["Closing Costs",       f"{CLOSING_COST_PCT*100:.0f}%"],
        ["Projection",          f"{PROJECTION_YEARS} yrs"],
    ]

    tbl = ax3.table(
        cellText=table_data,
        colLabels=["Variable", "Value"],
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("lightgray")
        if row == 0:
            cell.set_facecolor("#4472C4")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#EEF2FA")
        else:
            cell.set_facecolor("white")

    plt.savefig(OUTPUT_PLOT, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Plot → {OUTPUT_PLOT}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rows = run_analysis()
    write_csv(rows)
    if "--no-plot" not in sys.argv:
        plot_analysis(rows)
