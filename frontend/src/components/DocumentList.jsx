import React from 'react';
import { Layers, FileText, Clock, HardDrive, Play, Loader2, Braces, CheckCircle2, AlertTriangle, Workflow } from 'lucide-react';

export const DocumentList = ({ sessions, activeParseId, activeAnalyzeId, onParse, onAnalyze }) => {
  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="table-card">
      <h2 className="section-title">Active Analysis Workspaces</h2>
      <p className="section-desc">Managed sessions in MongoDB Atlas database.</p>

      {sessions.length === 0 ? (
        <div className="empty-state">
          <Layers size={40} style={{ color: '#4b5563', marginBottom: '12px' }} />
          <p>No analysis workspaces created yet. Upload a report to initialize a workspace.</p>
        </div>
      ) : (
        <table className="doc-table">
          <thead>
            <tr>
              <th>Workspace ID</th>
              <th>Report / Document</th>
              <th>File Size</th>
              <th>Pipeline Status</th>
              <th>Parsed Facts</th>
              <th>Action</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => {
              const docInfo = session.document_info;
              const status = session.status || 'created';
              const isParsing = activeParseId === session.analysis_id || status === 'parsing';
              const isAnalyzing = activeAnalyzeId === session.analysis_id || status === 'analyzing';
              const canParse = Boolean(docInfo) && !['parsed', 'analyzing', 'validated', 'completed'].includes(status) && !isParsing;
              const canAnalyze = Boolean(session.parsed_json) && !['analyzing', 'validated', 'completed'].includes(status) && !isAnalyzing;
              const labCount = session.parsed_json?.lab_results?.length || 0;
              const narrativeCount = session.parsed_json?.narrative_impressions?.length || 0;
              const displayCount = labCount + narrativeCount;
              const hasReasoning = Boolean(session.summary_report || session.risk_assessment || session.validation_status);
              const riskLevel = session.risk_assessment?.risk_level || 'LOW';
              const consultationRequired = Boolean(session.consultation_advice?.consultation_required);
              const executionLog = session.execution_log || [];
              const executionStage = executionLog.length > 0 ? executionLog[executionLog.length - 1]?.stage : status;

              return (
                <tr key={session.analysis_id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'monospace', color: '#93c5fd' }}>
                      <Layers size={16} color="#06b6d4" />
                      <span>{session.analysis_id.substring(0, 8)}...</span>
                    </div>
                  </td>
                  <td style={{ fontWeight: 600, color: '#f3f4f6' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <FileText size={18} color="#3b82f6" />
                      <span>{docInfo ? docInfo.original_filename : session.title || 'No file uploaded'}</span>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#9ca3af' }}>
                      <HardDrive size={14} />
                      <span>{docInfo ? formatSize(docInfo.file_size) : '0 B'}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-tag ${status}`}>{status}</span>
                    <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px', color: '#9ca3af', fontSize: '0.82rem' }}>
                      <Workflow size={14} />
                      <span>{executionStage}</span>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#9ca3af' }}>
                      {hasReasoning ? <CheckCircle2 size={14} color="#10b981" /> : <AlertTriangle size={14} color="#f59e0b" />}
                      <span>{hasReasoning ? `${displayCount} structured items` : 'Awaiting reasoning'}</span>
                    </div>
                    {hasReasoning && (
                      <div style={{ marginTop: '8px', color: '#cbd5e1', fontSize: '0.82rem', lineHeight: 1.5 }}>
                        <div>Risk: {riskLevel}</div>
                        <div>Consult: {consultationRequired ? 'Yes' : 'No'}</div>
                      </div>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <button
                        className="parse-btn"
                        onClick={() => onParse?.(session.analysis_id)}
                        disabled={!canParse}
                        title={canParse ? 'Parse uploaded report' : 'Parsing unavailable'}
                      >
                        {isParsing ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
                        {isParsing ? 'Parsing' : status === 'parsed' ? 'Parsed' : 'Parse'}
                      </button>
                      <button
                        className="analyze-btn"
                        onClick={() => onAnalyze?.(session.analysis_id)}
                        disabled={!canAnalyze}
                        title={canAnalyze ? 'Run structured reasoning' : 'Analysis unavailable'}
                      >
                        {isAnalyzing ? <Loader2 size={15} className="animate-spin" /> : <Workflow size={15} />}
                        {isAnalyzing ? 'Analyzing' : 'Analyze'}
                      </button>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#9ca3af' }}>
                      <Clock size={14} />
                      <span>{formatDate(session.created_at)}</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};
