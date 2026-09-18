import React, { useState, useContext } from 'react';
import { PatientContext } from '../context/PatientContext';
import { UploadCloud, Eye, FileText, CheckCircle2, FileQuestion } from 'lucide-react';

export function ReportsView({
  onOpenUpload,
  onViewResult
}) {
  const [activeTab, setActiveTab] = useState('All Reports');
  const { activePatient, sessions } = useContext(PatientContext);
  const patientName = activePatient?.display_name || activePatient?.name || 'Selected Patient';

  const reportsList = sessions || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>{patientName}</h1>
          <span className="badge badge-status-improving" style={{ padding: '4px 12px', fontSize: '0.82rem' }}>
            {activePatient ? 'Active Patient' : 'No Patient Selected'}
          </span>
        </div>
        <button className="btn-primary" onClick={onOpenUpload}>
          <UploadCloud size={16} /> Upload Report
        </button>
      </div>

      {/* Filter Tabs & Content */}
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

        {reportsList.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#64748b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileQuestion size={32} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>No Medical Reports Uploaded Yet</h3>
              <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '420px' }}>
                There are no uploaded reports recorded for {patientName}. Click "Upload Report" below to upload a PDF or image report for AI analysis.
              </p>
            </div>
            <button className="btn-primary" onClick={onOpenUpload} style={{ marginTop: '8px' }}>
              <UploadCloud size={16} /> Upload First Report
            </button>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Report Name</th>
                <th>Upload Date</th>
                <th>Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reportsList.map((report) => (
                <tr key={report.analysis_id || report.id}>
                  <td style={{ fontWeight: '600', color: '#0f172a' }}>{report.document_info?.original_filename || report.title || 'Medical Report'}</td>
                  <td>{report.created_at ? new Date(report.created_at).toLocaleString('en-US', { year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Recent'}</td>
                  <td>{(report.parsed_json && report.parsed_json.report_type) || 'General Lab'}</td>
                  <td>
                    <span className="badge badge-status-normal" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={12} color="#2563eb" /> {report.status || 'Analyzed'}
                    </span>
                  </td>
                  <td>
                    <button className="btn-outline-blue" onClick={() => onViewResult && onViewResult(report.analysis_id || report.id)}>
                      <Eye size={14} /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default ReportsView;

