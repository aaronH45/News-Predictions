# Survey Expectations Pipeline

Predicts and extrapolates survey-based macroeconomic expectations using
Shiller macro features, WSJ sentiment, recession indicators, and lagged
survey values. Designed to run on Duke DCC cluster or any environment
with Python 3.11+ and the packages below.

## Directory structure

```
survey_expectations_pipeline/
├── macro_expectations_pipeline.ipynb   ← main notebook
├── README.md
├── data/
│   ├── ie_data.xls                     ← Shiller S&P 500 data (1871–present)
│   ├── Dividend_growth_expectations.xlsx
│   ├── Earnings_growth_expectations.xlsx
│   ├── return_expectations_quarterly.xlsx
│   └── wsj_sentiment_quarterly.csv     ← quarterly WSJ LM/GI sentiment (1889–2026)
└── output/                             ← created automatically on first run
```

## Setup

```bash
pip install pandas numpy scikit-learn matplotlib openpyxl xlrd
```

All packages are standard — no GPU, no FinBERT, no torch required.

## Configuration (cell 2)

- `BASE_DIR = Path("./")` — run from this folder, or update to your path
- `DATA_DIR = BASE_DIR / "data"` — all input files live here
- `OUTPUT_DIR = BASE_DIR / "output"` — models and plots saved here
- `EXTRAP_START / EXTRAP_END` — historical extrapolation window (default 1920–1970)

For DCC cluster, update BASE_DIR to your project path, e.g.:
```python
BASE_DIR = Path("/hpc/home/ah620")
```

## Final walk-forward results

| Series          | WF R²  | Stab r | Key features                                      |
|-----------------|--------|--------|---------------------------------------------------|
| dividend_growth | +0.606 | 0.795  | 18 macro features + survey_lag1 (bootstrapped)   |
| earnings_growth | +0.707 | 0.941  | ep_ratio, cape_inv, real_price_gr, cf_tone, earn_salience, recession |
| returns_1yr     | +0.108 | 0.905  | gs10, dp_ratio, infl_yoy, sent_agg               |
| returns_10yr    | +0.176 | 0.693  | gs10, ep_ratio, dp_ratio, lm_unc, cf_tone, recession |

AR(1) baseline = prior survey wave (naive persistence).

## Survey lag note

`dividend_growth` uses the prior survey wave as a feature (`survey_lag1`).
During the survey period this is clean — each prediction uses the actual
prior survey value. During pre-survey extrapolation, it is bootstrapped:
the model's own prior prediction is fed back as the lag feature. This adds
uncertainty that compounds over the extrapolation window; treat early
extrapolation periods with appropriate caution.

## Outputs

After running all cells:
- `output/{series}/model_final.pkl` — fitted Ridge pipeline for extrapolation
- `output/{series}/extrapolated_expectations.csv` — monthly expectations 1920–survey start
- `output/diagnostics_{series}.png` — walk-forward plots with NBER shading
- `output/feature_importance.png` — standardised Ridge coefficients
- `output/extrapolated_expectations.png` — pre-survey extrapolation overview
