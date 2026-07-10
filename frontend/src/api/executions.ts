import { apiClient } from './client';
import type { ExecutionSummary, ExecutionDetail, JobStatus } from '../types/execution';

export interface GenerateJobResponse {
  job_id: string;
  status: string;
  queue: string;
}

export const executionsApi = {
  /**
   * Enqueue a new code generation job.
   */
  async generate(requirement: string): Promise<GenerateJobResponse> {
    const response = await apiClient.post<GenerateJobResponse>('/generate', {
      requirement,
    });
    return response.data;
  },

  /**
   * List all execution records belonging to the authenticated user.
   */
  async list(): Promise<ExecutionSummary[]> {
    const response = await apiClient.get<ExecutionSummary[]>('/executions/');
    return response.data;
  },

  /**
   * Fetch the details and iteration history of a single execution.
   */
  async get(executionId: string): Promise<ExecutionDetail> {
    const response = await apiClient.get<ExecutionDetail>(`/executions/${executionId}`);
    return response.data;
  },

  /**
   * Poll the status of an enqueued background job.
   */
  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await apiClient.get<JobStatus>(`/executions/jobs/${jobId}`);
    return response.data;
  },
};
