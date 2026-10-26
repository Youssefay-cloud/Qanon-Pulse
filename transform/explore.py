import os
import pandas as pd
from sqlalchemy import create_engine
from transform.arabic_text import normalize

engine = create_engine(os.environ["DATABASE_URL"])


laws = pd.read_sql("Select * from laws", engine)
articles = pd.read_sql("SELECT * FROM articles", engine)

print(laws.shape, articles.shape)
print(articles.columns.tolist())
print(articles.dtypes)
 
print(articles.isna().sum())


print("duplicates: ", articles["content"].duplicated().sum())
print("empty: ", (articles["content"].str.strip() == "").sum())

articles["n_words"] = articles["content"].str.split().str.len()
print(articles.groupby("law_number")["n_words"].describe())

for text in articles["content"].sample(5, random_state=1):
    print("------")
    print(text[:300])

