import os
import re
import pandas as pd
from transform.io import read_table, write_table

# Default fallback list if CSV is not found
DEFAULT_TERMS = [
    "محكمة", "دعوى", "استئناف", "بطلان", "التزام",
    "عقوبة", "تعويض", "مخالفة", "تشريع", "مشرع",
    "طعن", "نقض", "حكم", "قضاء", "دستور"
]

def load_terms() -> list[str]:
    csv_path = os.path.join(os.path.dirname(__file__), "data", "legal_terms.csv")
    if os.path.exists(csv_path):
        df_terms = pd.read_csv(csv_path)
        col = df_terms.columns[0]
        return [str(t).strip() for t in df_terms[col].dropna() if str(t).strip()]
    return DEFAULT_TERMS

def build_term_regex(term: str) -> re.Pattern:
    # Matches optional proclitics: و, ف, ك, ب, ل, ال, وال, فال, بال, كال
    prefix_pattern = r'(?:\b(?:و|ف|ك|ب|ل|ال|وال|فال|بال|كال)?'
    return re.compile(rf'{prefix_pattern}{re.escape(term)}\b)', flags=re.UNICODE)

def compute_term_density(df_articles: pd.DataFrame, terms: list[str]) -> pd.DataFrame:
    compiled_terms = {term: build_term_regex(term) for term in terms}
    rows = []
    
    for (law_number, year), group in df_articles.groupby(["law_number", "year"]):
        text = " ".join(group["article_content"].tolist())
        words = [w for w in text.split() if w]
        total_words = len(words)
        
        if total_words == 0:
            continue
            
        total_matches = sum(len(pattern.findall(text)) for pattern in compiled_terms.values())
        density_per_1000 = round((total_matches / total_words) * 1000, 2)
        
        rows.append({
            "law_number": law_number,
            "year": year,
            "legal_term_matches": total_matches,
            "term_density_per_1000_words": density_per_1000
        })
        
    return pd.DataFrame(rows)

def run():
    print("Reading articles_normalized from database...")
    df = read_table("articles_normalized")
    
    terms = load_terms()
    print(f"Computing jargon density using {len(terms)} legal terms...")
    metrics_df = compute_term_density(df, terms)
    
    print(f"Writing {len(metrics_df)} rows to table 'metrics_terms'...")
    write_table(metrics_df, "metrics_terms", if_exists="replace")
    print("Done! 'metrics_terms' table successfully populated.")

if __name__ == "__main__":
    run()