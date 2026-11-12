# Legal Text Metrics Definitions

This document defines the formulas and methodology used across the transformation and analytical layers of the project.

---

## 1. Structural Metrics (`metrics_structure`)
Derived from granular article extraction (`articles_normalized`).

- **total_articles:** Total count of individual articles identified and split within the law.
- **total_words:** Cumulative word count across all articles of the law after Arabic text normalization.
- **avg_words_per_article:** `total_words / total_articles`. Measures the typical length and verbosity of an article in this law.
- **max_article_words:** Word count of the longest article in the law.
- **min_article_words:** Word count of the shortest article in the law.

---

## 2. Text & Readability Metrics (`metrics_text`)
Derived from the concatenated normalized article bodies.

- **avg_sentence_length_words:** `total_words / total_sentences`. Sentences are delimited using the pattern `[\.\n؛!\؟]+`. Reflects syntactic density and readability.
- **avg_word_length_chars:** `total_characters / total_words`. Measures average word complexity.
- **long_word_ratio:** Count of words with $\ge 7$ characters divided by `total_words`. An established indicator of technical and legal verbosity in Arabic texts.
- **lexical_diversity (TTR):** Type-Token Ratio calculated as `unique_words / total_words`. Measures vocabulary richness versus repetitive phrasing.

---

## 3. Legal Terminology Metrics (`metrics_terms`)
Derived from keyword pattern matching against the curated dictionary (`transform/data/legal_terms.csv`).

- **legal_term_matches:** Total occurrences of curated legal terms identified across the law. Regex patterns support standard Arabic prefixes (`و`, `ف`, `ك`, `ب`, `ل`, `ال`, `وال`, `فال`, `بال`, `كال`).
- **term_density_per_1000_words:** `(legal_term_matches / total_words) * 1000`. Standardized jargon density permitting comparative analysis across statutes of varying lengths.