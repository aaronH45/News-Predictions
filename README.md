# Survey Expectations Pipeline

Constructs synthetic survey-consistent macroeconomic expectations back to 1920
using Shiller macro features, WSJ sentiment, NBER recession indicators, and
lagged/cross survey values. Designed for the Campbell-Shiller variance
decomposition.

Six target series are modelled and extrapolated: dividend growth and earnings
growth at both **1-year and 2-year horizons**, plus **1-year and 10-year** S&P
500 return expectations.

## Final walk-forward results

| Series                | WF R²  | vs AR(1) | Key features                                                          |
|-----------------------|--------|----------|----------------------------------------------------------------------|
| dividend_growth (1yr) | +0.606 | +0.0029  | 18 macro features + survey lag                                       |
| earnings_growth (1yr) | +0.707 | +0.0135  | ep_ratio, cape_inv, real_price_gr, cf_tone, earn_salience, recession |
| dividend_growth_2yr   | +0.722 | -0.0024  | exp_1yr_div (1yr forecast), dp_ratio, dp_dev, recession + survey lag |
| earnings_growth_2yr   | +0.752 | -0.0043  | ep_ratio, cape_inv, real_price_gr, cf_tone, earn_salience, recession |
| returns_1yr           | +0.108 | -0.1848  | gs10, dp_ratio, infl_yoy, sent_agg                                   |
| returns_10yr          | +0.176 | -0.1290  | gs10, ep_ratio, dp_ratio, lm_unc, cf_tone, recession                 |

`vs AR(1)` is the RMSE difference against predicting the prior survey wave
(naive persistence). Negative = model beats the naive baseline on RMSE.

---

## Setup

### Requirements
Python 3.11+ with the following packages (all standard, no GPU required):

```
pip install pandas numpy scikit-learn matplotlib openpyxl xlrd reportlab
```

Or install from the requirements file:

```
pip install -r requirements.txt
```

### Directory layout

```
project/
|-- macro_expectations_pipeline.ipynb   <- main notebook — run this
|-- README.md
|-- requirements.txt
|-- data/
|   |-- ie_data.xls                                       <- Shiller S&P 500 data (1871-present)
|   |-- Dividend_growth_expectations.xlsx                 <- 1yr dividend survey
|   |-- Earnings_growth_expectations.xlsx                 <- 1yr earnings survey
|   |-- Dividend_growth_expectations_reconstructed.xlsx   <- 1yr + 2yr dividend survey
|   |-- Earnings_growth_expectations_reconstructed.xlsx   <- 1yr + 2yr earnings survey
|   |-- return_expectations_quarterly.xlsx                <- 1yr + 10yr return survey
|   `-- wsj_sentiment_quarterly.csv                       <- quarterly WSJ LM/GI sentiment (1889-2026)
`-- output/                                               <- created automatically on first run
    |-- {series}/model_final.pkl
    |-- {series}/extrapolated_expectations.csv
    |-- full_range_expectations.png
    |-- expectations_clean.png
    |-- expectations_vs_realized.png
    |-- extrapolated_overlay_pct.png
    |-- extrapolated_overlay_with_realized_returns.png
    |-- extrapolation_summary_stats.csv
    |-- diagnostics_{series}.png
    `-- feature_importance.png
```

---

## Running

1. Open `macro_expectations_pipeline.ipynb` in Jupyter
2. Verify `BASE_DIR = Path("./")` in the config cell (default — run from this folder)
3. Kernel -> Restart & Run All

**On DCC cluster**, update the config cell:
```python
BASE_DIR = Path("/hpc/home/ah620")
DATA_DIR = BASE_DIR / "data"
```

**Expected runtime:** ~6-9 minutes on a laptop (walk-forward with 5-fold CV
across six series). Faster on DCC.

---

## Data series and units

| Series              | File / column                                              | Units                          |
|---------------------|-----------------------------------------------------------|--------------------------------|
| dividend_growth     | Dividend_growth_expectations.xlsx, "Expected one-year..." | log growth rate                |
| earnings_growth     | Earnings_growth_expectations.xlsx, col 2                   | log growth rate                |
| dividend_growth_2yr | Dividend_growth_expectations_reconstructed.xlsx, two-year | cumulative 2yr log growth      |
| earnings_growth_2yr | Earnings_growth_expectations_reconstructed.xlsx, col 5     | cumulative 2yr log growth      |
| returns_1yr         | return_expectations_quarterly.xlsx, sp_1yr_median         | percent per year (discrete)    |
| returns_10yr        | return_expectations_quarterly.xlsx, sp_10yr_median        | percent per year (annualised)  |

The 2-year growth series are **cumulative over two years** (~2x the 1-year
level), not annualised. The overlay plots annualise them (/2) so all series
share a common percentage-point scale.

---

## Outputs

After running all cells you will have:

- `output/{series}/extrapolated_expectations.csv` — monthly expectations
  1920-01-01 -> latest Shiller date. Columns: `date`, `predicted`, `ood`
- `output/{series}/model_final.pkl` — fitted sklearn Pipeline per series
- `output/full_range_expectations.png` — 3x2 panel: prediction + survey actual + OOD
- `output/expectations_clean.png` — clean prediction vs survey actual (no OOD markers)
- `output/expectations_vs_realized.png` — adds realized outcomes per series
- `output/extrapolated_overlay_pct.png` — all six series overlaid, annualised pct points
- `output/extrapolated_overlay_with_realized_returns.png` — overlay + realized returns only
- `output/extrapolation_summary_stats.csv` — per-series stats (pre-survey vs survey, OOD %)
- `output/feature_importance.png` — standardised Ridge coefficients per series
- `output/diagnostics_{series}.png` — walk-forward diagnostic plots

---

## Key design decisions

- **No FinBERT / no LLMs** — news embeddings added zero incremental R^2 over
  macro features; dropped entirely.
- **Ridge over Random Forest** — RF boundary averaging produces implausibly
  muted extrapolations in historical regimes; Ridge extrapolates linearly.
- **Per-series feature sets** — selected by parsimonious walk-forward search.
  Fewer features beat the full 18-feature set for most series; the full set
  overfits on the shorter calibration windows.
- **AR(1) baseline = prior survey wave** — correct naive persistence benchmark;
  using Shiller realised values introduced unit mismatches.
- **Survey lag for dividends** — the prior survey wave is the dominant predictor
  for dividend expectations (1yr and 2yr); appended dynamically during
  walk-forward and bootstrapped during pre-survey extrapolation.
- **2yr dividend uses the 1yr forecast** — the contemporaneous 1yr dividend
  forecast (`exp_1yr_div`, corr 0.92 with the 2yr) is the strongest predictor;
  WF R^2 rises from +0.561 (survey lag only) to +0.722 and beats AR(1). For
  extrapolation it chains on the extrapolated 1yr dividend series.

---

## Caveats for the Campbell-Shiller decomposition

The extrapolated series are **noisy proxies** for historical expectations, not
ground truth. Reliability varies by series, summarised by the OOD share
(fraction of pre-survey months whose macro environment is outside the
calibration window — see `extrapolation_summary_stats.csv`):

- **earnings_growth (18% OOD)** — most reliable; longest calibration window
  (1976+). Preferred for long-run decomposition claims.
- **earnings_growth_2yr (34% OOD)** — reasonably reliable.
- **returns_1yr / returns_10yr (~72% OOD)** — modest WF R^2 and high OOD share.
  Pre-2000 predictions outside the in-distribution range can be implausible;
  consider clipping or excluding OOD months.
- **dividend_growth (80% OOD) / dividend_growth_2yr (78% OOD)** — least
  reliable for extrapolation. Dividend expectations are near-random-walks driven
  by their own persistence, and that persistence cannot be reconstructed from
  the historical macro record. The 2yr dividend extrapolation, while better
  centred after chaining on the 1yr forecast, remains the noisiest pre-survey
  series. **Recommended: report the in-sample fit but flag (or exclude) the
  pre-survey dividend extrapolations in the decomposition.**

A finding in its own right: dividend expectations reflect genuine forecasting
skill (survey forecasts correlate ~0.55 with future realised growth) drawn from
forward-looking information not present in the historical macro record — which
is precisely why they cannot be credibly extrapolated to the pre-survey period.
