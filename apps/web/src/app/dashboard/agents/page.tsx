'use client';

import React, { useState, useEffect } from 'react';

const API = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004'}/api/v1/agents`;

/* ================================================================
   AxonBridge — Agent Monitor
   Real-time agent session monitoring with HITL confirmation UI
   ================================================================ */

export default function AgentsPage() {
  const [mounted, setMounted] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  
  const [agents, setAgents] = useState<any[]>([]);
  const agentsRef = React.useRef<any[]>([]);
  const [pendingActions, setPendingActions] = useState<any[]>([]);

  useEffect(() => { setMounted(true); }, []);

  const fetchState = async () => {
    try {
      const res = await fetch(`${API}?_t=${Date.now()}`, { cache: 'no-store' });
      const data = await res.json();
      setAgents(data.agents || []);
      agentsRef.current = data.agents || [];
      setPendingActions(data.pending_actions || []);
    } catch (e) {
      console.error('Failed to fetch agent state:', e);
    }
  };

  // Poll state every 3 seconds
  useEffect(() => {
    if (!mounted) return;
    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, [mounted]);

  // Trigger simulations for active agents
  useEffect(() => {
    if (!mounted) return;
    const interval = setInterval(() => {
      agentsRef.current.forEach(agent => {
        if (agent.status === 'active') {
          fetch(`${API}/${agent.id}/simulate`, { method: 'POST' }).catch(() => {});
        }
      });
    }, 4500);
    return () => clearInterval(interval);
  }, [mounted]);

  const handleNewAgent = async () => {
    const workflows = ["Patient Registration", "Billing Code Entry", "Lab Result Extraction", "Discharge Summary"];
    const hisList = ["eHospital", "Practo", "Cerner", "Epic"];
    
    await fetch(`${API}/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            his: hisList[Math.floor(Math.random() * hisList.length)],
            workflow: workflows[Math.floor(Math.random() * workflows.length)],
            mode: Math.random() > 0.3 ? 'assisted' : 'automated'
        })
    });
    fetchState();
  };

  const handleApprove = async (id: string) => {
      await fetch(`${API}/actions/${id}/approve`, { method: 'POST' });
      fetchState();
  };

  const handleReject = async (id: string) => {
      await fetch(`${API}/actions/${id}/reject`, { method: 'POST' });
      fetchState();
  };
  
  const handleAbortAll = async () => {
      await fetch(`${API}/abort_all`, { method: 'POST' });
      fetchState();
  };

  const statusColor = (status: string) => {
    const map: Record<string, string> = {
      active: '#22C55E', waiting_confirmation: '#F59E0B', completed: '#3B82F6',
      error: '#EF4444', paused: '#94A3B8', initializing: '#8B5CF6',
    };
    return map[status] || '#94A3B8';
  };

  const statusLabel = (status: string) => status.replace('_', ' ');

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s' }}>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Agent Monitor</h1>
          <p style={s.pageSubtitle}>Real-time browser automation agent tracking & human-in-the-loop</p>
        </div>
        <div style={s.headerActions}>
          <button onClick={handleAbortAll} style={s.abortAllBtn}>⚠ Emergency Stop All</button>
          <button onClick={handleNewAgent} style={s.primaryBtn}>+ New Agent Session</button>
        </div>
      </div>

      {/* Pending HITL Confirmations */}
      {pendingActions.length > 0 && (
        <div style={s.hitlSection}>
          <h2 style={s.sectionTitle}>
            <span style={s.hitlPulse} /> Pending Human Confirmation ({pendingActions.length})
          </h2>
          <div style={s.hitlGrid}>
            {pendingActions.map(pa => (
              <div key={pa.id} style={s.hitlCard}>
                <div style={s.hitlHeader}>
                  <span style={s.hitlAgent}>{pa.agent}</span>
                  <span style={s.hitlTime}>{pa.timestamp}</span>
                </div>
                <p style={s.hitlAction}>{pa.action}</p>
                <div style={s.hitlMeta}>
                  <span style={{
                    ...s.confidenceBadge,
                    color: pa.confidence >= 0.85 ? '#22C55E' : pa.confidence >= 0.7 ? '#F59E0B' : '#EF4444',
                    background: pa.confidence >= 0.85 ? 'rgba(34,197,94,0.1)' : pa.confidence >= 0.7 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)',
                  }}>
                    Confidence: {(pa.confidence * 100).toFixed(0)}%
                  </span>
                  {pa.screenshot && <span style={s.screenshotBadge}>📷 Screenshot available</span>}
                </div>
                <div style={s.hitlActions}>
                  <button onClick={() => handleApprove(pa.id)} style={s.approveBtn}>✓ Approve</button>
                  <button onClick={() => handleApprove(pa.id)} style={s.modifyBtn}>✎ Modify</button>
                  <button onClick={() => handleReject(pa.id)} style={s.rejectBtn}>✗ Reject</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Cards Grid */}
      <h2 style={{ ...s.sectionTitle, marginTop: '1.5rem' }}>Active Sessions ({agents.filter(a => a.status === 'active').length})</h2>
      
      {agents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'white', borderRadius: '0.75rem', border: '1px dashed #CBD5E1', marginTop: '1rem' }}>
            <p style={{ color: '#64748B', fontSize: '1rem', marginBottom: '1.5rem' }}>No agents currently running. Click "New Agent Session" to spawn an AI agent.</p>
          </div>
      ) : (
          <div style={s.agentGrid}>
            {agents.map((agent, i) => (
              <div
                key={agent.id}
                style={{
                  ...s.agentCard,
                  borderLeftColor: statusColor(agent.status),
                  animation: 'fadeInUp 0.4s ease-out forwards',
                  animationDelay: `${(i % 5) * 60}ms`,
                  opacity: 0,
                }}
                onClick={() => setSelectedAgent(agent.id === selectedAgent ? null : agent.id)}
              >
                <div style={s.agentCardHeader}>
                  <div style={s.agentNameRow}>
                    <span style={{ ...s.agentStatusDot, background: statusColor(agent.status), boxShadow: `0 0 8px ${statusColor(agent.status)}60` }} />
                    <span style={s.agentName}>{agent.name}</span>
                    <span style={{ ...s.modeBadge, background: agent.mode === 'automated' ? 'rgba(139,92,246,0.1)' : 'rgba(59,130,246,0.1)', color: agent.mode === 'automated' ? '#8B5CF6' : '#60A5FA' }}>
                      {agent.mode}
                    </span>
                  </div>
                  <span style={{ ...s.statusBadge, color: statusColor(agent.status), background: `${statusColor(agent.status)}15`, border: `1px solid ${statusColor(agent.status)}30` }}>
                    {statusLabel(agent.status)}
                  </span>
                </div>

                <div style={s.agentDetails}>
                  <div style={s.detailRow}><span style={s.detailLabel}>HIS Target</span><span style={s.detailValue}>{agent.his}</span></div>
                  <div style={s.detailRow}><span style={s.detailLabel}>Workflow</span><span style={s.detailValue}>{agent.workflow}</span></div>
                  <div style={s.detailRow}><span style={s.detailLabel}>Actions</span><span style={s.detailValue}>{agent.actions} completed</span></div>
                  <div style={s.detailRow}><span style={s.detailLabel}>Uptime</span><span style={s.detailValue}>{agent.uptime}</span></div>
                </div>

                {/* Progress bar */}
                <div style={s.progressContainer}>
                  <div style={s.progressHeader}>
                    <span style={s.progressLabel}>Progress</span>
                    <span style={s.progressValue}>{agent.progress}%</span>
                  </div>
                  <div style={s.progressBar}>
                    <div style={{ ...s.progressFill, width: `${agent.progress}%`, background: statusColor(agent.status) }} />
                  </div>
                </div>

                {/* Live Action Log */}
                <div style={s.actionLogContainer}>
                  <div style={s.actionLogHeader}>Live Action Log (Groq)</div>
                  <div style={s.actionLogContent}>
                    {agent.history && agent.history.length > 0 ? (
                       agent.history.slice(-3).map((hist: string, idx: number) => (
                           <div key={idx} style={s.actionLogItem}>
                             <span style={s.actionLogArrow}>→</span> {hist}
                           </div>
                       ))
                    ) : (
                       <div style={{ color: '#94A3B8', fontStyle: 'italic', fontSize: '0.7rem' }}>Initializing AI reasoning engine...</div>
                    )}
                  </div>
                </div>

                {/* Confidence */}
                <div style={s.confidenceRow}>
                  <span style={s.detailLabel}>Avg Confidence</span>
                  <span style={{
                    ...s.confidenceValue,
                    color: agent.confidence >= 0.85 ? '#22C55E' : agent.confidence >= 0.7 ? '#F59E0B' : '#EF4444',
                  }}>
                    {(agent.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
      )}
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' },
  pageTitle: { fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' },
  pageSubtitle: { fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' },
  headerActions: { display: 'flex', gap: '0.75rem' },
  abortAllBtn: {
    padding: '0.5rem 1rem', borderRadius: '0.5rem', border: '1px solid rgba(239,68,68,0.4)',
    background: 'rgba(239,68,68,0.1)', color: '#EF4444', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
  },
  primaryBtn: {
    padding: '0.5rem 1rem', borderRadius: '0.5rem', border: 'none',
    background: 'linear-gradient(135deg, #3B82F6, #2563EB)', color: 'white', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(59,130,246,0.3)',
  },
  hitlSection: {
    padding: '1.25rem', borderRadius: '0.75rem', background: 'rgba(245,158,11,0.05)',
    border: '1px solid rgba(245,158,11,0.2)', marginBottom: '1rem',
  },
  sectionTitle: { fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' },
  hitlPulse: {
    width: '8px', height: '8px', borderRadius: '50%', background: '#F59E0B',
    animation: 'pulse 2s infinite', display: 'inline-block',
  },
  hitlGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '0.75rem' },
  hitlCard: {
    padding: '1rem', borderRadius: '0.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)',
  },
  hitlHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' },
  hitlAgent: { fontSize: '0.85rem', fontWeight: 700, color: '#60A5FA' },
  hitlTime: { fontSize: '0.7rem', color: 'var(--text-tertiary)' },
  hitlAction: { fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: '0.75rem' },
  hitlMeta: { display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' as const },
  confidenceBadge: { fontSize: '0.7rem', fontWeight: 600, padding: '0.15rem 0.5rem', borderRadius: '9999px' },
  screenshotBadge: { fontSize: '0.7rem', color: 'var(--text-tertiary)', padding: '0.15rem 0.5rem', borderRadius: '9999px', background: 'var(--bg-tertiary)' },
  hitlActions: { display: 'flex', gap: '0.5rem' },
  approveBtn: {
    flex: 1, padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid rgba(34,197,94,0.3)',
    background: 'rgba(34,197,94,0.1)', color: '#22C55E', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
  },
  modifyBtn: {
    flex: 1, padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid rgba(59,130,246,0.3)',
    background: 'rgba(59,130,246,0.1)', color: '#60A5FA', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
  },
  rejectBtn: {
    flex: 1, padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid rgba(239,68,68,0.3)',
    background: 'rgba(239,68,68,0.1)', color: '#EF4444', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
  },
  agentGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem', marginTop: '1rem' },
  agentCard: {
    padding: '1.25rem', borderRadius: '0.75rem', background: 'var(--bg-card)',
    border: '1px solid var(--border-primary)', borderLeft: '3px solid',
    cursor: 'pointer', transition: 'transform 0.2s, box-shadow 0.2s',
  },
  agentCardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' },
  agentNameRow: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  agentStatusDot: { width: '8px', height: '8px', borderRadius: '50%' },
  agentName: { fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' },
  modeBadge: { fontSize: '0.6rem', fontWeight: 700, padding: '0.1rem 0.4rem', borderRadius: '9999px', textTransform: 'uppercase' as const },
  statusBadge: { fontSize: '0.65rem', fontWeight: 600, padding: '0.15rem 0.5rem', borderRadius: '9999px', textTransform: 'capitalize' as const },
  agentDetails: { display: 'flex', flexDirection: 'column' as const, gap: '0.35rem', marginBottom: '0.75rem' },
  detailRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  detailLabel: { fontSize: '0.75rem', color: 'var(--text-tertiary)' },
  detailValue: { fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 500 },
  progressContainer: { marginBottom: '0.75rem' },
  progressHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' },
  progressLabel: { fontSize: '0.7rem', color: 'var(--text-tertiary)' },
  progressValue: { fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' },
  progressBar: { height: '4px', borderRadius: '2px', background: 'var(--bg-tertiary)', overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: '2px', transition: 'width 0.5s ease-out' },
  confidenceRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-primary)' },
  confidenceValue: { fontSize: '0.9rem', fontWeight: 700, fontFamily: 'var(--font-mono)' },
  actionLogContainer: { marginTop: '0.75rem', marginBottom: '0.75rem', background: '#0F172A', borderRadius: '0.375rem', padding: '0.5rem', border: '1px solid #334155' },
  actionLogHeader: { fontSize: '0.65rem', color: '#94A3B8', textTransform: 'uppercase' as const, fontWeight: 700, letterSpacing: '0.05em', marginBottom: '0.35rem' },
  actionLogContent: { display: 'flex', flexDirection: 'column' as const, gap: '0.25rem', minHeight: '3.2rem', justifyContent: 'flex-end' },
  actionLogItem: { fontSize: '0.7rem', color: '#38BDF8', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  actionLogArrow: { color: '#64748B', marginRight: '0.25rem' },
};
