import React from 'react';
import { Activity, User, PlusCircle, LogOut } from 'lucide-react';

function getInitials(name = '') {
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?';
}

export function Navbar({ healthStatus, currentUser, activePatient, onSelectView, onOpenUpload, onLogout }) {
  const initials = currentUser ? getInitials(currentUser.full_name) : '?';

  return (
    <header className="navbar-header">
      {/* Brand */}
      <div className="navbar-brand" onClick={() => onSelectView('dashboard')}>
        <div className="navbar-brand-icon">
          <Activity size={22} />
        </div>
        <h1 className="navbar-brand-text">AI Medical Report Assistant</h1>
      </div>

      {/* Right Actions */}
      <div className="navbar-actions">
        {/* Active Patient chip */}
        {activePatient ? (
          <div className="active-patient-chip" onClick={() => onSelectView('patients')} style={{ cursor: 'pointer' }}>
            <User size={16} />
            <span>{activePatient.display_name || '—'}</span>
            <span style={{ fontSize: '0.75rem', background: '#2563eb', color: '#fff', padding: '2px 8px', borderRadius: '99px' }}>Active</span>
          </div>
        ) : (
          <button className="btn-secondary" onClick={() => onSelectView('patients')}>
            <User size={16} /> Select Patient
          </button>
        )}

        {/* Upload Button */}
        <button className="btn-primary" onClick={onOpenUpload}>
          <PlusCircle size={16} /> Upload Report
        </button>

        {/* Logout */}
        {currentUser && (
          <button
            className="btn-secondary"
            style={{ padding: '8px 12px', color: '#64748b' }}
            onClick={onLogout}
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        )}

        {/* Avatar */}
        <div
          onClick={() => onSelectView('settings')}
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: '#eff6ff',
            color: '#2563eb',
            border: '1px solid #bfdbfe',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '700',
            fontSize: '0.82rem',
            cursor: 'pointer',
          }}
          title="Profile & Settings"
        >
          {initials}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
