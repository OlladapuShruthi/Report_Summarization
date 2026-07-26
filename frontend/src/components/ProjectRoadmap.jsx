import React from 'react';
import { CheckCircle2, Clock3, CircleDashed, ArrowRight, Activity } from 'lucide-react';

const sprintItems = [
  {
    key: 'sprint1',
    label: 'Sprint 1',
    title: 'Foundation',
    description: 'FastAPI, React, MongoDB Atlas, analysis workspace, upload APIs.',
    status: 'complete',
  },
  {
    key: 'sprint2',
    label: 'Sprint 2',
    title: 'Parser Pipeline',
    description: 'PDF/OCR extraction, classification, deterministic parsing, JSON validation.',
    status: 'complete',
  },
  {
    key: 'sprint3',
    label: 'Sprint 3',
    title: 'Structured Reasoning',
    description: 'Graph state, anomaly reasoning, risk assessment, consultation, validation.',
    status: 'in-progress',
  },
  {
    key: 'sprint4',
    label: 'Sprint 4',
    title: 'Conversation & RAG',
    description: 'LLM-backed follow-up questions and report-aware retrieval.',
    status: 'planned',
  },
];

const statusConfig = {
  complete: {
    icon: CheckCircle2,
    text: 'Complete',
    className: 'roadmap-pill complete',
  },
  'in-progress': {
    icon: Activity,
    text: 'In progress',
    className: 'roadmap-pill progress',
  },
  planned: {
    icon: CircleDashed,
    text: 'Planned',
    className: 'roadmap-pill planned',
  },
};

const stageLabels = {
  created: 'Workspace created',
  uploaded: 'Document uploaded',
  parsing: 'Parsing in progress',
  parsed: 'Facts extracted',
  analyzing: 'Structured reasoning',
  validated: 'Validated',
  completed: 'Completed',
  failed: 'Needs attention',
};

const pipelineStages = [
  'created',
  'uploaded',
  'parsing',
  'parsed',
  'analyzing',
  'validated',
  'completed',
];

export const ProjectRoadmap = ({ sessions }) => {
  const statusCounts = sessions.reduce(
    (accumulator, session) => {
      const status = session.status || 'created';
      accumulator[status] = (accumulator[status] || 0) + 1;
      return accumulator;
    },
    {}
  );

  const activeStage = pipelineStages.findLast((stage) => (statusCounts[stage] || 0) > 0) || 'created';

  return (
    <section className="roadmap-card">
      <div className="roadmap-header">
        <div>
          <h2 className="section-title">Project Roadmap</h2>
          <p className="section-desc">A reviewer-friendly snapshot of what is built and where the workflow is now.</p>
        </div>
        <div className="roadmap-active-stage">
          <ArrowRight size={14} />
          <span>{stageLabels[activeStage] || 'Workspace created'}</span>
        </div>
      </div>

      <div className="roadmap-grid">
        {sprintItems.map((item) => {
          const config = statusConfig[item.status];
          const StatusIcon = config.icon;

          return (
            <article key={item.key} className={`roadmap-item ${item.status}`}>
              <div className="roadmap-item-head">
                <div>
                  <p className="roadmap-label">{item.label}</p>
                  <h3>{item.title}</h3>
                </div>
                <span className={config.className}>
                  <StatusIcon size={14} />
                  {config.text}
                </span>
              </div>
              <p className="roadmap-desc">{item.description}</p>
            </article>
          );
        })}
      </div>

      <div className="pipeline-summary">
        {pipelineStages.map((stage, index) => {
          const count = statusCounts[stage] || 0;
          const isActive = stage === activeStage;

          return (
            <div key={stage} className={`pipeline-step ${isActive ? 'active' : ''}`}>
              <span className="pipeline-step-index">{index + 1}</span>
              <div>
                <div className="pipeline-step-title">{stageLabels[stage]}</div>
                <div className="pipeline-step-count">{count} workspace(s)</div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};