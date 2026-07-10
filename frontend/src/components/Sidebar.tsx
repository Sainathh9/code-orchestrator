import React, { useState, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import type { ExecutionSummary } from '../types/execution';

interface SidebarProps {
  executions: ExecutionSummary[];
  loading: boolean;
  onNewExecution: () => void;
  collapsed: boolean;
  setCollapsed: (col: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  executions,
  loading,
  onNewExecution,
  collapsed,
  setCollapsed,
}) => {
  const [search, setSearch] = useState('');
  const location = useLocation();

  // Group by rough date (Today, Yesterday, Previous 7 Days, Older)
  const groupedExecutions = useMemo(() => {
    const groups: Record<string, ExecutionSummary[]> = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      Older: [],
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const msPerDay = 24 * 60 * 60 * 1000;

    const filtered = executions.filter((e) =>
      e.requirement.toLowerCase().includes(search.toLowerCase())
    );

    filtered.forEach((e) => {
      const d = new Date(e.created_at).getTime();
      const diff = today - d;

      if (diff <= 0) groups.Today.push(e);
      else if (diff <= msPerDay) groups.Yesterday.push(e);
      else if (diff <= 7 * msPerDay) groups['Previous 7 Days'].push(e);
      else groups.Older.push(e);
    });

    return groups;
  }, [executions, search]);

  const activeId = location.pathname.match(/\/executions\/(.+)/)?.[1];

  if (collapsed) {
    return (
      <div style={{ position: 'fixed', top: '16px', left: '16px', zIndex: 200 }}>
        <button
          onClick={() => setCollapsed(false)}
          title="Open sidebar"
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            color: 'var(--text-secondary)',
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background var(--duration-fast)',
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = 'var(--surface-hover)')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'var(--surface)')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        width: 'var(--sidebar-width)',
        flexShrink: 0,
        height: '100vh',
        background: 'var(--bg)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        overflow: 'hidden',
      }}
      className="animate-slide-in-left"
    >
      {/* ── Top actions ── */}
      <div style={{ padding: '16px' }}>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <button
            onClick={() => setCollapsed(true)}
            title="Close sidebar"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-sm)',
              transition: 'background var(--duration-fast)',
            }}
            onMouseOver={(e) => (e.currentTarget.style.background = 'var(--surface)')}
            onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
          >
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
               <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
               <line x1="9" y1="3" x2="9" y2="21"></line>
             </svg>
          </button>
          
          <Link
            to="/"
            onClick={onNewExecution}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0 12px',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background var(--duration-fast)',
              textDecoration: 'none',
            }}
            onMouseOver={(e) => (e.currentTarget.style.background = 'var(--surface-hover)')}
            onMouseOut={(e) => (e.currentTarget.style.background = 'var(--surface)')}
          >
            <span>New Chat</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </Link>
        </div>

        {/* Search */}
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              padding: '8px 12px 8px 32px',
              borderRadius: 'var(--radius-sm)',
              outline: 'none',
              transition: 'border-color var(--duration-fast)',
            }}
            onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--border-active)')}
            onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
          />
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--text-muted)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ position: 'absolute', left: '10px', top: '10px' }}
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>
      </div>

      {/* ── List ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px 16px' }}>
        {loading && executions.length === 0 ? (
          <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
            Loading...
          </div>
        ) : (
          Object.entries(groupedExecutions).map(([group, items]) => {
            if (items.length === 0) return null;
            return (
              <div key={group} style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', paddingLeft: '8px' }}>
                  {group}
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {items.map((e) => {
                    const isActive = activeId === e.execution_id;
                    return (
                      <Link
                        key={e.execution_id}
                        to={`/executions/${e.execution_id}`}
                        title={e.requirement}
                        style={{
                          display: 'block',
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          background: isActive ? 'var(--surface-active)' : 'transparent',
                          color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                          textDecoration: 'none',
                          fontSize: '13px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          transition: 'background var(--duration-fast)',
                        }}
                        onMouseOver={(el) => {
                          if (!isActive) el.currentTarget.style.background = 'var(--surface-hover)';
                        }}
                        onMouseOut={(el) => {
                          if (!isActive) el.currentTarget.style.background = 'transparent';
                        }}
                      >
                        {e.requirement}
                      </Link>
                    );
                  })}
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
