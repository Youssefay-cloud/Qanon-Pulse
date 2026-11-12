import pandas as pd
from transform.io import read_table, write_table

def compute_structure_metrics(df_articles: pd.DataFrame) -> pd.DataFrame:
    metrics = df_articles.groupby(["law_number", "year"]).agg(
        total_articles=("article_number", "count"),
        total_words=("word_count", "sum"),
        avg_words_per_article=("word_count", "mean"),
        max_article_words=("word_count", "max"),
        min_article_words=("word_count", "min")
    ).reset_index()
    
    metrics["avg_words_per_article"] = metrics["avg_words_per_article"].round(2)
    return metrics

def run():
    print("Reading articles_normalized from database...")
    df = read_table("articles_normalized")
    
    print("Computing structural metrics per law...")
    metrics_df = compute_structure_metrics(df)
    
    print(f"Writing {len(metrics_df)} rows to table 'metrics_structure'...")
    write_table(metrics_df, "metrics_structure", if_exists="replace")
    print("Done! 'metrics_structure' table successfully populated.")

if __name__ == "__main__":
    run()