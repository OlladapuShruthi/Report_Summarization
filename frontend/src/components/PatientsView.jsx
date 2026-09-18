import React, { useState } from 'react';
import { Plus, CheckCircle2, User, UserPlus } from 'lucide-react';

export function PatientsView({ patients = [], activePatient, onSelectPatient, onCreatePatient }) {
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onCreatePatient({
      display_name: name.trim(),
      date_of_birth: age ? `Age: ${age}` : undefined,
      sex: gender.toUpperCase(),
    });
    setName('');
    setAge('');
    setShowModal(false);
  };

  const selectedPatientObj = patients.find(p => p.patient_id === activePatient) || patients[0];

  const getInitials = (nameStr) => {
    if (!nameStr) return 'P';
    const parts = nameStr.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return nameStr.substring(0, 2).toUpperCase();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Screen 4 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Patient Management</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Select an active patient or create a new profile</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} /> Add Patient
        </button>
      </div>

      {/* Grid: Left Patient Selector Stack, Right Patient Details Card */}
      {patients.length === 0 ? (
        <div className="card" style={{ padding: '48px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <UserPlus size={32} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>No Patient Profiles Found</h3>
            <p style={{ color: '#64748b', fontSize: '0.92rem', maxWidth: '400px' }}>
              Your account currently has no patient profiles. Click "Add Patient" to create a new profile and start managing medical records.
            </p>
          </div>
          <button className="btn-primary" onClick={() => setShowModal(true)} style={{ marginTop: '8px' }}>
            <Plus size={16} /> Add First Patient
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Left Patient Cards Stack */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a' }}>Patients ({patients.length})</h3>

            {patients.map((p) => {
              const pId = p.patient_id || p.id;
              const isSelected = activePatient === pId || (!activePatient && selectedPatientObj?.patient_id === pId);
              return (
                <div
                  key={pId}
                  onClick={() => onSelectPatient && onSelectPatient(pId)}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                    backgroundColor: isSelected ? '#eff6ff' : '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '50%',
                      backgroundColor: isSelected ? '#2563eb' : '#f1f5f9',
                      color: isSelected ? '#fff' : '#475569',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: '600'
                    }}>
                      {getInitials(p.display_name || p.name)}
                    </div>
                    <div>
                      <div style={{ fontWeight: '600', color: '#0f172a' }}>{p.display_name || p.name}</div>
                      <div style={{ fontSize: '0.82rem', color: '#64748b' }}>
                        {p.sex || p.gender || 'Patient'} {p.date_of_birth ? `• ${p.date_of_birth}` : ''}
                      </div>
                    </div>
                  </div>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    border: isSelected ? 'none' : '2px solid #cbd5e1',
                    backgroundColor: isSelected ? '#2563eb' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {isSelected && <CheckCircle2 size={16} color="#fff" />}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Patient Details Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a' }}>Patient Profile Details</h3>

            {selectedPatientObj ? (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', paddingBottom: '16px', borderBottom: '1px solid #e2e8f0' }}>
                  <div style={{ width: '56px', height: '56px', borderRadius: '50%', backgroundColor: '#2563eb', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: '700' }}>
                    {getInitials(selectedPatientObj.display_name || selectedPatientObj.name)}
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>{selectedPatientObj.display_name || selectedPatientObj.name}</h2>
                    <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
                      Sex: {selectedPatientObj.sex || selectedPatientObj.gender || 'Unspecified'}
                    </p>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Patient ID</span>
                    <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                      {selectedPatientObj.patient_id || selectedPatientObj.id || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Date of Birth</span>
                    <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>
                      {selectedPatientObj.date_of_birth || 'Not Specified'}
                    </div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Profile Created</span>
                    <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.85rem' }}>
                      {selectedPatientObj.created_at ? new Date(selectedPatientObj.created_at).toLocaleDateString() : 'Today'}
                    </div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Medical Reports</span>
                    <div style={{ fontWeight: '600', color: '#2563eb', fontSize: '0.95rem' }}>
                      0 Reports
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="badge badge-status-improving" style={{ padding: '6px 16px', fontSize: '0.88rem' }}>
                    Active Workspace Context
                  </span>
                </div>
              </>
            ) : (
              <div style={{ color: '#64748b', textAlign: 'center', padding: '24px 0' }}>
                Select a patient from the list to view details.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Patient Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '440px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '16px' }}>Add Patient Profile</h3>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Patient Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Alice Smith"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Date of Birth / Age (Optional)</label>
                <input
                  type="text"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="e.g. 1990-05-15 or 35"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Sex</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Patient Profile</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default PatientsView;

