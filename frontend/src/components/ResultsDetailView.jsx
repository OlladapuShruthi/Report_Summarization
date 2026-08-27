import React, { useState } from 'react';
import { TrendChart } from './TrendChart';
import { ArrowLeft, Download, TrendingUp } from 'lucide-react';

export function ResultsDetailView({ result, onBack, onOpenExport, onSelectTab }) {
  const [activeSubTab, setActiveSubTab] = useState('Comparison');

  const historyData = [
    { date: '20 Mar 2025', value: 10.2 },
    { date: '18 Apr 2025', value: 10.4 },
    { date: '02 May 2025', value: 11.0 },
    { date: '26 May 2025', value: 12.4, isCurrent: true }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Bar matching Wireframe Box 9 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn-secondary" onClick={onBack} style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            <ArrowLeft size={16} /> Back
          </button>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a' }}>CBC Report – 26 May 2025</h1>
        </div>

        <button className="btn-outline-blue" onClick={onOpenExport}>
          <Download size={16} /> Download
        </button>
      </div>

      {/* Filter Tabs matching Wireframe Box 9 */}
      <div className="card" style={{ padding: '12px 20px' }}>
        <div className="filter-tabs" style={{ marginBottom: 0, borderBottom: 'none' }}>
          {['Overview', 'All Results', 'Comparison', 'Trends', 'Notes'].map((tab) => (
            <button
              key={tab}
              className={`filter-tab ${activeSubTab === tab ? 'active' : ''}`}
              onClick={() => {
                setActiveSubTab(tab);
                if (onSelectTab) onSelectTab(tab);
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid Content matching Wireframe Box 9 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px' }}>
        {/* Left Column: Interactive Trend Chart */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.88rem', fontWeight: '600', color: '#64748b' }}>Parameter</span>
            <select style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.88rem', fontWeight: '600' }}>
              <option value="Hemoglobin">Hemoglobin (Hb)</option>
              <option value="RBC">RBC Count</option>
              <option value="Hematocrit">Hematocrit (HCT)</option>
            </select>
          </div>

          <TrendChart
            testName="Hemoglobin (Hb)"
            unit="g/dL"
            referenceLow={13.5}
            referenceHigh={17.5}
            history={historyData}
          />
        </div>

        {/* Right Column: Finding Status Box matching Wireframe Box 9 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Finding Status</span>

          <div style={{ backgroundColor: '#dcfce7', borderRadius: '12px', padding: '16px', border: '1px solid #86efac' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#15803d', fontWeight: '700', fontSize: '1.1rem', marginBottom: '4px' }}>
              <TrendingUp size={20} />
              <span>Improving</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#166534' }}>
              Value is improving and moving towards normal range.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
              <span style={{ color: '#64748b' }}>Reference Range</span>
              <span style={{ fontWeight: '600', color: '#0f172a' }}>13.5 - 17.5 g/dL</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
              <span style={{ color: '#64748b' }}>Current Status</span>
              <span style={{ fontWeight: '600', color: '#c2410c' }}>Low (12.4 g/dL)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsDetailView;
