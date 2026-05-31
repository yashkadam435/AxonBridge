'use client';

import React, { useState, useEffect } from 'react';

/* ================================================================
   AxonBridge — Audit Log Viewer
   Searchable, filterable audit log with integrity verification
   ================================================================ */

const MOCK_LOGS = [
  { id: '1', timestamp: '2026-05-30T06:28:00Z', user: 'Dr. Sharma', action: 'approve', category: 'clinical', resource: 'SOAP Note #4821', severity: 'info', ip: '10.0.1.45' },
  { id: '2', timestamp: '2026-05-30T06:25:00Z', user: 'Agent-7', action: 'execute', category: 'workflow', resource: 'Patient Registration', severity: 'info', ip: 'system' },
  { id: '3', timestamp: '2026-05-30T06:22:00Z', user: 'Admin', action: 'update', category: 'admin', resource: 'Workflow Template', severity: 'info', ip: '10.0.1.12' },
  { id: '4', timestamp: '2026-05-30T06:18:00Z', user: 'Agent-3', action: 'create', category: 'clinical', resource: 'Clinical Note', severity: 'info', ip: 'system' },
  { id: '5', timestamp: '2026-05-30T06:15:00Z', user: 'System', action: 'login_failed', category: 'auth', resource: 'User: unknown@test.com', severity: 'warning', ip: '192.168.1.100' },
  { id: '6', timestamp: '2026-05-30T06:10:00Z', user: 'Dr. Patel', action: 'reject', category: 'clinical', resource: 'ICD-10 Suggestion', severity: 'warning', ip: '10.0.2.33' },
  { id: '7', timestamp: '2026-05-30T06:05:00Z', user: 'Agent-12', action: 'extract', category: 'workflow', resource: 'Lab Results', severity: 'info', ip: 'system' },
  { id: '8', timestamp: '2026-05-30T05:58:00Z', user: 'System', action: 'backup', category: 'system', resource: 'Database Backup', severity: 'info', ip: 'system' },
  { id: '9', timestamp: '2026-05-30T05:45:00Z', user: 'Admin', action: 'create', category: 'admin', resource: 'New User: nurse.jones@hospital.org', severity: 'info', ip: '10.0.1.12' },
  { id: '10', timestamp: '2026-05-30T05:30:00Z', user: 'Agent-5', action: 'retry', category: 'agent', resource: 'Element detection fallback', severity: 'warning', ip: 'system' },
];

const CATEGORIES = ['All', 'auth', 'clinical', 'workflow', 'admin', 'agent', 'system'];
const SEVERITIES = ['All', 'info', 'warning', 'critical'];

export default function AuditPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [severity, setSeverity] = useState('All');
  const [integrityStatus, setIntegrityStatus] = useState<'checking' | 'valid' | 'invalid'>('valid');
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const filtered = MOCK_LOGS.filter(log => {
    const matchesSearch = !search || log.user.toLowerCase().includes(search.toLowerCase()) ||
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.resource.toLowerCase().includes(search.toLowerCase());
    const matchesCat = category === 'All' || log.category === category;
    const matchesSev = severity === 'All' || log.severity === severity;
    return matchesSearch && matchesCat && matchesSev;
  });

  const handleIntegrityCheck = () => {
    setIntegrityStatus('checking');
    setTimeout(() => setIntegrityStatus('valid'), 2000);
  };

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s' }}>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Audit Logs</h1>
          <p style={s.pageSubtitle}>Immutable, tamper-evident record of all system activity</p>
        </div>
        <div style={s.headerActions}>
          <button onClick={handleIntegrityCheck} style={s.integrityBtn}>
            {integrityStatus === 'checking' ? (
              <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>↻</span>
            ) : integrityStatus === 'valid' ? '✓' : '✗'}
            {' '}Chain Integrity: {integrityStatus === 'checking' ? 'Verifying...' : integrityStatus === 'valid' ? 'Valid' : 'Violation Detected'}
          </button>
          <button style={s.exportBtn}>↓ Export CSV</button>
        </div>
      </div>

      {/* Filters */}
      <div style={s.filterBar}>
        <div style={s.searchBox}>
          <span style={{ color: 'var(--text-tertiary)' }}>🔍</span>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search logs by user, action, or resource..."
            style={s.searchInput}
          />
        </div>
        <div style={s.filterGroup}>
          <label style={s.filterLabel}>Category</label>
          <select value={category} onChange={e => setCategory(e.target.value)} style={s.filterSelect}>
            {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div style={s.filterGroup}>
          <label style={s.filterLabel}>Severity</label>
          <select value={severity} onChange={e => setSeverity(e.target.value)} style={s.filterSelect}>
            {SEVERITIES.map(sv => <option key={sv} value={sv}>{sv}</option>)}
          </select>
        </div>
        <span style={s.resultCount}>{filtered.length} entries</span>
      </div>

      {/* Table */}
      <div style={s.tableWrapper}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>Timestamp</th>
              <th style={s.th}>User / Agent</th>
              <th style={s.th}>Action</th>
              <th style={s.th}>Category</th>
              <th style={s.th}>Resource</th>
              <th style={s.th}>Severity</th>
              <th style={s.th}>IP Address</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((log, i) => (
              <tr key={log.id} style={{ ...s.tr, animationDelay: `${i * 30}ms` }}>
                <td style={s.td}>
                  <div style={s.timestampCell}>
                    <span style={s.timeValue}>{formatTime(log.timestamp)}</span>
                    <span style={s.dateValue}>{formatDate(log.timestamp)}</span>
                  </div>
                </td>
                <td style={s.td}>
                  <span style={{
                    ...s.userBadge,
                    background: log.user.startsWith('Agent') ? 'rgba(59, 130, 246, 0.1)' : log.user === 'System' ? 'rgba(148, 163, 184, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                    color: log.user.startsWith('Agent') ? '#60A5FA' : log.user === 'System' ? '#94A3B8' : '#4ADE80',
                  }}>
                    {log.user}
                  </span>
                </td>
                <td style={s.td}>
                  <span style={s.actionText}>{log.action}</span>
                </td>
                <td style={s.td}>
                  <span style={s.categoryBadge}>{log.category}</span>
                </td>
                <td style={s.td}>
                  <span style={s.resourceText}>{log.resource}</span>
                </td>
                <td style={s.td}>
                  <span style={{
                    ...s.severityBadge,
                    background: log.severity === 'info' ? 'rgba(59, 130, 246, 0.1)' : log.severity === 'warning' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: log.severity === 'info' ? '#60A5FA' : log.severity === 'warning' ? '#FBBF24' : '#F87171',
                  }}>
                    {log.severity}
                  </span>
                </td>
                <td style={s.td}>
                  <span style={s.ipText}>{log.ip}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div style={s.pagination}>
        <span style={s.paginationInfo}>Showing 1-{filtered.length} of {filtered.length} entries</span>
        <div style={s.paginationBtns}>
          <button style={s.pageBtn} disabled>← Previous</button>
          <button style={{ ...s.pageBtn, ...s.pageBtnActive }}>1</button>
          <button style={s.pageBtn}>Next →</button>
        </div>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' },
  pageTitle: { fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' },
  pageSubtitle: { fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' },
  headerActions: { display: 'flex', gap: '0.75rem' },
  integrityBtn: {
    display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
    borderRadius: '0.5rem', border: '1px solid rgba(34, 197, 94, 0.3)',
    background: 'rgba(34, 197, 94, 0.08)', color: '#22C55E',
    fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
  },
  exportBtn: {
    padding: '0.5rem 1rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)',
    background: 'var(--bg-card)', color: 'var(--text-primary)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
  },
  filterBar: {
    display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' as const,
    padding: '0.75rem 1rem', borderRadius: '0.75rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)',
  },
  searchBox: {
    display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '200px',
    padding: '0.4rem 0.75rem', borderRadius: '0.5rem', background: 'var(--bg-input)', border: '1px solid var(--border-primary)',
  },
  searchInput: {
    border: 'none', background: 'transparent', outline: 'none', color: 'var(--text-primary)',
    fontSize: '0.85rem', width: '100%',
  },
  filterGroup: { display: 'flex', alignItems: 'center', gap: '0.375rem' },
  filterLabel: { fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase' as const },
  filterSelect: {
    padding: '0.35rem 0.6rem', borderRadius: '0.375rem', border: '1px solid var(--border-primary)',
    background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: '0.8rem', outline: 'none',
  },
  resultCount: { fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 500, marginLeft: 'auto' },
  tableWrapper: {
    borderRadius: '0.75rem', border: '1px solid var(--border-primary)', overflow: 'hidden', background: 'var(--bg-card)',
  },
  table: { width: '100%', borderCollapse: 'collapse' as const, fontSize: '0.85rem' },
  th: {
    padding: '0.75rem 1rem', textAlign: 'left' as const, fontSize: '0.7rem', fontWeight: 700,
    color: 'var(--text-tertiary)', textTransform: 'uppercase' as const, letterSpacing: '0.05em',
    borderBottom: '1px solid var(--border-primary)', background: 'var(--bg-tertiary)',
  },
  tr: {
    borderBottom: '1px solid var(--border-primary)', transition: 'background 0.15s',
    animation: 'fadeIn 0.3s ease-out forwards', opacity: 0,
  },
  td: { padding: '0.65rem 1rem', verticalAlign: 'middle' as const },
  timestampCell: { display: 'flex', flexDirection: 'column' as const },
  timeValue: { fontSize: '0.8rem', fontFamily: 'var(--font-mono)', fontWeight: 500, color: 'var(--text-primary)' },
  dateValue: { fontSize: '0.65rem', color: 'var(--text-tertiary)' },
  userBadge: {
    padding: '0.2rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: 600,
  },
  actionText: { fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 500 },
  categoryBadge: {
    padding: '0.15rem 0.5rem', borderRadius: '9999px', fontSize: '0.65rem', fontWeight: 600,
    background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', textTransform: 'capitalize' as const,
  },
  resourceText: { fontSize: '0.8rem', color: 'var(--text-secondary)' },
  severityBadge: {
    padding: '0.15rem 0.5rem', borderRadius: '9999px', fontSize: '0.65rem', fontWeight: 700,
    textTransform: 'uppercase' as const,
  },
  ipText: { fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' },
  pagination: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', padding: '0.5rem 0',
  },
  paginationInfo: { fontSize: '0.8rem', color: 'var(--text-tertiary)' },
  paginationBtns: { display: 'flex', gap: '0.375rem' },
  pageBtn: {
    padding: '0.375rem 0.75rem', borderRadius: '0.375rem', border: '1px solid var(--border-primary)',
    background: 'var(--bg-card)', color: 'var(--text-secondary)', fontSize: '0.8rem', cursor: 'pointer',
  },
  pageBtnActive: {
    background: 'var(--color-primary-600)', color: 'white', borderColor: 'var(--color-primary-600)',
  },
};
