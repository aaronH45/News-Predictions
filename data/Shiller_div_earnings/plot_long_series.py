#!/usr/bin/env python3
"""Plot the long (1872-2026) Shiller nominal one-year cash-flow growth series.

Plots, from shiller_growth_quarterly.csv:
  g_div_trail  = ln(D_t) - ln(D_{t-4})   trailing one-year log dividend growth
  g_earn_trail = ln(E_t) - ln(E_{t-4})   trailing one-year log earnings growth
D, E = Shiller nominal dividend / earnings per share, S&P Composite, quarter-end.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

F = "/home/rpa9/Shiller_div_earnings"
q = pd.read_csv(f"{F}/shiller_growth_quarterly.csv", parse_dates=["date"])

plt.rcParams.update({"font.family": "serif", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 130})

fig, ax = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)

for a, col, ttl, color in [
        (ax[0], "g_div_trail",  "Dividend growth", "#1f3b73"),
        (ax[1], "g_earn_trail", "Earnings growth", "#7a1f1f")]:
    s = q.dropna(subset=[col])
    a.axhline(0, color="k", lw=0.6)
    # pre-1926: D, E are interpolated from annual data
    a.axvspan(s.date.min(), pd.Timestamp("1926-01-01"),
              color="0.85", alpha=0.55, lw=0)
    a.plot(s.date, s[col], color=color, lw=0.9)
    a.set_title(f"{ttl}  —  trailing one-year log growth  "
                f"({s.Year.iloc[0]}Q{s.Quarter.iloc[0]}–{s.Year.iloc[-1]}Q{s.Quarter.iloc[-1]})",
                fontsize=10.5)
    a.set_ylabel("one-year log growth")
    a.margins(x=0.01)

ax[0].text(0.105, 0.88, "pre-1926: D, E interpolated\nfrom annual data",
           transform=ax[0].transAxes, fontsize=7.5, ha="center", color="0.35")
ax[1].set_xlabel("date")
fig.suptitle("Shiller nominal one-year cash-flow growth — S&P Composite",
             fontsize=12.5, y=0.985)
fig.tight_layout()
fig.savefig(f"{F}/fig_long_series.pdf", bbox_inches="tight")
print("wrote fig_long_series.pdf | "
      f"div {q['g_div_trail'].notna().sum()} obs, earn {q['g_earn_trail'].notna().sum()} obs")
