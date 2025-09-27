import axios from "axios";

export interface AssetContext {
  name: string;
  criticality: string;
  exposure: string;
  data_sensitivity?: string;
}

export interface Finding {
  id: string;
  title: string;
  cve?: string;
  cvss: number;
  epss?: number;
  kev?: boolean;
  asset?: AssetContext;
  effort_hours?: number;
  sla_days?: number;
}

export interface ScoreContribution {
  name: string;
  weight: number;
  value: number;
  contribution: number;
  description: string;
}

export interface ScoredFinding {
  id: string;
  title: string;
  score: number;
  priority: string;
  contributions: ScoreContribution[];
  narrative: string;
  rules_applied: string[];
}

export interface ScoreComputeResponse {
  results: ScoredFinding[];
  summary: {
    counts_by_priority: Record<string, number>;
    generated_at: string;
  };
}

export interface OptimizePlanResponse {
  waves: {
    name: string;
    total_hours: number;
    expected_risk_reduction: number;
    items: {
      id: string;
      title: string;
      effort_hours: number;
      score: number;
      risk_reduction: number;
    }[];
  }[];
}

export interface ControlMapping {
  control: string;
  description: string;
  finding: string;
}

export interface MapControlsResponse {
  mappings: ControlMapping[];
}

export interface ImpactEstimateResponse {
  breach_reduction: number;
  compliance_gain: number;
  rationale: string;
}

export interface NLQueryResponse {
  intent: string;
  response: string;
  details: Record<string, number>;
}

export interface SummaryGenerateResponse {
  html: string;
}

const client = axios.create({
  baseURL: "/api"
});

export async function fetchSampleFindings(): Promise<Finding[]> {
  const { data } = await axios.get<Finding[]>("/api/findings/sample");
  return data;
}

export async function computeScores(findings: Finding[]): Promise<ScoreComputeResponse> {
  const { data } = await client.post<ScoreComputeResponse>("/score/compute", { findings });
  return data;
}

export async function optimizePlan(findings: Finding[], maxHoursPerWave: number): Promise<OptimizePlanResponse> {
  const { data } = await client.post<OptimizePlanResponse>("/optimize/plan", {
    findings,
    max_hours_per_wave: maxHoursPerWave
  });
  return data;
}

export async function mapControls(cves: string[]): Promise<MapControlsResponse> {
  const { data } = await client.post<MapControlsResponse>("/map/controls", { cves });
  return data;
}

export async function estimateImpact(findings: Finding[]): Promise<ImpactEstimateResponse> {
  const { data } = await client.post<ImpactEstimateResponse>("/impact/estimate", { findings });
  return data;
}

export async function queryIntent(query: string): Promise<NLQueryResponse> {
  const { data } = await client.post<NLQueryResponse>("/nl/query", { query });
  return data;
}

export async function generateSummary(findings: Finding[]): Promise<SummaryGenerateResponse> {
  const { data } = await client.post<SummaryGenerateResponse>("/summary/generate", { findings });
  return data;
}
