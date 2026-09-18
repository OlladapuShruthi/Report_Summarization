import React from 'react';
import { AlertTriangle, CheckCircle2, Stethoscope, ArrowRight, ShieldAlert, FileQuestion } from 'lucide-react';

export function ResultsOverviewView({ result, activePatient, onViewFullDetails, onOpenExport, onSelectReview }) {
  // Empty state
  if (!result) {
    return (
      <div className="card" style={{ padding: '48px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#64748b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <FileQuestion size={32} />
        </div>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a' }}>No Analysis Result Available</h3>
        <p style={{ color: '#64748b', fontSize: '0.92rem', maxWidth: '420px' }}>
          {activePatient
            ? `There are no active analysis results loaded for ${activePatient.display_name || 'this patient'}. Select a report from the Reports tab or upload a new one.`
            : 'Please select a patient and upload a report to view analysis results.'}
        </p>
      </div>
    );
  }

  // Active Patient Context Guard (Part 17)
  if (activePatient && result.patient_id && result.patient_id !== activePatient.patient_id) {
    return (
      <div className="card" style={{ padding: '40px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', textAlign: 'center' }}>
        <AlertTriangle size={36} color="#ef4444" style={{ marginBottom: '12px' }} />
        <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#991b1b' }}>Patient Context Mismatch</h3>
        <p style={{ color: '#b91c1c', fontSize: '0.9rem', maxWidth: '450px', margin: '0 auto 16px' }}>
          This analysis belongs to another patient record and cannot be rendered under the currently active patient context ({activePatient.display_name}).
        </p>
      </div>
    );
  }

  // Review Required State (Part 18)
  const isReviewRequired = result.review_required || result.status === 'needs_review';
  const analysisBlocked = result.review_policy && result.review_policy.analysis_allowed === false;

  const reportType = result.report_type || 'Clinical Report';
  const reportDate = result.patient_metadata?.report_date || 'Date not recorded';
  const patientDisplayName = activePatient?.display_name || result.patient_metadata?.name || 'Patient';

  const riskLevel = result.risk_assessment?.risk_level || 'UNKNOWN';
  const riskScore = result.risk_assessment?.risk_score != null ? result.risk_assessment.risk_score : null;
  const abnormalFindings = Array.isArray(result.abnormal_findings) ? result.abnormal_findings : [];
  const abnormalCount = abnormalFindings.length;
  const advice = result.consultation_advice?.consult_recommendation || result.consultation_advice?.specialty_recommended || 'Standard Clinical Review';
  const summaryText = result.summary_report || (analysisBlocked ? 'Detailed medical analysis is paused pending human clinical review.' : 'No narrative summary available.');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>
            {reportType}
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Patient: <strong>{patientDisplayName}</strong> • Report Date: {reportDate}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          {onViewFullDetails && !analysisBlocked && (
            <button className="btn-primary" onClick={onViewFullDetails}>
              View Full Findings <ArrowRight size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Review Required Banner */}
      {isReviewRequired && (
        <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fdba74', borderRadius: '12px', padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <ShieldAlert size={28} color="#c2410c" />
            <div>
              <h4 style={{ fontWeight: '700', color: '#9a3412', margin: 0 }}>Human Confirmation Required</h4>
              <p style={{ color: '#c2410c', fontSize: '0.88rem', margin: '4px 0 0' }}>
                {result.review_reasons?.length ? result.review_reasons.join(', ') : 'Additional evidence or confirmation is needed before finalizing analysis.'}
              </p>
            </div>
          </div>
          {onSelectReview && (
            <button className="btn-primary" style={{ backgroundColor: '#c2410c', borderColor: '#c2410c' }} onClick={onSelectReview}>
              Review Questions
            </button>
          )}
        </div>
      )}

      {/* 3 Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {/* Card 1: Overall Risk */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Overall Risk Assessment</span>
          <div>
            <span style={{ fontSize: '1.8rem', fontWeight: '700', color: riskLevel.toUpperCase().includes('HIGH') ? '#b91c1c' : (riskLevel.toUpperCase().includes('MODERATE') ? '#c2410c' : '#15803d') }}>
              {riskLevel}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', color: '#64748b', borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
            <span>Risk Score</span>
            <span style={{ fontWeight: '700', color: '#0f172a' }}>
              {riskScore !== null ? `${riskScore}/10` : 'UNKNOWN'}
            </span>
          </div>
        </div>

        {/* Card 2: Key Findings */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Objective Findings</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: abnormalCount > 0 ? '#b91c1c' : '#15803d' }}>
              <AlertTriangle size={20} />
              <span style={{ fontSize: '1.25rem', fontWeight: '700' }}>{abnormalCount}</span>
              <span style={{ fontSize: '0.85rem' }}>Abnormal Findings</span>
            </div>
          </div>
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '12px', fontSize: '0.82rem', color: '#64748b' }}>
            Extracted from objective lab report
          </div>
        </div>

        {/* Card 3: Recommendation */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Consultation Recommendation</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#2563eb' }}>
            <Stethoscope size={24} />
            <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>{advice}</span>
          </div>
          <div style={{ marginTop: 'auto', textAlign: 'right' }}>
            {onViewFullDetails && !analysisBlocked && (
              <button className="btn-outline-blue" onClick={onViewFullDetails} style={{ padding: '4px 12px', fontSize: '0.8rem' }}>
                View Details
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Quick Summary Card */}
      <div className="card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a', marginBottom: '12px' }}>AI Clinical Summary</h3>
        <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: '1.6', whiteSpace: 'pre-line' }}>{summaryText}</p>
      </div>
    </div>
  );
}

export default ResultsOverviewView;
