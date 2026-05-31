import React from 'react';

interface Props {
  score: number; // 0 to 1
  size?: 'sm' | 'md' | 'lg';
}

export function ConfidenceIndicator({ score, size = 'md' }: Props) {
  const percent = Math.round(score * 100);
  
  let color = '#22c55e'; // Green
  if (score < 0.7) color = '#ef4444'; // Red
  else if (score < 0.9) color = '#f59e0b'; // Amber

  const dimensions = {
    sm: { w: 24, stroke: 2, font: '0.6rem' },
    md: { w: 40, stroke: 3, font: '0.8rem' },
    lg: { w: 64, stroke: 4, font: '1.2rem' }
  }[size];

  const radius = (dimensions.w - dimensions.stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score * circumference);

  return (
    <div style={{ position: 'relative', width: dimensions.w, height: dimensions.w }} title={`AI Confidence: ${percent}%`}>
      <svg width={dimensions.w} height={dimensions.w} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={dimensions.w / 2}
          cy={dimensions.w / 2}
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={dimensions.stroke}
        />
        <circle
          cx={dimensions.w / 2}
          cy={dimensions.w / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={dimensions.stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: dimensions.font, fontWeight: 'bold', color: 'var(--text-secondary)'
      }}>
        {percent}%
      </div>
    </div>
  );
}
