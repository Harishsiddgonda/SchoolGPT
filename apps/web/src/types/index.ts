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
  created_at?: string;
  is_active: boolean;
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

export interface DocumentItem {
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
  status: string;
}

export interface QueryHistoryItem {
  id: number;
  user_id: number;
  query_text: string;
  answer_text: string;
  language: string;
  response_time_sec: number;
  model_used: string;
  created_at: string;
  sources: Citation[];
}

export interface BookmarkItem {
  id: number;
  user_id: number;
  query_id?: number;
  query_text: string;
  answer_text: string;
  note?: string;
  created_at: string;
}

export interface AnalyticsData {
  total_queries: number;
  avg_response_time: number;
  total_documents: number;
  total_users: number;
  total_bookmarks: number;
  role_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  recent_trend: Array<{ date: string; queries: number }>;
}

export interface SystemSettingsData {
  app_name: string;
  org_name: string;
  version: string;
  ai_provider: string;
  gemini_configured: boolean;
  gemini_model: string;
  ollama_connected: boolean;
  ollama_model: string;
  ollama_url: string;
  embedding_model: string;
  vector_db: string;
  total_vectors: number;
}
