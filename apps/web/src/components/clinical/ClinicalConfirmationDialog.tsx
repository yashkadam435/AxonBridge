import React, { useState } from 'react';
import { Shield, CheckCircle, XCircle, Edit3 } from 'lucide-react';
import { ConfidenceIndicator } from './ConfidenceIndicator';

export function ClinicalConfirmationDialog({ data, onAccept, onReject, onModify }: any) {
  const [reason, setReason] = useState('');
  
  if (!data) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(15, 23, 42, 0.7)', zIndex: 1000,
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{
        background: 'white', borderRadius: '1rem', width: '100%', maxWidth: '600px',
        overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)'
      }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.25rem' }}>
            <Shield className="text-blue-600" />
            Review Clinical Data
          </h2>
          <ConfidenceIndicator score={data.confidence || 0.85} size="sm" />
        </div>
        
        <div style={{ padding: '1.5rem', background: '#F8FAFC' }}>
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '0.5rem', padding: '1rem' }}>
            <h4 style={{ margin: '0 0 1rem', color: '#64748B' }}>Proposed Entry</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
              <div style={{ fontWeight: 600 }}>Field</div>
              <div style={{ fontWeight: 600 }}>Value</div>
              {Object.entries(data.fields || {}).map(([key, val]: any) => (
                <React.Fragment key={key}>
                  <div style={{ color: '#475569' }}>{key}</div>
                  <div style={{ background: '#FEF9C3', padding: '0.2rem 0.5rem', borderRadius: '0.25rem', display: 'inline-block' }}>{val}</div>
                </React.Fragment>
              ))}
            </div>
          </div>
          
          <div style={{ marginTop: '1.5rem' }}>
            <input 
              type="text" 
              placeholder="Reason for rejection/modification (optional)"
              value={reason}
              onChange={e => setReason(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #CBD5E1' }}
            />
          </div>
        </div>

        <div style={{ padding: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end', background: 'white' }}>
          <button 
            onClick={() => onReject(reason)}
            style={{ padding: '0.75rem 1.5rem', background: '#FEF2F2', color: '#DC2626', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', display: 'flex', gap: '0.5rem', fontWeight: 600 }}
          >
            <XCircle size={20} /> Reject
          </button>
          <button 
            onClick={() => onModify(data.fields)}
            style={{ padding: '0.75rem 1.5rem', background: '#EFF6FF', color: '#2563EB', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', display: 'flex', gap: '0.5rem', fontWeight: 600 }}
          >
            <Edit3 size={20} /> Modify
          </button>
          <button 
            onClick={() => onAccept(data.fields)}
            style={{ padding: '0.75rem 1.5rem', background: '#22C55E', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', display: 'flex', gap: '0.5rem', fontWeight: 600 }}
          >
            <CheckCircle size={20} /> Accept & Submit
          </button>
        </div>
      </div>
    </div>
  );
}
