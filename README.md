# AI-Powered AML Compliance Assistant

A locally runnable student project for AML screening with SQLite, deterministic rule screening, sanctions matching, regulatory retrieval, RBAC, PII masking, a two-agent workflow, audit logs, and feedback-aware risk scoring.

## Project Overview
The application combines regulatory demo material, transaction data, and a sanctions watchlist. It answers natural-language questions using only data permitted by the authenticated role. Missing LLM credentials activate a usable offline Demo Mode; no API key is hardcoded.

## Architecture
```text
DATA SOURCES -> ingestion -> SQLite + local vector index
USER -> authentication -> RBAC -> permitted/masked data
-> ScreeningAgent -> explicit state handoff -> InvestigationAgent
-> evidence-backed response -> analyst feedback -> adjusted future score
```

## Features
- 200 generated transactions with large, repeated, high-risk, narrative, and watchlist examples.
- CSV/Excel transaction and sanctions loaders with validation; PDF/TXT regulatory extraction and chunking.
- Local TF-style embeddings and cosine retrieval. The implementation is offline and evidence-bearing; optional FAISS/sentence-transformers can replace the adapter.
- Backend RBAC for ADMIN, AML_ANALYST, EXTERNAL_AUDITOR, and a portfolio-scoped RELATIONSHIP_MANAGER. PII is masked before restricted data can reach agents.
- Deterministic ScreeningAgent and separate InvestigationAgent with logged handoff.
- SQLite alerts/feedback/audit tables and a measurable FALSE POSITIVE score penalty.
- Streamlit dashboard, ingestion screen, assistant, alerts, feedback, evaluation, and audit views.
- Transaction descriptions are untrusted data; no description is executed as an instruction.

## Installation (Windows PowerShell)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python database/seed.py
streamlit run app.py
```

## Environment
Copy `.env.example` to `.env`. `GROQ_API_KEY`, `OPENAI_API_KEY`, and `LLM_PROVIDER` are optional. Without a key the UI displays `Demo Mode — LLM API key not configured` and continues with deterministic behavior.

## Demo accounts
`admin/admin123`, `analyst/analyst123`, `auditor/auditor123`, `relationship_manager/rm123`.

## Database and data ingestion
`database/schema.sql` creates users, transactions, sanctions, alerts, feedback, and audit_logs. `python database/seed.py` generates sample CSVs, a clearly labeled demo regulatory document, loads SQLite, and builds the local index. Upload/loader functions accept CSV and Excel paths and reject missing columns.

## RAG and agents
Regulatory text is extracted, cleaned, chunked with document/page metadata, embedded, and searched by similarity. Answers expose document, page, and evidence text; no result means `Insufficient regulatory evidence found.` Screening applies configurable rules for large transactions, repetition, high-risk countries, unusual narratives, and sanctions. Investigation verifies that findings have regulatory evidence and produces the final response.

## RBAC and PII
Permissions are backend configuration, not prompt text. ADMIN may see permitted customer fields, AML_ANALYST sees masked customer fields, EXTERNAL_AUDITOR cannot access customer records, and RELATIONSHIP_MANAGER sees masked records only for customers C001-C010. Scope checks happen before customer data is returned or passed to agents. A denied request returns `ACCESS DENIED` without retrieving the restricted record for an agent.

## Testing and evaluation
```powershell
pytest
python evaluation/evaluate.py
```
The evaluation runner has 15 cases covering screening, sanctions, RAG, combined reasoning, masking, three role refusals, portfolio scoping, handoff, and feedback. Results are calculated from the live in-memory database and the expected current pass rate is 100%.

## Data provenance and walkthrough
Transactions and customer names are fully synthetic and generated locally; the bundled demo guidance is clearly labeled synthetic material. The ingestion layer accepts public FATF/RBI/FCA PDFs and OFAC/UN CSV or Excel files through the Data Ingestion screen, so a walkthrough can replace the demo inputs without changing the agents. The understanding layer precomputes cleaned chunks, metadata, TF-style embeddings, and the local index; screening rules and analyst feedback remain online because they depend on current data and dispositions. For a walkthrough, show ingestion, analyst masking, auditor refusal, relationship-manager portfolio scope, the screening-to-investigation handoff, then submit a FALSE POSITIVE and compare the before/after risk score.

## Scalability
| Component | Current failure mode at 100x | Future solution |
|---|---|---|
| Transactions | SQLite write/concurrency bottleneck | PostgreSQL, indexes, partitioning, stream processing |
| Vector search | Single FAISS/local index growth | Scalable vector DB with metadata filtering and distributed indexing |
| LLM | API rate limits and latency | Queue, caching, async processing, model routing |
| Users | Concurrent Streamlit sessions | Horizontal scaling, load balancing, shared cache |
| Agents | Long-running synchronous workflows | Task queues and asynchronous workers |

## Limitations
The included regulation is synthetic demo material, not official FATF/RBI advice. The offline retrieval adapter is intentionally simple. Production use requires approved sources, stronger identity management, encryption, secrets management, legal review, and a production-grade vector/LLM deployment.
