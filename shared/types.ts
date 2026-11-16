/**
 * Shared Type Definitions & API Contracts for SchoolGPT
 * RSR Technologies
 */

export type UserRole =
  | 'Super Admin'
  | 'School Admin'
  | 'Principal'
  | 'Teacher'
  | 'Student'
  | 'Parent';

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: UserRole;
  email?: string;
  created_at: string;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DocumentMetadata {
  id: number;
  title: string;
  filename: string;
  category: string;
  file_type: string;
  file_size_kb: number;
  page_count: number;
  chunk_count: number;
  min_role: UserRole;
  uploaded_by: string;
  upload_date: string;
  status: 'indexed' | 'processing' | 'error';
}

export interface Citation {
  doc_id?: number;
  title: string;
  category?: string;
  page: number;
  section?: string;
  snippet: string;
  similarity?: number;
}

export interface QueryRequest {
  question: string;
  language?: 'en' | 'kn' | 'hi';
  conversation_history?: Array<{ role: 'user' | 'assistant'; content: string }>;
}

export interface QueryResponse {
  answer: string;
  sources: Citation[];
  model: string;
  response_time: number;
  query_id?: number | null;
  chunks_retrieved: number;
}

export interface QueryHistoryItem {
  id: number;
  user_id: number;
  query_text: string;
  answer_text: string;
  language: string;
  response_time_sec: number;
  created_at: string;
  sources: Citation[];
  is_bookmarked?: boolean;
}

export interface Bookmark {
  id: number;
  user_id: number;
  query_id?: number;
  query_text: string;
  answer_text: string;
  note?: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_queries: number;
  avg_response_time: number;
  total_documents: number;
  total_users: number;
  role_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  recent_trend: Array<{ date: string; queries: number }>;
}

export interface SystemSettings {
  ai_provider: 'gemini' | 'ollama';
  gemini_model: string;
  ollama_model: string;
  ollama_url: string;
  temperature: number;
  embedding_model: string;
  vector_db_status: string;
  total_vectors: number;
}
