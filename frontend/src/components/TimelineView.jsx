import React from 'react';
import { Calendar, ChevronRight, FileText } from 'lucide-react';

export function TimelineView({ timeline, activePatient, onViewResult }) {
  const events = [
    { date: '26 May 2025', title: 'CBC Report', details: '3 Abnormal • Risk: Moderate', risk: 'Moderate', id: '1' },
    { date: '02 May 2025', title: 'Lipid Profile', details: '2 Abnormal • Risk: Low', risk: 'Low', id: '2' },
    { date: '25 Apr 2025', title: 'Thyroid Profile', details: 'All Normal • Risk: Low', risk: 'Low', id: '3' },
    { date: '01 Apr 2025', title: 'Chest X-Ray', details: 'No Issues Detected', risk: 'Low', id: '4' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Box 11 */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Patient Timeline</h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Timeline view of all reports & key events</p>
      </div>

      {/* Filters Bar */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <select style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}>
          <option>All Types</option>
          <option>Lab Reports</option>
          <option>Radiology</option>
        </select>
        <select style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}>
          <option>2025</option>
          <option>2024</option>
        </select>
      </div>

      {/* Timeline Vertical Stack matching Wireframe Box 11 */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {events.map((evt, idx) => (
          <div
            key={idx}
            onClick={() => onViewResult && onViewResult(evt.id)}
            style={{
              padding: '16px',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#f8fafc',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={20} />
              </div>
              <div>
                <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: '500' }}>{evt.date}</span>
                <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '1rem' }}>{evt.title}</div>
                <div style={{ fontSize: '0.82rem', color: '#475569' }}>{evt.details}</div>
              </div>
            </div>
            <ChevronRight size={20} color="#94a3b8" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default TimelineView;
