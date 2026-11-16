/**
 * Mobile API Client for SchoolGPT
 * RSR Technologies
 */

let BASE_URL = 'http://10.0.2.2:8000'; // Default Android Emulator to local backend
let AUTH_TOKEN: string | null = null;

export const setBaseUrl = (url: string) => {
  BASE_URL = url.replace(/\/+$/, '');
};

export const getBaseUrl = () => BASE_URL;

export const setAuthToken = (token: string | null) => {
  AUTH_TOKEN = token;
};

const request = async (endpoint: string, options: RequestInit = {}) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `HTTP ${res.status}`);
  }

  return res.json();
};

export const mobileAPI = {
  login: (username: string, password: string) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  getMe: () => request('/api/auth/me'),

  sendQuery: (question: string, language: string = 'en') =>
    request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ question, language }),
    }),

  getHistory: () => request('/api/chat/history'),

  getDocuments: (category?: string) =>
    request(`/api/documents${category ? `?category=${category}` : ''}`),

  getBookmarks: () => request('/api/bookmarks'),

  addBookmark: (query_text: string, answer_text: string, query_id?: number) =>
    request('/api/bookmarks', {
      method: 'POST',
      body: JSON.stringify({ query_text, answer_text, query_id }),
    }),
};
