import os
import plotly.express as px
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Qanun Pulse", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    engine = create_engine(os.environ["DATABASE_URL"])
    keys = ["law_number", "year"]

    df = pd.read_sql("SELECT * FROM metrics_structure", engine)
    for table in ["metrics_text", "metrics_terms"]:
        df = df.merge(pd.read_sql(f"SELECT * FROM {table}", engine), on=keys)

    laws = pd.read_sql("SELECT law_number, year, title, category FROM laws", engine)
    return df.merge(laws, on=keys)


st.title("Qanun Pulse")
st.caption("Egyptian legislation: text metrics per law")

df = load_data()

categories = sorted(df["category"].unique())
selected = st.sidebar.multiselect("Document type", categories, default=categories)
df = df[df["category"].isin(selected)]

if df.empty:
    st.warning("Select at least one document type.")
    st.stop()

METRICS = {
    "Average words per article": "avg_words_per_article",
    "Average sentence length (words)": "avg_sentence_length_words",
    "Long-word ratio": "long_word_ratio",
    "Legal-term density (per 1000 words)": "term_density_per_1000_words",
}

df["law"] = df["law_number"].astype(str) + "/" + df["year"].astype(str)

choice = st.selectbox("Metric", list(METRICS))
fig = px.bar(
    df, x="law", y=METRICS[choice], color="category",
    hover_data=["title"], title=choice,
)
st.plotly_chart(fig)

with st.expander("Show data table"):
    # Segmentation fault with the st.dataframe() method, so using st.write() instead.
    st.write(df)

with st.expander("About these metrics"):
    st.markdown("""
- Covers 5 of the 10 laws in the database; the others have no article text yet.
- Law 258 of 2024 is excluded (its PDF text is reversed).
- Compare documents of the same type: a decree and a labor code are not alike.
- Legal-term density uses a short list of 15 general terms.
- Lexical diversity is not shown: it falls as texts get longer.
""")