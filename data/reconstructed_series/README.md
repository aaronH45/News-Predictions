# De La O & Myers (JF 2021) subjective expectations — reconstructed, with two-year measures

Aggregate S&P 500 subjective **cash-flow growth expectations**, rebuilt from raw
Compustat + I/B/E/S, in the **same format as the files Sean Myers shared**, plus the
**two-year** columns the 2021 paper uses but that weren't in the shared one-year files.

## Files
| file | what |
|---|---|
| `Dividend_growth_expectations_reconstructed.xlsx` | dividend expectations, **2002Q2–2024Q4** |
| `Earnings_growth_expectations_reconstructed.xlsx` | earnings expectations, **1976Q1–2024Q4** (two-year cols from 1985) |
| `reconstructed_series.csv` | the underlying quarterly series the Excels are built from |
| `build_excels.py` | regenerates the two Excels from the csv + Shiller earnings (for CAPE) |

Ranges run to all available data (not capped at Myers' shared files). Forward limit is
2024Q4 (CRSP membership/prices); dividends start 2002 (S&P 500 DPS forecasts don't exist
earlier in I/B/E/S). Realized columns are blank at the tail (no t+4 / t+8 outcomes yet),
as in Myers' files.

## Columns

**Dividend file** — Myers' columns + two-year (all logs):
`Year, Quarter,`
`Expected one-year log dividend growth` = E*ₜ[d₍ₜ₊₁₎−dₜ],
`Realized next year log dividend growth` = d₍ₜ₊₁₎−dₜ,
`Current log price-dividend ratio` = pₜ−dₜ,
`Expected two-year log dividend growth` = **E*ₜ[d₍ₜ₊₂₎−dₜ]** (cumulative over two years),
`Realized two-year log dividend growth` = d₍ₜ₊₂₎−dₜ.

**Earnings file** — three denominator blocks (current earnings eₜ, dividends dₜ, CAPE earnings e^ca_t),
each with five columns; two header rows exactly like Myers':
`Expected one-year log earnings growth` = E*ₜ[e₍ₜ₊₁₎−xₜ],
`Realized next year log earnings growth` = e₍ₜ₊₁₎−xₜ,
`Current price ratio` = pₜ−xₜ,
`Expected two-year log earnings growth` = **E*ₜ[e₍ₜ₊₂₎−xₜ]**,
`Realized two-year log earnings growth` = e₍ₜ₊₂₎−xₜ.

t is quarterly; cash flows are annual (trailing 4 quarters); e₍ₜ₊₁₎ / e₍ₜ₊₂₎ are 4 / 8 quarters ahead.

## Mapping to the replication code (`make_results_condensed.m`)
The 2-year columns are **cumulative** (level t+2 minus denominator), to mirror Myers' 1-year
columns (level t+1 minus denominator). To get the paper's variables:
- `d_growth(:,1)` = `Expected one-year log dividend growth`
- `d_growth(:,2)` = **(Expected two-year) − (Expected one-year)**  [the year-2 increment E*ₜ[Δd₍ₜ₊₂₎]]
- Table II 2-yr std = `std( (Expected two-year)/2 )`   (average annual growth)
- Table V `CF₂` = `cov( 1yr + ρ·(2yr−1yr), price )/var(price)`, ρ = exp(mean pd)/(1+exp(mean pd))
- Earnings: same, using the `eₜ` block.

## Validation (vs Myers' shared one-year Excel, and the paper)
| | corr vs Myers | std (paper) | CF₁ (paper) | CF₂ (paper) |
|---|---|---|---|---|
| Earnings 1-yr | **0.970** | 28.3% (27.5) | 0.42 (0.42) | 0.64 (0.64) |
| Dividend 1-yr | **0.918** | 7.5% (8.1) | 0.39 (0.39) | 0.60 (0.65) |

Differences from Myers' exact series are ~5–15% (quarter level) and come from data vintage
(2026 I/B/E/S/Compustat vs his ~2020 extract). The construction itself is faithful.

## Methodology (brief)
S&P 500 membership from `crsp.msp500list` (point-in-time); calendar quarter-end price & shares
from `crsp.msf`; ordinary dividends from `crsp.msedist`; earnings from `comp.fundq`; forecasts
from the **unadjusted** I/B/E/S summary (`statsumu_epsus`, `statsumu_xepsus`), median, snapshot
the month after quarter-end, FY1/FY2(/FY3) linearly interpolated to exactly 12/24 months,
scaled to the index by market value (representativeness). CAPE denominator = 10-year cyclically
adjusted earnings from Shiller's long series, level-matched to the index (scale 1.003).
Full WRDS pipeline: `~/IBES_Expectations/recon/` (working scripts 01–18).
