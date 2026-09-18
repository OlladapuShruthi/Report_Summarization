import React, { useState } from 'react';
import { ArrowLeft, Download, AlertTriangle, TrendingUp, Info, CheckCircle2, HelpCircle, ShieldAlert } from 'lucide-react';

export function ResultsDetailView({ result, activePatient, onBack, onOpenExport, onSelectTab }) {
  const [selectedFindingIndex, setSelectedFindingIndex] = useState(0);

  if (!result) {
    return (
      <div className="card" style={{ padding: '32px', textAlign: 'center' }}>
        <p style={{ color: '#64748b' }}>No analysis detail selected.</p>
        <button className="btn-secondary" onClick={onBack} style={{ marginTop: '12px' }}>
          <ArrowLeft size={16} /> Go Back
        </button>
      </div>
    );
  }

  const reportType = result.report_type || 'Clinical Lab Report';
  const reportDate = result.patient_metadata?.report_date || 'Date not recorded';
  const patientDisplayName = activePatient?.display_name || result.patient_metadata?.name || 'Patient';

  // 1. Current Objective Findings
  const abnormalFindings = Array.isArray(result.abnormal_findings) ? result.abnormal_findings : [];
  const comparisons = result.comparison_context?.comparisons || [];

  // 3. Patient-Reported Information
  const reviewQuestions = result.review_questions || [];
  const patientReportedInfo = reviewQuestions.filter(
    (q) => q.status === 'answered' || q.evidence_type === 'PATIENT_REPORTED'
  );

  // 4. Uncertainty Warnings
  const warnings = [
    ...(result.parser_metadata?.warnings || []),
    ...(result.validation_status?.uncertainty_warnings || []),
  ];
  if (comparisons.length === 0) {
    warnings.push('No prior historical reports available for longitudinal baseline comparison.');
  }

  // 5. AI Explanation
  const summaryText = result.summary_report || 'Grounded extraction completed from laboratory report.';

  const selectedFinding = abnormalFindings[selectedFindingIndex] || abnormalFindings[0] || null;
  const selectedComparison = comparisons.find(
    (c) => c.test_name?.toLowerCase() === (selectedFinding?.test_name || selectedFinding?.parameter)?.toLowerCase()
  );

  const formatStatus = (status) => {
    if (!status) return 'UNKNOWN';
    return String(status).replaceAll('_', ' ').toUpperCase();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn-secondary" onClick={onBack} style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            <ArrowLeft size={16} /> Back
          </button>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>
              {reportType}
            </h1>
            <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
              Patient: <strong>{patientDisplayName}</strong> • {reportDate}
            </span>
          </div>
        </div>

        {onOpenExport && (
          <button className="btn-outline-blue" onClick={onOpenExport}>
            <Download size={16} /> Export
          </button>
        )}
      </div>

      {/* Grid: Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Section 1: CURRENT OBJECTIVE FINDINGS */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <AlertTriangle size={18} color="#2563eb" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', margin: 0 }}>
              1. CURRENT OBJECTIVE FINDINGS
            </h2>
          </div>

          {abnormalFindings.length === 0 ? (
            <div style={{ padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px', color: '#166534', fontSize: '0.9rem' }}>
              ✓ No abnormal laboratory values flagged in this report.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Parameter / Test</th>
                    <th>Measured Value</th>
                    <th>Reference Range</th>
                    <th>Evaluation Status</th>
                    <th>Source Document</th>
                  </tr>
                </thead>
                <tbody>
                  {abnormalFindings.map((finding, idx) => (
                    <tr
                      key={idx}
                      onClick={() => setSelectedFindingIndex(idx)}
                      style={{
                        cursor: 'pointer',
                        backgroundColor: selectedFindingIndex === idx ? '#eff6ff' : undefined,
                      }}
                    >
                      <td style={{ fontWeight: '600', color: '#0f172a' }}>
                        {finding.test_name || finding.parameter || finding.name || 'Lab Test'}
                      </td>
                      <td style={{ fontWeight: '700', color: '#b91c1c' }}>
                        {finding.value ?? finding.current_value ?? '—'} {finding.unit || ''}
                      </td>
                      <td>
                        {finding.reference_range
                          ? (typeof finding.reference_range === 'object'
                            ? `${finding.reference_range.low ?? '?'} – ${finding.reference_range.high ?? '?'}`
                            : finding.reference_range)
                          : (finding.normal_range || 'N/A')}
                      </td>
                      <td>
                        <span className={`badge ${finding.status === 'LOW' || finding.status === 'HIGH' ? 'badge-status-persistent' : 'badge-status-normal'}`}>
                          {finding.status || 'ABNORMAL'} {finding.severity ? `(${finding.severity})` : ''}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.82rem', color: '#64748b' }}>
                        {reportType} ({reportDate})
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Section 2: HISTORICAL COMPARISON */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <TrendingUp size={18} color="#15803d" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', margin: 0 }}>
              2. HISTORICAL COMPARISON
            </h2>
          </div>

          {comparisons.length === 0 ? (
            <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', color: '#64748b', fontSize: '0.9rem' }}>
              No prior historical comparison available. Upload previous reports for this patient to establish a longitudinal baseline.
            </div>
          ) : (
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Test Name</th>
                  <th>Previous Value</th>
                  <th>Current Value</th>
                  <th>Lifecycle Status</th>
                  <th>Factual Trend</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((comp, cIdx) => (
                  <tr key={cIdx}>
                    <td style={{ fontWeight: '600', color: '#0f172a' }}>{comp.test_name}</td>
                    <td style={{ color: '#64748b' }}>
                      {comp.previous_value != null ? `${comp.previous_value} ${comp.unit || ''}` : '—'}
                    </td>
                    <td style={{ fontWeight: '700', color: '#0f172a' }}>
                      {comp.current_value} {comp.unit || ''}
                    </td>
                    <td>
                      <span className={`badge badge-status-${(comp.finding_status || '').toLowerCase().includes('improving') ? 'improving' : 'persistent'}`}>
                        {formatStatus(comp.finding_status)}
                      </span>
                    </td>
                    <td style={{ fontWeight: '600' }}>
                      {comp.lifecycle_state || comp.trend || formatStatus(comp.finding_status)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Section 3: PATIENT-REPORTED INFORMATION */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Info size={18} color="#c2410c" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', margin: 0 }}>
              3. PATIENT-REPORTED INFORMATION
            </h2>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '14px' }}>
            Information confirmed or reported by the patient during review sessions. Kept strictly distinct from laboratory findings.
          </p>

          {patientReportedInfo.length === 0 ? (
            <div style={{ padding: '14px', backgroundColor: '#f8fafc', borderRadius: '8px', color: '#64748b', fontSize: '0.88rem' }}>
              No patient-reported notes or confirmations recorded for this analysis.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {patientReportedInfo.map((info, iIdx) => (
                <div key={iIdx} style={{ padding: '12px 16px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#9a3412', textTransform: 'uppercase', marginBottom: '4px' }}>
                    PATIENT-REPORTED CONFIRMATION
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#431407' }}>
                    <strong>Q:</strong> {info.question}
                  </div>
                  {info.answer && (
                    <div style={{ fontSize: '0.9rem', color: '#9a3412', marginTop: '4px' }}>
                      <strong>Response:</strong> {info.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 4: UNCERTAINTY WARNINGS */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <HelpCircle size={18} color="#c2410c" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', margin: 0 }}>
              4. UNCERTAINTY & LIMITATION WARNINGS
            </h2>
          </div>

          {warnings.length === 0 ? (
            <div style={{ fontSize: '0.88rem', color: '#15803d' }}>
              No critical uncertainties flagged for this extraction.
            </div>
          ) : (
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '0.9rem', lineHeight: '1.6' }}>
              {warnings.map((warn, wIdx) => (
                <li key={wIdx}>{warn}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Section 5: AI EXPLANATION & CLINICAL SUMMARY */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <CheckCircle2 size={18} color="#2563eb" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', margin: 0 }}>
              5. AI CLINICAL EXPLANATION & SUMMARY
            </h2>
          </div>
          <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
            {summaryText}
          </p>
        </div>
      </div>
    </div>
  );
}

export default ResultsDetailView;
