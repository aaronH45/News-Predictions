# Survey Expectations Pipeline

Constructs synthetic survey-consistent macroeconomic expectations back to 1920
using Shiller macro features, WSJ sentiment, NBER recession indicators, and
lagged survey values. Designed for the Campbell-Shiller variance decomposition.

## Final walk-forward results

| Series              | WF R²  | Stab r | Key additions                        |
|---------------------|--------|--------|--------------------------------------|
| dividend_growth     | +0.606 | 0.795  | 18 macro features + survey_lag1      |
| earnings_growth     | +0.707 | 0.941  | ep_ratio, cape_inv, real_price_gr, cf_tone, earn_salience, recession |
| returns_1yr         | +0.108 | 0.905  | gs10, dp_ratio, infl_yoy, sent_agg   |
| returns_10yr        | +0.176 | 0.693  | gs10, ep_ratio, dp_ratio, lm_unc, cf_tone, recession |

AR(1) baseline = prior survey wave (naive persistence).

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
├── macro_expectations_pipeline.ipynb   ← main notebook — run this
├── README.md
├── requirements.txt
├── data/
│   ├── ie_data.xls                     ← Shiller S&P 500 data (1871–present)
│   ├── Dividend_growth_expectations.xlsx
│   ├── Earnings_growth_expectations.xlsx
│   ├── return_expectations_quarterly.xlsx
│   └── wsj_sentiment_quarterly.csv     ← quarterly WSJ LM/GI sentiment (1889–2026)
└── output/                             ← created automatically on first run
    ├── {series}/model_final.pkl
    ├── {series}/extrapolated_expectations.csv
    ├── full_range_expectations.png
    ├── expectations_vs_realized.png (if generated separately)
    ├── diagnostics_{series}.png
    └── feature_importance.png
```

---

## Running

1. Open `macro_expectations_pipeline.ipynb` in Jupyter
2. Verify `BASE_DIR = Path("./")` in cell 2 (default — run from this folder)
3. Run all cells in order

**On DCC cluster**, update cell 2:
```python
BASE_DIR = Path("/hpc/home/ah620")
DATA_DIR = BASE_DIR / "data"
```

**Expected runtime:** ~5–8 minutes on a laptop (walk-forward with 5-fold CV).
On DCC it will be faster.

---

## Outputs

After running all cells you will have:

- `output/{series}/extrapolated_expectations.csv` — monthly expectations
  1920-01-01 → latest Shiller date. Columns: `date`, `predicted`, `ood`
- `output/{series}/model_final.pkl` — fitted sklearn Pipeline for each series
- `output/full_range_expectations.png` — 4-panel time series plot
- `output/feature_importance.png` — Ridge coefficients per series
- `output/diagnostics_{series}.png` — walk-forward diagnostic plots

---

## Key design decisions

- **No FinBERT / no LLMs** — news embeddings added zero incremental R² over
  macro features; dropped entirely
- **Ridge over Random Forest** — RF boundary averaging produces implausibly
  muted extrapolations in historical regimes; Ridge extrapolates linearly
- **Per-series feature sets** — selected by parsimonious walk-forward search;
  parsimonious models outperform full-18-feature models for 3 of 4 series
- **AR(1) baseline = prior survey wave** — correct naive persistence benchmark;
  using Shiller realised values introduced unit mismatches
- **Survey lag for dividends** — prior quarter survey value adds +0.468 R²;
  bootstrapped during pre-survey extrapolation
- **Earnings outlier clipping** — COVID snap-back creates earn_gr_yoy = 7.9
  (790%); clipped at ±100% before feature construction

