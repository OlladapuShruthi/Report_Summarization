import React from 'react';
import { Stethoscope, Activity, Database } from 'lucide-react';

export const Header = ({ healthStatus }) => {
  const isHealthy = healthStatus?.status === 'healthy';
  const isDbConnected = healthStatus?.database === 'connected';
  const dbName = healthStatus?.database_name || 'Mreport';

  return (
    <header className="header">
      <div className="brand">
        <div className="brand-icon">
          <Stethoscope size={24} />
        </div>
        <div>
          <h1 className="brand-title">Medical Report Assistant</h1>
          <p className="brand-subtitle">AI Multi-Agent Workspace & Clinical Intelligence</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <div className="status-badge">
          <Activity size={14} color="#3b82f6" />
          <span>API Server:</span>
          <span className={`dot ${isHealthy ? 'green' : 'red'}`}></span>
          <span style={{ color: isHealthy ? '#10b981' : '#f43f5e' }}>
            {isHealthy ? 'Online' : 'Offline'}
          </span>
        </div>

        <div className="status-badge">
          <Database size={14} color="#10b981" />
          <span>MongoDB Atlas ({dbName}):</span>
          <span className={`dot ${isDbConnected ? 'green' : 'amber'}`}></span>
          <span style={{ color: isDbConnected ? '#10b981' : '#f59e0b' }}>
            {isDbConnected ? 'Connected' : 'Fallback / Offline'}
          </span>
        </div>
      </div>
    </header>
  );
};
