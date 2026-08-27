import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Screen Views
import LandingView from './components/LandingView';
import AuthView from './components/AuthView';
import DashboardView from './components/DashboardView';
import PatientsView from './components/PatientsView';
import ReportsView from './components/ReportsView';
import UploadModal from './components/UploadModal';
import ProcessingView from './components/ProcessingView';
import ResultsOverviewView from './components/ResultsOverviewView';
import ResultsDetailView from './components/ResultsDetailView';
import FindingsStatusView from './components/FindingsStatusView';
import TimelineView from './components/TimelineView';
import ChatView from './components/ChatView';
import SettingsView from './components/SettingsView';
import ExportModal from './components/ExportModal';
import LogoutView from './components/LogoutView';

import {
  checkHealth,
  fetchPatients,
  fetchAnalysisSessions,
  fetchPatientTimeline,
  fetchAnalysisResult,
  createPatient,
  parseAnalysisSession,
  analyzeAnalysisSession
} from './services/api';

// ─── Helper: restore persisted session ─────────────────────────────────────
function getStoredUser() {
  try {
    const raw = localStorage.getItem('med_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function App() {
  // ─── Auth state ───────────────────────────────────────────────────────────────
  const [currentUser, setCurrentUser] = useState(getStoredUser); // null = not logged in

  // ─── Navigation state ─────────────────────────────────────────────────────────
  // If user is already logged in (session restored), skip to dashboard
  const [currentView, setCurrentView] = useState(() => {
    return getStoredUser() ? 'dashboard' : 'landing';
  });
  // Track auth mode for when we go to the auth page
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'signup'

  // ─── Application Data state ───────────────────────────────────────────────────
  const [healthStatus, setHealthStatus] = useState(null);
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [activePatient, setActivePatient] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [activeAnalysisResult, setActiveAnalysisResult] = useState(null);

  // ─── Modal state ──────────────────────────────────────────────────────────────
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [activeParseId, setActiveParseId] = useState(null);
  const [activeAnalyzeId, setActiveAnalyzeId] = useState(null);

  // ─── Data fetching ────────────────────────────────────────────────────────────
  const loadData = async () => {
    if (!currentUser) return; // Don't fetch unless logged in
    try {
      const health = await checkHealth();
      setHealthStatus(health);

      // Pass user_id to scope patients to this account
      const fetchedPatients = await fetchPatients(currentUser.user_id);
      setPatients(fetchedPatients);

      // Auto-select first patient if none selected yet
      if (fetchedPatients.length > 0 && !selectedPatientId) {
        setSelectedPatientId(fetchedPatients[0].patient_id);
        setActivePatient(fetchedPatients[0]);
      }

      if (selectedPatientId) {
        const fetchedSessions = await fetchAnalysisSessions(selectedPatientId);
        setSessions(fetchedSessions);
      }
    } catch (error) {
      console.warn('Data load error (backend may be offline):', error);
    }
  };

  // Re-fetch whenever user logs in or selected patient changes
  useEffect(() => {
    loadData();
    if (!currentUser) return;
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, [currentUser, selectedPatientId]);

  // Sync active patient profile when selection changes
  useEffect(() => {
    if (selectedPatientId && patients.length > 0) {
      const found = patients.find((p) => p.patient_id === selectedPatientId);
      if (found) setActivePatient(found);
    }
  }, [selectedPatientId, patients]);

  // Load timeline when active patient changes
  useEffect(() => {
    if (!selectedPatientId) return;
    const loadTimeline = async () => {
      try {
        const data = await fetchPatientTimeline(selectedPatientId);
        setTimeline(data);
      } catch (err) {
        console.warn('Timeline load error:', err);
      }
    };
    loadTimeline();
  }, [selectedPatientId, sessions]);

  // ─── Auth handlers ────────────────────────────────────────────────────────────
  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    // Reset patient state for fresh account
    setPatients([]);
    setSelectedPatientId('');
    setActivePatient(null);
    setSessions([]);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('med_user');
    setCurrentUser(null);
    setPatients([]);
    setSelectedPatientId('');
    setActivePatient(null);
    setSessions([]);
    setCurrentView('logout');
  };

  // ─── Patient handlers ─────────────────────────────────────────────────────────
  const handleSelectPatient = (patientId) => {
    setSelectedPatientId(patientId);
    const found = patients.find((p) => p.patient_id === patientId);
    if (found) setActivePatient(found);
  };

  const handlePatientCreated = async (newPatientData) => {
    try {
      // Attach the current user's ID so it's scoped to this account
      const created = await createPatient({ ...newPatientData, user_id: currentUser?.user_id });
      setPatients((current) => [created, ...current]);
      setSelectedPatientId(created.patient_id);
      setActivePatient(created);
    } catch (err) {
      console.error('Create patient failed:', err);
      const mockCreated = {
        ...newPatientData,
        patient_id: `P_${Date.now()}`,
        user_id: currentUser?.user_id,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setPatients((current) => [mockCreated, ...current]);
      setSelectedPatientId(mockCreated.patient_id);
      setActivePatient(mockCreated);
    }
  };

  const handleParse = async (analysisId) => {
    setActiveParseId(analysisId);
    setCurrentView('processing');
    try {
      await parseAnalysisSession(analysisId);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setActiveParseId(null);
    }
  };

  const handleAnalyze = async (analysisId) => {
    setActiveAnalyzeId(analysisId);
    setCurrentView('processing');
    try {
      await analyzeAnalysisSession(analysisId);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setActiveAnalyzeId(null);
    }
  };

  const handleViewResult = async (analysisId) => {
    try {
      const resData = await fetchAnalysisResult(analysisId);
      setActiveAnalysisResult(resData);
      setCurrentView('results-overview');
    } catch (err) {
      setActiveAnalysisResult(null);
      setCurrentView('results-overview');
    }
  };

  // ─── Full-screen pages (no sidebar/navbar) ────────────────────────────────────

  if (currentView === 'landing') {
    return (
      <LandingView
        onGetStarted={() => { setAuthMode('login'); setCurrentView('auth'); }}
        onLogin={() => { setAuthMode('login'); setCurrentView('auth'); }}
        onSignUp={() => { setAuthMode('signup'); setCurrentView('auth'); }}
      />
    );
  }

  if (currentView === 'auth') {
    return (
      <AuthView
        initialMode={authMode}
        onLoginSuccess={handleLoginSuccess}
        onBackToHome={() => setCurrentView('landing')}
      />
    );
  }

  if (currentView === 'logout') {
    return (
      <LogoutView
        onLoginAgain={() => { setAuthMode('login'); setCurrentView('auth'); }}
        onBackHome={() => setCurrentView('landing')}
      />
    );
  }

  // ─── Main app shell (navbar + sidebar + content) ──────────────────────────────
  return (
    <div className="app-layout">
      <Navbar
        healthStatus={healthStatus}
        currentUser={currentUser}
        activePatient={activePatient}
        onSelectView={setCurrentView}
        onOpenUpload={() => setShowUploadModal(true)}
        onLogout={handleLogout}
      />

      <div className="app-main-body">
        <Sidebar
          currentView={currentView}
          onSelectView={setCurrentView}
          activePatient={activePatient}
        />

        <main className="app-content-viewport">
          {currentView === 'dashboard' && (
            <DashboardView
              currentUser={currentUser}
              patients={patients}
              activePatient={activePatient}
              sessions={sessions}
              onSelectPatient={handleSelectPatient}
              onSelectView={setCurrentView}
              onOpenUpload={() => setShowUploadModal(true)}
              onViewResult={handleViewResult}
              onCreatePatient={handlePatientCreated}
            />
          )}

          {currentView === 'patients' && (
            <PatientsView
              patients={patients}
              activePatient={activePatient}
              onSelectPatient={handleSelectPatient}
              onCreatePatient={handlePatientCreated}
              onSelectView={setCurrentView}
            />
          )}

          {currentView === 'reports' && (
            <ReportsView
              sessions={sessions}
              activePatient={activePatient}
              activeParseId={activeParseId}
              activeAnalyzeId={activeAnalyzeId}
              onOpenUpload={() => setShowUploadModal(true)}
              onParse={handleParse}
              onAnalyze={handleAnalyze}
              onViewResult={handleViewResult}
              onSelectView={setCurrentView}
            />
          )}

          {currentView === 'processing' && (
            <ProcessingView
              onComplete={() => setCurrentView('results-overview')}
            />
          )}

          {currentView === 'results-overview' && (
            <ResultsOverviewView
              result={activeAnalysisResult}
              activePatient={activePatient}
              onViewFullDetails={() => setCurrentView('results-detail')}
              onOpenExport={() => setShowExportModal(true)}
              onAskAI={() => setCurrentView('chat')}
            />
          )}

          {currentView === 'results-detail' && (
            <ResultsDetailView
              result={activeAnalysisResult}
              activePatient={activePatient}
              onBack={() => setCurrentView('results-overview')}
              onOpenExport={() => setShowExportModal(true)}
              onSelectTab={(tab) => {
                if (tab === 'Overview') setCurrentView('results-overview');
                if (tab === 'Comparison') setCurrentView('findings');
              }}
            />
          )}

          {currentView === 'findings' && (
            <FindingsStatusView
              result={activeAnalysisResult}
            />
          )}

          {currentView === 'timeline' && (
            <TimelineView
              timeline={timeline}
              activePatient={activePatient}
              onViewResult={handleViewResult}
            />
          )}

          {currentView === 'chat' && (
            <ChatView
              activePatient={activePatient}
            />
          )}

          {currentView === 'settings' && (
            <SettingsView
              currentUser={currentUser}
              activePatient={activePatient}
              onLogout={handleLogout}
            />
          )}
        </main>
      </div>

      {/* Global Modals */}
      {showUploadModal && (
        <UploadModal
          activePatient={activePatient}
          onClose={() => setShowUploadModal(false)}
          onUploadSuccess={() => {
            loadData();
            setShowUploadModal(false);
            setCurrentView('processing');
          }}
          onSelectPatientView={() => setCurrentView('patients')}
        />
      )}

      {showExportModal && (
        <ExportModal
          onClose={() => setShowExportModal(false)}
        />
      )}
    </div>
  );
}

export default App;
