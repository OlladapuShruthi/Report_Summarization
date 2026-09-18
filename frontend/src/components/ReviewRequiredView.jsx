import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, Clock, UploadCloud, ArrowLeft, FileText } from 'lucide-react';
import { answerReviewQuestion, uploadFollowUpReport } from '../services/api';

export function ReviewRequiredView({ analysisId, result, onBack, onAnswerSuccess, onFollowUpCreated }) {
  const [answeringQuestionId, setAnsweringQuestionId] = useState(null);
  const [responseText, setResponseText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [followUpFile, setFollowUpFile] = useState(null);
  const [uploadingFollowUp, setUploadingFollowUp] = useState(false);

  const reviewReasons = result?.review_reasons || result?.parser_metadata?.review_reasons || [];
  const reviewQuestions = result?.review_questions || [];
  const reviewPolicy = result?.review_policy || {};

  const handleAnswer = async (questionId, action) => {
    setSubmitting(true);
    setErrorMsg(null);
    try {
      await answerReviewQuestion(analysisId, questionId, {
        action,
        response: responseText.trim() || undefined,
        finding_id: undefined,
      });
      setResponseText('');
      setAnsweringQuestionId(null);
      if (onAnswerSuccess) onAnswerSuccess();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit response.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFollowUpUpload = async (e) => {
    e.preventDefault();
    if (!followUpFile) return;
    setUploadingFollowUp(true);
    setErrorMsg(null);
    try {
      const newSession = await uploadFollowUpReport(analysisId, followUpFile);
      if (onFollowUpCreated) onFollowUpCreated(newSession);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to upload follow-up report.');
    } finally {
      setUploadingFollowUp(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn-secondary" onClick={onBack} style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            <ArrowLeft size={16} /> Back
          </button>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>Clinical Review Required</h1>
            <p style={{ color: '#64748b', fontSize: '0.88rem' }}>Workspace: {analysisId}</p>
          </div>
        </div>
      </div>

      {/* WHY REVIEW IS REQUIRED */}
      <div className="card" style={{ backgroundColor: '#fff7ed', border: '1px solid #fdba74' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
          <ShieldAlert size={26} color="#c2410c" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#9a3412', marginBottom: '6px' }}>
              WHY REVIEW IS REQUIRED
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#c2410c', marginBottom: '10px' }}>
              Analysis is paused because automated clinical extraction flagged one or more confidence checks. Final analysis cannot proceed until evidence is confirmed or clarified.
            </p>
            {reviewReasons.length > 0 && (
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#9a3412', fontSize: '0.88rem' }}>
                {reviewReasons.map((reason, idx) => (
                  <li key={idx}>
                    <strong>{reason.replaceAll('_', ' ')}</strong>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* REVIEW QUESTIONS */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
          REVIEW QUESTIONS ({reviewQuestions.length})
        </h2>

        {errorMsg && (
          <div style={{ padding: '10px 14px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#b91c1c', fontSize: '0.88rem' }}>
            {errorMsg}
          </div>
        )}

        {reviewQuestions.length === 0 ? (
          <p style={{ color: '#64748b' }}>No pending review questions.</p>
        ) : (
          reviewQuestions.map((q) => {
            const isAnswered = q.status === 'answered' || q.status === 'confirmed';
            const isSelected = answeringQuestionId === q.question_id;

            return (
              <div
                key={q.question_id}
                style={{
                  padding: '16px',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  backgroundColor: isAnswered ? '#f8fafc' : '#ffffff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.92rem', fontWeight: '600', color: '#0f172a' }}>
                    {q.question}
                  </span>
                  <span
                    className={`badge ${isAnswered ? 'badge-status-improving' : 'badge-status-persistent'}`}
                    style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}
                  >
                    {isAnswered ? 'PATIENT-REPORTED INFORMATION' : 'PENDING REVIEW'}
                  </span>
                </div>

                {isAnswered && (
                  <div style={{ marginTop: '8px', padding: '8px 12px', backgroundColor: '#eff6ff', borderRadius: '6px', fontSize: '0.85rem', color: '#1e40af' }}>
                    <strong>Response:</strong> {q.answer || q.status}
                  </div>
                )}

                {!isAnswered && (
                  <div style={{ marginTop: '12px' }}>
                    {isSelected ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <input
                          type="text"
                          value={responseText}
                          onChange={(e) => setResponseText(e.target.value)}
                          placeholder="Type confirmation or clarification notes..."
                          style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
                          autoFocus
                        />
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          <button
                            className="btn-primary"
                            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                            onClick={() => handleAnswer(q.question_id, 'confirm')}
                            disabled={submitting}
                          >
                            <CheckCircle size={14} /> Confirm
                          </button>
                          <button
                            className="btn-secondary"
                            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                            onClick={() => handleAnswer(q.question_id, 'dismiss')}
                            disabled={submitting}
                          >
                            <XCircle size={14} /> Dismiss
                          </button>
                          <button
                            className="btn-secondary"
                            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                            onClick={() => handleAnswer(q.question_id, 'defer')}
                            disabled={submitting}
                          >
                            <Clock size={14} /> Defer
                          </button>
                          <button
                            className="btn-secondary"
                            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                            onClick={() => handleAnswer(q.question_id, 'no_report')}
                            disabled={submitting}
                          >
                            No Report Available
                          </button>
                          <button
                            type="button"
                            className="btn-secondary"
                            style={{ padding: '6px 10px', fontSize: '0.82rem', marginLeft: 'auto' }}
                            onClick={() => { setAnsweringQuestionId(null); setResponseText(''); }}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn-outline-blue"
                          style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                          onClick={() => { setAnsweringQuestionId(q.question_id); setResponseText(''); }}
                        >
                          Respond to Question
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* UPLOAD FOLLOW-UP REPORT */}
      <div className="card">
        <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
          UPLOAD FOLLOW-UP REPORT
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem', marginBottom: '16px' }}>
          Upload a follow-up medical report to resolve uncertainties. A new analysis session will be created and linked to this baseline report.
        </p>

        <form onSubmit={handleFollowUpUpload} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(e) => setFollowUpFile(e.target.files?.[0] || null)}
            style={{ fontSize: '0.88rem' }}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={!followUpFile || uploadingFollowUp}
            style={{ padding: '8px 16px', fontSize: '0.88rem' }}
          >
            <UploadCloud size={16} /> {uploadingFollowUp ? 'Uploading...' : 'Upload Follow-up Report'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ReviewRequiredView;
