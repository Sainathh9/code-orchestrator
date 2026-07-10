import React, { useState, useCallback } from 'react';

interface CodeBlockProps {
  code: string;
  language?: string;
  maxHeight?: string;
}

/**
 * Dark-themed code display block with a copy button and language label.
 * No external syntax highlighting library — uses monospace font + subtle styling.
 */
export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'python',
  maxHeight = '400px',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available
    }
  }, [code]);

  return (
    <div
      style={{
        background: '#0a0a0a',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        fontSize: '13px',
      }}
    >
      {/* Header bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '8px 14px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(255,255,255,0.02)',
        }}
      >
        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            color: 'var(--text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {language}
        </span>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent',
            border: 'none',
            color: copied ? 'var(--green)' : 'var(--text-dim)',
            cursor: 'pointer',
            fontSize: '11px',
            fontFamily: 'var(--sans)',
            fontWeight: 500,
            padding: '2px 8px',
            borderRadius: '4px',
            transition: 'all var(--duration-fast)',
          }}
          onMouseOver={(e) => !copied && (e.currentTarget.style.color = 'var(--text-secondary)')}
          onMouseOut={(e) => !copied && (e.currentTarget.style.color = 'var(--text-dim)')}
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>

      {/* Code content */}
      <pre
        style={{
          margin: 0,
          padding: '16px',
          overflow: 'auto',
          maxHeight,
          fontFamily: 'var(--mono)',
          fontSize: '13px',
          lineHeight: '1.65',
          color: '#e0dcd4',
          tabSize: 4,
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
};
