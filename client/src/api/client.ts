import axios from "axios";
import { Finding } from "../data/sampleFindings";

const api = axios.create({
  baseURL: "/api"
});

export type ScoreContribution = {
  signal: string;
  weight: number;
  value: number;
  impact: number;
  rationale: string;
};

export type ScoredFinding = {
  finding: Finding;
  score: number;
  priority: string;
  contributions: ScoreContribution[];
  recommended_action: string;
};

export type ScoreResponse = {
  findings: ScoredFinding[];
};

export async function fetchScores(findings: Finding[]): Promise<ScoreResponse> {
  const { data } = await api.post<ScoreResponse>("/score/compute", { findings });
  return data;
}

export type PlanItem = {
  finding_id: string;
  title: string;
  wave: number;
  estimated_hours: number;
  score: number;
  expected_risk_reduction: number;
};

export type PlanResponse = {
  plan: PlanItem[];
  summary: string;
};

export async function fetchPlan(findings: Finding[]): Promise<PlanResponse> {
  const { data } = await api.post<PlanResponse>("/optimize/plan", { findings });
  return data;
}

export type ControlMapping = {
  control: string;
  title: string;
  description: string;
};

export type ComplianceResponse = {
  mappings: Record<string, ControlMapping[]>;
};

export async function fetchCompliance(cves: string[]): Promise<ComplianceResponse> {
  const { data } = await api.post<ComplianceResponse>("/map/controls", { cves });
  return data;
}

export type ImpactResponse = {
  impact: {
    breach_cost: number;
    compliance_gain: number;
    risk_reduction: number;
  };
};

export async function fetchImpact(findings: Finding[]): Promise<ImpactResponse> {
  const { data } = await api.post<ImpactResponse>("/impact/estimate", { findings });
  return data;
}

export type SummaryResponse = {
  html: string;
};

export async function fetchSummary(scope: string, findings: Finding[]): Promise<SummaryResponse> {
  const { data } = await api.post<SummaryResponse>("/summary/generate", { scope, findings });
  return data;
}

export type NlQueryResponse = {
  intent: string;
  result: Record<string, string>;
};

export async function fetchNaturalLanguage(query: string, findings: Finding[]): Promise<NlQueryResponse> {
  const { data } = await api.post<NlQueryResponse>("/nl/query", { query, findings });
  return data;
}
