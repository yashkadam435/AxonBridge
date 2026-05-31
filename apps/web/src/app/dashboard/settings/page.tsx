'use client';

import React, { useState, useEffect } from 'react';

/* ================================================================
   AxonBridge — Settings
   ================================================================ */

const SECTIONS = ['General', 'HIS Connections', 'Security', 'Languages', 'Notifications'];

export default function SettingsPage() {
  const [mounted, setMounted] = useState(false);
  const [activeSection, setActiveSection] = useState('General');
  const [tenantName, setTenantName] = useState('City General Hospital');
  const [complianceRegion, setComplianceRegion] = useState('us');
  const [mfaRequired, setMfaRequired] = useState(true);
  const [sessionTimeout, setSessionTimeout] = useState('30');
  const [autoBackup, setAutoBackup] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.5s' }}>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Settings</h1>
          <p style={s.pageSubtitle}>System configuration and tenant preferences</p>
        </div>
        <button onClick={handleSave} style={s.saveBtn}>
          {saved ? '✓ Saved' : 'Save Changes'}
        </button>
      </div>

      <div style={s.layout}>
        {/* Section nav */}
        <nav style={s.sectionNav}>
          {SECTIONS.map(sec => (
            <button key={sec} onClick={() => setActiveSection(sec)} style={{ ...s.sectionBtn, ...(activeSection === sec ? s.sectionBtnActive : {}) }}>
              {sec}
            </button>
          ))}
        </nav>

        {/* Settings content */}
        <div style={s.settingsContent}>
          {activeSection === 'General' && (
            <div style={s.section}>
              <h2 style={s.sectionTitle}>General Settings</h2>
              <div style={s.formGroup}>
                <label style={s.label}>Organization Name</label>
                <input type="text" value={tenantName} onChange={e => setTenantName(e.target.value)} style={s.input} />
              </div>
              <div style={s.formGroup}>
                <label style={s.label}>Compliance Region</label>
                <select value={complianceRegion} onChange={e => setComplianceRegion(e.target.value)} style={s.select}>
                  <option value="us">United States (HIPAA)</option>
                  <option value="eu">European Union (GDPR)</option>
                  <option value="in">India (DISHA)</option>
                  <option value="ae">UAE (DHA)</option>
                  <option value="uk">United Kingdom (NHS)</option>
                  <option value="sg">Singapore (PDPA)</option>
                </select>
                <span style={s.helpText}>Determines data residency and compliance rules</span>
              </div>
              <div style={s.formGroup}>
                <label style={s.label}>Automatic Database Backup</label>
                <div style={s.toggleRow}>
                  <button onClick={() => setAutoBackup(!autoBackup)} style={{ ...s.toggle, background: autoBackup ? '#22C55E' : 'var(--bg-tertiary)' }}>
                    <span style={{ ...s.toggleDot, transform: autoBackup ? 'translateX(20px)' : 'translateX(2px)' }} />
                  </button>
                  <span style={s.toggleLabel}>{autoBackup ? 'Enabled' : 'Disabled'}</span>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'Security' && (
            <div style={s.section}>
              <h2 style={s.sectionTitle}>Security Settings</h2>
              <div style={s.formGroup}>
                <label style={s.label}>Require MFA for All Users</label>
                <div style={s.toggleRow}>
                  <button onClick={() => setMfaRequired(!mfaRequired)} style={{ ...s.toggle, background: mfaRequired ? '#22C55E' : 'var(--bg-tertiary)' }}>
                    <span style={{ ...s.toggleDot, transform: mfaRequired ? 'translateX(20px)' : 'translateX(2px)' }} />
                  </button>
                  <span style={s.toggleLabel}>{mfaRequired ? 'Required' : 'Optional'}</span>
                </div>
              </div>
              <div style={s.formGroup}>
                <label style={s.label}>Session Timeout (minutes)</label>
                <input type="number" value={sessionTimeout} onChange={e => setSessionTimeout(e.target.value)} style={{ ...s.input, maxWidth: '120px' }} />
              </div>
              <div style={s.formGroup}>
                <label style={s.label}>Password Policy</label>
                <div style={s.policyList}>
                  {['Minimum 12 characters', 'Uppercase + lowercase required', 'At least 1 number', 'At least 1 special character', 'No reuse of last 5 passwords'].map((p, i) => (
                    <div key={i} style={s.policyItem}>
                      <span style={s.policyCheck}>✓</span>
                      <span style={s.policyText}>{p}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={s.infoBox}>
                <span style={s.infoIcon}>🔐</span>
                <div>
                  <span style={s.infoTitle}>Encryption</span>
                  <span style={s.infoDetail}>AES-256-GCM field-level encryption active. All PHI fields encrypted at rest.</span>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'HIS Connections' && (
            <div style={s.section}>
              <h2 style={s.sectionTitle}>HIS Connections</h2>
              <p style={s.sectionDesc}>Manage target HIS/EHR systems for browser automation</p>
              {[
                { name: 'eHospital', type: 'web', url: 'https://ehospital.local', status: 'connected' },
                { name: 'Practo', type: 'web', url: 'https://practo.local', status: 'connected' },
              ].map((his, i) => (
                <div key={i} style={s.hisCard}>
                  <div style={s.hisLeft}>
                    <span style={{ ...s.hisDot, background: his.status === 'connected' ? '#22C55E' : '#EF4444' }} />
                    <div>
                      <span style={s.hisName}>{his.name}</span>
                      <span style={s.hisUrl}>{his.url}</span>
                    </div>
                  </div>
                  <span style={s.hisBadge}>{his.type}</span>
                </div>
              ))}
              <button style={s.addHisBtn}>+ Add HIS Connection</button>
            </div>
          )}

          {activeSection === 'Languages' && (
            <div style={s.section}>
              <h2 style={s.sectionTitle}>Language Configuration</h2>
              <p style={s.sectionDesc}>Configure supported languages for STT, TTS, and translation</p>
              <div style={s.langGrid}>
                {[
                  { code: 'en', name: 'English', native: 'English', active: true },
                  { code: 'hi', name: 'Hindi', native: 'हिन्दी', active: true },
                  { code: 'ar', name: 'Arabic', native: 'العربية', active: true },
                  { code: 'es', name: 'Spanish', native: 'Español', active: false },
                  { code: 'fr', name: 'French', native: 'Français', active: false },
                  { code: 'pt', name: 'Portuguese', native: 'Português', active: false },
                ].map((lang, i) => (
                  <div key={i} style={{ ...s.langCard, opacity: lang.active ? 1 : 0.6 }}>
                    <span style={s.langCode}>{lang.code.toUpperCase()}</span>
                    <span style={s.langName}>{lang.name}</span>
                    <span style={s.langNative}>{lang.native}</span>
                    <span style={{ ...s.langStatus, color: lang.active ? '#22C55E' : 'var(--text-tertiary)' }}>
                      {lang.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'Notifications' && (
            <div style={s.section}>
              <h2 style={s.sectionTitle}>Notification Preferences</h2>
              <p style={s.sectionDesc}>Configure how and when you receive alerts</p>
              {[
                { label: 'Agent Errors', desc: 'Get notified when an agent encounters an error', enabled: true },
                { label: 'HITL Requests', desc: 'Alerts for pending human confirmation', enabled: true },
                { label: 'Compliance Alerts', desc: 'Security and compliance violations', enabled: true },
                { label: 'System Health', desc: 'Service degradation or outage alerts', enabled: true },
                { label: 'Workflow Completion', desc: 'Notification when workflows complete', enabled: false },
              ].map((notif, i) => (
                <div key={i} style={s.notifRow}>
                  <div>
                    <span style={s.notifLabel}>{notif.label}</span>
                    <span style={s.notifDesc}>{notif.desc}</span>
                  </div>
                  <div style={{ ...s.toggle, background: notif.enabled ? '#22C55E' : 'var(--bg-tertiary)' }}>
                    <span style={{ ...s.toggleDot, transform: notif.enabled ? 'translateX(20px)' : 'translateX(2px)' }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' },
  pageTitle: { fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' },
  pageSubtitle: { fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' },
  saveBtn: { padding: '0.5rem 1.25rem', borderRadius: '0.5rem', border: 'none', background: 'linear-gradient(135deg, #3B82F6, #2563EB)', color: 'white', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 12px rgba(59,130,246,0.3)' },
  layout: { display: 'grid', gridTemplateColumns: '200px 1fr', gap: '1.5rem' },
  sectionNav: { display: 'flex', flexDirection: 'column' as const, gap: '0.25rem' },
  sectionBtn: { padding: '0.6rem 1rem', borderRadius: '0.5rem', border: 'none', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500, cursor: 'pointer', textAlign: 'left' as const, transition: 'all 0.2s' },
  sectionBtnActive: { background: 'rgba(59,130,246,0.1)', color: '#60A5FA', fontWeight: 600 },
  settingsContent: { minHeight: '400px' },
  section: { padding: '1.5rem', borderRadius: '0.75rem', background: 'var(--bg-card)', border: '1px solid var(--border-primary)' },
  sectionTitle: { fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem' },
  sectionDesc: { fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' },
  formGroup: { marginBottom: '1.25rem' },
  label: { fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.375rem' },
  input: { padding: '0.6rem 0.85rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: '0.875rem', width: '100%', maxWidth: '400px', outline: 'none' },
  select: { padding: '0.6rem 0.85rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: '0.875rem', width: '100%', maxWidth: '400px', outline: 'none' },
  helpText: { fontSize: '0.7rem', color: 'var(--text-tertiary)', marginTop: '0.25rem', display: 'block' },
  toggleRow: { display: 'flex', alignItems: 'center', gap: '0.75rem' },
  toggle: { width: '44px', height: '24px', borderRadius: '12px', border: 'none', cursor: 'pointer', position: 'relative' as const, transition: 'background 0.2s' },
  toggleDot: { width: '20px', height: '20px', borderRadius: '50%', background: 'white', position: 'absolute' as const, top: '2px', transition: 'transform 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' },
  toggleLabel: { fontSize: '0.85rem', color: 'var(--text-primary)' },
  policyList: { display: 'flex', flexDirection: 'column' as const, gap: '0.5rem', marginTop: '0.5rem' },
  policyItem: { display: 'flex', alignItems: 'center', gap: '0.5rem' },
  policyCheck: { color: '#22C55E', fontWeight: 700, fontSize: '0.85rem' },
  policyText: { fontSize: '0.8rem', color: 'var(--text-secondary)' },
  infoBox: { display: 'flex', gap: '0.75rem', padding: '1rem', borderRadius: '0.5rem', background: 'rgba(59,130,246,0.05)', border: '1px solid rgba(59,130,246,0.15)', marginTop: '1rem' },
  infoIcon: { fontSize: '1.25rem' },
  infoTitle: { fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block' },
  infoDetail: { fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem', display: 'block' },
  hisCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', marginBottom: '0.5rem' },
  hisLeft: { display: 'flex', alignItems: 'center', gap: '0.75rem' },
  hisDot: { width: '10px', height: '10px', borderRadius: '50%' },
  hisName: { fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block' },
  hisUrl: { fontSize: '0.7rem', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' },
  hisBadge: { fontSize: '0.65rem', fontWeight: 600, padding: '0.15rem 0.5rem', borderRadius: '9999px', background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', textTransform: 'uppercase' as const },
  addHisBtn: { padding: '0.5rem 1rem', borderRadius: '0.5rem', border: '1px dashed var(--border-secondary)', background: 'transparent', color: 'var(--text-secondary)', fontSize: '0.8rem', cursor: 'pointer', width: '100%', marginTop: '0.5rem' },
  langGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' },
  langCard: { padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border-primary)', textAlign: 'center' as const, transition: 'opacity 0.2s' },
  langCode: { fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', display: 'block', marginBottom: '0.25rem' },
  langName: { fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block' },
  langNative: { fontSize: '0.75rem', color: 'var(--text-tertiary)', display: 'block', marginBottom: '0.35rem' },
  langStatus: { fontSize: '0.65rem', fontWeight: 600 },
  notifRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 0', borderBottom: '1px solid var(--border-primary)' },
  notifLabel: { fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block' },
  notifDesc: { fontSize: '0.75rem', color: 'var(--text-tertiary)', display: 'block', marginTop: '0.15rem' },
};
