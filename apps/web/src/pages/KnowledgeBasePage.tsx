import React, { useState, useEffect } from 'react';
import { Search, Filter, FileText, Download, Trash2, Shield, Calendar, Layers } from 'lucide-react';
import { documentAPI } from '../api/client';
import { DocumentItem, User } from '../types';

interface KnowledgeBasePageProps {
  user: User;
}

export const KnowledgeBasePage: React.FC<KnowledgeBasePageProps> = ({ user }) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');

  const categories = [
    'all',
    'Academic Policy',
    'Student Handbook',
    'Fee Structure',
    'Circulars & Notices',
    'Timetables & Exams',
    'Transport & Facilities'
  ];

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentAPI.list(category, search);
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [category]);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to remove this document from the knowledge base?')) return;
    try {
      await documentAPI.delete(id);
      loadDocuments();
    } catch (e) {
      alert('Failed to delete document');
    }
  };

  const isPrincipalOrAdmin = user.role === 'Super Admin' || user.role === 'School Admin' || user.role === 'Principal';

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">School Knowledge Base</h1>
          <p className="text-xs text-slate-500 font-medium">Official verified documents indexed in RAG semantic vector store</p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadDocuments()}
            placeholder="Search documents by title..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Categories */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                category === cat
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat === 'all' ? 'All Documents' : cat}
            </button>
          ))}
        </div>

      </div>

      {/* Documents Grid / Table */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm animate-pulse space-y-3">
              <div className="h-5 bg-slate-200 rounded w-2/3"></div>
              <div className="h-3 bg-slate-100 rounded w-1/2"></div>
              <div className="h-8 bg-slate-100 rounded"></div>
            </div>
          ))}
        </div>
      ) : documents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <FileText className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No documents found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Try adjusting your search criteria or upload documents using the Upload Documents center.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    {doc.category}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500 flex items-center gap-1">
                    <Shield className="w-3 h-3 text-purple-600" />
                    {doc.min_role}+
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug line-clamp-2">
                  {doc.title}
                </h3>

                <p className="text-xs text-slate-500 font-mono truncate">
                  {doc.filename}
                </p>
              </div>

              {/* Stats badges */}
              <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-100 text-center">
                <div>
                  <p className="text-[10px] text-slate-400 font-semibold uppercase">Pages</p>
                  <p className="text-xs font-bold text-slate-800">{doc.page_count}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-400 font-semibold uppercase">Chunks</p>
                  <p className="text-xs font-bold text-slate-800">{doc.chunk_count}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-400 font-semibold uppercase">Size</p>
                  <p className="text-xs font-bold text-slate-800">{doc.file_size_kb} KB</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'Active'}
                </span>

                {isPrincipalOrAdmin && (
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};
