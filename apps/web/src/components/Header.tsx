import React from 'react';
import { User } from '../types';
import { GraduationCap, ShieldCheck, Globe, LogOut, Bell, Sparkles } from 'lucide-react';

interface HeaderProps {
  user: User;
  onLogout: () => void;
  language: string;
  onLanguageChange: (lang: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout, language, onLanguageChange }) => {
  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'Super Admin':
      case 'School Admin':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Principal':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Teacher':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'Parent':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
    }
  };

  return (
    <header className="gradient-header text-white border-b border-slate-700/60 sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Title */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white/10 px-3 py-1.5 rounded-lg border border-white/15">
            <div className="w-7 h-7 rounded-md bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-white shadow-sm">
              RSR
            </div>
            <div className="text-left leading-tight">
              <span className="text-xs font-bold tracking-wider text-blue-300 uppercase block">RSR TECHNOLOGIES</span>
              <span className="text-sm font-extrabold text-white tracking-tight flex items-center gap-1">
                SchoolGPT <span className="text-[10px] bg-red-600 text-white px-1.5 py-0.2 rounded font-semibold">RAG</span>
              </span>
            </div>
          </div>
          <div className="hidden lg:block border-l border-slate-700 h-8 ml-2 pl-3">
            <p className="text-xs font-medium text-slate-300">AI for Education</p>
            <p className="text-[11px] text-blue-400 font-semibold tracking-wide">Smart • Reliable • Instant Answers</p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-4">
          
          {/* Language Selector */}
          <div className="flex items-center bg-slate-800/80 rounded-lg px-2.5 py-1 border border-slate-700 text-xs">
            <Globe className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer pr-1 text-xs"
            >
              <option value="en" className="bg-slate-900 text-white">English</option>
              <option value="kn" className="bg-slate-900 text-white">ಕನ್ನಡ (Kannada)</option>
              <option value="hi" className="bg-slate-900 text-white">हिंदी (Hindi)</option>
            </select>
          </div>

          {/* User Role Badge */}
          <div className="hidden sm:flex items-center space-x-2">
            <span className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${getRoleBadgeColor(user.role)}`}>
              <ShieldCheck className="w-3.5 h-3.5 inline mr-1" />
              {user.role}
            </span>
          </div>

          {/* User Profile & Logout */}
          <div className="flex items-center space-x-3 border-l border-slate-700 pl-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-semibold text-white leading-tight">{user.full_name}</p>
              <p className="text-[11px] text-slate-400 leading-tight">@{user.username}</p>
            </div>
            <button
              onClick={onLogout}
              title="Logout"
              className="p-1.5 text-slate-300 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
