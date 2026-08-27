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
): Promise<LLMChatApiResponse> {
  return fetchJson<LLMChatApiResponse>("/api/llm/chat", {
    method: "POST",
    body: JSON.stringify({ message, top_k }),
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
