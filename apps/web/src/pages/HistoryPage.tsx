import React, { useState, useEffect } from 'react';
import { Clock, Trash2, MessageSquare, ExternalLink, Calendar, Search } from 'lucide-react';
import { chatAPI } from '../api/client';
import { QueryHistoryItem } from '../types';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await chatAPI.getHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await chatAPI.deleteHistoryItem(id);
      setHistory(history.filter((h) => h.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear all your past query history?')) return;
    try {
      await chatAPI.clearHistory();
      setHistory([]);
    } catch (e) {
      console.error(e);
    }
  };

  const filteredHistory = history.filter((h) =>
    h.query_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    h.answer_text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Query History</h1>
          <p className="text-xs text-slate-500 font-medium">Review past questions, AI answers, and response times</p>
        </div>
        {history.length > 0 && (
          <button
            onClick={handleClear}
            className="text-xs text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg font-semibold transition-colors flex items-center gap-1.5 w-fit"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear All History</span>
          </button>
        )}
      </div>

      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Filter history by question or answer keyword..."
          className="w-full bg-white border border-slate-200 rounded-xl pl-9 pr-3 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
        />
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm animate-pulse space-y-2">
              <div className="h-4 bg-slate-200 rounded w-1/3"></div>
              <div className="h-3 bg-slate-100 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <Clock className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No query history found</h3>
          <p className="text-xs text-slate-500">Ask a question to see your interactions saved here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((item) => (
            <div key={item.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-md bg-blue-100 text-blue-600 flex items-center justify-center">
                    <MessageSquare className="w-3.5 h-3.5" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{item.query_text}</h3>
                </div>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-slate-400 hover:text-red-500 p-1 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <p className="text-xs text-slate-700 whitespace-pre-line leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-100 font-sans">
                {item.answer_text}
              </p>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] text-slate-400">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                  <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                    {item.response_time_sec}s
                  </span>
                  <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded font-medium">
                    {item.model_used}
                  </span>
                </div>

                {item.sources && item.sources.length > 0 && (
                  <span className="text-blue-600 font-medium">
                    {item.sources.length} sources cited
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
