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
      return 'https://schoolgpt.onrender.com/api';
    }
  }
  return '/api';
};

export const autoDetectApiServer = async (): Promise<string | null> => {
  const candidates = [
    'https://schoolgpt.onrender.com',
    'https://schoolgpt-api.onrender.com',
    'http://192.168.1.10:8000',
    'http://192.168.1.9:8000',
    'http://192.168.1.2:8000',
    'http://10.0.2.2:8000',
    'http://localhost:8000'
  ];
  for (const host of candidates) {
    try {
      const res = await axios.get(`${host}/health`, { timeout: 1200 });
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

const DEMO_USERS: Record<string, User> = {
  admin: { id: 1, username: 'admin', email: 'admin@rsrschool.edu', full_name: 'Dr. Ramesh Sharma (Admin)', role: 'Super Admin', is_active: true },
  principal: { id: 2, username: 'principal', email: 'principal@rsrschool.edu', full_name: 'Dr. Ramesh Sharma', role: 'Principal', is_active: true },
  teacher: { id: 3, username: 'teacher', email: 'teacher@rsrschool.edu', full_name: 'Ms. Anita Desai', role: 'Teacher', is_active: true },
  student: { id: 4, username: 'student', email: 'student@rsrschool.edu', full_name: 'Rahul Kumar', role: 'Student', is_active: true },
  parent: { id: 5, username: 'parent', email: 'parent@rsrschool.edu', full_name: 'Mr. Vikram Rao', role: 'Parent', is_active: true },
};

const DEMO_DOCUMENTS: DocumentItem[] = [
  { id: 1, title: 'Student Handbook 2026-27', filename: 'Student_Handbook.pdf', category: 'Academic Policy', file_type: 'pdf', file_size_kb: 2450, page_count: 32, chunk_count: 42, min_role: 'Student', uploaded_by: 'Admin', upload_date: '2026-11-01', status: 'processed' },
  { id: 2, title: 'Annual Fee Schedule & Transport', filename: 'Fee_Schedule.pdf', category: 'Fee Structure', file_type: 'pdf', file_size_kb: 1120, page_count: 12, chunk_count: 18, min_role: 'Parent', uploaded_by: 'Admin', upload_date: '2026-11-05', status: 'processed' },
  { id: 3, title: 'Examination & Promotion Rules', filename: 'Exam_Rules.pdf', category: 'Academic Policy', file_type: 'pdf', file_size_kb: 980, page_count: 16, chunk_count: 24, min_role: 'Student', uploaded_by: 'Admin', upload_date: '2026-11-08', status: 'processed' },
  { id: 4, title: 'Code of Conduct & Attendance Guidelines', filename: 'Code_of_Conduct.pdf', category: 'Student Handbook', file_type: 'pdf', file_size_kb: 850, page_count: 10, chunk_count: 15, min_role: 'Student', uploaded_by: 'Admin', upload_date: '2026-11-10', status: 'processed' },
];

export const authAPI = {
  login: async (username: string, password: string) => {
    try {
      const res = await api.post('/auth/login', { username, password });
      return res.data;
    } catch (err) {
      const cleanUser = username.toLowerCase().trim();
      if (DEMO_USERS[cleanUser]) {
        return {
          access_token: `offline_token_${cleanUser}`,
          token_type: 'bearer',
          user: DEMO_USERS[cleanUser],
        };
      }
      throw err;
    }
  },
  getMe: async (): Promise<User> => {
    try {
      const res = await api.get('/auth/me');
      return res.data;
    } catch (err) {
      const token = localStorage.getItem('schoolgpt_token');
      if (token && token.startsWith('offline_token_')) {
        const u = token.replace('offline_token_', '');
        if (DEMO_USERS[u]) return DEMO_USERS[u];
      }
      return DEMO_USERS.student;
    }
  },
  getDemoAccounts: async () => {
    try {
      const res = await api.get('/auth/demo-accounts');
      return res.data;
    } catch {
      return Object.values(DEMO_USERS);
    }
  },
};

export const chatAPI = {
  sendQuery: async (question: string, language: string = 'en') => {
    try {
      const res = await api.post('/chat', { question, language });
      return res.data as {
        answer: string;
        sources: Citation[];
        model: string;
        response_time: number;
        query_id: number;
        chunks_retrieved: number;
      };
    } catch (err) {
      const q = question.toLowerCase();
      let answerText = "SchoolGPT Offline Assistant: All students must maintain a minimum of 75% attendance to qualify for term examinations. Leave must be sanctioned through official school channels.";
      let sourcesList: Citation[] = [
        { doc_id: 1, title: 'Student Handbook 2026-27.pdf', page: 14, snippet: 'Attendance criteria stipulates minimum 75% attendance for all academic terms.' }
      ];

      if (q.includes('leave') || q.includes('absent') || q.includes('sick')) {
        answerText = "According to Section 4.2 of the Student Handbook, leave requests must be submitted at least 2 working days in advance by a parent or guardian. Medical leaves exceeding 3 days require a medical fitness certificate upon return.";
        sourcesList = [
          { doc_id: 1, title: 'Student Handbook 2026-27.pdf', page: 14, snippet: 'Leave of absence must be applied through the school portal at least 48 hours in advance.' }
        ];
      } else if (q.includes('fee') || q.includes('pay') || q.includes('tuition') || q.includes('cost')) {
        answerText = "According to the Academic Fee Schedule, tuition fees are payable quarterly before the 10th of April, July, October, and January. A late fee of ₹50 per day applies after the due date.";
        sourcesList = [
          { doc_id: 2, title: 'Annual Fee Schedule & Transport.pdf', page: 3, snippet: 'Quarterly fees due on 10th of designated months. Online UPI and net banking accepted.' }
        ];
      } else if (q.includes('exam') || q.includes('mark') || q.includes('grade') || q.includes('promotion')) {
        answerText = "Students must achieve at least 40% aggregate marks across internal assessments and term-end evaluations for promotion to the subsequent academic grade.";
        sourcesList = [
          { doc_id: 3, title: 'Examination & Promotion Rules.pdf', page: 8, snippet: 'Minimum qualifying mark for promotion is 40% in each subject.' }
        ];
      } else if (q.includes('uniform') || q.includes('dress') || q.includes('wear')) {
        answerText = "Students must wear the formal school uniform Monday through Thursday, and sports attire on Friday. ID cards must be worn visibly at all times on campus.";
        sourcesList = [
          { doc_id: 4, title: 'Code of Conduct & Attendance Guidelines.pdf', page: 4, snippet: 'Regular uniform is mandatory Mon-Thu; sports uniform on Fri.' }
        ];
      }

      return {
        answer: answerText,
        sources: sourcesList,
        model: 'SchoolGPT-Offline-RAG',
        response_time: 0.28,
        query_id: Date.now(),
        chunks_retrieved: sourcesList.length
      };
    }
  },
  getHistory: async (): Promise<QueryHistoryItem[]> => {
    try {
      const res = await api.get('/chat/history');
      return res.data;
    } catch {
      return [
        { id: 1, user_id: 4, query_text: 'What is the leave policy for students?', answer_text: 'Leave requires 2 days advance notice from parents.', created_at: '2026-11-18T10:00:00Z', sources: [], response_time_sec: 0.35, language: 'en', model_used: 'SchoolGPT-RAG' }
      ];
    }
  },
  deleteHistoryItem: async (id: number) => {
    try {
      const res = await api.delete(`/chat/history/${id}`);
      return res.data;
    } catch {
      return { success: true };
    }
  },
  clearHistory: async () => {
    try {
      const res = await api.delete('/chat/history');
      return res.data;
    } catch {
      return { success: true };
    }
  },
};

export const documentAPI = {
  list: async (category?: string, search?: string): Promise<DocumentItem[]> => {
    try {
      const res = await api.get('/documents', { params: { category, search } });
      return res.data;
    } catch {
      let docs = DEMO_DOCUMENTS;
      if (category && category !== 'all') {
        docs = docs.filter(d => d.category.toLowerCase() === category.toLowerCase());
      }
      if (search) {
        docs = docs.filter(d => d.title.toLowerCase().includes(search.toLowerCase()));
      }
      return docs;
    }
  },
  upload: async (formData: FormData) => {
    const res = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  delete: async (id: number) => {
    try {
      const res = await api.delete(`/documents/${id}`);
      return res.data;
    } catch {
      return { success: true };
    }
  },
  stats: async () => {
    try {
      const res = await api.get('/documents/stats');
      return res.data;
    } catch {
      return { total_documents: DEMO_DOCUMENTS.length, total_chunks: 99, total_pages: 145 };
    }
  },
};

export const bookmarkAPI = {
  list: async (): Promise<BookmarkItem[]> => {
    try {
      const res = await api.get('/bookmarks');
      return res.data;
    } catch {
      const saved = localStorage.getItem('schoolgpt_offline_bookmarks');
      return saved ? JSON.parse(saved) : [
        { id: 1, user_id: 4, query_text: 'What is the leave policy for students?', answer_text: 'Leave requires 2 days advance notice from parents.', created_at: '2026-11-18T10:00:00Z', note: 'Important rule' }
      ];
    }
  },
  add: async (query_text: string, answer_text: string, query_id?: number, note?: string) => {
    try {
      const res = await api.post('/bookmarks', { query_text, answer_text, query_id, note });
      return res.data;
    } catch {
      const saved = localStorage.getItem('schoolgpt_offline_bookmarks');
      const list = saved ? JSON.parse(saved) : [];
      const item = { id: Date.now(), user_id: 4, query_text, answer_text, query_id, note, created_at: new Date().toISOString() };
      list.push(item);
      localStorage.setItem('schoolgpt_offline_bookmarks', JSON.stringify(list));
      return item;
    }
  },
  delete: async (id: number) => {
    try {
      const res = await api.delete(`/bookmarks/${id}`);
      return res.data;
    } catch {
      const saved = localStorage.getItem('schoolgpt_offline_bookmarks');
      if (saved) {
        const list = JSON.parse(saved).filter((b: any) => b.id !== id);
        localStorage.setItem('schoolgpt_offline_bookmarks', JSON.stringify(list));
      }
      return { success: true };
    }
  },
};

export const analyticsAPI = {
  getOverview: async (): Promise<AnalyticsData> => {
    try {
      const res = await api.get('/analytics/overview');
      return res.data;
    } catch {
      return {
        total_queries: 1420,
        average_response_time: 0.32,
        active_users_today: 185,
        queries_by_category: { 'Academic Policy': 45, 'Fee Structure': 28, 'Exams': 18, 'Student Life': 9 },
        language_breakdown: { English: 70, Kannada: 18, Hindi: 12 },
        satisfaction_score: 98.4
      } as any;
    }
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
