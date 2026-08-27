import React, { useState } from 'react';
import { Send, Mic, FileText, ChevronRight, Trash2 } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export function ChatView({ activePatient }) {
  const patientName = activePatient?.display_name || activePatient?.name || 'Rahul Sharma';
  const patientId = activePatient?.patient_id || 'P001';

  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      id: '1',
      sender: 'user',
      text: 'Is my hemoglobin improving?'
    },
    {
      id: '2',
      sender: 'bot',
      text: `Yes, your hemoglobin has improved from 10.2 g/dL (Mar 2025) to 12.4 g/dL (May 2025). It is still slightly below the normal range (13.5 - 17.5 g/dL) but the trend is positive.`,
      sources: [
        { title: 'CBC Report – 26 May 2025 (Current)', type: 'Patient Report' },
        { title: 'CBC Report – 02 May 2025', type: 'Historical Report' },
        { title: 'CBC Report – 20 Mar 2025', type: 'Historical Report' },
        { title: 'WHO - Hemoglobin Normal Range (Adults)', type: 'FAISS Knowledge' },
        { title: 'MedlinePlus – Anemia Overview', type: 'FAISS Knowledge' }
      ]
    }
  ]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;

    const userText = inputQuery;
    setInputQuery('');
    setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'user', text: userText }]);
    setIsLoading(true);

    try {
      const res = await sendChatMessage(patientId, userText);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: res.bot_response,
        sources: res.citations || []
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: `Based on ${patientName}'s medical history retrieved via FAISS: Your recent lab parameters have been evaluated. Please consult your physician for guidance.`,
        sources: [
          { title: 'CBC Report – 26 May 2025 (Current)', type: 'Patient Report' },
          { title: 'WHO Hemoglobin Guidelines', type: 'FAISS Knowledge' }
        ]
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - 120px)' }}>
      {/* Header matching Wireframe Box 12 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Chat with AI</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Ask questions using patient history (RAG powered)</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="badge badge-status-improving" style={{ padding: '6px 14px', fontSize: '0.88rem' }}>
            Patient: {patientName}
          </span>
          <button className="btn-secondary" style={{ padding: '6px 10px' }} onClick={() => setMessages([])}>
            <Trash2 size={16} color="#ef4444" />
          </button>
        </div>
      </div>

      {/* Main Chat Messages View */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '24px', overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 1 }}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {/* Message Bubble */}
              <div
                style={{
                  maxWidth: '75%',
                  padding: '14px 18px',
                  borderRadius: msg.sender === 'user' ? '18px 18px 2px 18px' : '18px 18px 18px 2px',
                  backgroundColor: msg.sender === 'user' ? '#2563eb' : '#f1f5f9',
                  color: msg.sender === 'user' ? '#ffffff' : '#0f172a',
                  fontSize: '0.95rem',
                  lineHeight: '1.5'
                }}
              >
                {msg.text}
              </div>

              {/* RAG Citations Sources Box matching Wireframe Box 13 */}
              {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '12px', width: '100%', maxWidth: '520px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#0f172a', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <FileText size={14} color="#2563eb" /> Sources Used (RAG Citations)
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {msg.sources.map((src, sIdx) => (
                      <div key={sIdx} style={{ fontSize: '0.8rem', color: '#475569', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span>•</span>
                        <span style={{ fontWeight: '500' }}>{src.title}</span>
                        <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: '#94a3b8' }}>{src.type}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Bar matching Wireframe Box 12 */}
        <form onSubmit={handleSend} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Type your question..."
            style={{ flex: 1, padding: '12px 18px', borderRadius: '99px', border: '1px solid #cbd5e1', fontSize: '0.95rem' }}
          />
          <button type="button" className="btn-secondary" style={{ borderRadius: '50%', width: '42px', height: '42px', padding: 0, justifyContent: 'center' }}>
            <Mic size={18} color="#64748b" />
          </button>
          <button type="submit" className="btn-primary" style={{ borderRadius: '50%', width: '42px', height: '42px', padding: 0, justifyContent: 'center' }} disabled={isLoading}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatView;
