import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, Trash2, MessageCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { sendChatMessage, fetchChatHistory, clearChatHistory } from '../services/api';

export function ChatView({ activePatient, onSelectPatientView }) {
  const patientName = activePatient?.display_name || activePatient?.name || null;
  const patientId = activePatient?.patient_id || null;

  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  const activePatientIdRef = useRef(patientId);

  // Load chat history whenever activePatient changes
  useEffect(() => {
    activePatientIdRef.current = patientId;
    setMessages([]);
    setErrorMsg(null);
    setInputQuery('');

    if (!patientId) return;

    let isMounted = true;
    const loadHistory = async () => {
      setIsHistoryLoading(true);
      try {
        const history = await fetchChatHistory(patientId);
        if (isMounted && activePatientIdRef.current === patientId) {
          const formatted = history.map((h) => ({
            id: h.message_id || h._id || String(Math.random()),
            sender: 'bot',
            userText: h.user_message,
            botText: h.bot_response || h.response,
            intent: h.intent || h.classified_intent,
            sources: h.citations || [],
            clarification: h.clarification_triggered,
          }));
          setMessages(formatted);
        }
      } catch (err) {
        if (isMounted && activePatientIdRef.current === patientId) {
          console.warn('Failed to load chat history:', err);
        }
      } finally {
        if (isMounted) setIsHistoryLoading(false);
      }
    };

    loadHistory();
    return () => {
      isMounted = false;
    };
  }, [patientId]);

  // Gate: No active patient selected
  if (!patientId) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - 120px)' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Ask Questions</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Ask questions about a patient's medical history (RAG powered)</p>
        </div>
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#64748b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <MessageCircle size={32} />
          </div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#0f172a' }}>Please select a patient first</h3>
          <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '420px', textAlign: 'center' }}>
            Medical chat requires an active patient context to ensure strict data privacy and isolation.
          </p>
          {onSelectPatientView && (
            <button className="btn-primary" onClick={onSelectPatientView} style={{ marginTop: '8px' }}>
              Select Patient
            </button>
          )}
        </div>
      </div>
    );
  }

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    const query = inputQuery.trim();
    if (!query || isLoading) return;

    setInputQuery('');
    setErrorMsg(null);

    const tempId = Date.now().toString();
    const currentPatient = patientId;
    setMessages((prev) => [
      ...prev,
      { id: tempId, sender: 'pending', userText: query, botText: null }
    ]);
    setIsLoading(true);

    try {
      const res = await sendChatMessage(currentPatient, query);
      // Ensure user hasn't switched to another patient while waiting
      if (activePatientIdRef.current === currentPatient) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === tempId
              ? {
                  id: res.message_id || tempId,
                  sender: 'bot',
                  userText: query,
                  botText: res.bot_response || res.response,
                  intent: res.intent || res.classified_intent,
                  sources: res.citations || [],
                  clarification: res.clarification_triggered,
                }
              : msg
          )
        );
      }
    } catch (err) {
      if (activePatientIdRef.current === currentPatient) {
        const errorText = err.response?.data?.message || err.message || 'Unable to process query.';
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === tempId
              ? {
                  id: tempId,
                  sender: 'bot',
                  userText: query,
                  botText: `Unable to process question: ${errorText}`,
                  isError: true,
                }
              : msg
          )
        );
        setErrorMsg(errorText);
      }
    } finally {
      if (activePatientIdRef.current === currentPatient) {
        setIsLoading(false);
      }
    }
  };

  const handleClearHistory = async () => {
    if (!patientId) return;
    try {
      await clearChatHistory(patientId);
      setMessages([]);
    } catch (err) {
      console.warn('Failed to clear chat history:', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - 120px)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Ask Questions</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Grounded medical assistant for {patientName}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="badge badge-status-improving" style={{ padding: '6px 14px', fontSize: '0.88rem' }}>
            Current Patient: {patientName}
          </span>
          {messages.length > 0 && (
            <button className="btn-secondary" style={{ padding: '6px 10px' }} onClick={handleClearHistory} title="Clear conversation history">
              <Trash2 size={16} color="#ef4444" />
            </button>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '24px', overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 1 }}>
          {isHistoryLoading ? (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
              <RefreshCw size={24} className="spin" />
              <span style={{ marginLeft: '8px' }}>Loading conversation history...</span>
            </div>
          ) : messages.length === 0 ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', color: '#64748b' }}>
              <MessageCircle size={40} color="#cbd5e1" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#334155' }}>No conversation history</h3>
              <p style={{ fontSize: '0.88rem', maxWidth: '420px', textAlign: 'center' }}>
                Ask a question about {patientName}'s medical reports or lab results. Grounded AI answers strictly from recorded clinical evidence.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px', justifyContent: 'center' }}>
                {[
                  'What were the key findings in the latest report?',
                  'Are there any abnormal values?',
                  'How has health changed over time?',
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputQuery(suggestion)}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '20px',
                      border: '1px solid #e2e8f0',
                      backgroundColor: '#f8fafc',
                      fontSize: '0.82rem',
                      color: '#475569',
                      cursor: 'pointer',
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {/* User Message */}
                {msg.userText && (
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <div
                      style={{
                        maxWidth: '75%',
                        padding: '12px 18px',
                        borderRadius: '18px 18px 2px 18px',
                        backgroundColor: '#2563eb',
                        color: '#ffffff',
                        fontSize: '0.95rem',
                        lineHeight: '1.5'
                      }}
                    >
                      {msg.userText}
                    </div>
                  </div>
                )}

                {/* Bot Response */}
                {msg.sender === 'pending' ? (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div
                      style={{
                        maxWidth: '75%',
                        padding: '12px 18px',
                        borderRadius: '18px 18px 18px 2px',
                        backgroundColor: '#f1f5f9',
                        color: '#64748b',
                        fontSize: '0.9rem',
                        fontStyle: 'italic',
                      }}
                    >
                      Thinking and searching medical records...
                    </div>
                  </div>
                ) : msg.botText ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', maxWidth: '80%' }}>
                    <div
                      style={{
                        padding: '14px 18px',
                        borderRadius: '18px 18px 18px 2px',
                        backgroundColor: msg.isError ? '#fef2f2' : '#f1f5f9',
                        color: msg.isError ? '#991b1b' : '#0f172a',
                        border: msg.isError ? '1px solid #fecaca' : 'none',
                        fontSize: '0.95rem',
                        lineHeight: '1.6',
                        whiteSpace: 'pre-line'
                      }}
                    >
                      {msg.intent && (
                        <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
                          Intent: {msg.intent.replaceAll('_', ' ')}
                        </div>
                      )}
                      {msg.botText}
                    </div>

                    {/* RAG Citations */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div style={{ marginTop: '8px', width: '100%', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '12px 14px' }}>
                        <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#0f172a', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <FileText size={13} color="#2563eb" /> Sources / Citations
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {msg.sources.map((src, sIdx) => (
                            <div key={sIdx} style={{ fontSize: '0.78rem', color: '#475569', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span>•</span>
                              <span style={{ fontWeight: '500' }}>{src.title}</span>
                              <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: '#94a3b8' }}>{src.type}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>

        {/* Error message */}
        {errorMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#b91c1c', fontSize: '0.85rem', marginTop: '12px' }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Input Bar */}
        <form onSubmit={handleSend} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={`Ask about ${patientName}'s medical data...`}
            style={{ flex: 1, padding: '12px 18px', borderRadius: '99px', border: '1px solid #cbd5e1', fontSize: '0.95rem' }}
            disabled={isLoading}
          />
          <button type="submit" className="btn-primary" style={{ borderRadius: '50%', width: '42px', height: '42px', padding: 0, justifyContent: 'center' }} disabled={isLoading || !inputQuery.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatView;
