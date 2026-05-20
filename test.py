import pandas as pd

df = pd.read_parquet("data/wsj_1965_2014_financial.parquet")  # read in the parquet file
print(df.columns.tolist())   # see all column names
print(df.dtypes)             # see what type each column is
df.head()                    # preview first 5 rows

print(len(df))
print(df["text"].isna().sum(), "missing text")
print(df["text_len"].describe())
df[["date", "headline", "text"]].head(3)