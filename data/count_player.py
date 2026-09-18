import pandas as pd

df = pd.read_csv("players_raw.csv")

total = len(df)
with_country = df["country_code"].fillna("").str.strip().ne("").sum()
with_title = df["title"].fillna("").str.strip().ne("").sum()

print(f"Total players:        {total}")
print(f"With country code:    {with_country}")
print(f"With title:           {with_title}")

print(f"Without country code: {total - with_country}")
print(f"Without title:        {total - with_title}")