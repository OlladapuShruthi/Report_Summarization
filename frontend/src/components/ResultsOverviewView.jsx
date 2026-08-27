import React from 'react';
import { AlertTriangle, CheckCircle2, Stethoscope, ArrowRight } from 'lucide-react';

export function ResultsOverviewView({ result, onViewFullDetails, onOpenExport }) {
  const summaryText = result?.summary_report || 
    "Your report shows some values outside the normal range. Please review the details and consult your physician.";

  const riskLevel = result?.risk_assessment?.risk_level || 'Moderate';
  const riskScore = result?.risk_assessment?.risk_score || 6;
  const abnormalCount = result?.abnormal_findings?.length || 3;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Screen 8 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>CBC Report - 26 May 2025</h1>
        <button className="btn-primary" onClick={onViewFullDetails}>
          View Full Results <ArrowRight size={16} />
        </button>
      </div>

      {/* 3 Metric Cards matching Wireframe Box 8 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {/* Card 1: Overall Risk */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Overall Risk</span>
          <div>
            <span style={{ fontSize: '2rem', fontWeight: '700', color: '#c2410c' }}>{riskLevel}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', color: '#64748b', borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
            <span>Risk Score</span>
            <span style={{ fontWeight: '700', color: '#0f172a' }}>{riskScore}/10</span>
          </div>
        </div>

        {/* Card 2: Key Findings */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Key Findings</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#b91c1c' }}>
              <AlertTriangle size={20} />
              <span style={{ fontSize: '1.25rem', fontWeight: '700' }}>{abnormalCount}</span>
              <span style={{ fontSize: '0.85rem' }}>Abnormal</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#15803d' }}>
              <CheckCircle2 size={20} />
              <span style={{ fontSize: '1.25rem', fontWeight: '700' }}>8</span>
              <span style={{ fontSize: '0.85rem' }}>Normal</span>
            </div>
          </div>
        </div>

        {/* Card 3: Recommendation */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Recommendation</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#15803d' }}>
            <Stethoscope size={24} />
            <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>Consult Physician Recommended</span>
          </div>
          <div style={{ marginTop: 'auto', textAlign: 'right' }}>
            <button className="btn-outline-blue" onClick={onViewFullDetails} style={{ padding: '4px 12px', fontSize: '0.8rem' }}>
              View Details
            </button>
          </div>
        </div>
      </div>

      {/* Quick Summary Card matching Wireframe Box 8 */}
      <div className="card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a', marginBottom: '12px' }}>Quick Summary</h3>
        <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: '1.6' }}>{summaryText}</p>
        <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #e2e8f0', fontSize: '0.78rem', color: '#94a3b8' }}>
          Generated on 26 May 2025 • 10:35 AM
        </div>
      </div>
    </div>
  );
}

export default ResultsOverviewView;
