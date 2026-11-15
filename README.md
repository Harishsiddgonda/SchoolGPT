# 🎓 SchoolGPT – LLM + RAG
### AI-Powered School Knowledge Base & Assistant
**Organization:** RSR Technologies  
**Tagline:** *Smart • Reliable • Instant Answers*  
**Website:** [www.rsrtechnologies.co.in](https://www.rsrtechnologies.co.in)  
**Contact:** +91 99453 21367 / +91 77605 94868  

---

## 📌 1. Project Overview

**SchoolGPT – LLM + RAG** is an enterprise-grade AI knowledge assistant built specifically for schools and educational institutions. Developed for **RSR Technologies**, SchoolGPT allows school administrators to upload institutional policy documents (PDF, Word DOCX, and TXT) into a secure, private vector repository.

Students, parents, teachers, principals, and administrative staff can ask natural language questions in **English, Kannada, or Hindi** and receive strictly grounded, verified answers with **explicit source citations** (document name, page number, and section references).

### 🛡️ Strict Hallucination Prevention
SchoolGPT adheres to a strict grounding policy. It does **not** fabricate school policies, examination dates, fee deadlines, or admission rules. When the requested information is absent from the uploaded documents, it responds:
> *"I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."*

---

## 🏗️ 2. Architecture & RAG Pipeline

```
[ Upload School Docs ]  -->  [ Document Parser (PyMuPDF / python-docx / txt) ]
                                            │
                                            ▼
[ Metadata Preservation (Page, Section) ] ──> [ Overlapping Semantic Chunking ]
                                            │
                                            ▼
[ ChromaDB Persistent Vector Store ]  <──  [ Vectorizer (Ollama nomic-embed-text-v2-moe) ]
                                            │
   User Question + User Role                │
          │                                 │
          ▼                                 │
[ Role Permission Filter (RBAC) ] ──────────┼──> [ Top-K Cosine Similarity Retrieval ]
                                            │                    │
                                            ▼                    ▼
                           [ Grounded Prompt Construction (Context + Question) ]
                                            │
                                            ▼
                           [ LLM Synthesis (Ollama Qwen3:4b / Grounded Engine) ]
                                            │
                                            ▼
                           [ Cited Answer + Clickable Page Reference Cards ]
```

---

## 💻 3. Technology Stack

- **Frontend:** Python Streamlit with responsive custom CSS, cards, and theme inspired by the official RSR Technologies visual identity.
- **Backend:** Python 3.10+ modular service architecture.
- **LLM Integration:** Ollama with default configurable model `qwen3:4b` (also compatible with `llama3.2:3b`, `mistral:7b`, etc.) with intelligent offline fallback.
- **Embeddings:** Ollama Embedding API (`nomic-embed-text-v2-moe`) + deterministic normalized on-device vectorizer.
- **Vector Database:** ChromaDB with persistent local storage.
- **Relational Database:** SQLite 3 (`users`, `documents`, `query_history`, `conversations`, `bookmarks`, `document_access`, `feedback`, `activity_logs`, `application_settings`).
- **Document Extractors:** PyMuPDF (`fitz`), `python-docx`, Python text processing with scanned PDF detection.
- **Data Visualizations:** Plotly Express & Graph Objects.
- **Security:** Bcrypt password hashing, role-based document access control (RBAC), and session protection.

---

## 📁 4. Project Directory Structure

```
SchoolGPT/
├── app.py                      # Main Streamlit application entrypoint
├── config/
│   ├── __init__.py
│   └── settings.py             # Global application configuration & env vars
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite connection manager & transactional helper
│   ├── models.py               # Data models and repository queries
│   └── schema.sql              # Database schema with 9 indexed tables
├── auth/
│   ├── __init__.py
│   ├── authentication.py       # Bcrypt hashing, verification, session login
│   └── permissions.py          # Granular Role-Based Access Control (RBAC)
├── rag/
│   ├── __init__.py
│   ├── document_loader.py      # PDF, DOCX, TXT parsers with page tracking
│   ├── text_splitter.py        # Semantic chunker preserving page & section metadata
│   ├── embeddings.py           # Ollama nomic-embed + high-speed local fallback
│   ├── vector_store.py         # Persistent ChromaDB collection manager
│   ├── retriever.py            # Role-filtered semantic search & top-k ranker
│   ├── llm.py                  # Ollama Qwen3 client + grounded reasoning engine
│   └── rag_pipeline.py         # Full end-to-end RAG orchestrator
├── modules/
│   ├── __init__.py
│   ├── dashboard.py            # Executive KPI cards and Plotly analytics
│   ├── chat.py                 # Core AI School Assistant replicating reference UI
│   ├── knowledge_base.py       # Searchable document repository with preview
│   ├── document_upload.py      # File upload, validation, parsing & Chroma indexing
│   ├── query_history.py        # User query telemetry & past conversation logs
│   ├── bookmarks.py            # Saved answers, citations, and categorization
│   ├── analytics.py            # Institutional analytics & CSV reporting
│   ├── user_management.py      # Admin user provisioning & role control
│   └── settings.py             # Ollama diagnostics, school info, Chroma reset
├── components/
│   ├── __init__.py
│   ├── header.py               # RSR Technologies top branding banner
│   ├── sidebar.py              # Left navigation menu & language selector
│   └── source_cards.py         # Formatted citation cards with page numbers
├── services/
│   ├── __init__.py
│   ├── document_service.py     # Document lifecycle & vector purging
│   ├── user_service.py         # User activation, role updating, password reset
│   └── analytics_service.py    # Metric aggregation and Plotly charting
├── assets/
│   ├── style.css               # Professional custom styling matching reference UI
│   ├── rsr_logo.svg            # RSR Technologies brand logo
│   └── schoolgpt_logo.svg      # SchoolGPT brand badge
├── demo_documents/             # 6 Realistic sample school documents
│   ├── Student_Handbook.pdf
│   ├── Student_Leave_Policy.pdf
│   ├── Admission_Policy.docx
│   ├── School_Fee_Structure.pdf
│   ├── Examination_Schedule.txt
│   └── School_Transport_Policy.pdf
├── data/
│   ├── schoolgpt.db            # Persistent SQLite database
│   ├── chroma_db/              # Persistent ChromaDB vector index
│   └── uploads/                # Physical document storage
├── scripts/
│   ├── create_admin.py         # Initial administrative account setup
│   ├── generate_sample_docs.py # Generates PDF, DOCX, TXT demo files
│   └── seed_demo_data.py       # One-click seeder for users & documents
├── tests/                      # Automated pytest verification suite (16 tests)
│   ├── test_auth.py
│   ├── test_document_loader.py
│   ├── test_text_splitter.py
│   ├── test_vector_store.py
│   ├── test_rag_pipeline.py
│   └── test_rbac_retrieval.py
├── .env.example                # Example environment variables
├── .env                        # Local configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Complete documentation
```

---

## 🚀 5. Step-by-Step Windows Installation Guide

Follow these simple steps in **Windows PowerShell**:

### Step 1: Open PowerShell and Navigate to the Workspace
```powershell
cd "c:\Users\HarishRuler\Downloads\School Gpt"
```

### Step 2: Set Up Python Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` (already done by default):
```powershell
Copy-Item .env.example .env
```

### Step 5: Seed Demo Users & School Documents
Run the seeder to populate the SQLite database and index the sample documents into ChromaDB:
```powershell
python scripts/seed_demo_data.py
```

### Step 6: Launch SchoolGPT Application!
```powershell
streamlit run app.py
```
Open your browser at: **`http://localhost:8501`**

---

## 🤖 6. Optional: Ollama Setup for Full Local Neural LLM

SchoolGPT includes a built-in offline grounded engine, meaning it runs **immediately** even before installing Ollama! To enable native local neural generation via Ollama:

1. Download and install Ollama for Windows from [https://ollama.com](https://ollama.com).
2. Start the Ollama background daemon:
   ```powershell
   ollama serve
   ```
3. In a separate PowerShell window, pull the recommended default models:
   ```powershell
   # Pull Qwen3 4B default model
   ollama pull qwen3:4b

   # (Optional alternative model)
   ollama pull llama3.2:3b

   # Pull high-precision embedding model
   ollama pull nomic-embed-text-v2-moe
   ```
4. SchoolGPT will automatically detect Ollama and switch the indicator in the top banner to **🟢 Ollama LLM Ready**!

---

## 👥 7. Demo Accounts & Role-Based Access Control (RBAC)

The application includes pre-configured accounts for all 6 supported roles. You can sign in using credentials or the **1-Click Quick Demo Sign-In** button on the login screen:

| Role | Username | Password | Accessible Documents / Privileges |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `AdminPassword123!` | Full system access, all documents, user management, analytics, vector reset |
| **School Administrator** | `school_admin` | `SchoolAdmin123!` | Document upload, user management, full analytics, all documents |
| **Principal** | `principal` | `Principal123!` | Academic & staff policies, fee structure, institutional analytics |
| **Teacher** | `teacher_sharma` | `Teacher123!` | Student handbook, circulars, exam schedule, leave policy |
| **Student** | `student_aarav` | `Student123!` | Student handbook, leave policy, transport, exam schedule (**Restricted from Fee Structure!**) |
| **Parent** | `parent_priya` | `Parent123!` | Fee structure, admission guidelines, transport policy, leave rules |

### 🔒 Verify RBAC in Action:
1. Log in as **`student_aarav`** and ask: *"What is the annual tuition fee for Grade 9 and one-time charges?"*
   - **Result:** The system strictly refuses to disclose fee information because the Fee Structure document is restricted to Parents and Administrators!
2. Log in as **`parent_priya`** and ask the exact same question:
   - **Result:** The system accurately retrieves the fee amounts (Rs. 1,15,000 per annum) and cites `School_Fee_Structure.pdf (Page 1)`.

---

## 🧪 8. Running Automated Tests

Run the comprehensive pytest suite verifying authentication, document loaders, chunking, ChromaDB lifecycle, RBAC isolation, and citations:

```powershell
pytest tests/ -v
```

Expected result:
```
tests/test_auth.py::test_password_hashing PASSED                         [  6%]
tests/test_auth.py::test_user_registration_and_auth PASSED               [ 12%]
tests/test_auth.py::test_role_permissions PASSED                         [ 18%]
tests/test_auth.py::test_document_access_control PASSED                  [ 25%]
tests/test_document_loader.py::test_load_pdf_extraction PASSED           [ 31%]
tests/test_document_loader.py::test_load_docx_extraction PASSED          [ 37%]
tests/test_document_loader.py::test_load_txt_extraction PASSED           [ 43%]
tests/test_document_loader.py::test_scanned_or_empty_detection PASSED    [ 50%]
tests/test_rag_pipeline.py::test_rag_grounded_answer_with_citations PASSED [ 56%]
tests/test_rag_pipeline.py::test_refusal_when_information_unavailable PASSED [ 62%]
tests/test_rag_pipeline.py::test_bookmark_lifecycle PASSED               [ 68%]
tests/test_rbac_retrieval.py::test_rbac_retrieval_student_vs_parent PASSED [ 75%]
tests/test_rbac_retrieval.py::test_rbac_admin_full_access PASSED         [ 81%]
tests/test_text_splitter.py::test_chunking_metadata_preservation PASSED  [ 87%]
tests/test_vector_store.py::test_vector_store_add_and_query PASSED       [ 93%]
tests/test_vector_store.py::test_vector_deletion_lifecycle PASSED        [100%]

======================== 16 passed in 2.94s ========================
```

---

## ❓ 9. Frequently Asked Inquiries (Suggested Test Questions)

Test SchoolGPT with these real inquiries:
1. **Leave Policy:** *"What is the schools leave policy for students?"*
   - Cites `Student_Leave_Policy.pdf` (Page 1 & 2) and `Student_Handbook.pdf`.
2. **Admission Process:** *"What documents are required for admission?"*
   - Cites `Admission_Policy.docx` (Section 2: Mandatory Documents).
3. **Fee Structure:** *"What is the fee payment deadline and late surcharge?"*
   - Cites `School_Fee_Structure.pdf` (Page 2, Section 3 & 4).
4. **School Timings:** *"What are the school working hours and attendance requirement?"*
   - Cites `Student_Handbook.pdf` (Page 1, Section 1.1 & 1.2).
5. **Examinations:** *"When are the mid-term examinations and pre-boards scheduled?"*
   - Cites `Examination_Schedule.txt` (Page 1, Section 1).
6. **Transport Safety:** *"What are the school bus safety rules and tracking guidelines?"*
   - Cites `School_Transport_Policy.pdf` (Page 1 & 2).
7. **Strict Refusal Test:** *"Can students drive helicopters to campus on Fridays?"*
   - AI Response: *"I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."*

---

## 🌐 10. Multilingual Support

SchoolGPT supports **English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी)**:
- Switch languages directly from the sidebar dropdown.
- Answers are formatted fluently in the selected language.
- Document citations and page numbers are strictly preserved in their original canonical form.

---

## 🛠️ 11. Troubleshooting

| Issue | Resolution |
| :--- | :--- |
| **Port 8501 is already in use** | Run `streamlit run app.py --server.port 8502` to use another port. |
| **Ollama shows 'Offline'** | Ensure `ollama serve` is running in PowerShell on port 11434. SchoolGPT will work in grounded fallback mode regardless. |
| **PDF text extraction warning** | Scanned PDFs with no text layers cannot be indexed without OCR. Ensure uploaded PDFs contain selectable text. |
| **Reset Vector Database** | Go to **Settings > Vector Database Health** as an Administrator and click *Reset All Vector Embeddings*. |

---

### Developed for **RSR Technologies**
*AI-Powered School Knowledge Base & Assistant — Smart • Reliable • Instant Answers.*
