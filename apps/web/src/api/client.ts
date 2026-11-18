import axios from 'axios';
import { User, DocumentItem, QueryHistoryItem, BookmarkItem, AnalyticsData, SystemSettingsData, Citation } from '../types';

export const getBaseURL = () => {
  const custom = localStorage.getItem('schoolgpt_custom_api_url');
  if (custom) return custom.replace(/\/$/, '');
  if (typeof window !== 'undefined') {
    if (
      window.location.protocol === 'file:' ||
      window.location.origin === 'null' ||
      window.location.hostname === 'appassets.androidplatform.net'
    ) {
      return 'http://192.168.1.10:8000/api';
    }
  }
  return '/api';
};

export const autoDetectApiServer = async (): Promise<string | null> => {
  const candidates = [
    'http://192.168.1.10:8000',
    'http://192.168.1.9:8000',
    'http://192.168.1.2:8000',
    'http://10.0.2.2:8000',
    'http://localhost:8000'
  ];
  for (const host of candidates) {
    try {
      const res = await axios.get(`${host}/health`, { timeout: 1000 });
      if (res.status === 200) {
        const fullApi = `${host}/api`;
        localStorage.setItem('schoolgpt_custom_api_url', fullApi);
        return host;
      }
    } catch (e) {
      // continue next candidate
    }
  }
  return null;
};

const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  config.baseURL = getBaseURL();
  const token = localStorage.getItem('schoolgpt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username: string, password: string) => {
    const res = await api.post('/auth/login', { username, password });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },
  getDemoAccounts: async () => {
    const res = await api.get('/auth/demo-accounts');
    return res.data;
  },
};

export const chatAPI = {
  sendQuery: async (question: string, language: string = 'en') => {
    const res = await api.post('/chat', { question, language });
    return res.data as {
      answer: string;
      sources: Citation[];
      model: string;
      response_time: number;
      query_id: number;
      chunks_retrieved: number;
    };
  },
  getHistory: async (): Promise<QueryHistoryItem[]> => {
    const res = await api.get('/chat/history');
    return res.data;
  },
  deleteHistoryItem: async (id: number) => {
    const res = await api.delete(`/chat/history/${id}`);
    return res.data;
  },
  clearHistory: async () => {
    const res = await api.delete('/chat/history');
    return res.data;
  },
};

export const documentAPI = {
  list: async (category?: string, search?: string): Promise<DocumentItem[]> => {
    const res = await api.get('/documents', { params: { category, search } });
    return res.data;
  },
  upload: async (formData: FormData) => {
    const res = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  delete: async (id: number) => {
    const res = await api.delete(`/documents/${id}`);
    return res.data;
  },
  stats: async () => {
    const res = await api.get('/documents/stats');
    return res.data;
  },
};

export const bookmarkAPI = {
  list: async (): Promise<BookmarkItem[]> => {
    const res = await api.get('/bookmarks');
    return res.data;
  },
  add: async (query_text: string, answer_text: string, query_id?: number, note?: string) => {
    const res = await api.post('/bookmarks', { query_text, answer_text, query_id, note });
    return res.data;
  },
  delete: async (id: number) => {
    const res = await api.delete(`/bookmarks/${id}`);
    return res.data;
  },
};

export const analyticsAPI = {
  getOverview: async (): Promise<AnalyticsData> => {
    const res = await api.get('/analytics/overview');
    return res.data;
  },
};

export const userAPI = {
  list: async (): Promise<User[]> => {
    const res = await api.get('/users');
    return res.data;
  },
  create: async (data: any) => {
    const res = await api.post('/users', data);
    return res.data;
  },
  updateRole: async (id: number, role: string) => {
    const res = await api.put(`/users/${id}/role`, { role });
    return res.data;
  },
  toggleStatus: async (id: number, is_active: boolean) => {
    const res = await api.put(`/users/${id}/status`, { is_active });
    return res.data;
  },
};

export const settingsAPI = {
  get: async (): Promise<SystemSettingsData> => {
    const res = await api.get('/settings');
    return res.data;
  },
  update: async (data: any) => {
    const res = await api.post('/settings', data);
    return res.data;
  },
};

export default api;
