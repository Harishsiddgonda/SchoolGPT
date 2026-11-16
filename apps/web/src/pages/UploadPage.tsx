import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Shield, FolderPlus, ArrowRight } from 'lucide-react';
import { documentAPI } from '../api/client';
import { User } from '../types';

interface UploadPageProps {
  user: User;
  onSuccess: () => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ user, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Academic Policy');
  const [minRole, setMinRole] = useState('Student');
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const categories = [
    'Academic Policy',
    'Student Handbook',
    'Fee Structure',
    'Circulars & Notices',
    'Timetables & Exams',
    'Transport & Facilities',
    'General'
  ];

  const roles = [
    'Student',
    'Parent',
    'Teacher',
    'Principal',
    'School Admin'
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setStatusMsg({ type: 'error', text: 'Please select a file to upload.' });
      return;
    }

    setUploading(true);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('category', category);
    formData.append('min_role', minRole);

    try {
      const res = await documentAPI.upload(formData);
      setStatusMsg({
        type: 'success',
        text: `Document "${title}" indexed successfully into vector database with ${res.chunks_indexed} chunks!`
      });
      setFile(null);
      setTitle('');
      setTimeout(() => onSuccess(), 1500);
    } catch (err: any) {
      setStatusMsg({
        type: 'error',
        text: err?.response?.data?.detail || 'Failed to upload and index document.'
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Upload School Documents</h1>
        <p className="text-xs text-slate-500 font-medium">Add official institutional PDFs, DOCX, or TXT documents to the RAG knowledge repository</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        
        {statusMsg && (
          <div className={`p-4 rounded-xl mb-6 flex items-start space-x-3 text-xs ${
            statusMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {statusMsg.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" /> : <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />}
            <div>
              <p className="font-bold">{statusMsg.type === 'success' ? 'Indexing Complete' : 'Upload Error'}</p>
              <p>{statusMsg.text}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* File Dropzone */}
          <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center hover:border-blue-500 transition-colors bg-slate-50/50">
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="text-sm font-bold text-slate-800">
              {file ? file.name : 'Drag & drop school documents here or browse'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Supports PDF (PyMuPDF indexed), Word (.docx), and plain text (.txt) up to 50 MB
            </p>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt"
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="mt-4 inline-block bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-4 py-2 rounded-xl cursor-pointer shadow-sm transition-all"
            >
              Select Document
            </label>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Official Document Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Student Code of Conduct 2026-27"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Document Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Minimum Role Visibility</label>
              <select
                value={minRole}
                onChange={(e) => setMinRole(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {roles.map((r) => (
                  <option key={r} value={r}>{r} and above</option>
                ))}
              </select>
            </div>

          </div>

          {/* Submit Button */}
          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={uploading || !file}
              className="gradient-accent hover:opacity-95 text-white font-semibold text-xs py-3 px-6 rounded-xl shadow-md transition-all flex items-center space-x-2 disabled:opacity-50"
            >
              <span>{uploading ? 'Extracting, Chunking & Indexing...' : 'Index Document Now'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </form>

      </div>

    </div>
  );
};
