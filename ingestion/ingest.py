import pandas as pd
from sqlalchemy import create_engine, text
import os




# 1. Load paths from environment variables (with local fallbacks for testing outside Docker)
data_path = os.getenv("DATA_FILE_PATH", r"C:\Users\Forsan\Desktop\Qanun Pulse\data\reshaped_laws.json")
db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://root:yoyo@localhost:5432/qanon_db")

print(f"📂 Loading data from: {data_path}")
df = pd.read_json(data_path)

engine = create_engine(db_url)




laws_df = df[['law_number', 'year', 'title', 'category', 'status', 'issue_date']].copy()


# 1. First, explode the lists so each dict gets its own row and drop the NAN articles
df_exploded = df.explode('articles').dropna(subset=['articles'])

# 2. Now, extract the dictionary keys ('article_number' and 'content') into separate columns.
# We use pd.json_normalize for this, which is perfect for dictionaries.
articles_df = pd.json_normalize(df_exploded['articles'])

# 3. Add the 'law_number' AND 'year' back to the articles_df so we can link them in the database.
# Law numbers repeat across years (Law 12 of 2003 vs Law 12 of 2010), so both are needed.
# Because we exploded, the index of articles_df perfectly matches the index of df_exploded.
articles_df['law_number'] = df_exploded['law_number'].values
articles_df['year'] = df_exploded['year'].values

# 4. Drop any article rows that have no content
articles_df = articles_df.dropna(subset=['content'])



# Explicit schema: primary keys + a foreign key, instead of letting pandas guess
DDL = """
CREATE TABLE IF NOT EXISTS laws (
    law_number INT NOT NULL,
    year INT NOT NULL,
    title TEXT,
    category TEXT,
    status TEXT,
    issue_date TEXT, 
    PRIMARY KEY (law_number, year)
);
CREATE TABLE IF NOT EXISTS articles (
    law_number INT NOT NULL,
    year INT NOT NULL,
    article_number TEXT NOT NULL,
    content TEXT NOT NULL,
    PRIMARY KEY (law_number, year, article_number),
    FOREIGN KEY (law_number, year) REFERENCES laws (law_number, year)
);
"""

print("Inserting data...")
with engine.begin() as connection:
    connection.execute(text(DDL))

    # Wipe and reload so re-running the script never creates duplicates
    connection.execute(text("TRUNCATE articles, laws"))

    # Laws first: the foreign key requires the law to exist before its articles
    laws_df.to_sql('laws', connection, if_exists='append', index=False)
    print(f"✅ Inserted {len(laws_df)} laws.")

    articles_df.to_sql('articles', connection, if_exists='append', index=False)
    print(f"✅ Inserted {len(articles_df)} articles.")

print("🎉 Database ingestion complete!")