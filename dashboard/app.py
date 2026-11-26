from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI  # Add this import

st.set_page_config(page_title="Qanun Pulse", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "metrics.csv"

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

st.title("Qanun Pulse")
st.caption("Egyptian legislation: text metrics per law")

try:
    df = load_data()
except Exception:
    st.error("No metrics file yet. Run the pipeline in Airflow (http://localhost:8081), then refresh.")
    st.stop()

# --- NEW: Create Tabs ---
tab_data, tab_chat = st.tabs(["📊 Data Dashboard", "🤖 AI Assistant"])

with tab_data:
    # --- ORIGINAL DASHBOARD CODE GOES HERE ---
    categories = sorted(df["category"].unique())
    selected = st.sidebar.multiselect("Document type", categories, default=categories)
    df_filtered = df[df["category"].isin(selected)]

    if df_filtered.empty:
        st.warning("Select at least one document type.")
    else:
        METRICS = {
            "Average words per article": "avg_words_per_article",
            "Average sentence length (words)": "avg_sentence_length_words",
            "Long-word ratio": "long_word_ratio",
            "Legal-term density (per 1000 words)": "term_density_per_1000_words",
        }

        df_filtered["law"] = df_filtered["law_number"].astype(str) + "/" + df_filtered["year"].astype(str)

        choice = st.selectbox("Metric", list(METRICS))
        fig = px.bar(
            df_filtered, x="law", y=METRICS[choice], color="category",
            hover_data=["title"], title=choice,
        )
        st.plotly_chart(fig)

        with st.expander("Show data table"):
            st.write(df_filtered)

        with st.expander("About these metrics"):
            st.markdown("""
- Covers 5 of the 10 laws in the database; the others have no article text yet.
- Law 258 of 2024 is excluded (its PDF text is reversed).
- Compare documents of the same type: a decree and a labor code are not alike.
- Legal-term density uses a short list of 15 general terms.
- Lexical diversity is not shown: it falls as texts get longer.
""")

# --- NEW: CHAT TAB IMPLEMENTATION ---
with tab_chat:
    st.header("Chat with Qanun Pulse AI")
    st.caption("Ask questions about the Egyptian legislation in the database.")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask about the laws..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # Connect to llama.cpp service (using the Docker service name)
            client = OpenAI(
                base_url="http://llm:8080/v1", 
                api_key="not-needed" # llama.cpp doesn't require an API key by default
            )
            
            try:
                # Create the streaming request
                stream = client.chat.completions.create(
                    model="local-model", # The model name doesn't matter much for llama.cpp
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                
                # Stream the response using st.write_stream
                response_text = st.write_stream(stream)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Could not connect to the AI model. Is the 'llm' service running? Error: {e}")