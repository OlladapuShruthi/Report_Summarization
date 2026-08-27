import React, { useState } from 'react';
import { Plus, CheckCircle2, User, Heart, Shield } from 'lucide-react';

export function PatientsView({ patients = [], activePatient, onSelectPatient, onCreatePatient }) {
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onCreatePatient({
      name,
      age: age ? parseInt(age, 10) : 30,
      gender,
    });
    setName('');
    setAge('');
    setShowModal(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Screen 4 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Select Active Patient</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Choose the patient to work with</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} /> Add Patient
        </button>
      </div>

      {/* Grid: Left Patient Selector Stack, Right Patient Details Card */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Left Patient Cards Stack */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a' }}>Patients</h3>

          {/* Rahul Sharma */}
          <div
            onClick={() => onSelectPatient && onSelectPatient('P001')}
            style={{
              padding: '16px',
              borderRadius: '12px',
              border: '2px solid #2563eb',
              backgroundColor: '#eff6ff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#2563eb', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600' }}>RS</div>
              <div>
                <div style={{ fontWeight: '600', color: '#0f172a' }}>Rahul Sharma</div>
                <div style={{ fontSize: '0.82rem', color: '#64748b' }}>32 Years, Male</div>
              </div>
            </div>
            <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle2 size={16} color="#fff" />
            </div>
          </div>

          {/* Meera Sharma */}
          <div
            onClick={() => onSelectPatient && onSelectPatient('P002')}
            style={{
              padding: '16px',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#475569', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600' }}>MS</div>
              <div>
                <div style={{ fontWeight: '600', color: '#0f172a' }}>Meera Sharma</div>
                <div style={{ fontSize: '0.82rem', color: '#64748b' }}>58 Years, Female</div>
              </div>
            </div>
            <div style={{ width: '20px', height: '20px', borderRadius: '50%', border: '2px solid #cbd5e1' }} />
          </div>

          {/* Arun Sharma */}
          <div
            onClick={() => onSelectPatient && onSelectPatient('P003')}
            style={{
              padding: '16px',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', backgroundColor: '#f1f5f9', color: '#475569', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600' }}>AS</div>
              <div>
                <div style={{ fontWeight: '600', color: '#0f172a' }}>Arun Sharma</div>
                <div style={{ fontSize: '0.82rem', color: '#64748b' }}>10 Years, Male</div>
              </div>
            </div>
            <div style={{ width: '20px', height: '20px', borderRadius: '50%', border: '2px solid #cbd5e1' }} />
          </div>
        </div>

        {/* Right Patient Details Card matching Wireframe Box 4 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a' }}>Patient Details</h3>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', paddingBottom: '16px', borderBottom: '1px solid #e2e8f0' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '50%', backgroundColor: '#2563eb', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: '700' }}>RS</div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>Rahul Sharma</h2>
              <p style={{ color: '#64748b', fontSize: '0.88rem' }}>32 Years, Male</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Blood Group</span>
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>O+</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Height</span>
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>175 cm</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Weight</span>
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>68 kg</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Allergies</span>
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.95rem' }}>None</div>
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Notes</span>
              <div style={{ fontWeight: '500', color: '#0f172a', fontSize: '0.9rem' }}>-</div>
            </div>
          </div>

          <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
            <span className="badge badge-status-improving" style={{ padding: '6px 16px', fontSize: '0.88rem' }}>
              Active Patient
            </span>
          </div>
        </div>
      </div>

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
                  placeholder="e.g. Rahul Sharma"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="e.g. 32"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Gender</label>
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
                <button type="submit" className="btn-primary">Save Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default PatientsView;
