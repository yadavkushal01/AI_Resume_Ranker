export type AnalysisPhase = "idle" | "uploading" | "processing";

export type BackendConnectionState = "checking" | "online" | "offline";

export type BackendStatus = {
  message: string;
};

export type RankedCandidate = {
  candidate_id: string;
  rank: number;
  candidate_name: string;
  headline: string;
  current_title: string;
  current_company: string;
  location: string;
  country: string;
  experience_years: number;
  match_score: number;
  recommendation: string;
  skills: string[];
  matched_required_skills: string[];
  matched_preferred_skills: string[];
  missing_skills: string[];
  reason: string;
  strengths: string[];
  weaknesses: string[];
  projects: string[];
  education: string[];
  summary: string;
  raw_scores: {
    jd_score?: number;
    quality_score?: number;
    behavior_score?: number;
    confidence?: number;
  };
};

export type RankResponse = {
  job: {
    job_title: string;
    job_description: string;
    required_skills: string[];
    preferred_skills: string[];
  };
  summary: {
    source_file: string;
    total_candidates: number;
    analyzed_at: string;
  };
  candidates: RankedCandidate[];
};
