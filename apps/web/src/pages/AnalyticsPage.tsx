import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, FileText, Clock, Shield, PieChart } from 'lucide-react';
import { analyticsAPI } from '../api/client';
import { AnalyticsData } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await analyticsAPI.getOverview();
        setData(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <div className="h-8 bg-slate-200 rounded w-1/4 animate-pulse"></div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className="h-28 bg-white rounded-2xl border border-slate-200 animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Analytics & Operational Telemetry</h1>
        <p className="text-xs text-slate-500 font-medium">Real-time usage patterns, response latencies, and knowledge coverage</p>
      </div>

      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Queries</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900">{data.total_queries}</p>
          <p className="text-[11px] text-emerald-600 font-semibold">+18% this month</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Avg Latency</span>
            <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900">{data.avg_response_time}s</p>
          <p className="text-[11px] text-purple-600 font-semibold">Sub-second generation</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Indexed Documents</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900">{data.total_documents}</p>
          <p className="text-[11px] text-amber-600 font-semibold">Verified school sources</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Active Users</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900">{data.total_users}</p>
          <p className="text-[11px] text-emerald-600 font-semibold">5 Stakeholder Roles</p>
        </div>

      </div>

      {/* Middle Row: Trend Chart & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Recent 7-Day Query Trend */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-900">7-Day Query Volume Trend</h3>
            </div>
            <span className="text-xs font-semibold text-slate-400">Past Week</span>
          </div>

          <div className="h-48 flex items-end gap-3 pt-6 pb-2 px-2">
            {data.recent_trend.map((t, idx) => {
              const maxQ = Math.max(...data.recent_trend.map((x) => x.queries), 1);
              const heightPercent = Math.max(15, Math.round((t.queries / maxQ) * 100));
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group">
                  <span className="text-[10px] font-bold text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    {t.queries}
                  </span>
                  <div
                    style={{ height: `${heightPercent}%` }}
                    className="w-full bg-gradient-to-t from-blue-600 to-indigo-500 rounded-t-lg transition-all group-hover:from-blue-700 group-hover:to-purple-600"
                  ></div>
                  <span className="text-[10px] text-slate-400 font-mono truncate max-w-full">
                    {t.date.split('-').slice(1).join('/')}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Stakeholder Role Distribution */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <PieChart className="w-4 h-4 text-purple-600" />
              <h3 className="font-bold text-sm text-slate-900">Stakeholder Role Distribution</h3>
            </div>
          </div>

          <div className="space-y-3 pt-1">
            {Object.entries(data.role_breakdown).map(([role, count]) => {
              const total = Object.values(data.role_breakdown).reduce((a, b) => a + b, 0) || 1;
              const pct = Math.round((count / total) * 100);
              return (
                <div key={role} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">{role}</span>
                    <span className="text-slate-500">{count} ({pct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${pct}%` }}
                      className="bg-purple-600 h-full rounded-full"
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
};
