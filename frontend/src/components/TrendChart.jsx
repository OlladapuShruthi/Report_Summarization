import React from 'react';

export function TrendChart({ testName = 'Hemoglobin (Hb)', unit = 'g/dL', history = [], referenceLow = 13.5, referenceHigh = 17.5 }) {
  // Fallback sample trend data if history is sparse
  const sampleHistory = history.length > 0 ? history : [
    { date: '20 Mar 2025', value: 10.2, status: 'LOW' },
    { date: '18 Apr 2025', value: 10.4, status: 'LOW' },
    { date: '02 May 2025', value: 11.0, status: 'LOW' },
    { date: '26 May 2025', value: 12.4, status: 'LOW', isCurrent: true },
  ];

  const padding = 40;
  const width = 500;
  const height = 220;

  const values = sampleHistory.map(h => typeof h.value === 'number' ? h.value : parseFloat(h.value) || 0);
  const minVal = Math.min(...values, referenceLow * 0.85);
  const maxVal = Math.max(...values, referenceHigh * 1.15);

  const getX = (index) => padding + (index * (width - 2 * padding)) / Math.max(sampleHistory.length - 1, 1);
  const getY = (val) => height - padding - ((val - minVal) * (height - 2 * padding)) / (maxVal - minVal || 1);

  const points = sampleHistory.map((h, i) => `${getX(i)},${getY(h.value)}`).join(' ');

  const refLowY = getY(referenceLow);
  const refHighY = getY(referenceHigh);

  return (
    <div className="trend-chart-card">
      <div className="trend-chart-header">
        <div>
          <h4 className="trend-chart-title">{testName}</h4>
          <p className="trend-chart-subtitle">
            Reference Range: <span className="highlight-text">{referenceLow} - {referenceHigh} {unit}</span>
          </p>
        </div>
        <div className="trend-badge improving">
          ↗ Improving (+2.2 {unit})
        </div>
      </div>

      <div className="svg-container">
        <svg viewBox={`0 0 ${width} ${height}`} className="trend-svg">
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Reference range band */}
          <rect
            x={padding}
            y={refHighY}
            width={width - 2 * padding}
            height={Math.max(refLowY - refHighY, 4)}
            fill="rgba(16, 185, 129, 0.08)"
            rx="4"
          />

          {/* Reference Low Line */}
          <line
            x1={padding}
            y1={refLowY}
            x2={width - padding}
            y2={refLowY}
            stroke="rgba(244, 63, 94, 0.4)"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text x={width - padding + 5} y={refLowY + 4} fill="#f43f5e" fontSize="10" fontWeight="600">
            Low ({referenceLow})
          </text>

          {/* Reference High Line */}
          <line
            x1={padding}
            y1={refHighY}
            x2={width - padding}
            y2={refHighY}
            stroke="rgba(16, 185, 129, 0.4)"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text x={width - padding + 5} y={refHighY + 4} fill="#10b981" fontSize="10" fontWeight="600">
            High ({referenceHigh})
          </text>

          {/* Area fill */}
          {sampleHistory.length > 1 && (
            <polygon
              points={`${getX(0)},${height - padding} ${points} ${getX(sampleHistory.length - 1)},${height - padding}`}
              fill="url(#chartGradient)"
            />
          )}

          {/* Trend line */}
          <polyline
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
          />

          {/* Data Points */}
          {sampleHistory.map((h, i) => {
            const cx = getX(i);
            const cy = getY(h.value);
            const isLatest = i === sampleHistory.length - 1;

            return (
              <g key={i} className="chart-node">
                <circle
                  cx={cx}
                  cy={cy}
                  r={isLatest ? "6" : "4"}
                  fill={isLatest ? "#06b6d4" : "#3b82f6"}
                  stroke="#111827"
                  strokeWidth="2"
                />
                <text
                  x={cx}
                  y={cy - 12}
                  fill="#ffffff"
                  fontSize="11"
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {h.value}
                </text>
                <text
                  x={cx}
                  y={height - 12}
                  fill="#9ca3af"
                  fontSize="9"
                  textAnchor="middle"
                >
                  {h.date.replace(' 2025', '')}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

export default TrendChart;
