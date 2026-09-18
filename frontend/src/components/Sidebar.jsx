import React from 'react';
import {
  LayoutDashboard,
  Users,
  FileText,
  BarChart3,
  MessageSquare,
  Settings,
  LogOut,
  Home
} from 'lucide-react';

export function Sidebar({ currentView, onSelectView }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'patients', label: 'Patients', icon: Users },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'results-overview', label: 'Results', icon: BarChart3 },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar-container">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id || (item.id === 'results-overview' && (currentView === 'results-detail' || currentView === 'findings'));
          return (
            <button
              key={item.id}
              className={`sidebar-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectView(item.id)}
            >
              <Icon size={18} className="sidebar-icon" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Extra Nav Shortcuts */}
      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <button className="sidebar-item" onClick={() => onSelectView('landing')}>
          <Home size={18} />
          <span>Home Page</span>
        </button>

        <button className="sidebar-item" onClick={() => onSelectView('logout')} style={{ color: '#ef4444' }}>
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
