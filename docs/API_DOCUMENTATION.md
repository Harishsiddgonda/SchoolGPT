# SchoolGPT API v1 Documentation
### RSR Technologies Enterprise AI Platform

Base URL: `/api/v1` (with `/api` alias for backwards compatibility)

---

## 1. Health & Telemetry
- `GET /health`: Basic health check.
- `GET /api/v1/health`: Detailed diagnostic endpoint checking database connection, AI provider availability, and vector store.

## 2. Authentication
- `POST /api/v1/auth/login`: Authenticate with username and password. Returns JWT access token and user profile.
- `POST /api/v1/auth/register`: Register new student or parent account.
- `GET /api/v1/auth/me`: Retrieve current user profile from bearer token.
- `GET /api/v1/auth/demo-accounts`: Retrieve 1-click test login credentials for Super Admin, Principal, Teacher, Student, and Parent.

## 3. Chat & Grounded RAG
- `POST /api/v1/chat`:
  - Request: `{ "question": "...", "language": "en" | "kn" | "hi", "conversation_history": [] }`
  - Response: `{ "answer": "...", "sources": [{ "title": "...", "page": 1, "section": "...", "snippet": "..." }], "model": "...", "response_time": 0.42 }`
- `GET /api/v1/chat/history`: List previous query history for authenticated user.
- `DELETE /api/v1/chat/history/{id}`: Delete specific query record.
- `DELETE /api/v1/chat/history`: Clear all query history for current user.

## 4. Document & Knowledge Base
- `GET /api/v1/documents`: List authorized documents filtered by user role, category, and search query.
- `POST /api/v1/documents/upload`: Upload PDF, DOCX, or TXT file with title, category, and minimum role access. Triggers text extraction, chunking, and vector indexing.
- `DELETE /api/v1/documents/{id}`: Delete document and remove associated chunks from vector store.
- `GET /api/v1/documents/stats`: Get summary count of documents, chunks, and category distribution.

## 5. Bookmarks & Queries
- `GET /api/v1/bookmarks`: List saved answers with notes.
- `POST /api/v1/bookmarks`: Bookmark a query answer.
- `DELETE /api/v1/bookmarks/{id}`: Delete a bookmark.

## 6. Analytics & Telemetry (Admin / Principal)
- `GET /api/v1/analytics/overview`: High-level metrics (total queries, average latency, document count, active users, 7-day volume trends, role distribution).

## 7. User Management (Admin / Principal)
- `GET /api/v1/users`: List all registered institutional accounts.
- `POST /api/v1/users`: Create a new user account.
- `PUT /api/v1/users/{id}/role`: Update a user's role.
- `PUT /api/v1/users/{id}/status`: Activate or deactivate an account.

## 8. System & AI Settings (Admin)
- `GET /api/v1/settings`: View active AI provider (Gemini / Ollama), model names, and vector database status.
- `POST /api/v1/settings`: Switch AI provider or update model configuration.
