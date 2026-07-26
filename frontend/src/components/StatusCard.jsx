import React from 'react';
import { Layers, Cpu, Database } from 'lucide-react';

export const StatusCard = ({ totalWorkspaces, healthStatus }) => {
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-icon-box blue">
          <Layers size={26} />
        </div>
        <div>
          <div className="metric-val">{totalWorkspaces}</div>
          <div className="metric-label">Analysis Workspaces</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon-box emerald">
          <Cpu size={26} />
        </div>
        <div>
          <div className="metric-val">Sprint 1</div>
          <div className="metric-label">Architecture Foundation</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon-box indigo">
          <Database size={26} />
        </div>
        <div>
          <div className="metric-val" style={{ fontSize: '1.1rem', textTransform: 'capitalize' }}>
            {healthStatus?.database || 'Initializing'}
          </div>
          <div className="metric-label">MongoDB Atlas Connection</div>
        </div>
      </div>
    </div>
  );
};
