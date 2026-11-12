import os

import pandas as pd

from transform.io import read_table

OUT_PATH = os.getenv("EXPORT_PATH", "dashboard/data/metrics.csv")
KEYS = ["law_number", "year"]


def build_dashboard_table(structure, text, terms, laws) -> pd.DataFrame:
    """One row per law: all metrics plus title and category."""
    df = structure.merge(text, on=KEYS).merge(terms, on=KEYS)
    return df.merge(laws[KEYS + ["title", "category"]], on=KEYS)


def run():
    print("Reading metrics tables...")
    df = build_dashboard_table(
        read_table("metrics_structure"),
        read_table("metrics_text"),
        read_table("metrics_terms"),
        read_table("laws"),
    )
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8")
    print(f"Done! Wrote {len(df)} rows to {OUT_PATH}")


if __name__ == "__main__":
    run()