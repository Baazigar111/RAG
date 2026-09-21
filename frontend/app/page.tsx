'use client';

import { useState } from 'react';

export default function TriageDashboard() {
  const [serviceName, setServiceName] = useState('auth-service');
  const [errorCode, setErrorCode] = useState('ERR_CONN_RESET');
  const [severity, setSeverity] = useState('HIGH');
  const [rawLog, setRawLog] = useState('2026-03-30T14:22:10Z [ERROR] auth-service connection pool exhausted due to socket leak');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleTriage = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service_name: serviceName, error_code: errorCode, severity, raw_log: rawLog }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityStyle = (sev: string) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'HIGH': return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      default: return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    }
  };

  return (
    <main className="min-h-screen bg-[#030712] text-slate-100 selection:bg-cyan-500 selection:text-black">
      {/* Background glow ambient effect */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[300px] bg-gradient-to-tr from-cyan-500/10 to-indigo-500/10 blur-[120px] pointer-events-none" />

      <div className="relative max-w-5xl mx-auto px-6 py-12 space-y-8">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <h1 className="text-2xl font-semibold tracking-tight text-white font-mono">LogIntel<span className="text-cyan-400">.ai</span></h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">Autonomous SRE Incident Triage & RAG Synthesizer</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-400">
              Engine: <span className="text-cyan-400">Groq Llama-3.3</span>
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Input Control Panel */}
          <form onSubmit={handleTriage} className="lg:col-span-5 bg-slate-900/50 backdrop-blur-xl border border-slate-800/80 p-6 rounded-2xl space-y-5 shadow-2xl">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Incident Parameters</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1.5">Service Name</label>
                <input
                  type="text"
                  value={serviceName}
                  onChange={(e) => setServiceName(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1.5">Error Code</label>
                  <input
                    type="text"
                    value={errorCode}
                    onChange={(e) => setErrorCode(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1.5">Severity</label>
                  <input
                    type="text"
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1.5">Raw Log Payload</label>
                <textarea
                  rows={4}
                  value={rawLog}
                  onChange={(e) => setRawLog(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500 transition-colors leading-relaxed"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold py-3 rounded-xl transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50 text-xs tracking-wider uppercase font-mono"
            >
              {loading ? 'Synthesizing Triage...' : 'Execute Live Triage'}
            </button>
          </form>

          {/* Results Display Panel */}
          <div className="lg:col-span-7 space-y-6">
            {!result && !loading && (
              <div className="h-[420px] border border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-center p-6 bg-slate-900/20">
                <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-3 font-mono text-sm">AI</div>
                <p className="text-sm font-medium text-slate-300">Awaiting Incident Log</p>
                <p className="text-xs text-slate-500 max-w-xs mt-1">Submit a raw log payload to trigger vector similarity search and automated LLM remediation.</p>
              </div>
            )}

            {loading && (
              <div className="h-[420px] border border-slate-800 rounded-2xl flex flex-col items-center justify-center text-center p-6 bg-slate-900/40 backdrop-blur animate-pulse">
                <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4" />
                <p className="text-sm font-mono text-cyan-400">Querying Vector Store & Groq Engine...</p>
              </div>
            )}

            {result && !loading && (
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800/80 p-6 rounded-2xl space-y-5 shadow-2xl">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">Service:</span>
                    <span className="font-mono text-xs text-white font-medium bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">{result.service_name}</span>
                  </div>
                  <span className={`text-[10px] font-mono uppercase px-2.5 py-1 rounded-md border ${getSeverityStyle(severity)}`}>
                    {severity}
                  </span>
                </div>

                <div className="space-y-1.5">
                  <h3 className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Sanitized Log</h3>
                  <div className="font-mono text-xs bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-amber-400/90 overflow-x-auto">
                    {result.sanitized_log}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <h3 className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Diagnosed Root Cause</h3>
                  <div className="text-slate-200 text-xs bg-slate-950/80 p-4 rounded-xl border border-slate-800 leading-relaxed font-sans">
                    {result.diagnosis.diagnosed_root_cause}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <h3 className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Recommended Action Steps</h3>
                  <ul className="space-y-2 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                    {result.diagnosis.remediation_steps.map((step: string, idx: number) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start gap-2.5 font-sans">
                        <span className="font-mono text-cyan-400 font-bold shrink-0">0{idx + 1}.</span>
                        <span className="leading-normal">{step.replace(/^\d+\.\s*/, '')}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}