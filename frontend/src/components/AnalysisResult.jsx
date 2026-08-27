import React from 'react';
import { Activity, AlertCircle, CheckCircle2, ClipboardCheck, Stethoscope, X } from 'lucide-react';

const humanize = (value) => String(value || '').replaceAll('_', ' ').toLowerCase();

export const AnalysisResult = ({ result, isLoading, error, onClose }) => {
  if (!result && !isLoading && !error) return null;
  const findings = result?.abnormal_findings || [];
  const comparisons = result?.comparison_context?.comparisons || [];

  return (
    <section className="result-card">
      <div className="result-heading">
        <div>
          <h2 className="section-title"><ClipboardCheck size={18} /> Analysis result</h2>
          <p className="section-desc">Structured findings and longitudinal facts from this report. This is not a diagnosis.</p>
        </div>
        <button className="icon-close-btn" onClick={onClose} aria-label="Close result"><X size={18} /></button>
      </div>
      {isLoading && <p className="timeline-empty">Loading analysis result…</p>}
      {error && <p className="timeline-error">{error}</p>}
      {result && !isLoading && (
        <div className="result-grid">
          <article className="result-panel">
            <h3><AlertCircle size={17} /> Current findings</h3>
            {findings.length ? findings.map((finding) => <p className="finding-row" key={`${finding.test_name}-${finding.status}`}><strong>{finding.test_name}</strong><span>{finding.value} {finding.unit}</span><span className={`finding-status ${finding.status?.toLowerCase()}`}>{finding.status}</span></p>) : <p className="timeline-muted">No out-of-range numeric values were detected.</p>}
          </article>
          <article className="result-panel">
            <h3><Activity size={17} /> Historical comparison</h3>
            {comparisons.length ? comparisons.map((comparison) => <p className="comparison-row" key={comparison.test_name}><strong>{comparison.test_name}</strong><span>{comparison.previous_value ?? 'No prior value'} → {comparison.current_value}</span><span>{humanize(comparison.finding_status)}</span></p>) : <p className="timeline-muted">No comparable prior report is available.</p>}
          </article>
          <article className="result-panel">
            <h3><Stethoscope size={17} /> Risk and consultation</h3>
            <p className="result-emphasis">Risk: {result.risk_assessment?.risk_level || 'Not assessed'}</p>
            <p>{result.consultation_advice?.consultation_required ? `${result.consultation_advice.recommended_specialist || 'Medical'} consultation recommended (${result.consultation_advice.urgency || 'routine'}).` : 'No consultation recommendation was generated from the current rules.'}</p>
          </article>
          <article className="result-panel result-summary">
            <h3><CheckCircle2 size={17} /> Validated summary</h3>
            <p>{result.summary_report || 'Analysis is not complete yet.'}</p>
          </article>
        </div>
      )}
    </section>
  );
};
