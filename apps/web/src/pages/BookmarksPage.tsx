import React, { useState, useEffect } from 'react';
import { Bookmark, Trash2, Calendar, FileText } from 'lucide-react';
import { bookmarkAPI } from '../api/client';
import { BookmarkItem } from '../types';

export const BookmarksPage: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadBookmarks = async () => {
    setLoading(true);
    try {
      const data = await bookmarkAPI.list();
      setBookmarks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookmarks();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await bookmarkAPI.delete(id);
      setBookmarks(bookmarks.filter((b) => b.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Saved Bookmarks</h1>
        <p className="text-xs text-slate-500 font-medium">Important school policies and answers bookmarked for quick reference</p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2].map((n) => (
            <div key={n} className="bg-white p-5 rounded-2xl border border-slate-200 animate-pulse space-y-2">
              <div className="h-4 bg-slate-200 rounded w-1/3"></div>
              <div className="h-3 bg-slate-100 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <Bookmark className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No bookmarks yet</h3>
          <p className="text-xs text-slate-500">
            Click the bookmark icon on any answer in the AI Assistant to save it here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookmarks.map((bm) => (
            <div key={bm.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <Bookmark className="w-4 h-4 text-amber-500 fill-current" />
                  <h3 className="text-sm font-bold text-slate-900">{bm.query_text}</h3>
                </div>
                <button
                  onClick={() => handleDelete(bm.id)}
                  className="text-slate-400 hover:text-red-500 p-1 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs text-slate-700 whitespace-pre-line leading-relaxed">
                {bm.answer_text}
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Saved on {new Date(bm.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
