export interface ExecutionSummary {
  execution_id: string;
  requirement: string;
  status: 'running' | 'success' | 'failed';
  tries_used: number;
  created_at: string;
}

export interface ExecutionIteration {
  iteration: number;
  code: string;
  test_output: string;
  passed: boolean;
}

export interface ExecutionDetail {
  execution_id: string;
  requirement: string;
  status: 'running' | 'success' | 'failed';
  tries_used: number;
  created_at: string;
  iterations: ExecutionIteration[];
}

export interface ExecutionResult {
  workspace: string;
  passed: boolean;
  tries_used: number;
  stdout: string;
  stderr: string;
  exit_code: number;
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'started' | 'finished' | 'failed' | 'stopped' | 'deferred';
  stepText?: string | null;
  enqueued_at: string | null;
  started_at: string | null;
  ended_at: string | null;
  result?: ExecutionResult;
  error?: string | null;
}
