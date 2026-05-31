import React from 'react';
import { ListOrdered, Percent, Plus } from 'lucide-react';

export function DifferentialDiagnosis({ differentials }: { differentials: any[] }) {
  if (!differentials || differentials.length === 0) return null;

  return (
    <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '0.75rem', overflow: 'hidden' }}>
      <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #E2E8F0', background: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <ListOrdered className="text-blue-600" size={20} />
        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Differential Diagnoses</h3>
      </div>
      
      <div style={{ padding: '1rem' }}>
        {differentials.map((diff, idx) => {
          const probColor = diff.probability === 'High' ? '#DC2626' : diff.probability === 'Medium' ? '#D97706' : '#2563EB';
          
          return (
            <div key={idx} style={{ padding: '1rem', border: '1px solid #E2E8F0', borderRadius: '0.5rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h4 style={{ margin: 0, fontSize: '1.1rem', color: '#0F172A' }}>{diff.diagnosis}</h4>
                <span style={{ 
                  background: `${probColor}20`, color: probColor, 
                  padding: '0.2rem 0.6rem', borderRadius: '1rem', fontSize: '0.8rem', fontWeight: 600,
                  display: 'flex', alignItems: 'center', gap: '0.25rem'
                }}>
                  <Percent size={14} /> {diff.probability} Probability
                </span>
              </div>
              <p style={{ color: '#475569', fontSize: '0.9rem', margin: '0 0 1rem' }}>{diff.reasoning}</p>
              
              <button style={{
                background: '#F1F5F9', border: '1px solid #CBD5E1', color: '#334155',
                padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500, fontSize: '0.85rem'
              }}>
                <Plus size={16} /> Add to Note
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
