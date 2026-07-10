import { useState, useEffect, useCallback } from 'react';
import { executionsApi } from '../api/executions';
import type { ExecutionSummary } from '../types/execution';

/**
 * Hook to fetch and manage the user's execution history for the sidebar.
 * Auto-refreshes when `refreshKey` changes (increment after submitting a new job).
 */
export function useExecutions(refreshKey: number = 0) {
  const [executions, setExecutions] = useState<ExecutionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExecutions = useCallback(async () => {
    try {
      setLoading(true);
      const data = await executionsApi.list();
      // Sort by created_at descending (newest first)
      data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setExecutions(data);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch executions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExecutions();
  }, [fetchExecutions, refreshKey]);

  return { executions, loading, error, refetch: fetchExecutions };
}
