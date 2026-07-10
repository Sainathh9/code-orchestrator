import React from 'react';
import { StatusIndicator } from './StatusIndicator';
import { IterationCard } from './IterationCard';
import type { ExecutionDetail, JobStatus } from '../types/execution';

interface ExecutionChatProps {
  /** The original requirement prompt */
  requirement: string;
  /** Live polling status (if active) */
  jobStatus: JobStatus | null;
  /** The step text derived from the jobStatus (if active) */
  stepText?: string;
  /** The full completed execution details (if finished and loaded) */
  executionDetail: ExecutionDetail | null;
}

/**
 * Chat-like view for a single execution.
 * Shows the user's requirement as a message bubble.
 * Shows the live status or completed iterations as the assistant's response.
 */
export const ExecutionChat: React.FC<ExecutionChatProps> = ({
  requirement,
  jobStatus,
  stepText = '',
  executionDetail,
}) => {
  // Determine if it's currently running
  const isRunning =
    jobStatus?.status === 'queued' || jobStatus?.status === 'started';

  // We have the iterations either from the execution detail, or perhaps we could show nothing yet
  const iterations = executionDetail?.iterations || [];

  const isStuck = executionDetail?.status === 'running' && !jobStatus;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', width: '100%', maxWidth: '800px', margin: '0 auto', paddingBottom: '80px' }}>
      
      {/* ── User Message (Requirement) ── */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', animation: 'fade-in-up var(--duration-normal)' }}>
        <div
          style={{
            background: 'var(--surface)',
            color: 'var(--text-primary)',
            padding: '16px 20px',
            borderRadius: 'var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)',
            fontSize: '15px',
            lineHeight: '1.6',
            maxWidth: '85%',
            whiteSpace: 'pre-wrap',
            boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
          }}
        >
          {requirement}
        </div>
      </div>

      {/* ── Assistant Message (Execution context) ── */}
      <div style={{ display: 'flex', gap: '16px', animation: 'fade-in-up var(--duration-normal) 100ms both' }}>
        
        {/* Status Indicator (Logo + Step Text) */}
        <div style={{ paddingTop: '4px' }}>
          <StatusIndicator active={isRunning} stepText={isRunning ? (stepText || 'Processing…') : ''} size={28} />
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px', paddingTop: '8px' }}>

          {/* Iteration Cards */}
          {iterations.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {iterations.map((iter, idx) => (
                <IterationCard
                  key={idx}
                  iteration={iter}
                  defaultExpanded={idx === iterations.length - 1} // expand the latest by default
                />
              ))}
            </div>
          )}

          {/* Final Status Banner */}
          {!isRunning && (executionDetail || jobStatus?.status === 'failed') && (
            <div
              style={{
                marginTop: '8px',
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                background: (executionDetail?.status === 'success') ? 'var(--green-dim)' : 'var(--red-dim)',
                color: (executionDetail?.status === 'success') ? 'var(--green)' : 'var(--red)',
                fontSize: '14px',
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {executionDetail?.status === 'success' ? (
                <>✓ Successfully completed in {executionDetail.tries_used} iterations.</>
              ) : (
                <>✗ Failed{executionDetail ? ` after ${executionDetail.tries_used} iterations.` : ` - ${jobStatus?.error?.split('\\n').pop() || 'Execution encountered an error (e.g. Gemini API 503).'}`}</>
              )}
            </div>
          )}

          {/* Interrupted/Crashed Status Banner */}
          {isStuck && (
            <div
              style={{
                marginTop: '8px',
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--red-dim)',
                color: 'var(--red)',
                fontSize: '14px',
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              ✗ This execution was interrupted or crashed.
            </div>
          )}
        </div>
      </div>

    </div>
  );
};
