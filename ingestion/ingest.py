import pandas as pd
from sqlalchemy import create_engine
import os




# 1. Load paths from environment variables (with local fallbacks for testing outside Docker)
data_path = os.getenv("DATA_FILE_PATH", r"C:\Users\Forsan\Desktop\Qanun Pulse\data\reshaped_laws.json")
db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://root:yoyo@localhost:5432/qanon_db")

print(f"📂 Loading data from: {data_path}")
df = pd.read_json(data_path)

engine = create_engine(db_url)




laws_df = df[['law_number', 'year', 'title', 'category', 'status', 'issue_date']].copy()
laws_df


# 1. First, explode the lists so each dict gets its own row
df_exploded = df.explode('articles')

# 2. Now, extract the dictionary keys ('article_number' and 'content') into separate columns.
# We use pd.json_normalize for this, which is perfect for dictionaries.
articles_df = pd.json_normalize(df_exploded['articles'])

# 3. Add the 'law_number' back to the articles_df so we can link them in the database.
# Because we exploded, the index of articles_df perfectly matches the index of df_exploded.
articles_df['law_number'] = df_exploded['law_number'].values

# 4. Reorder and rename columns to match our database schema
# We drop any rows where 'articles' might have been NaN (empty lists)
articles_df = articles_df.dropna(subset=['content'])



print(pd.io.sql.get_schema(laws_df, name='laws_data', con=engine))
print(pd.io.sql.get_schema(articles_df, name='articles_data', con=engine))

laws_df.head(n=0).to_sql(name='laws_data', con=engine, if_exists='replace')
articles_df.head(n=0).to_sql(name='articles_data', con=engine, if_exists='replace')


print("Inserting data...")
with engine.begin() as connection:
    # IMPORTANT: You MUST insert 'laws' first. 
    # If you insert articles first, the database will reject them because 
    # their law_number doesn't exist in the laws table yet!
    
    laws_df.to_sql('laws_data', connection, if_exists='append', index=False)
    print(f"✅ Inserted {len(laws_df)} laws.")
    
    articles_df.to_sql('articles_data', connection, if_exists='append', index=False)
    print(f"✅ Inserted {len(articles_df)} articles.")

print("🎉 Database ingestion complete!")