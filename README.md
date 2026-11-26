# SpecFlow AI

> **Enterprise RFP & SRS Intelligence Engine for Software Agencies and Engineering Teams**

SpecFlow AI is an asynchronous, multi-agent platform designed to parse unstructured 20–50 page client RFPs (Request for Proposals) and rough specification documents. It automatically extracts functional and non-functional requirements, performs scope-creep and risk auditing, queries historical agency benchmarks via hybrid RAG, calculates engineering effort and budget projections, and synthesizes structured IEEE-standard Software Requirements Specifications (SRS) and Statements of Work (SOW).

---

## Architecture Overview

```
   [ Client: React Frontend (Vite + Tailwind CSS) ]
                          |
             HTTP Upload  |  Live SSE Stream (/api/v1/documents/{id}/stream)
                          v
      [ Gateway: FastAPI Async Service (asyncpg + SQLAlchemy 2.0) ]
                          |
             Database-Backed State Machine (BackgroundTasks)
                          v
      [ AI Engine: LangGraph StateGraph ]
          ├── requirements_extractor (Gemini 2.5 Flash Structured JSON)
          ├── risk_auditor (Scope creep, edge cases, ambiguities) [Parallel]
          ├── effort_estimator (RAG with pgvector + Rate cards)  [Parallel]
          └── spec_compiler (Synthesis + Self-Critique / Retry Loop)
                          |
             Atomic Relational Writes & Vector Similarity
                          v
      [ Storage: PostgreSQL 16 + pgvector ]
```

---

## Key Features

- **Document Ingestion & Section Parsing:** High-fidelity PDF chunking with structure preservation via PyMuPDF (`fitz`).
- **Multi-Agent Orchestration (LangGraph):** State machine workflow featuring typed state transitions, parallel branch execution (Auditor & Estimator running concurrently), and a conditional self-correction retry edge.
- **Unified Relational & Vector Storage (`pgvector`):** Single ACID-compliant PostgreSQL 16 instance handling application tables, audit trails, and 768-dimensional document embeddings indexed with HNSW (Hierarchical Navigable Small World).
- **Structured Schema Enforcement:** Strict Pydantic v2 schemas paired with Gemini 2.5 Flash `response_schema` to guarantee valid JSON outputs without hallucinated formatting.
- **Live State Machine Streaming (SSE):** Real-time client visibility into multi-stage agent progress (`PENDING` $\rightarrow$ `PARSING` $\rightarrow$ `EXTRACTING` $\rightarrow$ `AUDITING` $\rightarrow$ `ESTIMATING` $\rightarrow$ `COMPLETED`).

---

## Tech Stack

| Layer | Technology | Primary Role |
| :--- | :--- | :--- |
| **Backend API** | Python 3.12+, FastAPI | Asynchronous HTTP endpoints & Server-Sent Events |
| **Database Driver** | SQLAlchemy 2.0 + `asyncpg` | Non-blocking database session pooling |
| **Database & Vectors**| PostgreSQL 16 + `pgvector` | Unified storage for relations and vector embeddings |
| **AI Orchestration** | LangGraph (`StateGraph`) | Stateful multi-agent graph with validation loops |
| **LLM & Embeddings** | Google Gemini (`gemini-2.5-flash`, `text-embedding-004`) | Structured extraction and semantic vectorization |
| **Document Processing**| PyMuPDF (`fitz`) | Fast, accurate PDF section and text extraction |
| **Frontend** | React, Vite, Tailwind CSS | High-craft, responsive split-view editor & pipeline UI |

---

## Architectural Decisions & Tradeoffs

1. **Why `pgvector` instead of a Dedicated Vector Database (Pinecone, Qdrant)?**
   - Eliminates dual-write consistency hazards. In RFP analysis, documents, workspaces, and vector chunks must stay transactionally synchronized. When a document is modified or deleted, both relational metadata and vector embeddings are updated atomically in the same SQL transaction.
2. **Why a Database-Backed State Machine instead of Distributed Brokers (Kafka)?**
   - For document processing workflows (tens to hundreds of RFPs per hour), distributed broker clusters introduce unnecessary operational overhead (consumer offsets, partition management, rebalance storms). A PostgreSQL-backed state machine with FastAPI background execution provides ACID-backed reliability, trivial retry handling, and low latency.
3. **Why `asyncpg` over synchronous drivers (`psycopg2`)?**
   - `asyncpg` operates directly on native async PostgreSQL wire protocols. Under concurrent API workloads and long-lived SSE streams, it ensures the Python asyncio event loop remains non-blocked.

---

## Project Structure

```
specFlowAI/
├── docker/
│   └── init-db.sql              # PostgreSQL vector extension initialization
├── backend/
│   ├── app/
│   │   ├── api/                 # API route controllers
│   │   ├── core/                # App config & environment validation
│   │   ├── db/                  # Async session & base models
│   │   ├── models/              # SQLAlchemy 2.0 data models
│   │   ├── schemas/             # Pydantic v2 validation schemas
│   │   ├── services/            # Ingestion, RAG & LLM integration
│   │   └── workflow/            # LangGraph multi-agent StateGraph
│   └── requirements.txt         # Pinned backend dependencies
├── frontend/                    # React + Vite client interface
├── docker-compose.yml           # PostgreSQL 16 + pgvector container definition
├── .env.example                 # Configuration template
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python 3.12+
- Node.js 18+ (for frontend)

### 2. Environment Configuration
Copy the template configuration file:
```bash
cp .env.example .env
```
Update your credentials in `.env` (such as `GEMINI_API_KEY`).

### 3. Start Database Container
```bash
docker compose up -d
```
This boots PostgreSQL 16 with the `pgvector` extension enabled on port `5432`.

### 4. Setup Backend
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r backend/requirements.txt
```

---

## License
MIT
