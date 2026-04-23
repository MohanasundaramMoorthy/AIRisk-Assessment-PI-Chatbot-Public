import streamlit as st
import requests

API_URL = "https://2gt339l3ia.execute-api.us-east-1.amazonaws.com/query"

st.set_page_config(page_title="AI Risk Management Toolkit — Q&A", page_icon="🤖", layout="wide")

st.title("AI Risk Management Toolkit — Q&A")
st.write("Ask questions about the AI Risk Management Toolkit document.")

# ── Session state initialisation ──────────────────────────────────────────────
# clear_count is used as a suffix for the text_area key.
# Incrementing it forces Streamlit to create a fresh, empty widget.
if "clear_count" not in st.session_state:
    st.session_state.clear_count = 0
if "result" not in st.session_state:
    st.session_state.result = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None

# ── Input ─────────────────────────────────────────────────────────────────────
query = st.text_area(
    "Enter your question",
    height=120,
    placeholder="Example: What is likelihood level 3?",
    key=f"query_input_{st.session_state.clear_count}",
)

show_matches = st.checkbox("Show retrieved matches", value=False)

col1, col2 = st.columns([1, 1])
with col1:
    ask_clicked = st.button("Ask", use_container_width=True)
with col2:
    clear_clicked = st.button("Clear", use_container_width=True)

# ── Clear ─────────────────────────────────────────────────────────────────────
if clear_clicked:
    st.session_state.clear_count += 1   # new key → fresh empty text_area
    st.session_state.result = None
    st.session_state.api_error = None
    st.rerun()

# ── Ask ───────────────────────────────────────────────────────────────────────
if ask_clicked:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Getting answer..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                )
                if response.status_code != 200:
                    st.session_state.api_error = (
                        f"API call failed with status {response.status_code}\n{response.text}"
                    )
                    st.session_state.result = None
                else:
                    st.session_state.result = response.json()
                    st.session_state.api_error = None
            except requests.exceptions.Timeout:
                st.session_state.api_error = "The request took too long. Please try again."
                st.session_state.result = None
            except requests.exceptions.RequestException:
                st.session_state.api_error = "Unable to connect to the service. Please try again."
                st.session_state.result = None

# ── Display ───────────────────────────────────────────────────────────────────
if st.session_state.api_error:
    st.error("Failed to connect to the API.")
    st.code(st.session_state.api_error)

if st.session_state.result:
    data = st.session_state.result

    st.subheader("Answer")
    st.write(data.get("answer", "No answer returned."))

    sources = data.get("sources", [])
    if sources:
        st.subheader("Sources used")
        for src in sources:
            st.markdown(
                f"- **{src.get('id')}** | {src.get('type')} | {src.get('heading')}  \n"
                f"  {src.get('path')}"
            )

    if show_matches:
        matches = data.get("retrieved_matches", [])
        if matches:
            st.subheader("Retrieved matches")
            for i, match in enumerate(matches, start=1):
                with st.expander(f"Match {i}: {match.get('heading')} ({match.get('id')})"):
                    st.write(f"**Type:** {match.get('type')}")
                    st.write(f"**Score:** {match.get('score')}")
                    st.write(f"**Path:** {match.get('path')}")
                    st.write("**Preview:**")
                    st.write(match.get("preview"))
