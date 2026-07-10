import React, { useState, useRef, useEffect } from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  onSubmit,
  disabled = false,
  placeholder = 'What would you like to build?',
  autoFocus = true,
}) => {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [value]);

  useEffect(() => {
    if (autoFocus && textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [autoFocus, disabled]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSubmit(trimmed);
      setValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '800px',
        margin: '0 auto',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
        transition: 'border-color var(--duration-normal)',
      }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        rows={1}
        style={{
          width: '100%',
          background: 'transparent',
          border: 'none',
          color: 'var(--text-primary)',
          fontSize: '15px',
          lineHeight: '1.5',
          padding: '16px 54px 16px 16px',
          resize: 'none',
          outline: 'none',
          maxHeight: '200px',
          fontFamily: 'var(--sans)',
          overflowY: 'auto',
          opacity: disabled ? 0.6 : 1,
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        style={{
          position: 'absolute',
          right: '12px',
          bottom: '12px',
          width: '32px',
          height: '32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: value.trim() && !disabled ? 'var(--text-primary)' : 'rgba(255,255,255,0.1)',
          color: value.trim() && !disabled ? 'var(--bg)' : 'rgba(255,255,255,0.3)',
          border: 'none',
          borderRadius: 'var(--radius-sm)',
          cursor: value.trim() && !disabled ? 'pointer' : 'default',
          transition: 'all var(--duration-fast)',
        }}
      >
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M8 14V2M8 2L2 8M8 2L14 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
};
