# SchoolGPT – LLM + RAG
### Enterprise AI School Knowledge Base & Grounded Assistant
**Organization:** RSR Technologies  
**Tagline:** *Smart. Reliable. Instant Answers.*  
**Version:** 2.5.0 (Monorepo Edition: Web + Native Mobile + Cloud Deployment)

---

## 📌 1. Project Overview

**SchoolGPT** is an enterprise-grade AI education platform developed for **RSR Technologies**. It empowers schools, educational institutions, and university chains to build a private, trusted knowledge base from official documents (academic policies, student handbooks, fee structures, exam timetables, circulars, and transportation guidelines).

Students, parents, teachers, principals, and administrators can query the assistant and receive instant, contextual answers. Every response is **strictly grounded** in official uploaded documents and includes **verified source citations** with document names and page references.

### 🛡️ Strict Hallucination Prevention Policy
SchoolGPT will **never invent** school policies, fee amounts, deadlines, or rules. If the required information is not present in official school documents, SchoolGPT strictly replies:
> *"I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."*

Multilingual translations are provided automatically for **Kannada (ಕನ್ನಡ)** and **Hindi (हिंदी)**.

---

## 🏗️ 2. Monorepo Architecture

```
School GPT/
├── apps/
│   ├── web/                    # React + Vite + TypeScript web application
│   │   ├── src/
│   │   │   ├── api/            # REST API client (Axios with Bearer Auth)
│   │   │   ├── components/     # Header, Sidebar, CitationCard
│   │   │   ├── pages/          # Chat, Knowledge Base, Upload, History, Bookmarks, Analytics, Users, Settings
│   │   │   ├── types/          # Shared frontend data contracts
│   │   │   └── App.tsx         # Responsive dashboard and role views
│   │   ├── tailwind.config.js  # RSR navy, royal blue, and purple palette
│   │   └── package.json
│   │
│   └── mobile/                 # Expo + React Native + TypeScript Android/iOS app
│       ├── src/
│       │   ├── api/            # Mobile API client
│       │   ├── screens/        # Login, Chat with citations, Knowledge Base, Profile
│       │   └── navigation/     # Mobile bottom navigation tabs
│       ├── app.json            # Package: com.rsrtechnologies.schoolgpt
│       ├── eas.json            # Preview profile for direct standalone APK build
│       └── package.json
│
├── backend/                    # Python FastAPI Enterprise REST API
│   ├── auth/                   # JWT security, password hashing (bcrypt), RBAC dependencies
│   ├── database/               # SQLAlchemy models (PostgreSQL pgvector & SQLite compatible)
│   ├── rag/                    # PyMuPDF/docx extractor, chunker, Gemini API & Ollama router
│   ├── routers/                # auth, chat, documents, bookmarks, analytics, users, settings
│   ├── services/               # Document indexing, analytics, and user services
│   ├── config.py               # Central environment settings & CORS
│   └── main.py                 # FastAPI master entrypoint with auto-seeding
│
├── database/                   # Database schemas & migrations
│   └── schema.sql              # PostgreSQL + pgvector and SQLite schema
│
├── shared/                     # Shared TypeScript contracts & DTOs
│   └── types.ts
│
├── data/                       # Local document storage and ChromaDB vectors
├── demo_documents/             # Preloaded sample school policy documents
├── render.yaml                 # Render Cloud Deployment Blueprint (Web, Static, PGVector)
├── SchoolGPT.apk               # Pre-built standalone native Android APK (Release)
├── requirements.txt            # Python dependencies (FastAPI, PyMuPDF, Gemini, ChromaDB, etc.)
└── package.json                # Monorepo scripts
```

---

## 🎨 3. UI/UX Design System (Reference-Inspired)

Designed using the signature **RSR Technologies** visual identity:
- **Navy Blue (`#0f172a`, `#1e293b`)**: Professional sidebar, deep header, and dark surfaces.
- **Royal Blue (`#2563eb`, `#1d4ed8`)**: Primary badges, active navigation, and institutional accents.
- **White (`#ffffff`)**: Clean, high-contrast answer panels and document cards.
- **Purple Accent (`#7c3aed`, `#8b5cf6`)**: Vibrant "Ask a Question" and "Ask" buttons.
- **Side-by-Side Dual Panels**: Matching the laptop mockup:
  - **Left Card**: Verified **Answer** with green checkmark badge and markdown formatting.
  - **Right Card**: **Sources (Cited)** displaying clickable document badges with page numbers and snippet modals.

---

## 👥 4. Role-Based Access Control (RBAC)

SchoolGPT provides 5 distinct stakeholder roles with 1-click test credentials:

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `password123` | Full administrative control, system settings, model switching, user management. |
| **Principal** | `principal` | `password123` | Executive analytics, confidential policy search, oversight, user audit. |
| **Teacher** | `teacher` | `password123` | Document upload, academic policies, syllabus, examinations, student records. |
| **Parent** | `parent` | `password123` | Fee structures, transport routes, leave policies, school circulars. |
| **Student** | `student` | `password123` | Student handbooks, code of conduct, timetables, clubs, library rules. |

---

## 🚀 5. Quick Start Guide (Windows PowerShell)

### Prerequisites
- **Python 3.10+** (Python 3.12 verified)
- **Node.js 18+** (Node.js v24.13.1 & npm 11.8.0 verified)
- (Optional) **Ollama** running locally on port 11434 (`ollama serve`) or a **Google Gemini API Key**.

---

### Step 1: Install Python Backend Dependencies
Open PowerShell in the project root:
```powershell
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY=your_key` in `.env` if you wish to use Google Gemini in the cloud, or leave blank to use the high-precision grounded reasoning engine).*

---

### Step 3: Start the FastAPI Backend
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/api/docs`
- Health check: `http://127.0.0.1:8000/health`

---

### Step 4: Run the React Web Application
Open a new PowerShell terminal:
```powershell
cd apps\web
npm install
npm run dev
```
Open your browser at:
👉 **`http://localhost:5173`**

Click any 1-Click Demo Profile (`Admin`, `Principal`, `Teacher`, `Parent`, `Student`) and immediately start asking school questions!

---

### Step 5: Run the Mobile Application (Expo)
Open a new PowerShell terminal:
```powershell
cd apps\mobile
npm install
npm run start
```
Scan the QR code with **Expo Go** on Android/iOS, or press `a` for Android Emulator.

---

## 📱 6. Android Mobile APK Build

### Option A: Use the Pre-Built Release APK (Included)
The standalone release APK is already compiled and present in the project root:
- File: **`SchoolGPT.apk`** (4.44 MB)
- Package Name: `com.rsrtechnologies.schoolgpt`
- You can transfer this file directly to any Android smartphone (Android 8.0 through Android 15) and tap to install!

### Option B: Build via Expo Application Services (EAS)
1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```
2. Log in to your Expo account:
   ```bash
   eas login
   ```
3. Build standalone APK using the pre-configured preview profile in `apps/mobile/eas.json`:
   ```bash
   cd apps/mobile
   eas build --platform android --profile preview
   ```
4. Download the generated `.apk` file directly from the Expo build URL.

---

## ☁️ 7. Cloud Deployment Blueprint on Render

The repository includes a ready-to-deploy **Infrastructure as Code** blueprint (`render.yaml`).

### Deploy in 3 Simple Steps:
1. Push this repository to your GitHub account:
   ```powershell
   git add .
   git commit -m "Deploy SchoolGPT Monorepo"
   git push origin main
   ```
2. Log in to [Render.com](https://render.com) and click **New +** → **Blueprint**.
3. Select your `SchoolGPT` GitHub repository. Render will automatically read `render.yaml` and provision:
   - **`schoolgpt-api`**: FastAPI Web Service with Python runtime.
   - **`schoolgpt-web`**: React Static Site with automatic Vite build.
   - **`schoolgpt-db`**: Managed PostgreSQL database with `pgvector` extension enabled.

---

## 🧪 8. Automated Testing

Run the automated backend test suite:
```powershell
pytest tests/ -v
```
All tests verify:
- Document loading (PDF, Word, TXT)
- Text chunking & section boundary preservation
- RBAC authorization filtering
- Strict refusal on queries absent from school documents
- Semantic similarity scoring

---

## 📞 Institutional Support & Contact

**RSR Technologies**  
*Training • Development • Projects • Products • Consulting*  
- **Website:** [www.rsrtechnologies.co.in](https://www.rsrtechnologies.co.in)  
- **Phone:** +91 99453 21367 | +91 77605 94868  
- **Email:** info@rsrtechnologies.co.in  
