import React from 'react';
import { 
  MessageSquarePlus, 
  BookOpen, 
  UploadCloud, 
  Clock, 
  Bookmark, 
  BarChart3, 
  Users, 
  Settings, 
  LogOut,
  GraduationCap
} from 'lucide-react';
import { UserRole } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  userRole: UserRole;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  userRole,
  onLogout
}) => {
  const isAdminOrPrincipal = userRole === 'Super Admin' || userRole === 'School Admin' || userRole === 'Principal';
  const isTeacherOrAbove = isAdminOrPrincipal || userRole === 'Teacher';

  return (
    <aside className="hidden md:flex w-64 bg-slate-900 border-r border-slate-800 flex-col justify-between shrink-0 shadow-xl min-h-[calc(100vh-4rem)]">
      
      {/* Top Section */}
      <div className="p-4 space-y-6">
        
        {/* Brand Header */}
        <div className="flex items-center space-x-2.5 px-2 py-1 text-slate-200">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-400 to-amber-600 flex items-center justify-center text-slate-950 shadow-md">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-extrabold text-base text-white tracking-tight leading-none">SchoolGPT</h2>
            <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">AI School Assistant</p>
          </div>
        </div>

        {/* Primary Action Button - Ask a Question (Featured in reference design) */}
        <div>
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full flex items-center justify-start space-x-3 px-4 py-3 rounded-xl font-semibold text-sm transition-all shadow-md ${
              activeTab === 'chat'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-purple-500/25 ring-2 ring-purple-400/30'
                : 'bg-slate-800 text-slate-200 hover:bg-slate-700/80 hover:text-white'
            }`}
          >
            <MessageSquarePlus className="w-4 h-4 text-purple-300" />
            <span>Ask a Question</span>
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          <button
            onClick={() => setActiveTab('knowledge')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'knowledge'
                ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Knowledge Base</span>
          </button>

          {isTeacherOrAbove && (
            <button
              onClick={() => setActiveTab('upload')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Documents</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab('history')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'history'
                ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>My Queries</span>
          </button>

          <button
            onClick={() => setActiveTab('bookmarks')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'bookmarks'
                ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Bookmark className="w-4 h-4" />
            <span>Bookmarks</span>
          </button>

          {isAdminOrPrincipal && (
            <>
              <div className="pt-4 pb-1">
                <span className="px-3.5 text-[10px] uppercase font-bold tracking-wider text-slate-500">Administration</span>
              </div>

              <button
                onClick={() => setActiveTab('analytics')}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  activeTab === 'analytics'
                    ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Analytics & Insights</span>
              </button>

              <button
                onClick={() => setActiveTab('users')}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  activeTab === 'users'
                    ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>User Management</span>
              </button>
            </>
          )}

          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'settings'
                ? 'bg-blue-600/20 text-blue-400 font-semibold border-l-2 border-blue-500'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>AI Settings</span>
          </button>
        </nav>
      </div>

      {/* Bottom Section */}
      <div className="p-4 border-t border-slate-800">
        <button
          onClick={onLogout}
          className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-red-400 hover:bg-red-950/20 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>

    </aside>
  );
};
