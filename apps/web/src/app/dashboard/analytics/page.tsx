'use client';

import React, { useState, useEffect } from 'react';

/* ================================================================
   AxonBridge — Analytics Dashboard
   Operational metrics, agent performance, and compliance overview
   ================================================================ */

const METRICS = [
  { label: 'Total Workflows (MTD)', value: '12,847', change: '+24%', positive: true },
  { label: 'Avg Agent Confidence', value: '93.2%', change: '+1.8%', positive: true },
  { label: 'HITL Interventions', value: '342', change: '-12%', positive: true },
  { label: 'Mean Time to Complete', value: '4.2m', change: '-0.8m', positive: true },
  { label: 'Error Rate', value: '1.3%', change: '-0.5%', positive: true },
  { label: 'Active Users', value: '156', change: '+18', positive: true },
];

const DAILY_DATA = [
  { day: 'Mon', workflows: 1823, errors: 24, hitl: 48 },
  { day: 'Tue', workflows: 2104, errors: 31, hitl: 52 },
  { day: 'Wed', workflows: 1956, errors: 18, hitl: 41 },
  { day: 'Thu', workflows: 2341, errors: 22, hitl: 55 },
  { day: 'Fri', workflows: 2567, errors: 15, hitl: 38 },
  { day: 'Sat', workflows: 1234, errors: 8, hitl: 22 },
  { day: 'Sun', workflows: 822, errors: 5, hitl: 14 },
];

const TOP_WORKFLOWS = [
  { name: 'Lab Result Extraction', runs: 3456, success: 99.1 },
  { name: 'Appointment Scheduling', runs: 2891, success: 99.5 },
  { name: 'Billing Code Entry', runs: 2341, success: 97.1 },
  { name: 'Patient Registration', runs: 1247, success: 98.2 },
  { name: 'SOAP Note Structuring', runs: 892, success: 96.8 },
];

const COMPLIANCE = [
  { metric: 'Audit Log Integrity', status: 'pass', detail: 'Chain hash verified — 0 violations' },
  { metric: 'PHI Encryption', status: 'pass', detail: 'AES-256-GCM on all PHI fields' },
  { metric: 'Access Control', status: 'pass', detail: 'RBAC enforced — 0 unauthorized attempts' },
  { metric: 'Data Retention', status: 'pass', detail: '7-year retention policy active' },
  { metric: 'Session Security', status: 'warning', detail: '3 sessions exceeded 8h duration' },
];

export default function AnalyticsPage() {
  const [mounted, setMounted] = useState(false);
  const [period, setPeriod] = useState('7d');
  useEffect(() => { setMounted(true); }, []);

  const maxWorkflows = Math.max(...DAILY_DATA.map(d => d.workflows));

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s' }}>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Analytics</h1>
          <p style={s.pageSubtitle}>Operational metrics, performance insights, and compliance overview</p>
        </div>
        <div style={s.periodTabs}>
          {['24h', '7d', '30d', '90d'].map(p => (
            <button key={p} onClick={() => setPeriod(p)} style={{ ...s.periodTab, ...(period === p ? s.periodTabActive : {}) }}>{p}</button>
          ))}
        </div>
      </div>

      {/* Metrics grid */}
      <div style={s.metricsGrid}>
        {METRICS.map((m, i) => (
          <div key={i} style={{ ...s.metricCard, animation: 'fadeInUp 0.4s ease-out forwards', animationDelay: `${i * 50}ms`, opacity: 0 }}>
            <span style={s.metricLabel}>{m.label}</span>
            <span style={s.metricValue}>{m.value}</span>
            <span style={{ ...s.metricChange, color: m.positive ? '#22C55E' : '#EF4444' }}>
              {m.positive ? '↑' : '↓'} {m.change}
            </span>
          </div>
        ))}
      </div>

      <div style={s.twoCol}>
        {/* Bar chart */}
        <div style={s.card}>
          <h2 style={s.cardTitle}>Workflow Volume (7 days)</h2>
          <div style={s.chartArea}>
            {DAILY_DATA.map((d, i) => (
              <div key={i} style={s.barGroup}>
                <div style={s.barContainer}>
                  <div style={{ ...s.bar, height: `${(d.workflows / maxWorkflows) * 100}%`, background: 'linear-gradient(to top, #3B82F6, #60A5FA)', animation: 'fadeInUp 0.5s ease-out forwards', animationDelay: `${i * 80}ms` }} />
                </div>
                <span style={s.barLabel}>{d.day}</span>
                <span style={s.barValue}>{d.workflows.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top workflows */}
        <div style={s.card}>
          <h2 style={s.cardTitle}>Top Workflows by Volume</h2>
          <div style={s.topList}>
            {TOP_WORKFLOWS.map((wf, i) => (
              <div key={i} style={s.topItem}>
                <div style={s.topLeft}>
                  <span style={s.topRank}>#{i + 1}</span>
                  <span style={s.topName}>{wf.name}</span>
                </div>
                <div style={s.topRight}>
                  <span style={s.topRuns}>{wf.runs.toLocaleString()} runs</span>
                  <div style={s.topSuccessBar}>
                    <div style={{ ...s.topSuccessFill, width: `${wf.success}%` }} />
                  </div>
                  <span style={{ ...s.topPercent, color: wf.success >= 98 ? '#22C55E' : '#F59E0B' }}>{wf.success}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance section */}
      <div style={{ ...s.card, marginTop: '1.25rem' }}>
        <h2 style={s.cardTitle}>HIPAA Compliance Status</h2>
        <div style={s.complianceGrid}>
          {COMPLIANCE.map((c, i) => (
            <div key={i} style={s.complianceItem}>
              <span style={{ ...s.complianceIcon, color: c.status === 'pass' ? '#22C55E' : '#F59E0B' }}>
                {c.status === 'pass' ? '✓' : '⚠'}
              </span>
              <div>
                <span style={s.complianceMetric}>{c.metric}</span>
                <span style={s.complianceDetail}>{c.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' },
  pageTitle: { fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' },
  pageSubtitle: { fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' },
  periodTabs: { display: 'flex', gap: '0.25rem', padding: '0.25rem', borderRadius: '0.5rem', background: 'var(--bg-tertiary)' },
  periodTab: { padding: '0.35rem 0.75rem', borderRadius: '0.375rem', border: 'none', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer' },
  periodTabActive: { background: 'var(--bg-card)', color: 'var(--text-primary)', fontWeight: 600, boxShadow: 'var(--shadow-sm)' },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '0.75rem', marginBottom: '1.25rem' },
  metricCard: { padding: '1rem', borderRadius: '0.75rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', textAlign: 'center' as const },
  metricLabel: { fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase' as const, letterSpacing: '0.05em', display: 'block', marginBottom: '0.35rem' },
  metricValue: { fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', display: 'block', fontFamily: 'var(--font-mono)' },
  metricChange: { fontSize: '0.7rem', fontWeight: 600, display: 'block', marginTop: '0.25rem' },
  twoCol: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' },
  card: { padding: '1.25rem', borderRadius: '0.75rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)' },
  cardTitle: { fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem' },
  chartArea: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', height: '200px', gap: '0.5rem', paddingTop: '0.5rem' },
  barGroup: { display: 'flex', flexDirection: 'column' as const, alignItems: 'center', gap: '0.25rem', flex: 1 },
  barContainer: { height: '160px', width: '100%', display: 'flex', alignItems: 'flex-end', justifyContent: 'center' },
  bar: { width: '70%', borderRadius: '4px 4px 0 0', minHeight: '4px', transition: 'height 0.5s ease-out' },
  barLabel: { fontSize: '0.7rem', color: 'var(--text-tertiary)', fontWeight: 500 },
  barValue: { fontSize: '0.6rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' },
  topList: { display: 'flex', flexDirection: 'column' as const, gap: '0.75rem' },
  topItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  topLeft: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  topRank: { fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-tertiary)', width: '24px' },
  topName: { fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' },
  topRight: { display: 'flex', alignItems: 'center', gap: '0.75rem' },
  topRuns: { fontSize: '0.75rem', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', width: '80px', textAlign: 'right' as const },
  topSuccessBar: { width: '80px', height: '4px', borderRadius: '2px', background: 'var(--bg-tertiary)', overflow: 'hidden' },
  topSuccessFill: { height: '100%', borderRadius: '2px', background: '#22C55E' },
  topPercent: { fontSize: '0.8rem', fontWeight: 700, width: '40px', textAlign: 'right' as const, fontFamily: 'var(--font-mono)' },
  complianceGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' },
  complianceItem: { display: 'flex', alignItems: 'flex-start', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', background: 'var(--bg-tertiary)' },
  complianceIcon: { fontSize: '1.1rem', fontWeight: 700, marginTop: '0.1rem' },
  complianceMetric: { fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block' },
  complianceDetail: { fontSize: '0.7rem', color: 'var(--text-tertiary)', display: 'block', marginTop: '0.15rem' },
};
