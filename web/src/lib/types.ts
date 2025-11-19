export type SortKey = 'ranking_position' | 'match_score' | 'candidate_name';
export type SortDirection = 'asc' | 'desc';

export interface CandidateResult {
  candidate_name: string;
  hard_skills: string[];
  soft_skills: string[];
  match_score: number;
  explanation: string;
  ranking_position: number;
}

export interface AnalyzeResponse {
  data: CandidateResult[];
  debug?: Record<string, unknown>;
}
