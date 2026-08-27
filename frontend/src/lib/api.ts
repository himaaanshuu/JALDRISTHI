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
