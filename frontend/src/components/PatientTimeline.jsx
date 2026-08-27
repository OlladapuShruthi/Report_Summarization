import React from 'react';
import { CalendarDays, GitCompareArrows, History, FileText } from 'lucide-react';

const formatDate = (dateValue) => {
  if (!dateValue) return 'Date unavailable';
  const date = new Date(dateValue);
  return Number.isNaN(date.getTime()) ? dateValue : date.toLocaleDateString();
};

export const PatientTimeline = ({ timeline, isLoading, error }) => {
  if (!timeline && !isLoading && !error) return null;
  const reports = [...(timeline?.reports || [])].sort((left, right) => String(left.date).localeCompare(String(right.date)));

  return (
    <section className="timeline-card">
      <div className="timeline-heading">
        <div>
          <h2 className="section-title"><History size={18} /> Patient timeline</h2>
          <p className="section-desc">Chronological reports and available factual comparisons for the selected patient.</p>
        </div>
      </div>
      {isLoading && <p className="timeline-empty">Loading patient history…</p>}
      {error && <p className="timeline-error">{error}</p>}
      {!isLoading && !error && reports.length === 0 && <p className="timeline-empty">No reports exist for this patient yet.</p>}
      {!isLoading && !error && reports.length > 0 && (
        <div className="timeline-list">
          {reports.map((report, index) => {
            const comparisons = report.comparison_context?.comparisons || [];
            return (
              <article className="timeline-entry" key={report.analysis_id}>
                <div className="timeline-marker"><span>{index + 1}</span></div>
                <div className="timeline-content">
                  <div className="timeline-report-heading">
                    <div>
                      <p className="timeline-date"><CalendarDays size={14} /> {formatDate(report.date)}</p>
                      <h3><FileText size={16} /> {report.title || report.report_type || 'Medical report'}</h3>
                    </div>
                    <span className={`status-tag ${report.status || 'created'}`}>{report.status || 'created'}</span>
                  </div>
                  {comparisons.length > 0 ? (
                    <div className="timeline-comparisons">
                      {comparisons.map((comparison) => (
                        <p key={comparison.test_name}><GitCompareArrows size={14} /> <strong>{comparison.test_name}</strong>: {comparison.previous_value ?? '—'} → {comparison.current_value} · {comparison.finding_status.replaceAll('_', ' ').toLowerCase()}</p>
                      ))}
                    </div>
                  ) : <p className="timeline-muted">No comparable prior result is available for this report.</p>}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
};
