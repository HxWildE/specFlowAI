# SpecFlow AI: Systems Blueprint & Operating Guide

## 1. System Vision
**SpecFlow AI** is an enterprise-grade RFP (Request for Proposal) and SRS (Software Requirements Specification) intelligence platform tailored for software agencies and engineering teams. It ingests complex, unstructured client documents (20–50 pages), extracts functional/non-functional requirements, performs scope-creep and risk auditing, retrieves historical agency estimates via hybrid RAG, computes engineering effort/budget estimates, and synthesizes structured IEEE-standard SRS documents and Statements of Work (SOWs).

---

## 2. Core Architecture & Tech Stack

```
   [ Client / React Frontend (Vite + Tailwind CSS) ]
                        |
            HTTP Upload | SSE Stream (/api/documents/{id}/stream)
                        v
     [ FastAPI Async Gateway (asyncpg + SQLAlchemy 2.0) ]
                        |
            Produce Event (document.uploaded)
                        v
     [ Apache Kafka Event Broker ] <---> [ Dead-Letter Queue (rfp.dlq) ]
                        |
            Consume Event
                        v
    [ Python Multi-Agent AI Worker (LangGraph StateGraph) ]
        |---> requirements_extractor (Gemini 2.5 Flash Structured JSON)
        |---> risk_auditor (Scope creep, edge cases, ambiguities) [Parallel]
        |---> effort_estimator (RAG with pgvector + Rate cards)  [Parallel]
        |---> spec_compiler (Synthesis + Self-Critique / Retry)
                        |
            Read/Write Vectors & Relational Records
                        v
     [ PostgreSQL 16 + pgvector (Relational Tables + HNSW Vector Index) ]
```

### Component Stack
* **Backend:** Python 3.12+, FastAPI (fully asynchronous), Pydantic v2 (strict JSON schemas), SQLAlchemy 2.0 (`asyncpg` driver).
* **AI Orchestration:** LangGraph (`StateGraph` with typed state, parallel branch fan-out, conditional validation edges) + Google Gemini (`gemini-2.5-flash` with structured outputs via `response_schema`, `text-embedding-004`).
* **Storage & Memory:** PostgreSQL 16 with `pgvector` extension (768-dim embeddings, HNSW indexing).
* **Asynchronous Queue & Streaming:** Apache Kafka (Docker Compose) for decoupled event streams, Dead-Letter Queue (`rfp.dlq`), and Server-Sent Events (SSE) for frontend streaming.
* **Frontend:** React + Vite + Tailwind CSS built under the OpenAI Frontend Skill philosophy (minimal chrome, memoized updates, high craft, no generic dashboard cards).

---

## 3. Two-Week Execution Roadmap

* **Phase 0 (Setup & Environment):**
  - Install OpenAI Frontend Skill into `.agents/skills/frontend-skill/`
  - Connect Git remote repository and enforce `.gitignore`
  - Monorepo directory structure & `docker-compose.yml` (Postgres + pgvector, Kafka)
* **Phase 1 (Database, Async FastAPI & Ingestion):**
  - PostgreSQL 16 + `pgvector` Docker setup
  - SQLAlchemy async models (`workspaces`, `documents`, `knowledge_chunks`, `generated_specs`)
  - FastAPI document upload & PyMuPDF chunking pipeline
* **Phase 2 (LangGraph Multi-Agent Engine):**
  - Typed state definition (`GraphState`)
  - 4 specialized nodes: `requirements_extractor`, `risk_auditor`, `effort_estimator`, `spec_compiler`
  - Parallel node execution and conditional self-critique/retry loop
* **Phase 3 (pgvector RAG & Kafka Event Streaming):**
  - Agency knowledge base ingestion (historical projects + rate cards)
  - Kafka producer on FastAPI upload $\rightarrow$ consumer in AI worker $\rightarrow$ DLQ on unrecoverable failure
  - SSE endpoint (`/api/documents/{id}/stream`) for real-time state transitions
* **Phase 4 (Crafted Frontend & Production Polish):**
  - Minimal React split-view UI (Upload & Live Pipeline, SRS Editor, Knowledge Base)
  - Docx/Markdown export and interview-readiness system design documentation
