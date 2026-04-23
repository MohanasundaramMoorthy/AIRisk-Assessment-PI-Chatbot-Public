# Page Index Chatbot for AI Risk Assessment

A question-answering system built over the UK Government AI Risk Management Toolkit. Users ask natural language questions and receive precise, sourced answers extracted directly from a structured page index.

---

## Overview

This is NOT traditional RAG (Retrieval-Augmented Generation).

Most RAG systems chunk documents into fixed-length text fragments, embed them as vectors, and retrieve by cosine similarity. This system instead uses structured page-index retrieval:

- The source document (`Advice_Summary.docx`) is parsed into a structured index (`Advice_Summary_index.json`)
- Sections and tables are stored with metadata (heading, keywords, summary, content, headers, rows)
- At query time, user tokens are matched against these structured fields using weighted scoring
- Top-ranked results are passed to an LLM for answer synthesis

This approach is deterministic, explainable, and table-aware — ideal for compliance and risk documents.

---

## Architecture

User (Streamlit UI — app.py)
      │
      ▼
API Gateway (POST /query)
      │
      ▼
AWS Lambda (lambda_function.py)
      │
      ├── S3 (Advice_Summary_index.json)
      │
      └── Amazon Bedrock (Nova Lite)

---

## Pipeline

The system follows a deterministic, multi-stage retrieval and reasoning pipeline.

---

### 1. Document Ingestion

- Source document: `Advice_Summary.docx`
- Uploaded to AWS S3
- Index generation handled by: `extract_index.py`

---

### 2. Preprocessing (`extract_index.py`)

- Uses `python-docx` to parse document
- Splits content using heading styles
- Extracts tables (headers + rows)

Outputs:
- Sections
- Tables

Each gets:
- `section_id`, `table_id`
- `section_path` (hierarchical structure)

---

### 3. Index Construction (`extract_index.py`)

Creates structured JSON:

File:
- `Advice_Summary_index.json`

Structure:

Sections:
- heading
- keywords
- summary
- content
- section_path
- parent_section_id

Tables:
- table_title
- headers
- keywords
- rows

Stored in:
- AWS S3

---

### 4. Query Processing (`lambda_function.py`)

User query is processed:

- lowercased
- stopwords removed
- numeric tokens preserved

Example:
"What is likelihood level 3?"
→ ["likelihood", "level", "3"]

---

### 5. Candidate Scoring (`lambda_function.py`)

Each section and table is scored.

Section scoring:
- heading: 10
- keywords: 6
- summary: 4
- content: 5

Table scoring:
- table_title: 10
- headers: 6
- keywords: 6
- rows: 2
- best row bonus: 12

---

### 6. Ranking Modifiers (`lambda_function.py`)

Applied after scoring:

- UNIQUE_CONTENT_BONUS (×2.5)
- SINGLE_TOKEN_STRUCTURAL_TABLE_CAP
- ROW_ONLY_MULTIPLIER (×0.20)
- EMPTY_SECTION_MULTIPLIER (×0.55)

---

### 7. Candidate Selection

- Top 3 matches selected
- Includes:
  - metadata
  - preview content

Debug testing available via:
- `retrieval_test.py`

---

### 8. Context Construction (`lambda_function.py`)

Builds LLM input:

- section previews
- table previews
- best matching rows (up to ~2000 characters)

---

### 9. LLM Answer Generation (`lambda_function.py`)

- Model: Amazon Nova Lite (Bedrock)
- Input:
  - user query
  - retrieved context

Output:
- grounded answer
- hallucination controlled via prompt

---

### 10. Response Construction (`lambda_function.py`)

Returned JSON:

- answer
- sources:
  - id
  - heading
  - path

Optional:
- retrieved_matches (debug mode)

---

### 11. Frontend Rendering (`app.py`)

Streamlit app:

- sends query to API
- displays:
  - answer
  - sources
  - retrieved matches (optional)

Error handling:
- timeout handling
- connection failure handling

---

### 12. Runtime Optimisations (`lambda_function.py`)

- In-memory caching (`INDEX_CACHE`)
- Logging:
  - incoming query
  - cache hit/miss
  - retrieved count
  - top score

---

## Key Files

- `app.py` → Streamlit frontend
- `lambda_function.py` → backend retrieval + LLM logic
- `extract_index.py` → index generation
- `retrieval_test.py` → retrieval validation/debug
- `Advice_Summary_index.json` → structured index (S3)
- `Advice_Summary.docx` → source document

---

## Deployment

### Backend

Update index:
aws s3 cp Advice_Summary.index.json \
  s3://<your-s3-bucket>/indexes/Advice_Summary_index.json

Deploy Lambda:
zip lambda_deployment.zip lambda_function.py

aws lambda update-function-code \
  --function-name <your-lambda-function-name> \
  --zip-file fileb://lambda_deployment.zip
---

### Frontend

Deploy via:
https://share.streamlit.io

Steps:
1. Push repo to GitHub
2. Select repo
3. Choose `app.py`
4. Deploy

---

## Local Development
pip install streamlit requests
streamlit run app.py
Test backend locally:
DEBUG=true LOCAL_MODE=true python3 lambda_function.py “What is likelihood level 3?”
---

## Future Improvements

- Hybrid retrieval (structured + embeddings)
- Observability (CloudWatch dashboards)
- Index versioning
- Multi-document support
- Feedback loop