import React, { useState } from 'react';
import { GraduationCap, ShieldCheck, Sparkles, ArrowRight, UserCheck, CheckCircle2, Lock, BookOpen } from 'lucide-react';
import { authAPI } from '../api/client';
import { User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User, token: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const demoRoles = [
    { role: 'Super Admin', username: 'admin', label: 'Admin', desc: 'Full permissions', color: 'from-purple-600 to-indigo-600' },
    { role: 'Principal', username: 'principal', label: 'Principal', desc: 'Executive oversight', color: 'from-blue-600 to-cyan-600' },
    { role: 'Teacher', username: 'teacher', label: 'Teacher', desc: 'Academic & exams', color: 'from-emerald-600 to-teal-600' },
    { role: 'Parent', username: 'parent', label: 'Parent', desc: 'Fees & transport', color: 'from-amber-600 to-orange-600' },
    { role: 'Student', username: 'student', label: 'Student', desc: 'Syllabus & rules', color: 'from-indigo-600 to-purple-600' },
  ];

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await authAPI.login(username, password);
      localStorage.setItem('schoolgpt_token', data.access_token);
      onLoginSuccess(data.user, data.access_token);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const selectDemoRole = (demoUser: string) => {
    setUsername(demoUser);
    setPassword('password123');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 sm:p-6 lg:p-8 relative overflow-hidden">
      
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Container */}
      <div className="max-w-4xl w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center z-10">
        
        {/* Left Side: Brand & Value Prop */}
        <div className="lg:col-span-6 text-left space-y-6">
          <div className="inline-flex items-center space-x-2 bg-blue-900/40 border border-blue-500/30 px-3 py-1.5 rounded-full text-blue-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI for Education • RSR Technologies</span>
          </div>

          <div className="space-y-2">
            <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight leading-tight">
              SchoolGPT <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">LLM + RAG</span>
            </h1>
            <p className="text-base text-slate-300 font-medium">
              Smart. Reliable. Instant Answers for Students, Parents, and Staff.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-start space-x-3 text-slate-300 text-sm">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Grounding Guarantee:</strong> Strictly answers from school policies with page citations.</span>
            </div>
            <div className="flex items-start space-x-3 text-slate-300 text-sm">
              <CheckCircle2 className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <span><strong>Role-Based Access:</strong> Tailored document visibility for Admin, Principal, Teacher, Student, Parent.</span>
            </div>
            <div className="flex items-start space-x-3 text-slate-300 text-sm">
              <CheckCircle2 className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
              <span><strong>Multilingual Intelligence:</strong> Instant responses in English, Kannada, and Hindi.</span>
            </div>
          </div>

          {/* Quick Demo Selector */}
          <div className="pt-4 border-t border-slate-800">
            <p className="text-xs font-semibold text-slate-400 mb-2.5 uppercase tracking-wider">
              1-Click Demo Profiles (Click to test):
            </p>
            <div className="flex flex-wrap gap-2">
              {demoRoles.map((dr) => (
                <button
                  key={dr.role}
                  type="button"
                  onClick={() => selectDemoRole(dr.username)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-all flex items-center space-x-1.5 ${
                    username === dr.username
                      ? 'bg-blue-600 text-white border-blue-400 shadow-md font-bold'
                      : 'bg-slate-900/80 text-slate-300 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  <span>{dr.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side: Login Card */}
        <div className="lg:col-span-6 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Sign In to SchoolGPT</h2>
              <p className="text-xs text-slate-400">Enter your official institutional credentials</p>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-200 text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="e.g. admin or student"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full gradient-accent hover:opacity-95 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center space-x-2 disabled:opacity-50 text-sm mt-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Enter Assistant</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center border-t border-slate-800/80 pt-4">
            <p className="text-[11px] text-slate-500">
              RSR Technologies Institutional AI • ISO 9001:2015 Compliant
            </p>
          </div>
        </div>

      </div>

    </div>
  );
};
