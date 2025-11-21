import { env } from '$env/dynamic/public';
import type { CandidateResult, StructuredJob } from '$lib/types';

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
export interface AnalyzeOptions {
  jobText?: string;
  jobFile?: File;
  structuredJob?: StructuredJob; // modo avançado
}

export async function analyzeResumes(
  files: File[],
  options?: AnalyzeOptions,
  signal?: AbortSignal
): Promise<CandidateResult[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append('resumes', file));

  if (options) {
    if (options.jobFile) formData.append('job_file', options.jobFile);
    if (options.jobText) formData.append('job_text', options.jobText);
    if (options.structuredJob) {
      // Enviar JSON serializado
      formData.append('structured_job', JSON.stringify(options.structuredJob));
    }
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

/**
 * Carrega lista de skills (hard e soft) do backend.
 */
export async function getSkills(signal?: AbortSignal): Promise<{ hard_skills: string[]; soft_skills: string[] }> {
  const response = await fetch(buildUrl('/api/skills'), { method: 'GET', signal });
  if (!response.ok) {
    throw new Error('Falha ao carregar lista de skills');
  }
  return response.json();
}
