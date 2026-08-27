import React from 'react';
import { CheckCircle2, LogIn, Home } from 'lucide-react';

export function LogoutView({ onLoginAgain, onBackHome }) {
  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '32px' }}>
      <div className="card" style={{ maxWidth: '420px', width: '100%', padding: '40px 32px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#dcfce7', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <CheckCircle2 size={36} />
        </div>

        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>Logged Out</h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
            You have been logged out successfully.<br />Your patient data remains safely stored.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%' }}>
          <button className="btn-primary" style={{ padding: '12px 32px', width: '100%', justifyContent: 'center' }} onClick={onLoginAgain}>
            <LogIn size={16} /> Login Again
          </button>
          <button className="btn-secondary" style={{ width: '100%', justifyContent: 'center' }} onClick={onBackHome}>
            <Home size={16} /> Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default LogoutView;
