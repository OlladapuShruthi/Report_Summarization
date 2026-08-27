import React from 'react';
import { Download, Share2, X, FileText, FileCode } from 'lucide-react';

export function ExportModal({ onClose }) {
  const handleDownload = (filename) => {
    const element = document.createElement("a");
    const file = new Blob(["Medical Report Data"], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '520px', width: '100%', padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>Export / Download</h2>
            <p style={{ fontSize: '0.88rem', color: '#64748b' }}>Download reports or share results</p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div className="card" onClick={() => handleDownload("Report.pdf")} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px', cursor: 'pointer' }}>
            <FileText size={20} color="#2563eb" />
            <span style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>Download Report (PDF)</span>
            <Download size={18} color="#64748b" style={{ marginLeft: 'auto' }} />
          </div>

          <div className="card" onClick={() => handleDownload("Analysis_Summary.pdf")} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px', cursor: 'pointer' }}>
            <FileText size={20} color="#15803d" />
            <span style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>Download Analysis Summary (PDF)</span>
            <Download size={18} color="#64748b" style={{ marginLeft: 'auto' }} />
          </div>

          <div className="card" onClick={() => handleDownload("results.json")} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px', cursor: 'pointer' }}>
            <FileCode size={20} color="#0369a1" />
            <span style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>Download All Results (JSON)</span>
            <Download size={18} color="#64748b" style={{ marginLeft: 'auto' }} />
          </div>

          <div className="card" onClick={() => alert("Shareable link copied!")} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px', cursor: 'pointer' }}>
            <Share2 size={20} color="#2563eb" />
            <span style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>Share Report Link</span>
            <Share2 size={18} color="#64748b" style={{ marginLeft: 'auto' }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExportModal;
