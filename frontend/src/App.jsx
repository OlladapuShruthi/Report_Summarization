import React, { useState, useEffect, useContext, useRef } from 'react';
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
import ReviewRequiredView from './components/ReviewRequiredView';

import {
  checkHealth,
  fetchPatients,
  fetchAnalysisSessions,
  fetchPatientTimeline,
  fetchAnalysisResult,
  createPatient,
  parseAnalysisSession,
  analyzeAnalysisSession,
} from './services/api';

import { AuthContext } from './context/AuthContext';
import { PatientContext } from './context/PatientContext';

export function App() {
  // Auth context
  const { authUser, logout } = useContext(AuthContext);

  // Patient context
  const {
    patients,
    activePatient,
    selectedPatientId,
    sessions,
    timeline,
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
  } = useContext(PatientContext);

  // Listen for global 401 token expiry to cleanly wipe patient state & route to login
  useEffect(() => {
    const handleUnauthorized = () => {
      resetAll();
      logout();
      setCurrentView('auth');
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [logout, resetAll]);

  // Navigation state
  const [currentView, setCurrentView] = useState(() => (authUser ? 'dashboard' : 'landing'));
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'signup'
  const [healthStatus, setHealthStatus] = useState(null);

  // Modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [activeParseId, setActiveParseId] = useState(null);
  const [activeAnalyzeId, setActiveAnalyzeId] = useState(null);
  const [activeAnalysisResult, setActiveAnalysisResult] = useState(null);

  // Load health and patient data when authenticated
  useEffect(() => {
    const loadData = async () => {
      if (!authUser) return;
      try {
        const health = await checkHealth();
        setHealthStatus(health);
        const fetchedPatients = await loadPatients(authUser.user_id);
        // Auto-select first patient if none selected
        if (fetchedPatients.length > 0 && !selectedPatientId) {
          selectPatient(fetchedPatients[0].patient_id);
        }
        if (selectedPatientId) {
          const fetchedSessions = await loadSessions(selectedPatientId);
          setSessions(fetchedSessions);
        }
      } catch (error) {
        console.warn('Data load error (backend may be offline):', error);
      }
    };
    loadData();
    if (authUser) {
      const interval = setInterval(loadData, 15000);
      return () => clearInterval(interval);
    }
  }, [authUser, selectedPatientId]);

  // Sync timeline when patient changes
  useEffect(() => {
    if (!selectedPatientId) return;
    const load = async () => {
      try {
        const data = await loadTimeline(selectedPatientId);
        setTimeline(data);
      } catch (err) {
        console.warn('Timeline load error:', err);
      }
    };
    load();
  }, [selectedPatientId]);

  // Store the most recent upload session so we can fetch its result after processing
  const [latestUploadSession, setLatestUploadSession] = useState(null);
  // Track whether view change came from browser back/forward to avoid re-pushing
  const isPopStateNav = useRef(false);

  // Sync navigation history with browser back/forward
  useEffect(() => {
    if (isPopStateNav.current) {
      // This view change came from browser back/forward — don't push again
      isPopStateNav.current = false;
      return;
    }
    // Use replaceState for transient views (processing) to avoid polluting history
    const transientViews = ['processing'];
    if (transientViews.includes(currentView)) {
      window.history.replaceState({ view: currentView }, '');
    } else {
      window.history.pushState({ view: currentView }, '');
    }
  }, [currentView]);

  useEffect(() => {
    const onPopState = (e) => {
      isPopStateNav.current = true;
      if (e.state && e.state.view) {
        setCurrentView(e.state.view);
      } else {
        setCurrentView(authUser ? 'dashboard' : 'landing');
      }
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, [authUser]);


  // Handlers
  const handleLogout = () => {
    resetAll();
    logout();
    setCurrentView('landing');
  };

  // Create-patient handler (used by DashboardView & PatientsView)
  const handlePatientCreated = async (patientData) => {
    try {
      const created = await addPatient(patientData);
      if (created?.patient_id) {
        selectPatient(created.patient_id);
      }
      return created;
    } catch (err) {
      console.error('Failed to create patient:', err);
      throw err;
    }
  };

  // Handler for successful upload, store session for later result fetching
  const handleUploadSuccess = (session) => {
    setLatestUploadSession(session);
    // After upload, navigate to processing view
    setCurrentView('processing');
  };

  // Called when processing view signals completion
  const handleCompleteProcessing = async (result) => {
    if (result) {
      setActiveAnalysisResult(result);
    }
    if (selectedPatientId) {
      loadSessions(selectedPatientId).then(setSessions).catch(console.warn);
    }
    setCurrentView('results-overview');
  };

  const handleReviewRequired = async (analysisId) => {
    try {
      const resData = await fetchAnalysisResult(analysisId);
      setActiveAnalysisResult(resData);
    } catch (err) {
      console.warn('Failed to fetch analysis result for review:', err);
    }
    if (selectedPatientId) {
      loadSessions(selectedPatientId).then(setSessions).catch(console.warn);
    }
    setCurrentView('review');
  };

  // Existing upload success handling in modal
  // Updated prop passed below

  const handleParse = async (analysisId) => {
    setActiveParseId(analysisId);
    setLatestUploadSession({ analysis_id: analysisId });
    setCurrentView('processing');
  };

  const handleAnalyze = async (analysisId) => {
    setActiveAnalyzeId(analysisId);
    setLatestUploadSession({ analysis_id: analysisId });
    setCurrentView('processing');
  };

  const handleViewResult = async (analysisId) => {
    try {
      const resData = await fetchAnalysisResult(analysisId);
      setActiveAnalysisResult(resData);
    } catch (err) {
      setActiveAnalysisResult(null);
    }
    setCurrentView('results-overview');
  };

  // Full-screen pages
  // Sync currentView with auth state
  useEffect(() => {
    if (!authUser) {
      // User logged out → send to landing
      setCurrentView('landing');
    } else if (currentView === 'auth' || currentView === 'landing') {
      // User just logged in but view is still auth/landing → send to dashboard
      setCurrentView('dashboard');
    }
  }, [authUser]); // eslint-disable-line react-hooks/exhaustive-deps

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
        onLoginSuccess={(user) => {
          // AuthContext will already have set authUser via login function, but we also need to update local state
          // Here we simply rely on authUser from context; ensure view switches
          setCurrentView('dashboard');
        }}
        onBackToHome={() => setCurrentView('landing')}
      />
    );
  }

  // Main app shell
  return (
    <div className="app-layout">
      <Navbar
        healthStatus={healthStatus}
        currentUser={authUser}
        activePatient={activePatient}
        onSelectView={setCurrentView}
        onOpenUpload={() => setShowUploadModal(true)}
        onLogout={handleLogout}
      />

      <div className="app-main-body">
        <Sidebar
          currentView={currentView}
          onSelectView={setCurrentView}
        />

        <main className="app-content-viewport">
          {currentView === 'dashboard' && (
            <DashboardView
              currentUser={authUser}
              patients={patients}
              activePatient={activePatient}
              sessions={sessions}
              onSelectPatient={selectPatient}
              onSelectView={setCurrentView}
              onOpenUpload={() => setShowUploadModal(true)}
              onViewResult={handleViewResult}
              onCreatePatient={handlePatientCreated}
            />
          )}

          {currentView === 'patients' && (
            <PatientsView
              patients={patients}
              activePatient={activePatient?.patient_id || activePatient}
              onSelectPatient={selectPatient}
              onCreatePatient={handlePatientCreated}
              onSelectView={setCurrentView}
            />
          )}

          {currentView === 'reports' && (
            selectedPatientId ? (
              <ReportsView
                sessions={sessions}
                activePatient={activePatient}
                onOpenUpload={() => setShowUploadModal(true)}
                onParse={handleParse}
                onAnalyze={handleAnalyze}
                onViewResult={handleViewResult}
                onSelectView={setCurrentView}
              />
            ) : (
              <PatientsView
                patients={patients}
                activePatient={activePatient}
                onSelectPatient={(id) => { selectPatient(id); setCurrentView('reports'); }}
                onCreatePatient={handlePatientCreated}
                onSelectView={setCurrentView}
              />
            )
          )}

          {/* ProcessingView is rendered outside <main> below to overlay correctly */}

          {currentView === 'results-overview' && (
            <ResultsOverviewView
              result={activeAnalysisResult}
              activePatient={activePatient}
              onViewFullDetails={() => setCurrentView('results-detail')}
              onOpenExport={() => setShowExportModal(true)}
              onAskAI={() => setCurrentView('chat')}
              onSelectReview={() => setCurrentView('review')}
            />
          )}

          {currentView === 'review' && (
            <ReviewRequiredView
              activePatient={activePatient}
              activeAnalysisId={activeAnalysisResult?.analysis_id}
              reviewResult={activeAnalysisResult}
              onBack={() => setCurrentView('results-overview')}
              onReviewAnswered={async () => {
                if (activeAnalysisResult?.analysis_id) {
                  try {
                    const updated = await fetchAnalysisResult(activeAnalysisResult.analysis_id);
                    setActiveAnalysisResult(updated);
                  } catch (e) {
                    console.warn(e);
                  }
                }
                if (selectedPatientId) {
                  const refreshed = await loadSessions(selectedPatientId);
                  setSessions(refreshed);
                }
                setCurrentView('results-overview');
              }}
              onFollowUpUploaded={async (followUpResult) => {
                if (selectedPatientId) {
                  const refreshed = await loadSessions(selectedPatientId);
                  setSessions(refreshed);
                }
                if (followUpResult?.analysis_id) {
                  setActiveAnalysisResult(followUpResult);
                }
                setCurrentView('results-overview');
              }}
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
            <FindingsStatusView result={activeAnalysisResult} />
          )}

          {currentView === 'timeline' && (
            selectedPatientId ? (
              <TimelineView
                timeline={timeline}
                activePatient={activePatient}
                onViewResult={handleViewResult}
              />
            ) : (
              <PatientsView
                patients={patients}
                activePatient={activePatient}
                onSelectPatient={(id) => { selectPatient(id); setCurrentView('timeline'); }}
                onCreatePatient={handlePatientCreated}
                onSelectView={setCurrentView}
              />
            )
          )}

          {currentView === 'chat' && (
            selectedPatientId ? (
              <ChatView activePatient={activePatient} />
            ) : (
              <PatientsView
                patients={patients}
                activePatient={activePatient}
                onSelectPatient={(id) => { selectPatient(id); setCurrentView('chat'); }}
                onCreatePatient={handlePatientCreated}
                onSelectView={setCurrentView}
              />
            )
          )}

          {currentView === 'processing' && (
            <ProcessingView 
              analysisId={latestUploadSession?.analysis_id || latestUploadSession?.session_id || activeParseId || activeAnalyzeId}
              patientName={activePatient?.display_name || activePatient?.name}
              onComplete={handleCompleteProcessing} 
              onReviewRequired={handleReviewRequired}
              onError={(err) => console.error("Pipeline Error:", err)}
            />
          )}

          {currentView === 'settings' && (
            <SettingsView
              currentUser={authUser}
              activePatient={activePatient}
              onLogout={handleLogout}
            />
          )}
        </main>
      </div>

      {showUploadModal && (
        <UploadModal
          activePatient={activePatient}
          onClose={() => setShowUploadModal(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      )}

      {showExportModal && (
        <ExportModal onClose={() => setShowExportModal(false)} />
      )}
    </div>
  );
}

export default App;
