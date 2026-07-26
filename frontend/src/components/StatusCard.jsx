import React from 'react';
import { Layers, Cpu, Database, Workflow } from 'lucide-react';

export const StatusCard = ({ totalWorkspaces, healthStatus, sessions = [] }) => {
  const parsedCount = sessions.filter((session) => session.status === 'parsed').length;
  const analyzedCount = sessions.filter((session) => ['analyzing', 'validated', 'completed'].includes(session.status)).length;
  const activeCount = sessions.filter((session) => ['uploaded', 'parsing', 'analyzing'].includes(session.status)).length;

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
          <div className="metric-val">{analyzedCount}</div>
          <div className="metric-label">Reasoned workspaces</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon-box indigo">
          <Workflow size={26} />
        </div>
        <div>
          <div className="metric-val">{parsedCount}</div>
          <div className="metric-label">Parsed workspaces</div>
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

      <div className="metric-card">
        <div className="metric-icon-box blue">
          <Layers size={26} />
        </div>
        <div>
          <div className="metric-val">{activeCount}</div>
          <div className="metric-label">Active processing queues</div>
        </div>
      </div>
    </div>
  );
};
