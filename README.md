# Page Index Chatbot for AI Risk Assessment

A question-answering system built over the UK Government AI Risk Management Toolkit.

**Live app:** [pageindexchatbotpi.streamlit.app](https://pageindexchatbotpi.streamlit.app/)

---

## What it does

Users ask natural language questions about AI risk management and receive precise, sourced answers extracted directly from the document. Every answer includes the source section or table it came from.

---

## How it works

This is **not traditional RAG**. Instead of embedding chunks and retrieving by cosine similarity, it uses **structured page-index retrieval**:

- The source document is pre-processed into a typed JSON index of sections and tables, each with metadata (heading, keywords, summary, content, table headers, rows)
- At query time, user tokens are matched against these structured fields using weighted scoring
- The top 3 ranked results are passed to an LLM (Amazon Nova Lite via Bedrock) for grounded answer synthesis
- Answers are deterministic, explainable, and table-aware

---

## Architecture

```
User → Streamlit UI → API Gateway → AWS Lambda → S3 (page index) → Amazon Bedrock (Nova Lite)
```

---

## Key Features

- Table-aware retrieval — scores tables at both structural and row level
- Explainable answers — every response shows source IDs, headings, and document paths
- No hallucination design — model is constrained to retrieved context only
- In-memory index caching on Lambda for fast warm responses

---

## Deployment

### Frontend (Streamlit Cloud)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select `app.py`
3. Add your API endpoint under **Secrets**:
   ```toml
   [api]
   url = "https://<your-api-gateway-endpoint>/query"
   ```
4. Deploy

### Backend (AWS)

Deploy your own Lambda + S3 index + API Gateway, then point the Streamlit secret to your endpoint.

---

## Local Development

```bash
pip install streamlit requests
```

Create `.streamlit/secrets.toml`:
```toml
[api]
url = "https://<your-api-gateway-endpoint>/query"
```

```bash
streamlit run app.py
```

---

## Future Improvements

- Hybrid retrieval (structured scoring + semantic embeddings)
- Multi-document support
- Observability dashboard (query logs, answer quality metrics)
- User feedback loop
