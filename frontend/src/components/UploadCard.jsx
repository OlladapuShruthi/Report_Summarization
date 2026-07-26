import React, { useState, useRef } from 'react';
import { UploadCloud, FileCheck, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { quickStartAnalysis } from '../services/api';

export const UploadCard = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadMessage(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setUploadMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadMessage(null);

    try {
      const response = await quickStartAnalysis(selectedFile);
      setUploadMessage({
        type: 'success',
        text: `Workspace created! Workspace ID: ${response.analysis_id}`
      });
      setSelectedFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setUploadMessage({
        type: 'error',
        text: err.message || 'Failed to initialize analysis workspace.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 className="section-title">New Analysis Workspace</h2>
          <p className="section-desc">Upload a medical report (PDF/Image) to initialize an analysis workspace.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#06b6d4', fontSize: '0.85rem', fontWeight: 600 }}>
          <Sparkles size={16} />
          <span>Multi-Agent Ready</span>
        </div>
      </div>

      <div
        className={`dropzone ${isDragActive ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud className="upload-icon" />
        <p style={{ fontWeight: 600, fontSize: '1rem', color: '#e5e7eb' }}>
          {selectedFile ? selectedFile.name : 'Click or Drag & Drop Medical Report Here'}
        </p>
        <p style={{ fontSize: '0.82rem', color: '#6b7280', marginTop: '6px' }}>
          {selectedFile ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB` : 'PDF, PNG, JPG, JPEG (Max 25MB)'}
        </p>

        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
        />
      </div>

      {uploadMessage && (
        <div
          style={{
            marginTop: '16px',
            padding: '12px 16px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.88rem',
            background: uploadMessage.type === 'success' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
            border: uploadMessage.type === 'success' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
            color: uploadMessage.type === 'success' ? '#10b981' : '#f43f5e'
          }}
        >
          {uploadMessage.type === 'success' ? <FileCheck size={18} /> : <AlertCircle size={18} />}
          <span>{uploadMessage.text}</span>
        </div>
      )}

      <div style={{ textAlign: 'right', marginTop: '16px' }}>
        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
        >
          {isUploading ? (
            <>
              <Loader2 size={18} className="animate-spin" /> Creating Workspace...
            </>
          ) : (
            'Create Workspace & Upload'
          )}
        </button>
      </div>
    </div>
  );
};
