import React, { useState } from 'react';
import { UploadCloud, Eye, FileText, CheckCircle2 } from 'lucide-react';

export function ReportsView({
  sessions = [],
  activePatient,
  onOpenUpload,
  onViewResult
}) {
  const [activeTab, setActiveTab] = useState('All Reports');
  const patientName = activePatient?.display_name || activePatient?.name || 'Rahul Sharma';

  const sampleReports = [
    { id: '1', name: 'CBC Report', date: '12 May 2025', type: 'Lab', status: 'Analyzed' },
    { id: '2', name: 'Lipid Profile', date: '02 May 2025', type: 'Lab', status: 'Analyzed' },
    { id: '3', name: 'Thyroid Profile', date: '25 Apr 2025', type: 'Lab', status: 'Analyzed' },
    { id: '4', name: 'Vitamin D', date: '10 Apr 2025', type: 'Lab', status: 'Analyzed' },
    { id: '5', name: 'Chest X-Ray', date: '01 Apr 2025', type: 'Radiology', status: 'Analyzed' },
    { id: '6', name: 'Urine Routine', date: '20 Mar 2025', type: 'Lab', status: 'Analyzed' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Screen 5 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>{patientName}</h1>
          <span className="badge badge-status-improving" style={{ padding: '4px 12px', fontSize: '0.82rem' }}>
            Active Patient
          </span>
        </div>
        <button className="btn-primary" onClick={onOpenUpload}>
          <UploadCloud size={16} /> Upload Report
        </button>
      </div>

      {/* Filter Tabs matching Wireframe Screen 5 */}
      <div className="card">
        <div className="filter-tabs" style={{ marginBottom: '16px' }}>
          {['All Reports', 'Lab Reports', 'Radiology', 'Others'].map((tab) => (
            <button
              key={tab}
              className={`filter-tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Data Table */}
        <table className="custom-table">
          <thead>
            <tr>
              <th>Report Name</th>
              <th>Date</th>
              <th>Type</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sampleReports.map((report) => (
              <tr key={report.id}>
                <td style={{ fontWeight: '600', color: '#0f172a' }}>{report.name}</td>
                <td>{report.date}</td>
                <td>{report.type}</td>
                <td>
                  <span className="badge badge-status-normal" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <CheckCircle2 size={12} color="#2563eb" /> {report.status}
                  </span>
                </td>
                <td>
                  <button className="btn-outline-blue" onClick={() => onViewResult && onViewResult(report.id)}>
                    <Eye size={14} /> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ReportsView;
