import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Database, Save, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { settingsAPI } from '../api/client';
import { SystemSettingsData } from '../types';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aiProvider, setAiProvider] = useState<'gemini' | 'ollama'>('gemini');
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [geminiModel, setGeminiModel] = useState('gemini-1.5-flash');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('qwen3:4b');
  const [notice, setNotice] = useState<string | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const data = await settingsAPI.get();
      setSettings(data);
      setAiProvider((data.ai_provider as 'gemini' | 'ollama') || 'gemini');
      setGeminiModel(data.gemini_model || 'gemini-1.5-flash');
      setOllamaModel(data.ollama_model || 'qwen3:4b');
      setOllamaUrl(data.ollama_url || 'http://localhost:11434');
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    try {
      await settingsAPI.update({
        ai_provider: aiProvider,
        gemini_api_key: geminiApiKey || undefined,
        gemini_model: geminiModel,
        ollama_model: ollamaModel,
        ollama_url: ollamaUrl
      });
      setNotice('Settings successfully updated!');
      fetchSettings();
    } catch (e: any) {
      setNotice('Failed to update settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">AI & System Settings</h1>
        <p className="text-xs text-slate-500 font-medium">Configure dual AI providers (Google Gemini / Ollama), vector storage, and RAG pipelines</p>
      </div>

      {notice && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* System Status Cards */}
      {settings && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Google Gemini API</span>
            <div className="flex items-center space-x-2">
              <span className={`w-2.5 h-2.5 rounded-full ${settings.gemini_configured ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
              <span className="text-xs font-bold text-slate-800">
                {settings.gemini_configured ? 'Configured & Active' : 'Key Optional (Uses Grounded Fallback)'}
              </span>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Local Ollama Status</span>
            <div className="flex items-center space-x-2">
              <span className={`w-2.5 h-2.5 rounded-full ${settings.ollama_connected ? 'bg-emerald-500' : 'bg-slate-300'}`}></span>
              <span className="text-xs font-bold text-slate-800">
                {settings.ollama_connected ? 'Connected (Port 11434)' : 'Offline (Auto Fallback)'}
              </span>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Vector Knowledge Store</span>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span className="text-xs font-bold text-slate-800">
                {settings.total_vectors} Vectors Indexed
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Configuration Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <form onSubmit={handleSave} className="space-y-6">
          
          {/* AI Provider Switcher */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-2">Preferred AI Provider</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setAiProvider('gemini')}
                className={`p-4 rounded-xl border text-left transition-all ${
                  aiProvider === 'gemini'
                    ? 'border-blue-500 bg-blue-50/50 ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-blue-600" />
                  <span className="text-xs font-bold text-slate-900">Google Gemini API</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  High-speed, cloud inference with Gemini 1.5 Flash
                </p>
              </button>

              <button
                type="button"
                onClick={() => setAiProvider('ollama')}
                className={`p-4 rounded-xl border text-left transition-all ${
                  aiProvider === 'ollama'
                    ? 'border-purple-500 bg-purple-50/50 ring-2 ring-purple-500/20'
                    : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-purple-600" />
                  <span className="text-xs font-bold text-slate-900">Local Ollama LLM</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Private on-premise execution with Qwen3:4b
                </p>
              </button>
            </div>
          </div>

          {/* Gemini Fields */}
          {aiProvider === 'gemini' && (
            <div className="space-y-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h4 className="text-xs font-bold text-slate-800">Google Gemini Configuration</h4>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Gemini API Key</label>
                <input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  placeholder="AIzaSy... (leave blank to keep current)"
                  className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Gemini Model</label>
                <select
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="gemini-1.5-flash">gemini-1.5-flash (Fast, Grounded, Default)</option>
                  <option value="gemini-1.5-pro">gemini-1.5-pro (High reasoning)</option>
                  <option value="gemini-pro">gemini-pro</option>
                </select>
              </div>
            </div>
          )}

          {/* Ollama Fields */}
          {aiProvider === 'ollama' && (
            <div className="space-y-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h4 className="text-xs font-bold text-slate-800">Ollama Configuration</h4>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Ollama Service URL</label>
                <input
                  type="text"
                  value={ollamaUrl}
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  placeholder="http://localhost:11434"
                  className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Ollama LLM Model</label>
                <input
                  type="text"
                  value={ollamaModel}
                  onChange={(e) => setOllamaModel(e.target.value)}
                  placeholder="qwen3:4b or llama3"
                  className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="gradient-accent hover:opacity-95 text-white font-semibold text-xs py-2.5 px-6 rounded-xl shadow-md transition-all flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving Changes...' : 'Save AI Settings'}</span>
            </button>
          </div>

        </form>
      </div>

    </div>
  );
};
