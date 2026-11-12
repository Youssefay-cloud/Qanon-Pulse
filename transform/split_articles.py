import re
import pandas as pd
from transform.io import read_table, write_table
from transform.arabic_text import normalize

# Matches standard Egyptian law article headers (e.g. مادة 1, المادة (1), المادة الأولى)
ARTICLE_PATTERN = re.compile(
    r'(?:^|\n)[ \t]*\(?[ \t]*(?:المادة|مادة)[ \t]*\(?[ \t]*(\d+|[\u0621-\u064A]+(?:[ \t]+عشرة?)?)[ \t]*\)?[ \t]*:?',
    flags=re.UNICODE
)

# "المادة 143 من هذا القانون" is a reference inside a sentence, not a heading
CROSS_REFERENCE = re.compile(r'[ \t]*من[ \t]')


def clean_unicode_artifacts(text: str) -> str:
    """Removes private-use unicode glyphs like \uf242 left by PDF extraction."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\ue000-\uf8ff]', '', text).strip()

def split_law_into_articles(law_number: int, year: int, content: str) -> list[dict]:
    content = clean_unicode_artifacts(content)
    matches = [m for m in ARTICLE_PATTERN.finditer(content)
           if not CROSS_REFERENCE.match(content, m.end())]
    
    # If no article headers found, store the whole block as article 1
    if not matches:
        clean_text = normalize(content)
        return [{
            "law_number": law_number,
            "year": year,
            "article_number": "1",
            "article_content": clean_text,
            "word_count": len(clean_text.split())
        }]

    articles = []
    for i, match in enumerate(matches):
        raw_num = match.group(1) 
        article_num = normalize(raw_num) if raw_num else str(i + 1)
        
        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        
        body = content[start_idx:end_idx].strip()
        body_clean = normalize(body)
        
        if body_clean:
            articles.append({
                "law_number": law_number,
                "year": year,
                "article_number": article_num,
                "article_content": body_clean,
                "word_count": len(body_clean.split())
            })
            
    return articles

def run():
    print("Reading raw 'articles' table from local database...")
    raw_df = read_table("articles")
    
    # Exclude law 258 (known reversed OCR issue documented in summary)
    raw_df = raw_df[~((raw_df["law_number"] == 258) & (raw_df["year"] == 2024))]
    
    records = []
    for _, row in raw_df.iterrows():
        records.extend(split_law_into_articles(row["law_number"], row["year"], str(row["content"])))
        
    split_df = pd.DataFrame(records)
    
    print(f"Writing {len(split_df)} split articles to table 'articles_normalized'...")
    write_table(split_df, "articles_normalized", if_exists="replace")
    print("Done! 'articles_normalized' table successfully populated.")

if __name__ == "__main__":
    run()