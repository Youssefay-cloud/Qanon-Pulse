import re
import pandas as pd
from transform.io import read_table, write_table

# Arabic and legal sentence delimiters: period, newline, semicolon (؛), exclamation, question marks
SENTENCE_SPLIT_REGEX = re.compile(r'[\.\n؛!\؟]+')

def compute_text_metrics(df_articles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (law_number, year), group in df_articles.groupby(["law_number", "year"]):
        all_text = " ".join(group["article_content"].tolist())
        words = [w for w in all_text.split() if w]
        total_words = len(words)
        
        if total_words == 0:
            continue
            
        sentences = [s.strip() for s in SENTENCE_SPLIT_REGEX.split(all_text) if len(s.strip()) > 3]
        total_sentences = len(sentences) if sentences else 1
        
        # Vocabulary richness (Type-Token Ratio)
        unique_words = len(set(words))
        lexical_diversity = round(unique_words / total_words, 4)
        
        # Word length measurements
        char_counts = [len(w) for w in words]
        avg_word_length = round(sum(char_counts) / total_words, 2)
        
        long_words = [w for w in words if len(w) >= 7]
        long_word_ratio = round(len(long_words) / total_words, 4)
        
        # Sentence length measurement
        avg_sentence_length = round(total_words / total_sentences, 2)
        
        rows.append({
            "law_number": law_number,
            "year": year,
            "avg_sentence_length_words": avg_sentence_length,
            "avg_word_length_chars": avg_word_length,
            "long_word_ratio": long_word_ratio,
            "lexical_diversity": lexical_diversity
        })
    return pd.DataFrame(rows)

def run():
    print("Reading articles_normalized from database...")
    df = read_table("articles_normalized")
    
    print("Computing text and complexity metrics per law...")
    metrics_df = compute_text_metrics(df)
    
    print(f"Writing {len(metrics_df)} rows to table 'metrics_text'...")
    write_table(metrics_df, "metrics_text", if_exists="replace")
    print("Done! 'metrics_text' table successfully populated.")

if __name__ == "__main__":
    run()