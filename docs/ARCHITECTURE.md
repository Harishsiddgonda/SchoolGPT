# SchoolGPT System Architecture
### RSR Technologies Enterprise AI Education Platform
**Tagline:** *Smart. Reliable. Instant Answers.*

---

## 1. High-Level Architecture Overview

SchoolGPT is engineered as an enterprise-grade monorepo containing:
1. **Frontend Website (`apps/web`)**: React 18, Vite, TypeScript, Tailwind CSS, Lucide icons.
2. **Mobile Application (`apps/mobile`)**: Expo SDK 52, React Native, TypeScript, EAS Build.
3. **Backend REST API (`backend`)**: Python 3.12, FastAPI, SQLAlchemy ORM, PyMuPDF, python-docx.
4. **Database & Storage (`database`)**: PostgreSQL with `pgvector` extension (and local SQLite fallback) + S3-compatible cloud object storage.
5. **AI Inference & RAG Engine (`backend/rag`)**: Google Gemini API (`gemini-1.5-flash`) for cloud production, local Ollama (`qwen3:4b`) for local development, and a strict grounded fallback engine preventing hallucinations.

```
                              ┌──────────────────────────────────┐
                              │       RSR TECHNOLOGIES           │
                              │           SchoolGPT              │
                              └──────────────────────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
     ┌───────────────────────┐                                     ┌───────────────────────┐
     │  React Web Dashboard  │                                     │ Expo React Native App │
     │      (apps/web)       │                                     │     (apps/mobile)     │
     └───────────────────────┘                                     └───────────────────────┘
                 │                                                             │
                 └──────────────────────────────┬──────────────────────────────┘
                                                ▼ HTTP / REST (JWT Bearer Auth)
                                 ┌─────────────────────────────┐
                                 │       FastAPI Backend       │
                                 │          (backend)          │
                                 │  /api/v1/... & /health      │
                                 └─────────────────────────────┘
                                                │
         ┌──────────────────────────────┬───────┴──────────────────────┬──────────────────────────────┐
         ▼                              ▼                              ▼                              ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│   PostgreSQL     │           │  Google Gemini   │           │   Local Ollama   │           │  Cloud S3 / R2   │
│   + pgvector     │           │    API Client    │           │    (Qwen3:4b)    │           │  Object Storage  │
│  (Managed Cloud) │           │ (Production AI)  │           │   (Local Dev)    │           │ (School Docs)    │
└──────────────────┘           └──────────────────┘           └──────────────────┘           └──────────────────┘
```

---

## 2. End-to-End RAG Lifecycle

1. **Document Ingestion**:
   - Authorized staff upload official documents (PDF, DOCX, TXT).
   - Saved to S3-compatible cloud storage (or local `./data/documents`).
   - Page-by-page extraction using PyMuPDF (`fitz`) and `python-docx`.
2. **Chunking & Metadata Tagging**:
   - Split using character window and overlap.
   - Each chunk retains its `doc_id`, `doc_title`, `doc_category`, `page_number`, `section`, and `allowed_roles`.
3. **Vector Indexing**:
   - Embeddings generated and persisted in PostgreSQL `pgvector` or local ChromaDB.
4. **Role-Enforced Retrieval**:
   - User asks a question (via Web or Mobile).
   - Before semantic similarity scoring, chunks are filtered by the requester's role.
   - Top matching chunks are retrieved with similarity scores and page references.
5. **Strict Grounded Synthesis**:
   - Chunks passed to Google Gemini / Ollama with a strict zero-hallucination prompt.
   - If information is not in the documents, returns the standard refusal message:
     *"I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."*
   - Returns cited sources with title, page number, section, and excerpt.
