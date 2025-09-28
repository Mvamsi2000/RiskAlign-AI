import axios from "axios";

export interface AssetContext {
  name: string;
  criticality: string;
  exposure: string;
  data_sensitivity?: string;
}

export interface Finding {
  id?: string;
  title?: string;
  cve?: string;
  cvss: number;
  epss?: number;
  mvi?: number;
  kev?: boolean;
  asset?: AssetContext;
  effort_hours?: number;
}

export interface ScoreComponents {
  cvss: number;
  epss: number;
  mvi: number;
  kev: number;
  context: number;
}

export interface ScoreFinding {
  id?: string;
  title?: string;
  score: number;
  priority: string;
  effort_hours: number;
  components: ScoreComponents;
  context_multiplier: number;
}

export interface ScoreTotals {
  count: number;
  total_score: number;
  average_score: number;
  total_effort_hours: number;
  by_priority: Record<string, number>;
}

export interface ScoreComputeResponse {
  findings: ScoreFinding[];
  totals: ScoreTotals;
}

export interface PlanItem {
  id?: string;
  title?: string;
  priority: string;
  effort_hours: number;
  score: number;
  risk_saved: number;
}

export interface RemediationWave {
  name: string;
  total_hours: number;
  risk_saved: number;
  items: PlanItem[];
}

export interface PlanTotals {
  waves: number;
  total_hours: number;
  total_risk_saved: number;
}

export interface OptimizePlanResponse {
  waves: RemediationWave[];
  totals: PlanTotals;
}

export interface ControlMapping {
  cve: string;
  control: string;
  description: string;
  finding_id?: string;
}

export interface MapControlsResponse {
  framework: string;
  coverage: number;
  unique_controls: string[];
  mappings: ControlMapping[];
  unmapped: string[];
}

export interface RiskCurvePoint {
  wave: string;
  cumulative_risk_saved: number;
  percent_of_total: number;
}

export interface ImpactEstimateResponse {
  readiness_percent: number;
  compliance_boost: number;
  risk_saved_curve: RiskCurvePoint[];
  controls_covered: string[];
}

export interface NLQueryResponse {
  intent: string;
  response: string;
  details: {
    matched_keywords: string[];
    confidence: number;
    endpoint: string | null;
  };
}

export interface SummaryGenerateResponse {
  path: string;
  html: string;
}

export interface FeedbackResponse {
  status: string;
  path: string;
  recorded_at: string;
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

export async function mapControls(findings: Finding[], framework = "CIS"): Promise<MapControlsResponse> {
  const { data } = await client.post<MapControlsResponse>("/map/controls", {
    findings,
    framework
  });
  return data;
}

export async function estimateImpact(findings: Finding[], waves: RemediationWave[]): Promise<ImpactEstimateResponse> {
  const { data } = await client.post<ImpactEstimateResponse>("/impact/estimate", {
    findings,
    waves
  });
  return data;
}

export async function queryIntent(query: string): Promise<NLQueryResponse> {
  const { data } = await client.post<NLQueryResponse>("/nl/query", { query });
  return data;
}

export async function generateSummary(options: {
  findings?: Finding[];
  scope?: string;
  framework?: string;
  max_hours_per_wave?: number;
}): Promise<SummaryGenerateResponse> {
  const { data } = await client.post<SummaryGenerateResponse>("/summary/generate", options);
  return data;
}

export async function submitFeedback(payload: {
  finding_id: string;
  action: string;
  comment?: string;
}): Promise<FeedbackResponse> {
  const { data } = await client.post<FeedbackResponse>("/feedback/submit", payload);
  return data;
}
