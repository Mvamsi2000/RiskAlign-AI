import axios, { AxiosError, AxiosRequestConfig } from "axios";

export type AIProviderId = "local" | "online";

export interface AIProviderOption {
  id: AIProviderId;
  label: string;
}

export interface AIProvidersResponse {
  providers: AIProviderOption[];
}

export interface AssetContext {
  name: string;
  criticality: string;
  exposure: string;
  data_sensitivity?: string;
}

export interface Finding {
  id?: string;
  title?: string;
  description?: string;
  severity?: string;
  cve?: string;
  cvss?: number;
  epss?: number;
  mvi?: number;
  kev?: boolean;
  asset?: AssetContext;
  effort_hours?: number;
  tags?: string[];
  source?: string;
  observed_at?: string;
  signals?: { epss?: number; kev?: boolean };
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

export interface IngestUploadResponse {
  detected: string;
  adapter_label: string;
  count: number;
  accepted: number;
  rejected: number;
  path: string;
  sample: Finding[];
}

export interface CanonicalBatchInfo {
  name: string;
  path: string;
  findings: number;
  created_at: string;
}

export interface CanonicalBatchesResponse {
  namespace: string;
  batches: CanonicalBatchInfo[];
}

export interface CanonicalFindingsResponse {
  namespace: string;
  batch?: string;
  fallback: boolean;
  findings: Finding[];
  count: number;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatResponse {
  provider: string;
  messages: ChatMessage[];
}

type ProviderErrorListener = (message: string) => void;

const providerErrorListeners = new Set<ProviderErrorListener>();

function notifyProviderError(message: string) {
  providerErrorListeners.forEach((listener) => {
    try {
      listener(message);
    } catch (error) {
      console.warn("AI provider listener error", error);
    }
  });
}

export function onAIProviderError(listener: ProviderErrorListener): () => void {
  providerErrorListeners.add(listener);
  return () => {
    providerErrorListeners.delete(listener);
  };
}

export function withAIProvider(
  init: RequestInit = {},
  provider?: AIProviderId
): RequestInit {
  const stored = provider ?? getStoredProvider();
  if (!stored) {
    return init;
  }

  const headers = new Headers(init.headers ?? {});
  headers.set("X-AI-Provider", stored);

  return {
    ...init,
    headers
  };
}

function getStoredProvider(): AIProviderId | null {
  if (typeof window === "undefined") {
    return null;
  }
  const value = window.localStorage.getItem("aiProvider");
  return value === "local" || value === "online" ? value : null;
}

function headersFromInit(headers?: HeadersInit): Record<string, string> {
  if (!headers) return {};
  if (headers instanceof Headers) {
    return Object.fromEntries(headers.entries());
  }
  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }
  return headers as Record<string, string>;
}

function configWithAIProvider(provider?: AIProviderId): AxiosRequestConfig {
  const init = withAIProvider({}, provider);
  return {
    headers: headersFromInit(init.headers)
  };
}

const client = axios.create({
  baseURL: "/api"
});

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status ?? 0;
    const message =
      (error.response?.data as { error?: { message?: string } } | undefined)?.error?.message ||
      error.message;
    if (message && (status >= 500 || message.toLowerCase().includes("provider"))) {
      notifyProviderError(message);
    }
    return Promise.reject(error);
  }
);

export async function listAIProviders(): Promise<AIProviderOption[]> {
  const { data } = await client.get<AIProvidersResponse>("/ai/providers", configWithAIProvider());
  return data.providers;
}

export async function listCanonicalBatches(): Promise<CanonicalBatchInfo[]> {
  const { data } = await client.get<CanonicalBatchesResponse>(
    "/ingest/batches",
    configWithAIProvider()
  );
  return data.batches;
}

export async function fetchCanonicalFindings(batch?: string): Promise<CanonicalFindingsResponse> {
  const params = batch ? { params: { batch } } : {};
  const { data } = await client.get<CanonicalFindingsResponse>(
    "/findings/canonical",
    { ...configWithAIProvider(), ...params }
  );
  return data;
}

export async function uploadIngest(file: File): Promise<IngestUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const headers = { ...configWithAIProvider().headers };
  const { data } = await client.post<IngestUploadResponse>("/ingest/upload", form, {
    headers,
  });
  return data;
}

export async function computeScores(findings: Finding[]): Promise<ScoreComputeResponse> {
  const { data } = await client.post<ScoreComputeResponse>(
    "/score/compute",
    { findings },
    configWithAIProvider()
  );
  return data;
}

export async function optimizePlan(
  findings: Finding[],
  maxHoursPerWave: number
): Promise<OptimizePlanResponse> {
  const { data } = await client.post<OptimizePlanResponse>(
    "/optimize/plan",
    {
      findings,
      max_hours_per_wave: maxHoursPerWave
    },
    configWithAIProvider()
  );
  return data;
}

export async function mapControls(
  findings: Finding[],
  framework = "CIS"
): Promise<MapControlsResponse> {
  const { data } = await client.post<MapControlsResponse>(
    "/map/controls",
    {
      findings,
      framework
    },
    configWithAIProvider()
  );
  return data;
}

export async function estimateImpact(
  findings: Finding[],
  waves: RemediationWave[]
): Promise<ImpactEstimateResponse> {
  const { data } = await client.post<ImpactEstimateResponse>(
    "/impact/estimate",
    {
      findings,
      waves
    },
    configWithAIProvider()
  );
  return data;
}

export async function queryIntent(query: string): Promise<NLQueryResponse> {
  const { data } = await client.post<NLQueryResponse>(
    "/nl/query",
    { query },
    configWithAIProvider()
  );
  return data;
}

export async function chatWithAI(messages: ChatMessage[]): Promise<ChatResponse> {
  const { data } = await client.post<ChatResponse>(
    "/ai/chat",
    { messages },
    configWithAIProvider()
  );
  return data;
}

export async function generateSummary(options: {
  findings?: Finding[];
  scope?: string;
  framework?: string;
  max_hours_per_wave?: number;
}): Promise<SummaryGenerateResponse> {
  const { data } = await client.post<SummaryGenerateResponse>(
    "/summary/generate",
    options,
    configWithAIProvider()
  );
  return data;
}

export async function submitFeedback(payload: {
  finding_id: string;
  action: string;
  comment?: string;
}): Promise<FeedbackResponse> {
  const { data } = await client.post<FeedbackResponse>(
    "/feedback/submit",
    payload,
    configWithAIProvider()
  );
  return data;
}
