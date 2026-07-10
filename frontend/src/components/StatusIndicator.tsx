import React from 'react';

interface StatusIndicatorProps {
  /** Whether the execution is actively running */
  active: boolean;
  /** Step text like "Generating code…" */
  stepText: string;
  /** Size of the logo in px */
  size?: number;
}

/**
 * Animated star logo that pulses while an execution is in-flight.
 * Shows step text beneath when active.
 */
export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  active,
  stepText,
  size = 28,
}) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
      <div
        style={{
          width: size,
          height: size,
          flexShrink: 0,
          animation: active ? 'pulse-logo 1.8s ease-in-out infinite' : 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg
          width={size}
          height={size}
          viewBox="0 0 28 28"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M14 0L17.2 10.8L28 14L17.2 17.2L14 28L10.8 17.2L0 14L10.8 10.8L14 0Z"
            fill="var(--accent)"
          />
        </svg>
      </div>
      {stepText && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              fontSize: '14px',
              color: active ? 'var(--text-secondary)' : 'var(--text-muted)',
              fontWeight: 500,
              transition: 'color var(--duration-normal)',
            }}
          >
            {stepText}
          </span>
          {active && <TypingDots />}
        </div>
      )}
    </div>
  );
};

/** Three animated dots that appear while processing */
const TypingDots: React.FC = () => (
  <span style={{ display: 'inline-flex', gap: '3px', marginLeft: '2px' }}>
    {[0, 1, 2].map((i) => (
      <span
        key={i}
        style={{
          width: '4px',
          height: '4px',
          borderRadius: '50%',
          background: 'var(--accent)',
          display: 'inline-block',
          animation: `typing-dots 1.4s ${i * 0.2}s ease-in-out infinite`,
        }}
      />
    ))}
  </span>
);
