import React, { useState } from 'react';
import { Search } from 'lucide-react';

export function FindingsStatusView({ result }) {
  const [activeTab, setActiveTab] = useState('ALL');

  // Extract findings from actual analysis result
  const abnormalFindings = result?.abnormal_findings || [];
  const findingsList = abnormalFindings.map((f) => {
    const rawStatus = f.lifecycle_state || f.lifecycle_status || f.status || 'UNKNOWN';
    const statusUpper = String(rawStatus).toUpperCase().trim();
    return {
      parameter: f.parameter || f.name || f.test_name || 'Lab Parameter',
      current: f.value != null ? `${f.value} ${f.unit || ''}` : (f.current_value != null ? `${f.current_value} ${f.unit || ''}` : '—'),
      status: statusUpper,
      change: f.change_description || (f.previous_value != null ? `${f.previous_value} → ${f.value || f.current_value}` : 'No prior baseline'),
      trend: f.trend || f.lifecycle_state || rawStatus,
    };
  });

  const validStatuses = ['ALL', 'ACTIVE', 'PERSISTENT', 'IMPROVING', 'WORSENED', 'CURRENTLY_NORMAL', 'UNKNOWN'];

  const counts = {
    ALL: findingsList.length,
    ACTIVE: findingsList.filter(f => f.status === 'ACTIVE').length,
    PERSISTENT: findingsList.filter(f => f.status === 'PERSISTENT').length,
    IMPROVING: findingsList.filter(f => f.status === 'IMPROVING').length,
    WORSENED: findingsList.filter(f => f.status === 'WORSENED').length,
    CURRENTLY_NORMAL: findingsList.filter(f => f.status === 'CURRENTLY_NORMAL').length,
    UNKNOWN: findingsList.filter(f => f.status === 'UNKNOWN' || !['ACTIVE', 'PERSISTENT', 'IMPROVING', 'WORSENED', 'CURRENTLY_NORMAL'].includes(f.status)).length,
  };

  const filteredList = activeTab === 'ALL'
    ? findingsList
    : findingsList.filter(f => f.status === activeTab);

  const getStatusBadge = (status) => {
    const s = String(status || '').toUpperCase();
    if (s === 'IMPROVING') return <span className="badge badge-status-improving">IMPROVING</span>;
    if (s === 'WORSENED') return <span className="badge badge-status-persistent" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>WORSENED</span>;
    if (s === 'PERSISTENT') return <span className="badge badge-status-persistent">PERSISTENT</span>;
    if (s === 'CURRENTLY_NORMAL') return <span className="badge badge-status-normal">CURRENTLY NORMAL</span>;
    if (s === 'ACTIVE') return <span className="badge badge-status-persistent">ACTIVE</span>;
    return <span className="badge" style={{ backgroundColor: '#f1f5f9', color: '#475569' }}>UNKNOWN</span>;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Longitudinal Finding Lifecycle</h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
          Backend-verified lifecycle states: ACTIVE, PERSISTENT, IMPROVING, WORSENED, CURRENTLY NORMAL, and UNKNOWN
        </p>
      </div>

      {findingsList.length === 0 ? (
        <div className="card" style={{ padding: '48px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#64748b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Search size={32} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>No Medical Findings Recorded</h3>
            <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '420px' }}>
              There are no analyzed findings recorded for this patient. Upload and analyze a medical report to view clinical findings.
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* Filter Pills Bar */}
          <div className="card" style={{ padding: '16px 20px' }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {validStatuses.map((tab) => (
                <button
                  key={tab}
                  className={`filter-tab ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab.replaceAll('_', ' ')} ({counts[tab] || 0})
                </button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="card">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Parameter</th>
                  <th>Current Value</th>
                  <th>Lifecycle Status</th>
                  <th>Comparison Change</th>
                  <th>Evidence Trend</th>
                </tr>
              </thead>
              <tbody>
                {filteredList.map((item, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: '600', color: '#0f172a' }}>{item.parameter}</td>
                    <td>{item.current}</td>
                    <td>{getStatusBadge(item.status)}</td>
                    <td style={{ fontFamily: 'monospace' }}>{item.change}</td>
                    <td style={{ fontWeight: '600', color: '#2563eb' }}>{item.trend}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default FindingsStatusView;
