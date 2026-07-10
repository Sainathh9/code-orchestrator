import React, { useState } from 'react';
import { CodeBlock } from './CodeBlock';
import type { ExecutionIteration } from '../types/execution';

interface IterationCardProps {
  iteration: ExecutionIteration;
  defaultExpanded?: boolean;
}

/**
 * Expandable card showing one iteration's generated code and test output.
 */
export const IterationCard: React.FC<IterationCardProps> = ({
  iteration,
  defaultExpanded = false,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        background: 'var(--bg-elevated)',
        transition: 'border-color var(--duration-fast)',
      }}
      onMouseOver={(e) => (e.currentTarget.style.borderColor = 'var(--border-hover)')}
      onMouseOut={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
    >
      {/* Header — always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          fontFamily: 'var(--sans)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
            }}
          >
            Iteration {iteration.iteration}
          </span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '4px',
              background: iteration.passed ? 'var(--green-dim)' : 'var(--red-dim)',
              color: iteration.passed ? 'var(--green)' : 'var(--red)',
              letterSpacing: '0.3px',
              textTransform: 'uppercase',
            }}
          >
            {iteration.passed ? 'Pass' : 'Fail'}
          </span>
        </div>
        <svg
          width="14"
          height="14"
          viewBox="0 0 16 16"
          fill="none"
          style={{
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform var(--duration-fast)',
            color: 'var(--text-dim)',
          }}
        >
          <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Body — shown when expanded */}
      {expanded && (
        <div
          style={{
            borderTop: '1px solid var(--border)',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
            animation: 'fade-in var(--duration-fast) var(--ease-out)',
          }}
        >
          {iteration.code && (
            <div>
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'block' }}>
                Generated Code
              </label>
              <CodeBlock code={iteration.code} language="python" maxHeight="300px" />
            </div>
          )}
          {iteration.test_output && (
            <div>
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'block' }}>
                Test Output
              </label>
              <CodeBlock code={iteration.test_output} language="shell" maxHeight="200px" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
