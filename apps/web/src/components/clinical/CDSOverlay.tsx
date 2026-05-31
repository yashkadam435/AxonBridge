import React, { useState } from 'react';
import { AlertTriangle, Info, CheckCircle, ChevronRight, X } from 'lucide-react';

export function CDSOverlay({ overlayData }: { overlayData: any }) {
  const [collapsed, setCollapsed] = useState(false);

  if (!overlayData || !overlayData.alerts || overlayData.alerts.length === 0) {
    return null;
  }

  if (collapsed) {
    return (
      <div 
        onClick={() => setCollapsed(false)}
        style={{
          position: 'fixed', right: 0, top: '20%', background: 'white',
          padding: '1rem', borderTopLeftRadius: '0.5rem', borderBottomLeftRadius: '0.5rem',
          boxShadow: '-4px 0 15px rgba(0,0,0,0.1)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: '0.5rem', zIndex: 100,
          border: '1px solid #e2e8f0', borderRight: 'none'
        }}
      >
        <AlertTriangle size={20} color="#DC2626" />
        <span style={{ fontWeight: 600 }}>{overlayData.total_alerts} Alerts</span>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed', right: 0, top: 0, bottom: 0, width: '380px',
      background: '#F8FAFC', borderLeft: '1px solid #E2E8F0',
      boxShadow: '-4px 0 25px rgba(0,0,0,0.05)', zIndex: 100,
      display: 'flex', flexDirection: 'column'
    }}>
      <div style={{
        padding: '1.25rem', borderBottom: '1px solid #E2E8F0',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'white'
      }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Info size={20} className="text-blue-500" />
          Clinical Advisory
        </h3>
        <button onClick={() => setCollapsed(true)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
          <ChevronRight size={24} className="text-slate-400" />
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {overlayData.alerts.map((alert: any) => {
          const isEmergency = alert.priority === 'emergency';
          return (
            <div key={alert.id} style={{
              background: 'white', borderRadius: '0.5rem', padding: '1rem',
              borderLeft: `4px solid ${isEmergency ? '#DC2626' : '#3B82F6'}`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <h4 style={{ margin: '0 0 0.5rem', color: isEmergency ? '#DC2626' : '#0F172A' }}>{alert.title}</h4>
                <span style={{ fontSize: '0.75rem', background: '#F1F5F9', padding: '0.2rem 0.5rem', borderRadius: '1rem' }}>
                  {alert.source}
                </span>
              </div>
              <p style={{ fontSize: '0.9rem', color: '#475569', margin: '0 0 1rem' }}>{alert.description}</p>
              
              {alert.actions && alert.actions.map((action: any, idx: number) => (
                <button key={idx} style={{
                  width: '100%', padding: '0.5rem', background: '#EFF6FF',
                  color: '#1D4ED8', border: '1px solid #BFDBFE', borderRadius: '0.25rem',
                  fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: '0.5rem'
                }}>
                  <CheckCircle size={16} /> {action.label}
                </button>
              ))}
            </div>
          )
        })}
      </div>
    </div>
  );
}
