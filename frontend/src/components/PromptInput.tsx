import React, { useState, useRef, useEffect } from 'react';

const AVAILABLE_MODELS = [
  { id: 'gemini-3.6-flash', label: 'Gemini 3.6 Flash' },
  { id: 'gemini-3.6-flash-lite', label: 'Gemini 3.6 Flash Lite' },
];

interface PromptInputProps {
  onSubmit: (prompt: string, model: string) => void;
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
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0].id);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSubmit(trimmed, selectedModel);
      setValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const currentModelLabel = AVAILABLE_MODELS.find(m => m.id === selectedModel)?.label ?? selectedModel;

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
          padding: '16px 54px 44px 16px',
          resize: 'none',
          outline: 'none',
          maxHeight: '200px',
          fontFamily: 'var(--sans)',
          overflowY: 'auto',
          opacity: disabled ? 0.6 : 1,
        }}
      />

      {/* Bottom bar: model selector + send */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 12px 10px 12px',
        }}
      >
        {/* Model selector */}
        <div ref={dropdownRef} style={{ position: 'relative' }}>
          <button
            type="button"
            onClick={() => setDropdownOpen((o) => !o)}
            disabled={disabled}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 10px',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-secondary)',
              fontSize: '12px',
              fontFamily: 'var(--sans)',
              cursor: disabled ? 'default' : 'pointer',
              transition: 'all var(--duration-fast)',
              opacity: disabled ? 0.5 : 1,
              whiteSpace: 'nowrap',
            }}
            onMouseOver={(e) => {
              if (!disabled) {
                e.currentTarget.style.background = 'rgba(255,255,255,0.09)';
                e.currentTarget.style.borderColor = 'var(--border-hover)';
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
              e.currentTarget.style.borderColor = 'var(--border)';
            }}
          >
            {/* Sparkle icon */}
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
              <path d="M8 0L9.6 6.4L16 8L9.6 9.6L8 16L6.4 9.6L0 8L6.4 6.4L8 0Z" fill="var(--accent)" />
            </svg>
            {currentModelLabel}
            {/* Chevron */}
            <svg
              width="10"
              height="10"
              viewBox="0 0 10 10"
              fill="none"
              style={{
                transform: dropdownOpen ? 'rotate(180deg)' : 'rotate(0)',
                transition: 'transform var(--duration-fast)',
              }}
            >
              <path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>

          {/* Dropdown menu */}
          {dropdownOpen && (
            <div
              style={{
                position: 'absolute',
                bottom: 'calc(100% + 6px)',
                left: 0,
                minWidth: '180px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-hover)',
                borderRadius: 'var(--radius-md)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                padding: '4px',
                zIndex: 100,
                animation: 'fade-in var(--duration-fast) var(--ease-out) both',
              }}
            >
              {AVAILABLE_MODELS.map((model) => (
                <button
                  key={model.id}
                  type="button"
                  onClick={() => {
                    setSelectedModel(model.id);
                    setDropdownOpen(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    width: '100%',
                    padding: '8px 10px',
                    background: model.id === selectedModel ? 'var(--accent-dim)' : 'transparent',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    color:
                      model.id === selectedModel
                        ? 'var(--accent)'
                        : 'var(--text-secondary)',
                    fontSize: '13px',
                    fontFamily: 'var(--sans)',
                    cursor: 'pointer',
                    transition: 'background var(--duration-fast)',
                    textAlign: 'left',
                  }}
                  onMouseOver={(e) => {
                    if (model.id !== selectedModel) {
                      e.currentTarget.style.background = 'var(--surface-hover)';
                    }
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background =
                      model.id === selectedModel ? 'var(--accent-dim)' : 'transparent';
                  }}
                >
                  {/* Check mark for selected */}
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="none"
                    style={{ opacity: model.id === selectedModel ? 1 : 0 }}
                  >
                    <path d="M2 6L5 9L10 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  {model.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          style={{
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
    </div>
  );
};
