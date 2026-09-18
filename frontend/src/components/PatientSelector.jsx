import React, { useState } from 'react';
import { Plus, Users } from 'lucide-react';
import { createPatient } from '../services/api';

export const PatientSelector = ({ patients, selectedPatientId, onSelect, onCreated }) => {
  const [name, setName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');

  const createProfile = async (event) => {
    event.preventDefault();
    if (!name.trim()) return;
    setIsCreating(true);
    setError('');
    try {
      const patient = await createPatient({ display_name: name.trim() });
      setName('');
      onCreated(patient);
    } catch (err) {
      setError(err.message || 'Could not create the patient profile.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <section className="patient-card">
      <div>
        <h2 className="section-title"><Users size={18} /> Patient context</h2>
        <p className="section-desc">Every report is scoped to one patient, keeping future history, comparison, and chat retrieval isolated.</p>
      </div>
      <div className="patient-controls">
        <label>
          Selected patient
          <select value={selectedPatientId} onChange={(event) => onSelect(event.target.value)}>
            <option value="">Choose a patient</option>
            {patients.map((patient) => <option key={patient.patient_id} value={patient.patient_id}>{patient.display_name}</option>)}
          </select>
        </label>
        <form onSubmit={createProfile} className="patient-create-form">
          <label>
            New patient name
            <input value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. John Doe" maxLength="120" />
          </label>
          <button type="submit" className="patient-add-btn" disabled={isCreating || !name.trim()}><Plus size={16} /> {isCreating ? 'Creating' : 'Add patient'}</button>
        </form>
      </div>
      {error && <p className="patient-error">{error}</p>}
    </section>
  );
};
