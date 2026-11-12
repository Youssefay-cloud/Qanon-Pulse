import os
import pandas as pd
from sqlalchemy import create_engine

# When you run locally: uses local_laws.db
# When your teammate runs inside Docker: automatically connects to PostgreSQL via DATABASE_URL
DB_URL = os.getenv("DATABASE_URL", "sqlite:///local_laws.db")
engine = create_engine(DB_URL)

def read_table(table_name: str, query: str = None) -> pd.DataFrame:
    sql = query if query else f"SELECT * FROM {table_name}"
    return pd.read_sql(sql, con=engine)

def write_table(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
    df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)