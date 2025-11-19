import { env } from '$env/dynamic/public';
import type { CandidateResult } from '$lib/types';

// API base URL: use PUBLIC_API_BASE_URL from .env or default to http://localhost:8000
const API_BASE_URL = env.PUBLIC_API_BASE_URL || 'http://localhost:8000';

function buildUrl(path: string) {
  const base = API_BASE_URL.replace(/\/$/, '');
  const trimmed = path.startsWith('/') ? path : `/${path}`;
  return `${base}${trimmed}`;
}

/**
 * Optional health check to show backend status in the UI.
 */
export async function checkHealth(signal?: AbortSignal): Promise<boolean> {
  try {
    const res = await fetch(buildUrl('/api/health'), { method: 'GET', signal });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Sends selected resume files to the backend for analysis.
 * Supports either a job identifier/path string or an object with jobText/jobFile.
 * Example usage:
 * ```ts
 * await analyzeResumes(files, 'data/samples/job.txt');
 * await analyzeResumes(files, { jobText, jobFile });
 * ```
 */
export async function analyzeResumes(
  files: File[],
  jobOrOptions?: string | { jobText?: string; jobFile?: File },
  signal?: AbortSignal
): Promise<CandidateResult[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append('resumes', file));

  if (typeof jobOrOptions === 'string' && jobOrOptions) {
    formData.append('job', jobOrOptions);
  } else if (jobOrOptions && typeof jobOrOptions === 'object') {
    if (jobOrOptions.jobFile) formData.append('job_file', jobOrOptions.jobFile);
    if (jobOrOptions.jobText) formData.append('job_text', jobOrOptions.jobText);
  }

  try {
    const response = await fetch(buildUrl('/api/analyze'), {
      method: 'POST',
      body: formData,
      signal
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || 'Falha ao analisar currículos');
    }

    const payload = (await response.json()) as CandidateResult[] | { data: CandidateResult[] };
    return Array.isArray(payload) ? payload : payload.data;
  } catch (err) {
    throw err instanceof Error ? err : new Error('Falha ao analisar currículos');
  }
}
