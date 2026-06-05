# Data dictionary — `wsj_sentiment_quarterly.{csv,parquet}`

Quarterly WSJ news-sentiment feature panel, produced inside ProQuest TDM Studio by
`proquest_wsj_sentiment_quarterly.ipynb` from the full-text corpus
`wsj_full_corpus.parquet` (WSJ 1889–2026, four ProQuest products: historical OCR DB
1889–2014 + current product 2015–2026).

- **Grain:** one row per calendar quarter. ~550 rows (1889Q3 → 2026).
- **Columns:** 45.
- **Purpose:** feature inputs for the DCC model recovering subjective discount-rate,
  earnings-growth, and dividend-growth expectations.

## How the numbers are built

Each article is tokenized (letters only, uppercased) and its **body** and **headline**
are scored separately against word lists. Per quarter:

- **Level columns** (e.g. `lm_neg`, `dr_salience`) are **token-weighted (pooled)**:
  `level = (total category word-occurrences in the quarter) / (total body tokens in the quarter)`.
  Interpretation: *fraction of all WSJ body words that quarter belonging to the category.*
  Dimensionless, typically 0–0.05. Tones (`lm_tone`, `cf_tone`) are differences of two
  levels and can be negative.
- **Headline columns** (`hl_*`) are the same, computed over **headline** tokens
  (denominator = total headline tokens that quarter).
- **Dispersion columns** (`*_disp`) are **equal-weighted across articles**: the standard
  deviation, across that quarter's articles, of the article-level fraction. They proxy
  **disagreement** in coverage (orthogonal-to-macro signal). Computed for body only.
- **Salience** lists are direction-neutral ("how much is the quarter *about* X");
  **directional** lists (`cf_growth`/`cf_decline`) capture expansion vs. contraction.

Lexicons: **Loughran–McDonald** (finance standard), **Harvard General Inquirer**
(Tetlock 2007), and three **author-curated** custom lists (inline in the notebook,
editable). Word-list sizes are in the appendix.

---

## Identifiers & coverage

| # | Variable | Type | Definition |
|---|----------|------|------------|
| 0 | `quarter` | str | Quarter label, e.g. `1915Q2`. |
| 1 | `quarter_start` | date | First day of the quarter (e.g. `1915-04-01`). |
| 2 | `year` | int | Calendar year. |
| 3 | `q` | int | Quarter number 1–4. |
| 4 | `n_articles` | int | Number of dated articles in the quarter. Coverage; thin early quarters are noisier. |
| 42 | `mean_body_tokens` | float | Mean body token count per article in the quarter. |
| 43 | `ocr_quality` | float ∈ [0,1] | Token-weighted share of body tokens found in the LM master word list. Proxy for OCR/text quality; **relative, not absolute** (LM vocab is finance-skewed). Low in early decades. |

## Body sentiment — Loughran–McDonald (token-weighted level, fraction of body words)

| # | Variable | Definition / interpretation |
|---|----------|------------------------------|
| 5 | `lm_neg` | LM **Negative** words (financial negative sentiment). |
| 6 | `lm_pos` | LM **Positive** words. |
| 7 | `lm_unc` | LM **Uncertainty** words (risk/ambiguity). Feeds the discount-rate target. |
| 8 | `lm_lit` | LM **Litigious** words (legal/regulatory). |
| 9 | `lm_strong` | LM **Strong-Modal** words (e.g. *always, definitely*). |
| 10 | `lm_weak` | LM **Weak-Modal** words (e.g. *may, might, could*). |
| 11 | `lm_constr` | LM **Constraining** words (e.g. *require, restrict*). |
| 19 | `lm_tone` | **Net LM tone** = `lm_pos − lm_neg`. Higher = more optimistic. |

## Body sentiment — Harvard General Inquirer (Tetlock)

| # | Variable | Definition |
|---|----------|------------|
| 12 | `gi_neg` | GI **Negativ** words — Tetlock (2007) pessimism factor. |
| 13 | `gi_pos` | GI **Positiv** words. |

## Body — custom target-aligned lists (author-curated)

| # | Variable | Definition / target |
|---|----------|---------------------|
| 14 | `earn_salience` | Earnings/fundamentals terms (earnings, profit, margin, revenue, output…). **Earnings-growth** target. Direction-neutral salience. |
| 15 | `div_salience` | Dividend terms (dividend, payout, distribution + events: declared/omitted/suspended/resumed/arrears/scrip…). **Dividend-growth** target. |
| 16 | `dr_salience` | Discount-rate/risk terms (risk, premium, yield, interest, discount, credit, volatility…). **Discount-rate** target; pairs with `lm_unc`. |
| 17 | `cf_growth` | General **expansion/improvement** terms (grow, rise, increase, surge, strong…). |
| 18 | `cf_decline` | General **contraction/deterioration** terms (decline, fall, drop, recession, weak…). |
| 20 | `cf_tone` | **Net directional tone** = `cf_growth − cf_decline`. Interact with the salience columns for direction-by-topic. |

## Headline sentiment (`hl_` = same measures over headline tokens)

| # | Variable | Definition |
|---|----------|------------|
| 21–27 | `hl_lm_neg`, `hl_lm_pos`, `hl_lm_unc`, `hl_lm_lit`, `hl_lm_strong`, `hl_lm_weak`, `hl_lm_constr` | LM categories, headline. |
| 28–29 | `hl_gi_neg`, `hl_gi_pos` | GI categories, headline. |
| 30–32 | `hl_earn_salience`, `hl_div_salience`, `hl_dr_salience` | Custom salience, headline. |
| 33–34 | `hl_cf_growth`, `hl_cf_decline` | Directional, headline. |
| 35 | `hl_lm_tone` | `hl_lm_pos − hl_lm_neg`. |
| 36 | `hl_cf_tone` | `hl_cf_growth − hl_cf_decline`. |

*Headlines largely restate the macro state, so they tend to be more redundant with
macro-news features than the body columns — kept separate so the model can choose.*

## Disagreement / dispersion (across-article std, body)

| # | Variable | Definition |
|---|----------|------------|
| 37 | `lm_tone_disp` | Std across the quarter's articles of article-level LM tone. Disagreement in overall sentiment. |
| 38 | `lm_neg_disp` | Std of article-level `lm_neg`. |
| 39 | `lm_unc_disp` | Std of article-level `lm_unc`. |
| 40 | `gi_neg_disp` | Std of article-level GI Negativ (Tetlock disagreement). |
| 41 | `cf_tone_disp` | Std of article-level `cf_tone`. Disagreement about growth direction. |

## Aggregate

| # | Variable | Definition |
|---|----------|------------|
| 44 | `sent_agg` | Headline composite: mean of the **full-sample z-scores** of `lm_tone`, `gi_tone` (= `gi_pos − gi_neg`), and `cf_tone`. Higher = more optimistic. The z-score is a fixed cross-quarter rescale to balance the three lexicons (**not** temporal/rolling). Interpretable single series; redundant for the model, which has the components. |

---

## Target mapping (which columns feed which expectation series)

- **Discount-rate expectations** ← `dr_salience`, `lm_unc`, `gi_neg`, dispersion (`*_disp`)
- **Earnings-growth expectations** ← `earn_salience` × `cf_tone`, `lm_tone`
- **Dividend-growth expectations** ← `div_salience` × `cf_tone`

## Caveats (read before using)

- **No negation handling** — "not profitable" counts as positive. Tones are *noisy*
  valence proxies, not clean ones.
- **OCR noise** in early decades (pre-~1950). Carry `ocr_quality`/`n_articles` and
  down-weight or residualize; see the notebook's diagnostics cell.
- **Semantic drift** over 130 years — *discount, stock, security* shift meaning; affects
  the early end of `dr_salience`/`earn_salience` most.
- **Bag-of-words, market-level aggregate** — no firm/sector resolution.
- **`div_salience` event bucket** (declared/suspended/resumed/preferred…) can fire outside
  dividend context; the notebook flags it so it can be pruned.
- **Custom lists are author-curated, not canonical** — inline in the notebook Cell 1,
  editable; re-running regenerates the panel.
- **`sent_agg`** uses full-sample moments to standardize (a fixed rescale). If you need
  strict train-only standardization for the model, do it downstream on the raw components.

## Appendix — word-list sizes (count-verified)

| List | Words | Source |
|------|-------|--------|
| `lm_neg` | 2,355 | Loughran–McDonald Negative |
| `lm_pos` | 354 | LM Positive |
| `lm_unc` | 297 | LM Uncertainty |
| `lm_lit` | 905 | LM Litigious |
| `lm_strong` | 19 | LM Strong-Modal |
| `lm_weak` | 27 | LM Weak-Modal |
| `lm_constr` | 184 | LM Constraining |
| `gi_neg` | 2,005 | Harvard GI Negativ (2,291 entries → unique words) |
| `gi_pos` | 1,637 | Harvard GI Positiv (1,915 entries → unique words) |
| `earn_salience` | 21 | custom |
| `div_salience` | 27 | custom |
| `dr_salience` | 31 | custom |
| `cf_growth` | 57 | custom |
| `cf_decline` | 54 | custom |
| LM master vocab (OCR ref.) | 86,553 | LM master dictionary |
