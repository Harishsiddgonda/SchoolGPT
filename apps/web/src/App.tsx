import React, { useState, useEffect } from 'react';
import { MessageSquarePlus, BookOpen, Bookmark, Clock } from 'lucide-react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { ChatPage } from './pages/ChatPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { UploadPage } from './pages/UploadPage';
import { HistoryPage } from './pages/HistoryPage';
import { BookmarksPage } from './pages/BookmarksPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { UsersPage } from './pages/UsersPage';
import { SettingsPage } from './pages/SettingsPage';
import { authAPI } from './api/client';
import { User } from './types';

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('schoolgpt_token'));
  const [activeTab, setActiveTab] = useState<string>('chat');
  const [language, setLanguage] = useState<string>('en');
  const [initializing, setInitializing] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('schoolgpt_token');
      if (savedToken) {
        try {
          const userData = await authAPI.getMe();
          setUser(userData);
        } catch (e) {
          localStorage.removeItem('schoolgpt_token');
          setToken(null);
          setUser(null);
        }
      }
      setInitializing(false);
    };
    initAuth();
  }, []);

  const handleLoginSuccess = (loggedInUser: User, authToken: string) => {
    setUser(loggedInUser);
    setToken(authToken);
    setActiveTab('chat');
  };

  const handleLogout = () => {
    localStorage.removeItem('schoolgpt_token');
    setToken(null);
    setUser(null);
  };

  if (initializing) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-semibold tracking-wider uppercase">Loading SchoolGPT...</p>
        </div>
      </div>
    );
  }

  if (!user || !token) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navigation Header */}
      <Header
        user={user}
        onLogout={handleLogout}
        language={language}
        onLanguageChange={setLanguage}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar Navigation */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          userRole={user.role}
          onLogout={handleLogout}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto bg-slate-50 pb-20 md:pb-0">
          {activeTab === 'chat' && <ChatPage user={user} language={language} />}
          {activeTab === 'knowledge' && <KnowledgeBasePage user={user} />}
          {activeTab === 'upload' && <UploadPage user={user} onSuccess={() => setActiveTab('knowledge')} />}
          {activeTab === 'history' && <HistoryPage />}
          {activeTab === 'bookmarks' && <BookmarksPage />}
          {activeTab === 'analytics' && <AnalyticsPage />}
          {activeTab === 'users' && <UsersPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar (Visible only on mobile screens < 768px) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-md border-t border-slate-800 px-3 py-2 flex items-center justify-around shadow-2xl">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex flex-col items-center py-1.5 px-3 rounded-xl transition-all ${
            activeTab === 'chat'
              ? 'text-white bg-gradient-to-tr from-purple-600 to-indigo-600 shadow-md scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <MessageSquarePlus className="w-5 h-5" />
          <span className="text-[10px] font-bold mt-0.5">Ask AI</span>
        </button>

        <button
          onClick={() => setActiveTab('knowledge')}
          className={`flex flex-col items-center py-1.5 px-3 rounded-xl transition-all ${
            activeTab === 'knowledge'
              ? 'text-blue-400 font-bold bg-blue-600/20 scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BookOpen className="w-5 h-5" />
          <span className="text-[10px] font-bold mt-0.5">Docs</span>
        </button>

        <button
          onClick={() => setActiveTab('bookmarks')}
          className={`flex flex-col items-center py-1.5 px-3 rounded-xl transition-all ${
            activeTab === 'bookmarks'
              ? 'text-amber-400 font-bold bg-amber-600/20 scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Bookmark className="w-5 h-5" />
          <span className="text-[10px] font-bold mt-0.5">Saved</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`flex flex-col items-center py-1.5 px-3 rounded-xl transition-all ${
            activeTab === 'history'
              ? 'text-indigo-400 font-bold bg-indigo-600/20 scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-5 h-5" />
          <span className="text-[10px] font-bold mt-0.5">History</span>
        </button>
      </nav>
    </div>
  );
}

export default App;
