import React, { useState, useEffect } from 'react';
import { 
  Send, 
  CheckCircle2, 
  ExternalLink, 
  FileText, 
  Bookmark, 
  Copy, 
  Check, 
  Sparkles, 
  Clock, 
  Info,
  BookOpen,
  Volume2,
  VolumeX,
  GraduationCap
} from 'lucide-react';
import { chatAPI, bookmarkAPI } from '../api/client';
import { Citation, User } from '../types';

interface ChatPageProps {
  user: User;
  language: string;
}

export const ChatPage: React.FC<ChatPageProps> = ({ user, language }) => {
  const [question, setQuestion] = useState('What is the schools leave policy for students?');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Citation[]>([]);
  const [model, setModel] = useState<string>('');
  const [responseTime, setResponseTime] = useState<number>(0);
  const [queryId, setQueryId] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [speaking, setSpeaking] = useState(false);

  const studentShortcuts = [
    { label: "🎒 Leave Policy", query: "What is the schools leave policy for students?" },
    { label: "📅 Exams & Schedule", query: "What are the examination dates and guidelines?" },
    { label: "💻 Lab & Library", query: "What are the rules for computer lab and library usage?" },
    { label: "⚽ Sports & Clubs", query: "What extracurricular activities and sports clubs are available?" },
    { label: "🚌 Timings & Bus", query: "What are the school operating hours and bus routes?" }
  ];

  const handleSpeak = () => {
    if (!answer) return;
    if ('speechSynthesis' in window) {
      if (speaking) {
        window.speechSynthesis.cancel();
        setSpeaking(false);
      } else {
        window.speechSynthesis.cancel();
        const cleanText = answer.replace(/[#*`_\[\]()]/g, ' ');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-US';
        utterance.onend = () => setSpeaking(false);
        utterance.onerror = () => setSpeaking(false);
        setSpeaking(true);
        window.speechSynthesis.speak(utterance);
      }
    }
  };

  const sampleQuestions = [
    "What is the schools leave policy for students?",
    "Explain the fee structure and refund policy",
    "What are the rules for computer lab usage?",
    "What are the school operating hours and transport routes?",
    "How are parent-teacher meetings scheduled?"
  ];

  const handleAsk = async (queryText?: string) => {
    const q = (queryText || question).trim();
    if (!q) return;

    setLoading(true);
    setBookmarked(false);
    try {
      const res = await chatAPI.sendQuery(q, language);
      setAnswer(res.answer);
      setSources(res.sources || []);
      setModel(res.model);
      setResponseTime(res.response_time);
      setQueryId(res.query_id);
    } catch (err: any) {
      setAnswer("An error occurred while querying the school knowledge base. Please try again or verify backend connectivity.");
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!answer) return;
    navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleBookmark = async () => {
    if (!answer || bookmarked) return;
    try {
      await bookmarkAPI.add(question, answer, queryId || undefined);
      setBookmarked(true);
    } catch (e) {
      console.error(e);
    }
  };

  // Run initial query on mount so user immediately sees working RAG output matching reference
  useEffect(() => {
    handleAsk("What is the schools leave policy for students?");
  }, []);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Laptop UI Screen Header Card matching reference image */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 space-y-4">
        
        {/* Top Header Badge */}
        <div className="flex items-center space-x-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-600 font-bold">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              SchoolGPT <span className="text-xs bg-blue-100 text-blue-700 font-bold px-2 py-0.5 rounded-full">LLM + RAG</span>
            </h1>
            <p className="text-xs text-slate-500 font-medium">AI School Assistant – Powered by LLM + RAG</p>
          </div>
        </div>

        {/* Input Question Bar */}
        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="What is the schools leave policy for students?"
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all shadow-inner"
            />
          </div>
          <button
            onClick={() => handleAsk()}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-6 py-3 rounded-xl shadow-md transition-all flex items-center justify-center space-x-2 shrink-0 disabled:opacity-60 text-sm"
          >
            <span>{loading ? 'Retrieving...' : 'Ask'}</span>
            <Send className="w-4 h-4 ml-1" />
          </button>
        </div>

        {/* Suggested Queries Chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[11px] font-semibold text-slate-400 mr-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-500" /> Suggestions:
          </span>
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuestion(q);
                handleAsk(q);
              }}
              className="text-xs bg-slate-100 hover:bg-blue-50 hover:text-blue-600 text-slate-600 px-2.5 py-1 rounded-lg border border-slate-200 transition-colors truncate max-w-xs"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Student Quick Topic Shortcuts */}
        <div className="pt-2 border-t border-slate-100">
          <div className="flex items-center gap-1.5 mb-2">
            <GraduationCap className="w-4 h-4 text-indigo-600" />
            <span className="text-[11px] font-bold text-indigo-900 uppercase tracking-wider">
              Student Quick Topics:
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {studentShortcuts.map((s, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuestion(s.query);
                  handleAsk(s.query);
                }}
                className="text-xs bg-indigo-50/90 hover:bg-indigo-100 text-indigo-800 font-semibold px-3 py-1.5 rounded-xl border border-indigo-200 transition-all active:scale-95 shadow-2xs"
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* Main Results Display: Two Side-by-Side Cards (Answer + Sources Cited) */}
      {(answer || loading) && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Panel: Verified Answer */}
          <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            
            {/* Answer Header with Green Checkmark Badge */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <h3 className="font-extrabold text-base text-slate-900 tracking-tight">Answer</h3>
              </div>

              {/* Utility actions: Copy, Bookmark, Latency */}
              <div className="flex items-center space-x-2">
                {responseTime > 0 && (
                  <span className="hidden sm:inline-flex items-center text-[11px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">
                    <Clock className="w-3 h-3 mr-1" />
                    {responseTime}s
                  </span>
                )}
                {model && (
                  <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-md">
                    {model}
                  </span>
                )}
                <button
                  onClick={handleSpeak}
                  title={speaking ? "Stop listening" : "Listen to answer"}
                  className={`p-1.5 rounded-lg transition-colors ${
                    speaking ? 'text-purple-600 bg-purple-100 animate-pulse' : 'text-slate-400 hover:text-purple-600 hover:bg-slate-100'
                  }`}
                >
                  {speaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>
                <button
                  onClick={handleCopy}
                  title="Copy answer"
                  className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                </button>
                <button
                  onClick={handleBookmark}
                  title="Bookmark answer"
                  className={`p-1.5 rounded-lg hover:bg-slate-100 transition-colors ${
                    bookmarked ? 'text-amber-500' : 'text-slate-400 hover:text-amber-500'
                  }`}
                >
                  <Bookmark className="w-4 h-4 fill-current" />
                </button>
              </div>
            </div>

            {/* Answer Content */}
            <div className="text-slate-800 text-sm sm:text-base leading-relaxed whitespace-pre-line font-normal">
              {loading ? (
                <div className="space-y-3 animate-pulse py-4">
                  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                  <div className="h-4 bg-slate-200 rounded w-5/6"></div>
                  <div className="h-4 bg-slate-200 rounded w-2/3"></div>
                </div>
              ) : (
                answer
              )}
            </div>

          </div>

          {/* Right Panel: Sources (Cited) */}
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            
            <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
              <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <h3 className="font-extrabold text-base text-slate-900 tracking-tight">Sources (Cited)</h3>
            </div>

            {loading ? (
              <div className="space-y-3 animate-pulse py-2">
                <div className="h-10 bg-slate-100 rounded-xl"></div>
                <div className="h-10 bg-slate-100 rounded-xl"></div>
              </div>
            ) : sources.length === 0 ? (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-center text-xs text-slate-500">
                <Info className="w-5 h-5 text-slate-400 mx-auto mb-1.5" />
                No institutional documents cited for this query.
              </div>
            ) : (
              <div className="space-y-2.5">
                {sources.map((src, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedCitation(src)}
                    className="p-3 bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 rounded-xl cursor-pointer transition-all group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                        <span className="text-xs font-bold text-blue-900 group-hover:underline">
                          {src.title}
                        </span>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 shrink-0 ml-1" />
                    </div>

                    <div className="mt-1.5 pl-6 text-[11px] text-slate-500 flex items-center gap-1.5">
                      <span className="bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 font-medium">
                        Page {src.page}
                      </span>
                      {src.section && (
                        <span className="bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded font-medium">
                          {src.section}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="pt-2 border-t border-slate-100">
              <p className="text-[11px] text-slate-400 flex items-center gap-1">
                <Info className="w-3.5 h-3.5" /> Click any source above to inspect verified page citations.
              </p>
            </div>

          </div>

        </div>
      )}

      {/* Citation Snippet Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-base text-slate-900">{selectedCitation.title}</h3>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-600">
              <span className="bg-blue-50 text-blue-700 font-semibold px-2 py-0.5 rounded">
                Page {selectedCitation.page}
              </span>
              {selectedCitation.section && (
                <span className="bg-purple-50 text-purple-700 font-semibold px-2 py-0.5 rounded">
                  {selectedCitation.section}
                </span>
              )}
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed font-mono">
              "{selectedCitation.snippet}"
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCitation(null)}
                className="bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-4 py-2 rounded-xl"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
