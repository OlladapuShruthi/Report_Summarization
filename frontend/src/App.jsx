import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { StatusCard } from './components/StatusCard';
import { ProjectRoadmap } from './components/ProjectRoadmap';
import { UploadCard } from './components/UploadCard';
import { DocumentList } from './components/DocumentList';
import { checkHealth, fetchAnalysisSessions, parseAnalysisSession } from './services/api';

export function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeParseId, setActiveParseId] = useState(null);

  const loadData = async () => {
    const health = await checkHealth();
    setHealthStatus(health);

    const fetchedSessions = await fetchAnalysisSessions();
    setSessions(fetchedSessions);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleParse = async (analysisId) => {
    setActiveParseId(analysisId);
    try {
      await parseAnalysisSession(analysisId);
      await loadData();
    } finally {
      setActiveParseId(null);
    }
  };

  return (
    <div className="app-container">
      <Header healthStatus={healthStatus} />

      <StatusCard
        totalWorkspaces={sessions.length}
        healthStatus={healthStatus}
        sessions={sessions}
      />

      <ProjectRoadmap sessions={sessions} />

      <UploadCard onUploadSuccess={loadData} />

      <DocumentList
        sessions={sessions}
        activeParseId={activeParseId}
        onParse={handleParse}
      />
    </div>
  );
}

export default App;
