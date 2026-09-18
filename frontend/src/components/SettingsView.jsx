import React, { useState } from 'react';
import { User, Globe, Bell, Shield, Edit3 } from 'lucide-react';

export function SettingsView({ currentUser, activePatient }) {
  const [activeTab, setActiveTab] = useState('Profile');
  const [name, setName] = useState(currentUser?.full_name || 'User Account');
  const [email, setEmail] = useState(currentUser?.email || '');
  const [phone, setPhone] = useState('');

  const initials = (name || 'U').split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || 'U';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header matching Wireframe Box 14 */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a' }}>Profile & Settings</h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Manage profile, preferences and app settings</p>
      </div>

      {/* Grid: Left Settings Navigation, Right Profile Info Card */}
      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: '24px' }}>
        {/* Left Subtabs matching Wireframe Box 14 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '16px' }}>
          {[
            { key: 'Profile', icon: User },
            { key: 'Preferences', icon: Globe },
            { key: 'Notifications', icon: Bell },
            { key: 'Language', icon: Globe },
            { key: 'Privacy & Security', icon: Shield },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                className={`sidebar-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.key)}
              >
                <Icon size={18} />
                <span>{tab.key}</span>
              </button>
            );
          })}
        </div>

        {/* Right Profile Info Form matching Wireframe Box 14 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0f172a' }}>Profile Information</h3>
            <button className="btn-outline-blue" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
              <Edit3 size={14} /> Edit
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#2563eb', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: '700' }}>
              {initials}
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>{name}</h2>
              <p style={{ color: '#64748b', fontSize: '0.88rem' }}>Primary Account Profile</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '480px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>Phone</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsView;
