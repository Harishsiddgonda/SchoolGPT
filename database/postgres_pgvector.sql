-- SchoolGPT Database Schema (PostgreSQL + pgvector for Cloud Deployment on Render)
-- Organization: RSR Technologies
-- Tagline: Smart. Reliable. Instant Answers.

CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(128) UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'Student',
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    category VARCHAR(64) DEFAULT 'General',
    file_type VARCHAR(16) DEFAULT 'pdf',
    file_size_kb FLOAT DEFAULT 0.0,
    page_count INTEGER DEFAULT 1,
    chunk_count INTEGER DEFAULT 0,
    min_role VARCHAR(32) DEFAULT 'Student',
    uploaded_by VARCHAR(64) DEFAULT 'Admin',
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(32) DEFAULT 'indexed'
);

-- 3. Document Chunks Table with Vector Embedding (768-dim)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    page_number INTEGER DEFAULT 1,
    section VARCHAR(128) DEFAULT '',
    token_count INTEGER DEFAULT 0,
    embedding vector(768),
    embedding_json TEXT
);

-- 4. Query History Table
CREATE TABLE IF NOT EXISTS query_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    language VARCHAR(16) DEFAULT 'en',
    response_time_sec FLOAT DEFAULT 0.0,
    model_used VARCHAR(64) DEFAULT 'SchoolGPT Grounded Engine',
    sources_json TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Bookmarks Table
CREATE TABLE IF NOT EXISTS bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query_id INTEGER REFERENCES query_history(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    note VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query_id INTEGER REFERENCES query_history(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_min_role ON documents(min_role);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON query_history(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
