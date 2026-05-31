'use client';

import React, { useState, useEffect } from 'react';
import { 
  Home, 
  Activity, 
  MonitorPlay, 
  FileText, 
  ShieldCheck, 
  PieChart, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  Bell, 
  Search, 
  User, 
  Sun, 
  Moon,
  Mic
} from 'lucide-react';

/* ================================================================
   AxonBridge — Dashboard Layout
   Sidebar + Header + Main Content with real-time indicators
   ================================================================ */

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, href: '/dashboard' },
  { id: 'nlp', label: 'Clinical Dictation', icon: Mic, href: '/dashboard/nlp' },
  { id: 'workflows', label: 'Workflows', icon: Activity, href: '/dashboard/workflows' },
  { id: 'agents', label: 'Agent Monitor', icon: MonitorPlay, href: '/dashboard/agents' },
  { id: 'clinical', label: 'Clinical Docs', icon: FileText, href: '/dashboard/clinical' },
  { id: 'audit', label: 'Audit Logs', icon: ShieldCheck, href: '/dashboard/audit' },
  { id: 'analytics', label: 'Analytics', icon: PieChart, href: '/dashboard/analytics' },
  { id: 'settings', label: 'Settings', icon: Settings, href: '/dashboard/settings' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeNav, setActiveNav] = useState('dashboard');
  const [theme, setTheme] = useState<'dark' | 'light'>('light'); // Default to light theme
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
      }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Detect active page from URL
  useEffect(() => {
    const path = window.location.pathname;
    const match = NAV_ITEMS.find(item => path === item.href || (item.id !== 'dashboard' && path.startsWith(item.href)));
    if (match) setActiveNav(match.id);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('axb_access_token');
    localStorage.removeItem('axb_refresh_token');
    window.location.href = '/';
  };

  return (
    <div style={layoutStyles.wrapper}>
      {/* Sidebar */}
      <aside style={{
        ...layoutStyles.sidebar,
        width: sidebarCollapsed ? '76px' : '280px',
      }}>
        <div style={layoutStyles.sidebarHeader}>
          <div style={layoutStyles.sidebarLogo}>
            <svg width="38" height="38" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#sideLogoGrad)" />
              <path d="M14 24L22 16L30 24L22 32Z" fill="white" opacity="0.9" />
              <defs>
                <linearGradient id="sideLogoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stopColor="#3B82F6" /><stop offset="1" stopColor="#06B6D4" />
                </linearGradient>
              </defs>
            </svg>
            {!sidebarCollapsed && (
              <span style={layoutStyles.sidebarTitle}>AxonBridge</span>
            )}
          </div>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            style={layoutStyles.collapseBtn}
            aria-label="Toggle sidebar"
            className="hover:bg-slate-700 hover:text-white"
          >
            {sidebarCollapsed ? <Menu size={22} /> : <X size={22} />}
          </button>
        </div>

        {/* Navigation */}
        <nav style={layoutStyles.nav}>
          {NAV_ITEMS.map(item => {
            const IconComponent = item.icon;
            const isActive = activeNav === item.id;
            return (
              <a
                key={item.id}
                href={item.href}
                onClick={(e) => { e.preventDefault(); setActiveNav(item.id); window.location.href = item.href; }}
                style={{
                  ...layoutStyles.navItem,
                  ...(isActive ? layoutStyles.navItemActive : {}),
                  justifyContent: sidebarCollapsed ? 'center' : 'flex-start'
                }}
                className={isActive ? "" : "hover:bg-slate-800 hover:text-slate-200 transition-all group"}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <IconComponent size={24} className={isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200 transition-colors'} />
                {!sidebarCollapsed && <span style={isActive ? { color: '#ffffff', fontWeight: 700 } : { fontWeight: 600 }}>{item.label}</span>}
              </a>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div style={layoutStyles.sidebarFooter}>
          <button 
            onClick={handleLogout} 
            style={{...layoutStyles.navItem, justifyContent: sidebarCollapsed ? 'center' : 'flex-start'}} 
            className="hover:bg-red-500/20 hover:text-red-400 transition-all group"
            title="Logout"
          >
            <LogOut size={24} className="text-slate-400 group-hover:text-red-400 transition-colors" />
            {!sidebarCollapsed && <span style={{ fontWeight: 600 }}>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div style={{
        ...layoutStyles.mainArea,
        marginLeft: sidebarCollapsed ? '76px' : '280px',
      }}>
        {/* Header */}
        <header style={layoutStyles.header}>
          <div style={layoutStyles.headerLeft}>
            <div style={layoutStyles.searchBox}>
              <Search size={16} className="text-slate-400" />
              <input
                type="text"
                placeholder="Search workflows, agents, logs..."
                style={layoutStyles.searchInput}
              />
            </div>
          </div>

          <div style={layoutStyles.headerRight}>
            {/* Live clock */}
            <span style={layoutStyles.clock}>{currentTime}</span>

            {/* System status */}
            <div style={layoutStyles.statusIndicator}>
              <span className="status-dot active" style={{ width: 8, height: 8, borderRadius: '50%', background: '#22C55E', display: 'inline-block' }} />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>System OK</span>
            </div>

            {/* Theme toggle */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              style={layoutStyles.iconBtn}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Notifications */}
            <button style={layoutStyles.iconBtn} aria-label="Notifications">
              <Bell size={20} />
              <span style={layoutStyles.notifDot} />
            </button>

            {/* User avatar */}
            <div style={layoutStyles.avatar}>
              <User size={20} />
            </div>
          </div>
        </header>

        {/* Content */}
        <main style={layoutStyles.content}>
          {children}
        </main>
      </div>
    </div>
  );
}

const layoutStyles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    minHeight: '100vh',
    background: 'var(--bg-primary)',
  },
  sidebar: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    height: '100vh',
    background: '#0F172A', // Slate 900 for extremely high contrast
    borderRight: '1px solid #1E293B',
    display: 'flex',
    flexDirection: 'column' as const,
    transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: 50,
    overflow: 'hidden',
    boxShadow: '4px 0 15px rgba(0,0,0,0.1)',
  },
  sidebarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1.75rem 1.25rem',
    borderBottom: '1px solid #1E293B', // Slate 800
  },
  sidebarLogo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.85rem',
    minWidth: 0,
  },
  sidebarTitle: {
    fontSize: '1.5rem',
    fontWeight: 800,
    color: '#F8FAFC', // Slate 50
    whiteSpace: 'nowrap' as const,
    letterSpacing: '-0.02em',
  },
  collapseBtn: {
    background: '#1E293B', // Slate 800
    border: '1px solid #334155', // Slate 700
    color: '#94A3B8', // Slate 400
    cursor: 'pointer',
    padding: '0.6rem',
    borderRadius: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    transition: 'background 0.2s, color 0.2s',
  },
  nav: {
    flex: 1,
    padding: '1.5rem 1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
    overflowY: 'auto' as const,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '0.85rem 1.15rem',
    borderRadius: '0.75rem',
    color: '#94A3B8', // Slate 400
    fontSize: '1.05rem',
    fontWeight: 600,
    textDecoration: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease-in-out',
    border: 'none',
    background: 'transparent',
    width: '100%',
    whiteSpace: 'nowrap' as const,
  },
  navItemActive: {
    background: 'linear-gradient(135deg, #2563EB, #0891B2)', // Deep Blue/Cyan gradient
    color: '#ffffff',
    boxShadow: '0 4px 15px rgba(37, 99, 235, 0.4)',
    border: 'none',
  },
  sidebarFooter: {
    padding: '1.25rem',
    borderTop: '1px solid #1E293B', // Slate 800
  },
  mainArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
    transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    minHeight: '100vh',
  },
  header: {
    height: '72px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 2rem',
    borderBottom: '1px solid var(--border-primary)',
    background: 'var(--bg-secondary)',
    position: 'sticky' as const,
    top: 0,
    zIndex: 40,
    boxShadow: 'var(--shadow-sm)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    flex: 1,
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.65rem 1rem',
    borderRadius: '0.75rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border-primary)',
    maxWidth: '480px',
    width: '100%',
    color: 'var(--text-tertiary)',
    transition: 'border 0.2s',
  },
  searchInput: {
    border: 'none',
    background: 'transparent',
    outline: 'none',
    color: 'var(--text-primary)',
    fontSize: '0.95rem',
    width: '100%',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.25rem',
  },
  clock: {
    fontSize: '0.9rem',
    fontFamily: 'var(--font-mono)',
    color: 'var(--text-secondary)',
    fontWeight: 500,
    paddingRight: '0.5rem',
    borderRight: '1px solid var(--border-primary)',
  },
  statusIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.4rem 1rem',
    borderRadius: '9999px',
    background: 'var(--color-success-50)',
    border: '1px solid var(--color-success-400)',
    marginRight: '0.5rem',
  },
  iconBtn: {
    position: 'relative' as const,
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border-primary)',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
    padding: '0.65rem',
    borderRadius: '0.75rem',
    display: 'flex',
    alignItems: 'center',
    transition: 'background 0.2s, color 0.2s, border 0.2s',
  },
  notifDot: {
    position: 'absolute' as const,
    top: '8px',
    right: '8px',
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'var(--color-danger-500)',
    border: '2px solid var(--bg-tertiary)',
  },
  avatar: {
    width: '42px',
    height: '42px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #2563EB, #0891B2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    cursor: 'pointer',
    boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)',
  },
  content: {
    flex: 1,
    padding: '2rem',
    overflowY: 'auto' as const,
  },
};
