import os
import pandas as pd
from sqlalchemy import create_engine
from transform.arabic_text import normalize

engine = create_engine(os.environ["DATABASE_URL"])


laws = pd.read_sql("Select * from laws", engine)
articles = pd.read_sql("SELECT * FROM articles", engine)

articles["content_clean"] = articles["content"].map(normalize)

print(articles["content"].iloc[0][:200])
print(articles["content_clean"].iloc[0][:200])

articles["n_words"] = articles["content"].str.split().str.len()
articles["n_words_clean"] = articles["content_clean"].str.split().str.len()
print(articles[["law_number", "n_words", "n_words_clean"]])

out = articles[["law_number", "year", "article_number", "content_clean"]]
out.to_sql("articles_clean", engine, if_exists="replace", index=False)