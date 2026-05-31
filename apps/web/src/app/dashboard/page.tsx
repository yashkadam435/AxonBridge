'use client';

import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Zap, 
  HeartPulse, 
  Users, 
  Play, 
  Search, 
  UserPlus, 
  Link2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Info,
  Server,
  Database,
  HardDrive,
  DatabaseBackup,
  Mic,
  Stethoscope,
  ChevronRight
} from 'lucide-react';
import { useRouter } from 'next/navigation';

/* ================================================================
   AxonBridge — Dashboard Home
   Stats cards, system health, activity feed, and quick actions
   ================================================================ */

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  
  useEffect(() => { setMounted(true); }, []);

  const STATS = [
    { label: 'Active Agents', value: '12', change: '+3 today', changeType: 'up', icon: Bot, color: '#3B82F6' },
    { label: 'Workflows Today', value: '247', change: '+18% vs yesterday', changeType: 'up', icon: Zap, color: '#06B6D4' },
    { label: 'System Health', value: '99.8%', change: 'All services OK', changeType: 'neutral', icon: HeartPulse, color: '#22C55E' },
    { label: 'Active Sessions', value: '38', change: '5 pending review', changeType: 'neutral', icon: Users, color: '#8B5CF6' },
  ];

  const HEALTH_SERVICES = [
    { name: 'API Server', status: 'healthy', latency: '12ms', uptime: '99.99%', icon: Server },
    { name: 'PostgreSQL', status: 'healthy', latency: '3ms', uptime: '99.98%', icon: Database },
    { name: 'Redis Cache', status: 'healthy', latency: '1ms', uptime: '100%', icon: HardDrive },
    { name: 'MinIO Storage', status: 'healthy', latency: '8ms', uptime: '99.95%', icon: DatabaseBackup },
    { name: 'Whisper STT', status: 'degraded', latency: '245ms', uptime: '98.5%', icon: Mic },
    { name: 'HIS: eHospital', status: 'healthy', latency: '89ms', uptime: '99.2%', icon: Stethoscope },
  ];

  const ACTIVITY_FEED = [
    { time: '2 min ago', actor: 'Agent-7', type: 'agent', action: 'Completed patient registration workflow', status: 'success' },
    { time: '5 min ago', actor: 'Dr. Sharma', type: 'human', action: 'Approved SOAP note for encounter #4821', status: 'success' },
    { time: '8 min ago', actor: 'Agent-3', type: 'agent', action: 'Awaiting confirmation — billing code review', status: 'pending' },
    { time: '12 min ago', actor: 'System', type: 'system', action: 'Automated backup completed successfully', status: 'success' },
    { time: '18 min ago', actor: 'Agent-12', type: 'agent', action: 'Extracted lab results from eHospital', status: 'success' },
    { time: '25 min ago', actor: 'Admin', type: 'human', action: 'Updated workflow template: Discharge Summary', status: 'info' },
    { time: '32 min ago', actor: 'Agent-5', type: 'agent', action: 'Failed to locate element — retrying with vision', status: 'warning' },
    { time: '45 min ago', actor: 'Dr. Patel', type: 'human', action: 'Rejected AI-suggested ICD-10 code (confidence: 72%)', status: 'rejected' },
  ];

  const QUICK_ACTIONS = [
    { label: 'Start Clinical Dictation', icon: Play, color: '#3B82F6', onClick: () => router.push('/dashboard/nlp') },
    { label: 'View Audit Logs', icon: Search, color: '#06B6D4', onClick: () => router.push('/dashboard/audit') },
    { label: 'Manage Users', icon: UserPlus, color: '#8B5CF6', onClick: () => router.push('/dashboard/settings') },
    { label: 'HIS Connections', icon: Link2, color: '#F59E0B', onClick: () => router.push('/dashboard/settings') },
  ];

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'success': return <CheckCircle2 size={14} className="text-green-500" />;
      case 'pending': return <Clock size={14} className="text-amber-500" />;
      case 'warning': return <AlertTriangle size={14} className="text-amber-500" />;
      case 'info': return <Info size={14} className="text-blue-500" />;
      case 'rejected': return <AlertTriangle size={14} className="text-red-500" />;
      default: return null;
    }
  };

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s ease-out' }} className="pb-10">
      {/* Page header */}
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Dashboard Overview</h1>
          <p style={s.pageSubtitle}>Real-time metrics and system health for your AxonBridge platform</p>
        </div>
        <div style={s.headerActions}>
          <button style={s.primaryBtn} onClick={() => router.push('/dashboard/nlp')}>
            <Play size={18} fill="currentColor" /> Start Workflow
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div style={s.statsGrid}>
        {STATS.map((stat, i) => {
          const IconComponent = stat.icon;
          return (
            <div key={i} style={{ ...s.statCard, animationDelay: `${i * 80}ms` }} className="animate-fadeInUp">
              <div style={s.statHeader}>
                <span style={s.statLabel}>{stat.label}</span>
                <span style={{ ...s.statIcon, background: `${stat.color}15`, color: stat.color }}>
                  <IconComponent size={20} />
                </span>
              </div>
              <div style={s.statValue}>{stat.value}</div>
              <div style={{
                ...s.statChange,
                color: stat.changeType === 'up' ? '#16A34A' : stat.changeType === 'down' ? '#DC2626' : 'var(--text-tertiary)',
              }}>
                {stat.changeType === 'up' && '↑ '}
                {stat.changeType === 'down' && '↓ '}
                {stat.change}
              </div>
            </div>
          );
        })}
      </div>

      {/* Main grid: Health + Activity */}
      <div style={s.mainGrid}>
        {/* System Health */}
        <div style={{ ...s.card, animationDelay: '200ms' }} className="animate-fadeInUp">
          <div style={s.cardHeader}>
            <h2 style={s.cardTitle}>System Health</h2>
            <button style={s.refreshBtn}>↻ Refresh</button>
          </div>
          <div style={s.healthList}>
            {HEALTH_SERVICES.map((service, i) => {
              const ServiceIcon = service.icon;
              return (
                <div key={i} style={s.healthRow}>
                  <div style={s.healthLeft}>
                    <div style={{
                      ...s.healthIconWrapper,
                      background: service.status === 'healthy' ? 'var(--color-success-50)' : 'var(--color-warning-50)',
                      color: service.status === 'healthy' ? 'var(--color-success-600)' : 'var(--color-warning-600)',
                      border: `1px solid ${service.status === 'healthy' ? 'var(--color-success-400)' : 'var(--color-warning-400)'}`
                    }}>
                      <ServiceIcon size={14} />
                    </div>
                    <span style={s.healthName}>{service.name}</span>
                  </div>
                  <div style={s.healthRight}>
                    <span style={s.healthLatency}>{service.latency}</span>
                    <span style={{
                      ...s.healthBadge,
                      background: service.status === 'healthy' ? 'var(--color-success-50)' : 'var(--color-warning-50)',
                      color: service.status === 'healthy' ? 'var(--color-success-600)' : 'var(--color-warning-600)',
                      border: `1px solid ${service.status === 'healthy' ? 'var(--color-success-400)' : 'var(--color-warning-400)'}`,
                    }}>
                      {service.uptime}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Activity Feed */}
        <div style={{ ...s.card, animationDelay: '300ms' }} className="animate-fadeInUp">
          <div style={s.cardHeader}>
            <h2 style={s.cardTitle}>Activity Feed</h2>
            <span style={s.liveDot}>
              <span style={s.livePulse} />
              Live
            </span>
          </div>
          <div style={s.activityList} className="custom-scrollbar">
            {ACTIVITY_FEED.map((item, i) => (
              <div key={i} style={s.activityRow}>
                <div style={{
                  ...s.activityIndicator,
                  background: item.type === 'agent' ? 'var(--color-primary-50)' : item.type === 'human' ? 'var(--color-success-50)' : 'var(--bg-tertiary)',
                  color: item.type === 'agent' ? 'var(--color-primary-600)' : item.type === 'human' ? 'var(--color-success-600)' : 'var(--text-secondary)',
                  border: `1px solid ${item.type === 'agent' ? 'var(--color-primary-200)' : item.type === 'human' ? 'var(--color-success-200)' : 'var(--border-secondary)'}`,
                }}>
                  {item.type === 'agent' ? <Bot size={16} /> : item.type === 'human' ? <Users size={16} /> : <Server size={16} />}
                </div>
                <div style={s.activityContent}>
                  <div style={s.activityTop}>
                    <span style={s.activityActor}>{item.actor}</span>
                    <span style={s.activityTime}>{item.time}</span>
                  </div>
                  <p style={s.activityAction}>{item.action}</p>
                </div>
                <div style={{
                  ...s.activityStatus,
                  background: item.status === 'success' ? 'var(--color-success-50)' : item.status === 'pending' ? 'var(--color-warning-50)' : item.status === 'warning' ? 'var(--color-warning-50)' : item.status === 'rejected' ? 'var(--color-danger-50)' : 'var(--color-primary-50)',
                  color: item.status === 'success' ? 'var(--color-success-600)' : item.status === 'pending' ? 'var(--color-warning-600)' : item.status === 'warning' ? 'var(--color-warning-600)' : item.status === 'rejected' ? 'var(--color-danger-600)' : 'var(--color-primary-600)',
                  border: `1px solid ${item.status === 'success' ? 'var(--color-success-200)' : item.status === 'pending' ? 'var(--color-warning-200)' : item.status === 'warning' ? 'var(--color-warning-200)' : item.status === 'rejected' ? 'var(--color-danger-200)' : 'var(--color-primary-200)'}`,
                }}>
                  {getStatusIcon(item.status)}
                  <span style={{textTransform: 'capitalize'}}>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ ...s.quickActionsSection, animationDelay: '400ms' }} className="animate-fadeInUp">
        <h2 style={{ ...s.cardTitle, marginBottom: '1.25rem' }}>Quick Actions</h2>
        <div style={s.quickActionsGrid}>
          {QUICK_ACTIONS.map((action, i) => {
            const ActionIcon = action.icon;
            return (
              <button key={i} style={s.quickActionCard} onClick={action.onClick} className="group hover:border-blue-300 hover:shadow-md">
                <div style={{...s.quickActionIconWrapper, background: `${action.color}15`, color: action.color}} className="group-hover:scale-110 transition-transform">
                  <ActionIcon size={24} />
                </div>
                <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>{action.label}</span>
                <ChevronRight size={16} className="text-slate-400 mt-2 opacity-0 group-hover:opacity-100 transition-opacity translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300" />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem',
  },
  pageTitle: {
    fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em',
  },
  pageSubtitle: {
    fontSize: '1rem', color: 'var(--text-secondary)', marginTop: '0.25rem', fontWeight: 500,
  },
  headerActions: { display: 'flex', gap: '0.75rem' },
  primaryBtn: {
    display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1.5rem',
    borderRadius: '0.75rem', border: 'none', background: 'linear-gradient(135deg, #2563EB, #0891B2)',
    color: 'white', fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)', transition: 'transform 0.2s, box-shadow 0.2s',
  },
  statsGrid: {
    display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem', marginBottom: '2rem',
  },
  statCard: {
    padding: '1.5rem', borderRadius: '1rem', background: 'var(--bg-card)',
    border: '1px solid var(--border-primary)', transition: 'transform 0.2s, box-shadow 0.2s',
    animation: 'fadeInUp 0.5s ease-out forwards', opacity: 0,
    boxShadow: 'var(--shadow-sm)',
  },
  statHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem',
  },
  statLabel: { fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' as const, letterSpacing: '0.05em' },
  statIcon: { width: '40px', height: '40px', borderRadius: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  statValue: { fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em', lineHeight: 1.1 },
  statChange: { fontSize: '0.85rem', fontWeight: 600, marginTop: '0.75rem' },
  mainGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' },
  card: {
    borderRadius: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)',
    overflow: 'hidden', boxShadow: 'var(--shadow-sm)',
  },
  cardHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-primary)',
    background: 'var(--bg-tertiary)',
  },
  cardTitle: { fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' },
  refreshBtn: {
    fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.35rem 0.75rem',
    borderRadius: '0.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)',
    transition: 'background 0.2s',
  },
  healthList: { padding: '0.5rem 0' },
  healthRow: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '0.85rem 1.5rem', transition: 'background 0.2s',
    borderBottom: '1px solid var(--border-primary)',
  },
  healthLeft: { display: 'flex', alignItems: 'center', gap: '1rem' },
  healthIconWrapper: { width: '28px', height: '28px', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  healthName: { fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' },
  healthRight: { display: 'flex', alignItems: 'center', gap: '1rem' },
  healthLatency: { fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', fontWeight: 500 },
  healthBadge: {
    fontSize: '0.75rem', fontWeight: 600, padding: '0.2rem 0.6rem', borderRadius: '9999px',
  },
  liveDot: {
    display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem',
    color: '#16A34A', fontWeight: 700,
  },
  livePulse: {
    width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E',
    animation: 'pulse 2s infinite', display: 'inline-block',
  },
  activityList: { maxHeight: '420px', overflowY: 'auto' as const },
  activityRow: {
    display: 'flex', alignItems: 'flex-start', gap: '1rem',
    padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-primary)',
    transition: 'background 0.2s',
  },
  activityIndicator: {
    width: '36px', height: '36px', borderRadius: '0.75rem', display: 'flex',
    alignItems: 'center', justifyContent: 'center', flexShrink: 0,
  },
  activityContent: { flex: 1, minWidth: 0 },
  activityTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' },
  activityActor: { fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' },
  activityTime: { fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 500 },
  activityAction: { fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, fontWeight: 500 },
  activityStatus: {
    display: 'flex', alignItems: 'center', gap: '0.3rem',
    fontSize: '0.75rem', fontWeight: 600, padding: '0.25rem 0.75rem', borderRadius: '9999px',
    flexShrink: 0, marginTop: '0.25rem',
  },
  quickActionsSection: { marginTop: '1rem' },
  quickActionsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' },
  quickActionCard: {
    display: 'flex', flexDirection: 'column' as const, alignItems: 'center', justifyContent: 'center',
    gap: '0.75rem', padding: '1.75rem', borderRadius: '1rem', background: 'var(--bg-card)',
    border: '1px solid var(--border-primary)', cursor: 'pointer', transition: 'all 0.2s',
    boxShadow: 'var(--shadow-sm)',
  },
  quickActionIconWrapper: {
    width: '56px', height: '56px', borderRadius: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
};
