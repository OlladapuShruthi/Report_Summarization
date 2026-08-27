import React from 'react';
import { Check, ArrowRight, FileText, Cpu, Clock, Loader } from 'lucide-react';

export function ProcessingView({ onComplete }) {
  const steps = [
    { label: 'Report uploaded', status: 'completed' },
    { label: 'Extracting text', status: 'completed' },
    { label: 'Parsing medical values', status: 'completed' },
    { label: 'Detecting abnormalities', status: 'completed' },
    { label: 'Comparing previous reports', status: 'active' },
    { label: 'Assessing risk', status: 'pending' },
    { label: 'Generating explanation', status: 'pending' },
    { label: 'Validating result', status: 'pending' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '840px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '32px' }}>
        {/* Title matching Item 8 in User Request */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>Analyzing Rahul's Report</h1>
          <p style={{ fontSize: '0.88rem', color: '#64748b', marginTop: '2px' }}>LangGraph Multi-Agent Pipeline Execution</p>
        </div>

        {/* Live Staged Progress List matching Item 8 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '32px' }}>
          {steps.map((step, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.95rem' }}>
              {step.status === 'completed' && (
                <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#dcfce7', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Check size={14} />
                </div>
              )}
              {step.status === 'active' && (
                <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Loader size={14} className="spin-icon" />
                </div>
              )}
              {step.status === 'pending' && (
                <div style={{ width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #cbd5e1' }} />
              )}
              <span style={{ fontWeight: step.status === 'active' ? '600' : '500', color: step.status === 'completed' ? '#15803d' : (step.status === 'active' ? '#2563eb' : '#94a3b8') }}>
                {step.label}
              </span>
              {step.status === 'active' && <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#2563eb', fontWeight: '600' }}>In Progress...</span>}
            </div>
          ))}
        </div>

        {/* Progress Bar */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.88rem', fontWeight: '600' }}>
            <span style={{ color: '#0f172a' }}>Comparing previous reports</span>
            <span style={{ color: '#2563eb' }}>62%</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ width: '62%', height: '100%', backgroundColor: '#2563eb', borderRadius: '99px' }} />
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
          <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Processing report stages...</span>
          <button className="btn-primary" onClick={onComplete}>
            View Results Dashboard <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProcessingView;
