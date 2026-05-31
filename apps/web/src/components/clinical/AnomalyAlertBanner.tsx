import React, { useState } from 'react';
import { AlertOctagon, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';

export function AnomalyAlertBanner({ anomalies = [] }: { anomalies: any[] }) {
  const [expanded, setExpanded] = useState(false);
  
  if (!anomalies || anomalies.length === 0) return null;
  
  const criticalCount = anomalies.filter(a => a.severity === 'critical').length;
  
  return (
    <div style={{
      background: criticalCount > 0 ? '#FEF2F2' : '#FFFBEB',
      borderBottom: `1px solid ${criticalCount > 0 ? '#FCA5A5' : '#FCD34D'}`,
      padding: '0.75rem 1.5rem',
      width: '100%'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertOctagon size={24} color={criticalCount > 0 ? '#DC2626' : '#D97706'} />
          <span style={{ fontWeight: 600, color: criticalCount > 0 ? '#991B1B' : '#92400E' }}>
            {anomalies.length} clinical {anomalies.length === 1 ? 'anomaly' : 'anomalies'} detected in current encounter
          </span>
        </div>
        <button 
          onClick={() => setExpanded(!expanded)}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
        >
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>
      
      {expanded && (
        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {anomalies.map((a, i) => (
            <div key={i} style={{ 
              background: 'white', padding: '1rem', borderRadius: '0.5rem',
              border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <p style={{ margin: 0, fontWeight: 600 }}>{a.title || `Abnormal ${a.field}`}</p>
                <p style={{ margin: '0.25rem 0 0', fontSize: '0.9rem', color: '#64748B' }}>{a.message || a.description}</p>
                <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', fontWeight: 600, color: '#0F172A' }}>Action: {a.suggested_action}</p>
              </div>
              <button style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                background: '#F1F5F9', border: '1px solid #CBD5E1', padding: '0.5rem 1rem',
                borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 500
              }}>
                <CheckCircle size={16} className="text-green-600" /> Acknowledge
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
