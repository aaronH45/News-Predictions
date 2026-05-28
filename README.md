# News Encoder → Survey Expectation Pipeline

A research pipeline that maps aggregated WSJ financial news embeddings to
survey-based macroeconomic expectations (dividend and earnings growth),
then extrapolates fitted expectations backward through the full historical
news record to 1965.

## Project overview

Survey-based expectations are only available from the early 1980s onward.
This project uses a frozen FinBERT encoder to embed WSJ headlines, aggregates
embeddings to quarterly wave vectors, and fits regression models that predict
median survey forecasts. The validated models are then applied to the full
news corpus to construct a long-run expectations series.

**Key findings:**
- Earnings growth expectations exhibit a predominantly linear relationship
  with news embeddings and Shiller macro features (Ridge WF R² ≈ 0.46)
- Dividend growth expectations exhibit nonlinear regime-dependent dynamics
  better captured by Random Forest (positive directional accuracy post-2014)
- The two series warrant different models: Ridge for earnings, RF for dividends

## Data sources

| File | Description |
|---|---|
| `data/wsj_headlines_1965_2014_zstd.parquet` | WSJ headlines 1965–2014 |
| `data/wsj_headlines_2015_2026_zstd.parquet` | WSJ headlines 2015–2026 |
| `data/ie_data.xls` | Shiller S&P 500 data (price, dividends, earnings, CPI, rates) back to 1871. Download from http://www.econ.yale.edu/~shiller/data.htm |
| `data/Dividend_growth_expectations.xlsx` | Quarterly median dividend growth survey forecasts |
| `data/Earnings_growth_expectations.xlsx` | Quarterly median earnings growth survey forecasts |

## Environment setup

```bash
conda create -n news-encoder python=3.11 pip -y
conda activate news-encoder
pip install -r requirements.txt
```

## Running order

Run notebooks in order. Each subsequent notebook expects the previous one
to have been run in the **same Jupyter kernel session** so that variables
like `all_results`, `news_df`, and `article_embeddings` are in memory.

### Step 1 — Main pipeline
**`notebooks/1_news_encoder_pipeline.ipynb`**

The core pipeline. Encodes all headlines with frozen FinBERT, tunes a
Random Forest regression via LOO-CV, and evaluates using walk-forward
expanding-window cross-validation.

Key outputs:
- `output/{series}/walkforward_predictions.csv` — walk-forward predictions
- `output/{series}/model_final.pkl` — final model fitted on all waves
- `output/{series}/tuning_log.csv` — hyperparameter search results

> **Test mode:** set `TEST_MODE = True` in the config cell to skip
> hyperparameter search and use cached parameters. Reduces runtime from
> ~30 min to ~2 min. Update `CACHED_PARAMS` after a production run.

### Step 2 — Historical extrapolation
**`notebooks/2_historical_extrapolation.ipynb`**

Selects the best model for each series (Ridge for earnings, RF for
dividends), refits on the full calibration sample, and generates
quarterly predictions back to 1965.

Key outputs:
- `output/extrapolated_earnings_growth.csv`
- `output/extrapolated_dividend_growth.csv`
- `output/best_model_{series}_{type}.pkl`
- `output/extrapolated_series.png`

### Step 3 — Signal decomposition (optional)
**Run inline in notebook 1**, cells after the summary table.

Fits Ridge on three feature variants (news only, macro only, news+macro)
to decompose how much predictive power comes from each source.

### Step 4 — Model comparison for dividends (optional)
**`notebooks/4_model_comparison_dividend.ipynb`**

Compares Ridge, PLS, PLS→Ridge, PLS→KernelRidge, Random Forest, and
Gaussian Process on the dividend series. Useful for exploring alternative
model architectures.

### Step 5 — RF vs Ridge convergence experiments (optional)
**`notebooks/5_rf_ridge_convergence.ipynb`**

Investigates the RF/Ridge performance gap on earnings growth. Tests
fixed hyperparameters, adaptive retuning, and a Ridge+RF residual stack.

### Headline filtering (optional, run before Step 1)
**`notebooks/6_headline_inspection.ipynb`**
Explore corpus quality: random samples, length distributions, keyword
frequencies, FinBERT anchor similarity, and manual labelling tools.

**`notebooks/7_headline_cleanup_pipeline.ipynb`**
Three-stage filter: structural (length), blocklist (explicit non-financial
terms), anchor similarity (FinBERT cosine distance to financial phrases).
Saves a boolean filter mask to cache; integrate into main pipeline via
the snippet in the final cell.

**`notebooks/8_anchor_filter_calibration.ipynb`**
Validates the anchor similarity threshold via decade stability analysis,
manual label cross-validation, and wave coverage checks.

## Pipeline architecture

```
WSJ Headlines (1965–2026)
        │
        ▼
  FinBERT Encoder (frozen, ProsusAI/finbert)
  ┌─────────────────────────────────────┐
  │  CLS embedding (768-dim) per article│  ← cached to disk
  │  P(neutral) score per article       │  ← cached to disk
  └─────────────────────────────────────┘
        │
        ▼
  Wave Aggregation (quarterly)
  ┌─────────────────────────────────────┐
  │  Sentiment filter (P(neutral) > θ) │  ← θ tuned by LOO-CV
  │  Recency-weighted mean (exp decay) │
  │  Shiller macro features appended   │  ← 8 features, back to 1871
  └─────────────────────────────────────┘
        │  (n_waves × 776)
        ▼
  Regression head (tuned by LOO-CV on initial window)
  ┌──────────────────┬──────────────────┐
  │ earnings_growth  │ dividend_growth  │
  │    Ridge         │  Random Forest   │
  │   R² ≈ 0.46      │  dir acc ≈ 63%  │
  └──────────────────┴──────────────────┘
        │
        ▼
  Walk-forward evaluation (expanding window)
  → Honest out-of-sample performance metrics
        │
        ▼
  Full-sample refit → Historical extrapolation
  → extrapolated_{series}.csv (1965–2026)
```

## Evaluation methodology

**Walk-forward expanding window:** hyperparameters are tuned once on the
first `MIN_TRAIN_WAVES` observations, then held fixed. For each subsequent
wave, the model is trained on all preceding waves and predicts one step
ahead. This respects temporal ordering and avoids look-ahead bias.

Walk-forward R² is the primary performance metric for earnings (117 eval
steps). Directional accuracy is the primary metric for dividends (19 eval
steps — series is too short for reliable R²).

## Key configuration

All parameters are in the config cell (cell 5) of notebook 1:

| Parameter | Default | Description |
|---|---|---|
| `TEST_MODE` | `True` | Skip HP search, use CACHED_PARAMS |
| `MIN_TRAIN_WAVES_PER_SERIES` | 30 / 40 | Initial training window per series |
| `NEUTRAL_THRESHOLD_GRID` | [0.75–1.01] | Sentiment filter threshold search |
| `RF_MSL_GRID` | [2,3,5,8,13,20,30] | min_samples_leaf search grid |
| `ANCHOR_THRESHOLD` | 0.30 | FinBERT anchor similarity cutoff |

## Cache files

Large intermediate files are cached to `CACHE_DIR` (default:
`/hpc/dctrl/ah620/storgae` on DCC, `./cache` locally).
Cache files are named with corpus size and content hashes so stale
files are never silently reused.

| File pattern | Contents |
|---|---|
| `news_emb_n{N}_{dates}.npy` | Article embeddings (768-dim per article) |
| `p_neutral_n{N}_{dates}.npy` | P(neutral) scores per article |
| `anchor_sim_n{N}_{hash}.npy` | Anchor cosine similarity per article |
| `filter_mask_n{N}_...npy` | Boolean relevance filter mask |

## Citation

If you use this code or the extrapolated expectations series, please cite:

```
[Citation to be added upon publication]
```

## Authors

Aaron, Rafael Alves — Duke University
