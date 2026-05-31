'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Settings2, History, Activity } from 'lucide-react';

/* ================================================================
   AxonBridge — Workflow Management
   ================================================================ */

const WORKFLOWS = [
  { id: 'registration', name: 'Patient Registration', category: 'administrative', mode: 'automated', risk: 'low', status: 'active', executions: 1247, successRate: 98.2, lastRun: '5 min ago', his: 'eHospital' },
  { id: 'nlp', name: 'SOAP Note Structuring', category: 'clinical', mode: 'assisted', risk: 'high', status: 'active', executions: 892, successRate: 96.8, lastRun: '12 min ago', his: 'eHospital' },
  { id: 'billing', name: 'Billing Code Entry', category: 'billing', mode: 'assisted', risk: 'medium', status: 'active', executions: 2341, successRate: 97.1, lastRun: '3 min ago', his: 'Practo' },
  { id: 'lab-results', name: 'Lab Result Extraction', category: 'clinical', mode: 'automated', risk: 'low', status: 'active', executions: 3456, successRate: 99.1, lastRun: '1 min ago', his: 'eHospital' },
  { id: 'discharge', name: 'Discharge Summary', category: 'clinical', mode: 'assisted', risk: 'critical', status: 'active', executions: 456, successRate: 95.4, lastRun: '45 min ago', his: 'eHospital' },
  { id: 'scheduling', name: 'Appointment Scheduling', category: 'administrative', mode: 'automated', risk: 'low', status: 'paused', executions: 5678, successRate: 99.5, lastRun: '2h ago', his: 'Practo' },
];

const riskColor = (risk: string) => {
  const m: Record<string, string> = { low: '#22C55E', medium: '#F59E0B', high: '#EF4444', critical: '#DC2626' };
  return m[risk] || '#94A3B8';
};

export default function WorkflowsPage() {
  const [mounted, setMounted] = useState(false);
  const [filter, setFilter] = useState('all');
  const router = useRouter();

  useEffect(() => { setMounted(true); }, []);

  const filtered = WORKFLOWS.filter(w => filter === 'all' || w.category === filter);

  const handleRun = (id: string) => {
    if (id === 'nlp') {
      router.push('/dashboard/nlp');
    } else {
      router.push(`/dashboard/workflows/${id}`);
    }
  };

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s' }} className="pb-10">
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Workflows</h1>
          <p style={s.pageSubtitle}>Manage automation workflow templates and run LLM-powered orchestrations</p>
        </div>
        <button style={s.primaryBtn} onClick={() => router.push('/dashboard/workflows/registration')}>
          <Activity size={16} /> Create Workflow
        </button>
      </div>

      {/* Filter tabs */}
      <div style={s.tabs}>
        {['all', 'clinical', 'administrative', 'billing'].map(tab => (
          <button key={tab} onClick={() => setFilter(tab)} style={{ ...s.tab, ...(filter === tab ? s.tabActive : {}) }}>
            {tab === 'all' ? 'All' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            {tab === 'all' && <span style={s.tabCount}>{WORKFLOWS.length}</span>}
          </button>
        ))}
      </div>

      {/* Workflow Cards */}
      <div style={s.grid}>
        {filtered.map((wf, i) => (
          <div key={wf.id} style={{ ...s.card, animation: 'fadeInUp 0.4s ease-out forwards', animationDelay: `${i * 60}ms`, opacity: 0 }} className="group hover:border-blue-300 hover:shadow-md transition-all">
            <div style={s.cardTop}>
              <div>
                <h3 style={s.cardName}>{wf.name}</h3>
                <span style={s.cardHis}>{wf.his}</span>
              </div>
              <span style={{ ...s.statusDot, background: wf.status === 'active' ? '#22C55E' : '#94A3B8', boxShadow: wf.status === 'active' ? '0 0 8px rgba(34,197,94,0.4)' : 'none' }} />
            </div>
            
            <div style={s.badgeRow}>
              <span style={{ ...s.badge, background: wf.mode === 'automated' ? 'var(--color-primary-50)' : 'var(--color-teal-50)', color: wf.mode === 'automated' ? 'var(--color-primary-600)' : 'var(--color-teal-600)' }}>{wf.mode}</span>
              <span style={{ ...s.badge, background: `${riskColor(wf.risk)}15`, color: riskColor(wf.risk), border: `1px solid ${riskColor(wf.risk)}30` }}>Risk: {wf.risk}</span>
              <span style={{ ...s.badge, background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>{wf.category}</span>
            </div>
            
            <div style={s.statsRow}>
              <div style={s.stat}><span style={s.statNum}>{wf.executions.toLocaleString()}</span><span style={s.statLbl}>Executions</span></div>
              <div style={s.stat}><span style={{ ...s.statNum, color: wf.successRate >= 98 ? '#22C55E' : '#F59E0B' }}>{wf.successRate}%</span><span style={s.statLbl}>Success Rate</span></div>
              <div style={s.stat}><span style={s.statNum}>{wf.lastRun}</span><span style={s.statLbl}>Last Run</span></div>
            </div>
            
            <div style={s.cardActions}>
              <button style={s.runBtn} onClick={() => handleRun(wf.id)} className="hover:bg-green-100 transition-colors">
                <Play size={14} fill="currentColor" /> Run AI Model
              </button>
              <button style={s.editBtn} className="hover:bg-slate-50 transition-colors">
                <Settings2 size={14} /> Edit
              </button>
              <button style={s.viewBtn} className="hover:bg-slate-50 transition-colors">
                <History size={14} /> History
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' },
  pageTitle: { fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' },
  pageSubtitle: { fontSize: '1rem', color: 'var(--text-secondary)', marginTop: '0.25rem', fontWeight: 500 },
  primaryBtn: { display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 1.25rem', borderRadius: '0.75rem', border: 'none', background: 'linear-gradient(135deg, #2563EB, #0891B2)', color: 'white', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)' },
  tabs: { display: 'flex', gap: '0.5rem', marginBottom: '2rem', padding: '0.35rem', borderRadius: '0.75rem', background: 'var(--bg-tertiary)', width: 'fit-content' },
  tab: { padding: '0.5rem 1.25rem', borderRadius: '0.5rem', border: 'none', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'all 0.2s' },
  tabActive: { background: 'var(--bg-card)', color: 'var(--text-primary)', fontWeight: 700, boxShadow: 'var(--shadow-sm)' },
  tabCount: { fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '9999px', background: 'var(--color-primary-100)', color: 'var(--color-primary-700)' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' },
  card: { padding: '1.5rem', borderRadius: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', boxShadow: 'var(--shadow-sm)' },
  cardTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' },
  cardName: { fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' },
  cardHis: { fontSize: '0.8rem', color: 'var(--text-tertiary)', marginTop: '0.25rem', fontWeight: 500 },
  statusDot: { width: '10px', height: '10px', borderRadius: '50%', flexShrink: 0, marginTop: '0.35rem' },
  badgeRow: { display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' as const },
  badge: { fontSize: '0.7rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '0.375rem', textTransform: 'capitalize' as const },
  statsRow: { display: 'flex', justifyContent: 'space-between', padding: '1rem 0', borderTop: '1px solid var(--border-primary)', borderBottom: '1px solid var(--border-primary)', marginBottom: '1.25rem' },
  stat: { display: 'flex', flexDirection: 'column' as const, alignItems: 'center', gap: '0.25rem' },
  statNum: { fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' },
  statLbl: { fontSize: '0.7rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' as const, fontWeight: 600 },
  cardActions: { display: 'flex', gap: '0.75rem' },
  runBtn: { flex: 1, padding: '0.65rem', borderRadius: '0.5rem', border: 'none', background: 'var(--color-success-50)', color: 'var(--color-success-600)', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' },
  editBtn: { flex: 1, padding: '0.65rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' },
  viewBtn: { flex: 1, padding: '0.65rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' },
};
