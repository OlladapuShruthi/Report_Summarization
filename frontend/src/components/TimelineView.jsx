import React from 'react';
import { Calendar, ChevronRight, FileText, Clock, UserCheck, Activity } from 'lucide-react';

export function TimelineView({ timeline, activePatient, onViewResult }) {
  const patientName = activePatient?.display_name || activePatient?.name || 'Selected Patient';

  const reports = timeline?.reports || [];
  const findingEvents = timeline?.finding_events || [];
  const humanConfirmations = timeline?.human_confirmations || [];

  // Build unified chronological timeline items
  const unifiedEvents = [];

  // 1. Report events
  for (const rep of reports) {
    unifiedEvents.push({
      id: rep.analysis_id,
      date: rep.date || rep.created_at,
      type: 'REPORT',
      badge: 'OBJECTIVE EVIDENCE',
      badgeClass: 'badge-status-normal',
      title: rep.title || rep.report_type || 'Clinical Report',
      details: `Status: ${rep.status || 'PARSED'}`,
      comparisons: rep.comparison_context?.comparisons || [],
      analysis_id: rep.analysis_id,
    });
  }

  // 2. Finding Events (detailed lab measurements)
  for (const fe of findingEvents) {
    unifiedEvents.push({
      id: `${fe.analysis_id}_${fe.finding_id}_${fe.date}`,
      date: fe.date || fe.created_at,
      type: 'FINDING_EVENT',
      badge: 'OBJECTIVE EVIDENCE',
      badgeClass: 'badge-status-normal',
      title: `${fe.test_name}: ${fe.value} ${fe.unit || ''}`,
      details: `Status: ${fe.status || 'NORMAL'} • Reference: ${fe.reference_range || 'N/A'}`,
      analysis_id: fe.analysis_id,
    });
  }

  // 3. Human Confirmation events (patient reported information)
  for (const hc of humanConfirmations) {
    unifiedEvents.push({
      id: hc.confirmation_id || `${hc.analysis_id}_${hc.question_id}`,
      date: hc.created_at,
      type: 'HUMAN_CONFIRMATION',
      badge: 'PATIENT-REPORTED INFORMATION',
      badgeClass: 'badge-status-improving',
      title: hc.response ? `Patient reported: "${hc.response}"` : `Patient response: ${hc.action}`,
      details: `Action: ${hc.action} • Question ID: ${hc.question_id}`,
      analysis_id: hc.analysis_id,
    });
  }

  // Sort chronologically (oldest first or newest first)
  unifiedEvents.sort((a, b) => {
    const da = a.date ? new Date(a.date).getTime() : 0;
    const db = b.date ? new Date(b.date).getTime() : 0;
    return db - da; // newest first
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Patient Timeline</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
            Chronological longitudinal history for <strong>{patientName}</strong>
          </p>
        </div>
      </div>

      {/* Timeline Vertical Stack */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {unifiedEvents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#64748b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={32} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>No Medical History Recorded</h3>
              <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '420px' }}>
                There are no timeline events recorded for {patientName}. Upload a medical report to start building this patient's longitudinal timeline.
              </p>
            </div>
          </div>
        ) : (
          unifiedEvents.map((evt, idx) => (
            <div
              key={evt.id || idx}
              onClick={() => evt.analysis_id && onViewResult && onViewResult(evt.analysis_id)}
              style={{
                padding: '16px',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                backgroundColor: evt.type === 'HUMAN_CONFIRMATION' ? '#fff7ed' : '#f8fafc',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: evt.analysis_id ? 'pointer' : 'default',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '10px',
                    backgroundColor: evt.type === 'HUMAN_CONFIRMATION' ? '#ffedd5' : '#eff6ff',
                    color: evt.type === 'HUMAN_CONFIRMATION' ? '#c2410c' : '#2563eb',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {evt.type === 'HUMAN_CONFIRMATION' ? <UserCheck size={20} /> : <FileText size={20} />}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '2px' }}>
                    <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: '500' }}>
                      {evt.date ? new Date(evt.date).toLocaleDateString() : 'Date unavailable'}
                    </span>
                    <span
                      className="badge"
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: '700',
                        padding: '2px 8px',
                        backgroundColor: evt.type === 'HUMAN_CONFIRMATION' ? '#fed7aa' : '#dbeafe',
                        color: evt.type === 'HUMAN_CONFIRMATION' ? '#9a3412' : '#1e40af',
                      }}
                    >
                      {evt.badge}
                    </span>
                  </div>
                  <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.98rem' }}>
                    {evt.title}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#475569' }}>
                    {evt.details}
                  </div>
                </div>
              </div>
              {evt.analysis_id && <ChevronRight size={20} color="#94a3b8" />}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TimelineView;
