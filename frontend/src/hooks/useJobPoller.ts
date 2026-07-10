import { useState, useEffect, useRef, useCallback } from 'react';
import { executionsApi } from '../api/executions';
import type { JobStatus } from '../types/execution';

const POLL_INTERVAL = 2000; // ms

/**
 * Polls the job status endpoint every 2 seconds while the job is
 * 'queued' or 'started'. Stops polling when the job finishes, fails,
 * or the component unmounts.
 */
export function useJobPoller(jobId: string | null) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setPolling(false);
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      stopPolling();
    };
  }, [stopPolling]);

  useEffect(() => {
    if (!jobId) {
      setStatus(null);
      setPolling(false);
      return;
    }

    const poll = async () => {
      try {
        const data = await executionsApi.getJobStatus(jobId);
        if (!mountedRef.current) return;
        setStatus(data);
        setError(null);

        // Stop polling on terminal states
        if (data.status === 'finished' || data.status === 'failed' || data.status === 'stopped') {
          stopPolling();
        }
      } catch (err: any) {
        if (!mountedRef.current) return;
        setError(err?.message || 'Failed to fetch job status');
        stopPolling();
      }
    };

    // Initial fetch immediately
    setPolling(true);
    poll();

    // Then poll every 2s
    intervalRef.current = setInterval(poll, POLL_INTERVAL);

    return () => {
      stopPolling();
    };
  }, [jobId, stopPolling]);

  /** The human-friendly step text shown during execution */
  const stepText = getStepText(status);

  return { status, polling, error, stepText, stopPolling };
}

function getStepText(status: JobStatus | null): string {
  if (!status) return '';
  if (status.stepText) return status.stepText;
  
  switch (status.status) {
    case 'queued':
      return 'Queued — waiting for a worker…';
    case 'started':
      if (status.started_at) {
        return 'Generating code…';
      }
      return 'Starting execution…';
    case 'finished':
      return 'Completed';
    case 'failed':
      return 'Execution failed';
    case 'stopped':
      return 'Stopped';
    default:
      return 'Processing…';
  }
}
