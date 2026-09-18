import React, { createContext, useState, useCallback, useRef } from 'react';
import { fetchPatients, createPatient, fetchPatientTimeline, fetchAnalysisSessions } from '../services/api';

export const PatientContext = createContext();

export const PatientProvider = ({ children }) => {
  const [patients, setPatients] = useState([]);
  const [activePatient, setActivePatient] = useState(null);
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [sessions, setSessions] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [activeAnalysisResult, setActiveAnalysisResult] = useState(null);
  const [reviewQuestions, setReviewQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Stale-response guard: tracks the currently selected patient ID
  const activePatientIdRef = useRef('');

  const resetAll = useCallback(() => {
    activePatientIdRef.current = '';
    setPatients([]);
    setActivePatient(null);
    setSelectedPatientId('');
    setSessions([]);
    setTimeline(null);
    setActiveAnalysisResult(null);
    setReviewQuestions([]);
    setIsLoading(false);
    setError(null);
  }, []);

  const loadPatients = useCallback(async (userId) => {
    try {
      const data = await fetchPatients(userId);
      setPatients(data);
      return data;
    } catch (err) {
      console.warn('Failed to load patients:', err);
      setPatients([]);
      return [];
    }
  }, []);

  const addPatient = useCallback(async (patientData) => {
    const created = await createPatient(patientData);
    setPatients((prev) => [created, ...prev]);
    return created;
  }, []);

  const selectPatient = useCallback((patientId) => {
    if (!patientId) {
      activePatientIdRef.current = '';
      setSelectedPatientId('');
      setActivePatient(null);
      setSessions([]);
      setTimeline(null);
      setActiveAnalysisResult(null);
      setReviewQuestions([]);
      return;
    }

    // Immediately clear previous patient's records
    activePatientIdRef.current = patientId;
    setSelectedPatientId(patientId);
    setSessions([]);
    setTimeline(null);
    setActiveAnalysisResult(null);
    setReviewQuestions([]);
    setError(null);

    const found = patients.find((p) => (p.patient_id || p.id) === patientId);
    setActivePatient(found || { patient_id: patientId, display_name: 'Patient' });
  }, [patients]);

  // Re-resolve activePatient when the patients list loads/changes
  // This handles the case where selectPatient was called before patients finished loading
  React.useEffect(() => {
    if (!selectedPatientId || patients.length === 0) return;
    const found = patients.find((p) => (p.patient_id || p.id) === selectedPatientId);
    if (found && activePatient?.display_name === 'Patient') {
      setActivePatient(found);
    }
  }, [patients, selectedPatientId]);

  const loadTimeline = useCallback(async (patientId) => {
    if (!patientId) {
      setTimeline(null);
      return null;
    }
    const targetPatientId = patientId;
    try {
      const data = await fetchPatientTimeline(targetPatientId);
      // Stale response check: discard if user switched to another patient
      if (activePatientIdRef.current === targetPatientId) {
        setTimeline(data);
      }
      return data;
    } catch (err) {
      if (activePatientIdRef.current === targetPatientId) {
        setTimeline(null);
      }
      return null;
    }
  }, []);

  const loadSessions = useCallback(async (patientId) => {
    if (!patientId) {
      setSessions([]);
      return [];
    }
    const targetPatientId = patientId;
    try {
      const data = await fetchAnalysisSessions(targetPatientId);
      // Stale response check: discard if user switched to another patient
      if (activePatientIdRef.current === targetPatientId) {
        setSessions(data);
      }
      return data;
    } catch (err) {
      if (activePatientIdRef.current === targetPatientId) {
        setSessions([]);
      }
      return [];
    }
  }, []);

  return (
    <PatientContext.Provider
      value={{
        patients,
        activePatient,
        selectedPatientId,
        sessions,
        timeline,
        activeAnalysisResult,
        reviewQuestions,
        isLoading,
        error,
        loadPatients,
        addPatient,
        selectPatient,
        loadTimeline,
        loadSessions,
        resetAll,
        setPatients,
        setActivePatient,
        setSelectedPatientId,
        setSessions,
        setTimeline,
        setActiveAnalysisResult,
        setReviewQuestions,
        setIsLoading,
        setError,
      }}
    >
      {children}
    </PatientContext.Provider>
  );
};

export default PatientContext;
