import React, { useState } from 'react';
import { TrendingUp, ArrowRight } from 'lucide-react';

export function FindingsStatusView({ result }) {
  const [activeTab, setActiveTab] = useState('All');

  const findingsList = [
    { parameter: 'Hemoglobin (Hb)', current: '12.4 g/dL', status: 'Improving', change: '10.2 → 12.4', trend: '↗', category: 'Improving' },
    { parameter: 'RBC Count', current: '4.2 million/uL', status: 'Persistent', change: '4.1 → 4.2', trend: '↗', category: 'Persistent' },
    { parameter: 'Hematocrit (HCT)', current: '39 %', status: 'Improving', change: '34 → 39', trend: '↗', category: 'Improving' },
    { parameter: 'MCV', current: '82 fL', status: 'Resolved', change: '78 → 82', trend: '↗', category: 'Resolved' },
    { parameter: 'WBC Count', current: '7,600 /uL', status: 'Normal', change: 'Normal', trend: '—', category: 'Normal' },
  ];

  const counts = {
    All: 11,
    New: 1,
    Persistent: 2,
    Improving: 3,
    Resolved: 1,
    Normal: 4,
  };

  const getStatusBadge = (status) => {
    if (status === 'Improving') return <span className="badge badge-status-improving">Improving</span>;
    if (status === 'Persistent') return <span className="badge badge-status-persistent">Persistent</span>;
    if (status === 'Resolved') return <span className="badge badge-status-resolved">Resolved</span>;
    return <span className="badge badge-status-normal">Normal</span>;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Box 10 */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Findings Status (New / Persistent / Resolved)</h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>AI identifies how each finding is changing</p>
      </div>

      {/* Filter Pills Bar matching Wireframe Box 10 */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { key: 'All', label: `All (${counts.All})` },
            { key: 'New', label: `New (${counts.New})` },
            { key: 'Persistent', label: `Persistent (${counts.Persistent})` },
            { key: 'Improving', label: `Improving (${counts.Improving})` },
            { key: 'Resolved', label: `Resolved (${counts.Resolved})` },
            { key: 'Normal', label: `Normal (${counts.Normal})` },
          ].map((tab) => (
            <button
              key={tab.key}
              className={`filter-tab ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table matching Wireframe Box 10 */}
      <div className="card">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Current Value</th>
              <th>Status</th>
              <th>Change</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {findingsList.map((item, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: '600', color: '#0f172a' }}>{item.parameter}</td>
                <td>{item.current}</td>
                <td>{getStatusBadge(item.status)}</td>
                <td style={{ fontFamily: 'monospace' }}>{item.change}</td>
                <td style={{ fontWeight: '700', color: '#2563eb' }}>{item.trend}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '16px' }}>
          Status is AI-detected based on available historical reports.
        </div>
      </div>
    </div>
  );
}

export default FindingsStatusView;
