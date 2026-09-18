import React, { useState, useEffect, useRef } from 'react';
import { Check, ArrowRight, AlertTriangle, Loader } from 'lucide-react';
import { parseAnalysisSession, analyzeAnalysisSession, fetchAnalysisResult } from '../services/api';

export function ProcessingView({ analysisId, patientName, onComplete, onReviewRequired, onError }) {
  const [currentStage, setCurrentStage] = useState(0);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(true);
  const hasStarted = useRef(false);

  const stages = [
    { id: 'upload', label: 'Report uploaded' },
    { id: 'parse', label: 'Extracting text & parsing medical values' },
    { id: 'analyze', label: 'Detecting abnormalities & assessing risk' },
    { id: 'fetch', label: 'Validating result' },
  ];

  useEffect(() => {
    if (!analysisId) {
      setError("No analysis session provided.");
      setIsProcessing(false);
      return;
    }

    if (hasStarted.current) return;
    hasStarted.current = true;

    const runPipeline = async () => {
      try {
        // Stage 0: Uploaded (already done before reaching here)
        setCurrentStage(1); // Move to Parse

        // Stage 1: Parse
        await parseAnalysisSession(analysisId);
        
        setCurrentStage(2); // Move to Analyze

        // Stage 2: Analyze
        try {
          await analyzeAnalysisSession(analysisId);
        } catch (analyzeErr) {
          // If review required, trigger callback and stop
          if (
            analyzeErr.message.toLowerCase().includes('review') ||
            analyzeErr.response?.data?.error?.code === 'ANALYSIS_REVIEW_REQUIRED'
          ) {
            setIsProcessing(false);
            if (onReviewRequired) onReviewRequired(analysisId);
            return;
          }
          throw analyzeErr; // Re-throw other errors
        }

        setCurrentStage(3); // Move to Fetch

        // Stage 3: Fetch Result
        const result = await fetchAnalysisResult(analysisId);
        
        setCurrentStage(4); // All Complete
        setIsProcessing(false);
        
        if (onComplete) {
          // Add a short delay so the user can see the 100% completion before jumping
          setTimeout(() => {
            onComplete(result);
          }, 1500);
        }

      } catch (err) {
        console.error("Pipeline failed:", err);
        setError(err.message || "An error occurred during analysis.");
        setIsProcessing(false);
        if (onError) onError(err);
      }
    };

    runPipeline();
  }, [analysisId, onComplete, onReviewRequired, onError]);

  const progressPercent = Math.min(100, Math.round((currentStage / stages.length) * 100));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '840px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>
            Analyzing {patientName ? `${patientName}'s` : 'Patient'} Report
          </h1>
          <p style={{ fontSize: '0.88rem', color: '#64748b', marginTop: '2px' }}>
            LangGraph Multi-Agent Pipeline Execution
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '32px' }}>
          {stages.map((stage, idx) => {
            let status = 'pending';
            if (currentStage > idx) status = 'completed';
            else if (currentStage === idx && isProcessing) status = 'active';
            else if (currentStage === idx && error) status = 'error';

            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.95rem' }}>
                {status === 'completed' && (
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#dcfce7', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Check size={14} />
                  </div>
                )}
                {status === 'active' && (
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Loader size={14} className="spin-icon" />
                  </div>
                )}
                {status === 'pending' && (
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #cbd5e1' }} />
                )}
                {status === 'error' && (
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#fef2f2', color: '#dc2626', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <AlertTriangle size={14} />
                  </div>
                )}
                
                <span style={{ 
                  fontWeight: status === 'active' ? '600' : '500', 
                  color: status === 'completed' ? '#15803d' : (status === 'active' ? '#2563eb' : (status === 'error' ? '#dc2626' : '#94a3b8')) 
                }}>
                  {stage.label}
                </span>
                {status === 'active' && <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#2563eb', fontWeight: '600' }}>In Progress...</span>}
                {status === 'error' && <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#dc2626', fontWeight: '600' }}>Failed</span>}
              </div>
            );
          })}
        </div>

        {error && (
          <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', color: '#991b1b' }}>
            <strong>Analysis Error:</strong> {error}
          </div>
        )}

        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.88rem', fontWeight: '600' }}>
            <span style={{ color: '#0f172a' }}>Pipeline Progress</span>
            <span style={{ color: '#2563eb' }}>{progressPercent}%</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ width: `${progressPercent}%`, height: '100%', backgroundColor: '#2563eb', borderRadius: '99px', transition: 'width 0.5s ease-in-out' }} />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
          <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
            {isProcessing ? 'Processing report stages...' : (error ? 'Processing failed.' : 'Processing complete.')}
          </span>
          {(!isProcessing && !error) && (
            <button className="btn-primary" onClick={() => onComplete && onComplete()}>
              View Results Dashboard <ArrowRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProcessingView;
