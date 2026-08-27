import React, { useState } from 'react';
import { UploadCloud, File, X, AlertTriangle, User } from 'lucide-react';
import { quickStartAnalysis } from '../services/api';

export function UploadModal({ activePatient, onClose, onUploadSuccess, onSelectPatientView }) {
  const [file, setFile] = useState(null);
  const [reportType, setReportType] = useState('Select Type');
  const [reportDate, setReportDate] = useState('2026-07-26');
  const [notes, setNotes] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const patientId = activePatient?.patient_id || null;
  const patientName = activePatient?.display_name || activePatient?.name || null;

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientId) return;

    setIsUploading(true);
    try {
      if (file) {
        await quickStartAnalysis(file, patientId);
      }
      onUploadSuccess();
      onClose();
    } catch (err) {
      onUploadSuccess();
      onClose();
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '800px', width: '100%', padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>Upload Medical Report</h2>
            {patientName ? (
              <p style={{ fontSize: '0.88rem', color: '#2563eb', fontWeight: '600', marginTop: '2px' }}>
                Target Patient: {patientName}
              </p>
            ) : (
              <p style={{ fontSize: '0.88rem', color: '#c2410c', fontWeight: '600', marginTop: '2px' }}>
                ⚠️ No Active Patient Selected
              </p>
            )}
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>

        {/* UI Rule 7 Guard: If no patient is selected */}
        {!patientId ? (
          <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fdba74', borderRadius: '12px', padding: '24px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <AlertTriangle size={36} color="#c2410c" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#9a3412', marginBottom: '4px' }}>Please Select or Create a Patient First</h3>
              <p style={{ fontSize: '0.88rem', color: '#c2410c' }}>
                Reports must be associated with a specific patient profile to maintain strict health history isolation.
              </p>
            </div>
            <button
              className="btn-primary"
              onClick={() => {
                onClose();
                if (onSelectPatientView) onSelectPatientView();
              }}
            >
              <User size={16} /> Go to Patient Selection
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
              {/* Dropzone Area */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', border: '2px dashed #cbd5e1', backgroundColor: '#f8fafc', padding: '32px 16px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                  <UploadCloud size={24} />
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#0f172a', marginBottom: '4px' }}>Drag & Drop File</h3>
                <p style={{ fontSize: '0.88rem', color: '#475569', marginBottom: '12px' }}>or Browse Files</p>

                <label className="btn-outline-blue" style={{ cursor: 'pointer', display: 'inline-block' }}>
                  Browse Files
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileChange} style={{ display: 'none' }} />
                </label>

                {file ? (
                  <div style={{ marginTop: '12px', fontSize: '0.82rem', color: '#15803d', fontWeight: '600' }}>
                    Selected: {file.name}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '16px' }}>
                    PDF / JPG / PNG
                  </div>
                )}
              </div>

              {/* Form details area */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '14px', padding: '20px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#0f172a' }}>Report Details</h3>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Report Type</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.88rem' }}
                  >
                    <option value="Select Type">Select Type</option>
                    <option value="CBC Report">CBC Report</option>
                    <option value="Lipid Profile">Lipid Profile</option>
                    <option value="Thyroid Profile">Thyroid Profile</option>
                    <option value="Radiology">Radiology</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Report Date</label>
                  <input
                    type="date"
                    value={reportDate}
                    onChange={(e) => setReportDate(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.88rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Notes (Optional)</label>
                  <textarea
                    rows="3"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add optional notes..."
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.88rem' }}
                  />
                </div>

                <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: 'auto', padding: '10px' }} disabled={isUploading}>
                  {isUploading ? 'Uploading...' : 'Upload Report'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default UploadModal;
