export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export interface ChatSource {
  title: string;
  endpoint: string;
  record_count: number;
  data: unknown[];
}

export interface Evidence {
  source: string;
  assessment_year: number | null;
  location: string;
  records_used: number;
  confidence: string;
  source_url: string;
  data_type: string;
}

export interface ParsedIntent {
  intent: string;
  state: string | null;
  district: string | null;
  block: string | null;
  year: number | null;
  comparison_years: number[];
  metric: string | null;
  category: string | null;
  confidence: number;
  language: string;
}

export interface ChatApiResponse {
  reply: string;
  sources: ChatSource[];
  suggested_followups: string[];
  parsed_intent: ParsedIntent;
  evidence: Evidence | null;
}

export function sendChatMessage(message: string): Promise<ChatApiResponse> {
  return fetchJson<ChatApiResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

// ─── LLM Chat (Ollama RAG) ──────────────────────────────────────────────────

export interface LLMSource {
  title: string;
  relevance: number;
  content_preview: string;
}

export interface LLMChatApiResponse {
  reply: string;
  sources: LLMSource[];
  model: string;
  mode: string;
}

export function sendLLMChatMessage(
  message: string,
  top_k: number = 5,
  language: string = "english",
): Promise<LLMChatApiResponse> {
  return fetchJson<LLMChatApiResponse>("/api/llm/chat", {
    method: "POST",
    body: JSON.stringify({ message, top_k, language }),
  });
}

export interface LLMHealthResponse {
  status: string;
  ollama_installed: boolean;
  model_available: boolean;
  model?: string;
  models_list?: string;
  error?: string;
}

export function checkLLMHealth(): Promise<LLMHealthResponse> {
  return fetchJson<LLMHealthResponse>("/api/llm/health");
}

// ─── Smart Chat (Hybrid RAG + SQL) ──────────────────────────────────────────

export interface SmartChatSource {
  title: string;
  type: string;
  relevance?: number;
}

export interface SmartChatApiResponse {
  reply: string;
  sources: SmartChatSource[];
  query_type: string;
  entities: Record<string, string | null>;
  session_id: string;
  route: string;
}

export function sendSmartChatMessage(
  message: string,
  sessionId: string = "default",
  language: string = "english",
): Promise<SmartChatApiResponse> {
  return fetchJson<SmartChatApiResponse>("/api/smart/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId, language }),
  });
}

export async function* streamSmartChat(
  message: string,
  sessionId: string = "default",
  language: string = "english",
): AsyncGenerator<{ type: string; content: string | SmartChatSource[] }> {
  const response = await fetch("/api/smart/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, language }),
  });

  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          yield data;
        } catch { /* skip invalid JSON */ }
      }
    }
  }
}

// ─── Groundwater Data API ────────────────────────────────────────────────────

export interface GroundwaterStateData {
  state: string;
  data: {
    total_recharge: number;
    total_extractable: number;
    total_extraction: number;
    avg_stage: number;
    districts: number;
    blocks: number;
    oe_blocks: number;
    critical_blocks: number;
    sc_blocks: number;
    safe_blocks: number;
    assessment_year: number;
  };
  trend: {
    direction: string;
    total_change: number;
    percentage_change: number;
  } | null;
}

export function getGroundwaterState(state: string, year?: number): Promise<GroundwaterStateData> {
  const params = year ? `?year=${year}` : "";
  return fetchJson<GroundwaterStateData>(`/api/groundwater/state/${encodeURIComponent(state)}${params}`);
}

export interface RankingEntry {
  state: string;
  avg_stage: number;
  total_extraction: number;
  total_recharge: number;
  blocks: number;
}

export function getRankings(limit: number = 10): Promise<{ rankings: RankingEntry[] }> {
  return fetchJson(`/api/groundwater/rankings?limit=${limit}`);
}

export interface TrendData {
  state: string;
  metric: string;
  direction: string;
  total_change: number;
  percentage_change: number;
  avg_annual_change: number;
  points: { year: number; value: number }[];
}

export function getStateTrends(state: string): Promise<TrendData> {
  return fetchJson<TrendData>(`/api/groundwater/trends/${encodeURIComponent(state)}`);
}

export interface OverviewData {
  total_extraction: number;
  total_recharge: number;
  avg_stage: number;
  states: number;
  districts: number;
  blocks: number;
  total_records: number;
  oe_blocks: number;
  critical_blocks: number;
  sc_blocks: number;
  safe_blocks: number;
}

export function getOverview(): Promise<OverviewData> {
  return fetchJson<OverviewData>("/api/groundwater/overview");
}

// ─── Map-Specific API ────────────────────────────────────────────────────────

export interface StateSummary {
  state: string;
  districts: number;
  blocks: number;
  latest_assessment_year: number;
  avg_extraction_stage: number;
}

export function getAllStates(): Promise<StateSummary[]> {
  return fetchJson<StateSummary[]>("/api/states");
}

export interface AssessmentRecord {
  id: number;
  state: string;
  district: string;
  block: string;
  assessment_year: number;
  annual_groundwater_recharge: number;
  extractable_groundwater_resource: number;
  groundwater_extraction: number;
  extraction_stage: number;
  category: string;
  latitude?: number;
  longitude?: number;
}

export function getAssessments(params: {
  state?: string;
  district?: string;
  year?: number;
  category?: string;
  limit?: number;
} = {}): Promise<AssessmentRecord[]> {
  const searchParams = new URLSearchParams();
  if (params.state) searchParams.set('state', params.state);
  if (params.district) searchParams.set('district', params.district);
  if (params.year) searchParams.set('year', String(params.year));
  if (params.category) searchParams.set('category', params.category);
  if (params.limit) searchParams.set('limit', String(params.limit));
  const qs = searchParams.toString();
  return fetchJson<AssessmentRecord[]>(`/api/assessments${qs ? '?' + qs : ''}`);
}

export function getDistricts(state?: string): Promise<{ state: string; district: string; blocks: number; latest_assessment_year: number; avg_extraction_stage: number }[]> {
  const params = state ? `?state=${encodeURIComponent(state)}` : '';
  return fetchJson(`/api/districts${params}`);
}

export function getBlocks(params: { state?: string; district?: string } = {}): Promise<{ state: string; district: string; block: string; latitude: number; longitude: number; latest_extraction_stage: number; latest_category: string }[]> {
  const searchParams = new URLSearchParams();
  if (params.state) searchParams.set('state', params.state);
  if (params.district) searchParams.set('district', params.district);
  const qs = searchParams.toString();
  return fetchJson(`/api/blocks${qs ? '?' + qs : ''}`);
}

export function getCategoryDistribution(state?: string, year?: number): Promise<{ category: string; count: number; percentage: number }[]> {
  const searchParams = new URLSearchParams();
  if (state) searchParams.set('state', state);
  if (year) searchParams.set('year', String(year));
  const qs = searchParams.toString();
  return fetchJson(`/api/analytics/category-distribution${qs ? '?' + qs : ''}`);
}

export function getTrend(state?: string): Promise<{ assessment_year: number; total_extraction: number; avg_extraction_stage: number; total_recharge: number; blocks_assessed: number }[]> {
  const params = state ? `?state=${encodeURIComponent(state)}` : '';
  return fetchJson(`/api/analytics/trend${params}`);
}

export function getWhatChanged(state: string, year1: number, year2: number): Promise<any> {
  return fetchJson(`/api/analytics/what-changed?state=${encodeURIComponent(state)}&year1=${year1}&year2=${year2}`);
}

export function getRiskScore(state: string, year?: number): Promise<any> {
  const params = year ? `?year=${year}` : '';
  return fetchJson(`/api/analytics/risk-score?state=${encodeURIComponent(state)}${params}`);
}

// ─── Map Action Types (for LLM integration) ─────────────────────────────────

export type MapActionType =
  | 'SELECT_STATE'
  | 'SELECT_DISTRICT'
  | 'SELECT_BLOCK'
  | 'ZOOM_TO_LOCATION'
  | 'SHOW_LAYER'
  | 'HIDE_LAYER'
  | 'SET_YEAR'
  | 'SET_FILTER'
  | 'SHOW_STATIONS'
  | 'SHOW_QUALITY'
  | 'SHOW_TREND'
  | 'COMPARE_LOCATIONS'
  | 'RESET_MAP';

export interface MapAction {
  type: MapActionType;
  state?: string;
  district?: string;
  block?: string;
  layer?: string;
  year?: number;
  filter?: string;
  value?: string;
  states?: string[];
  lat?: number;
  lng?: number;
  zoom?: number;
}

export interface VisualizationAction {
  type: string;
  metric?: string;
  state?: string;
  states?: string[];
}

export interface LLMMapResponse {
  message: string;
  map_action?: MapAction;
  visualization?: VisualizationAction;
}

// ─── District Data ───────────────────────────────────────────────────────────

export function getDistrictData(state: string): Promise<{ districts: any[] }> {
  return fetchJson(`/api/groundwater/district/${encodeURIComponent(state)}`);
}

export function getBlockData(state: string, district?: string): Promise<any[]> {
  const params = district ? `?district=${encodeURIComponent(district)}` : '';
  return fetchJson(`/api/groundwater/block/${encodeURIComponent(state)}${params}`);
}

export function getComparison(stateA: string, stateB: string): Promise<any> {
  return fetchJson(`/api/groundwater/compare?state_a=${encodeURIComponent(stateA)}&state_b=${encodeURIComponent(stateB)}`);
}

export function getOverExploited(): Promise<any> {
  return fetchJson('/api/groundwater/over-exploited');
}

export function getQualityInfo(state?: string): Promise<any> {
  const params = state ? `?state=${encodeURIComponent(state)}` : '';
  return fetchJson(`/api/groundwater/quality${params}`);
}
