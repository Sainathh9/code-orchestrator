import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Sidebar } from '../components/Sidebar';
import { useExecutions } from '../hooks/useExecutions';

export interface AppOutletContext {
  triggerRefreshExecutions: () => void;
}

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const { executions, loading } = useExecutions(refreshKey);
  const navigate = useNavigate();

  const handleNewExecution = () => {
    navigate('/');
  };

  const triggerRefreshExecutions = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--bg)', color: 'var(--text-primary)' }}>
      {/* Sidebar */}
      <Sidebar
        executions={executions}
        loading={loading}
        onNewExecution={handleNewExecution}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, position: 'relative' }}>
        
        {/* Header (Top Right only) */}
        <header
          style={{
            height: 'var(--header-height)',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            padding: '0 24px',
            position: 'absolute',
            top: 0,
            right: 0,
            left: 0,
            zIndex: 100,
            pointerEvents: 'none', // let clicks pass through the invisible parts
          }}
        >
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', pointerEvents: 'auto' }}>
              {user.profilePicture ? (
                <img src={user.profilePicture} alt={user.name || ''} style={{ width: '28px', height: '28px', borderRadius: '50%', border: '1px solid var(--border)' }} />
              ) : (
                <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 700, color: '#fff' }}>
                  {(user.name || user.email)[0].toUpperCase()}
                </div>
              )}
              <button
                onClick={logout}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  color: 'var(--text-muted)',
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: 500,
                  transition: 'all var(--duration-fast)',
                }}
                onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--border-active)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
              >
                Sign out
              </button>
            </div>
          )}
        </header>

        {/* Content */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Outlet context={{ triggerRefreshExecutions } satisfies AppOutletContext} />
        </main>
      </div>
    </div>
  );
};
