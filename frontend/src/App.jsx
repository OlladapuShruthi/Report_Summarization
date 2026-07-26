import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { StatusCard } from './components/StatusCard';
import { UploadCard } from './components/UploadCard';
import { DocumentList } from './components/DocumentList';
import { checkHealth, fetchAnalysisSessions } from './services/api';

export function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [sessions, setSessions] = useState([]);

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

  return (
    <div className="app-container">
      <Header healthStatus={healthStatus} />

      <StatusCard
        totalWorkspaces={sessions.length}
        healthStatus={healthStatus}
      />

      <UploadCard onUploadSuccess={loadData} />

      <DocumentList sessions={sessions} />
    </div>
  );
}

export default App;
