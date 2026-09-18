import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { PatientContext } from '../context/PatientContext';
import {
  FileText,
  AlertTriangle,
  Stethoscope,
  Calendar,
  Plus,
  User,
  ChevronRight,
  Clock,
  X,
} from 'lucide-react';

function AddPatientModal({ onClose, onSubmit }) {
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [sex, setSex] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    await onSubmit({ display_name: name.trim(), date_of_birth: dob || null, sex: sex || null });
    setLoading(false);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '440px', width: '100%', padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a' }}>Add Patient</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '5px' }}>Patient Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Jane Doe"
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem', boxSizing: 'border-box' }}
              required
              autoFocus
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '5px' }}>Date of Birth / Age</label>
            <input
              type="text"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              placeholder="e.g. 1992-05-14 or 32 years"
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '5px' }}>Gender</label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
            >
              <option value="">Select Gender</option>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '11px', marginTop: '4px' }}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Patient'}
          </button>
        </form>
      </div>
    </div>
  );
}

function getInitials(name = '') {
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?';
}

export function DashboardView({
  onSelectPatient,
  onSelectView,
  onOpenUpload,
  onViewResult,
  onCreatePatient,
}) {
  const [showAddModal, setShowAddModal] = useState(false);
  const { authUser } = useContext(AuthContext);
  const { patients, activePatient, sessions } = useContext(PatientContext);
  const userName = authUser?.full_name?.split(' ')[0] || 'there';

  // Total reports & findings strictly derived from real data
  const totalReports = sessions ? sessions.length : 0;
  const abnormalCount = (sessions || []).filter(s =>
    (s.risk_assessment?.risk_level || '').toLowerCase().includes('high') ||
    ((s.abnormal_findings || []).length > 0)
  ).length;

  // Reorder patients: active first
  const sortedPatients = activePatient
    ? [activePatient, ...patients.filter(p => p.patient_id !== activePatient.patient_id)]
    : patients;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Welcome, {userName}!</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '2px' }}>Manage your patients and track their health history.</p>
        </div>
      </div>

      {/* My Patients Section */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a' }}>My Patients</h2>
          <button className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }} onClick={() => setShowAddModal(true)}>
            <Plus size={15} /> Add Patient
          </button>
        </div>

        {patients.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: '#64748b' }}>
            <User size={40} color="#cbd5e1" style={{ marginBottom: '12px' }} />
            <p style={{ fontWeight: '600', color: '#0f172a', marginBottom: '4px' }}>No patients yet</p>
            <p style={{ fontSize: '0.88rem' }}>Add your first patient profile to start tracking health records.</p>
            <button className="btn-primary" style={{ marginTop: '16px' }} onClick={() => setShowAddModal(true)}>
              <Plus size={15} /> Add First Patient
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
            {sortedPatients.map((patient) => {
              const isActive = activePatient?.patient_id === patient.patient_id;
              return (
                <div
                  key={patient.patient_id}
                  onClick={() => onSelectPatient && onSelectPatient(patient.patient_id)}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    border: isActive ? '2px solid #2563eb' : '1px solid #e2e8f0',
                    backgroundColor: isActive ? '#eff6ff' : '#ffffff',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    transition: 'border-color 0.15s',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '50%',
                      backgroundColor: isActive ? '#2563eb' : '#f1f5f9',
                      color: isActive ? '#fff' : '#475569',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: '700', fontSize: '0.85rem'
                    }}>
                      {getInitials(patient.display_name)}
                    </div>
                    <div>
                      <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.92rem' }}>{patient.display_name}</div>
                      <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                        {patient.date_of_birth ? `DOB: ${patient.date_of_birth}` : '—'}
                        {patient.sex ? ` | ${patient.sex.charAt(0) + patient.sex.slice(1).toLowerCase()}` : ''}
                      </div>
                    </div>
                  </div>
                  <button
                    className={isActive ? 'btn-primary' : 'btn-outline-blue'}
                    style={{ width: '100%', justifyContent: 'center', padding: '6px 10px', fontSize: '0.82rem' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectPatient && onSelectPatient(patient.patient_id);
                      onSelectView('reports');
                    }}
                  >
                    Open {isActive && <ChevronRight size={14} />}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Health Summary KPIs */}
      <div>
        <h2 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a', marginBottom: '14px' }}>
          Health Summary {activePatient ? `— ${activePatient.display_name}` : '(All Patients)'}
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '18px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileText size={20} />
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>{totalReports}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Reports</div>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '18px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: '#fff7ed', color: '#c2410c', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AlertTriangle size={20} />
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#c2410c' }}>{abnormalCount}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Abnormal Findings</div>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '18px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Stethoscope size={20} />
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>{patients.length}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Patients</div>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '18px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: '#f0fdf4', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Calendar size={20} />
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#15803d' }}>0</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Upcoming Follow-ups</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses — from backend sessions */}
      {sessions.length > 0 && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a' }}>Recent Activity</h2>
            <button className="btn-outline-blue" onClick={() => onSelectView('reports')}>View All Reports</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {sessions.slice(0, 5).map((s) => (
              <div key={s.analysis_id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '10px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileText size={18} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.9rem' }}>{s.title || 'Medical Report'}</div>
                  <div style={{ fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} /> {s.created_at ? new Date(s.created_at).toLocaleDateString() : '—'}
                  </div>
                </div>
                <span className={`badge ${s.status === 'ANALYZED' ? 'badge-improving' : 'badge-status-normal'}`} style={{ fontSize: '0.75rem' }}>
                  {s.status || 'Uploaded'}
                </span>
                {s.status === 'ANALYZED' && (
                  <button className="btn-outline-blue" style={{ padding: '4px 10px', fontSize: '0.78rem' }} onClick={() => onViewResult(s.analysis_id)}>
                    View
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Patient Modal */}
      {showAddModal && (
        <AddPatientModal
          onClose={() => setShowAddModal(false)}
          onSubmit={onCreatePatient}
        />
      )}
    </div>
  );
}

export default DashboardView;
