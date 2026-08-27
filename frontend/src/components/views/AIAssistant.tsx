import { useState, useRef, useEffect, type FormEvent } from "react";
import {
  streamSmartChat,
  checkLLMHealth,
  type SmartChatApiResponse,
  type LLMHealthResponse,
  type SmartChatSource,
} from "../../lib/api";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  smartData?: SmartChatApiResponse;
  timestamp: Date;
  streaming?: boolean;
}

const suggestedQueries = [
  "What is the groundwater status of Punjab?",
  "Compare Rajasthan and Punjab.",
  "Which states have the highest extraction?",
  "Show over-exploited areas in Haryana.",
  "What is the trend for Tamil Nadu?",
  "Which states are in critical condition?",
  "Compare extraction in Karnataka and Maharashtra.",
  "What management measures help groundwater?",
];

const quickActions = [
  { label: "Overview", query: "Give me an overview of India's groundwater situation." },
  { label: "Top Stressed", query: "Which states have the highest groundwater extraction stage?" },
  { label: "Trends", query: "How has groundwater extraction changed over the years?" },
  { label: "Solutions", query: "What management solutions exist for groundwater problems?" },
];

function renderMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>")
    .replace(/^/, "<p>")
    .replace(/$/, "</p>");
}

let msgCounter = 0;
function nextId(): string {
  return `msg-${++msgCounter}-${Date.now()}`;
}

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [llmHealth, setLlmHealth] = useState<LLMHealthResponse | null>(null);
  const [language, setLanguage] = useState<"english" | "hindi">("english");
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const threadRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, loading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    checkLLMHealth()
      .then(setLlmHealth)
      .catch(() => setLlmHealth({ status: "error", ollama_installed: false, model_available: false }));
  }, []);

  const isLLMAvailable = llmHealth?.status === "ok";

  async function handleSend(e: FormEvent, overrideText?: string) {
    e.preventDefault();
    const text = overrideText || input.trim();
    if (!text || loading) return;

    const userMsg: Message = {
      id: nextId(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // Create placeholder for streaming AI response
    const aiMsgId = nextId();
    const aiMsg: Message = {
      id: aiMsgId,
      role: "ai",
      content: "",
      timestamp: new Date(),
      streaming: true,
    };
    setMessages((prev) => [...prev, aiMsg]);

    try {
      let fullReply = "";
      let sources: SmartChatSource[] = [];
      let queryType = "";
      let route = "";

      for await (const chunk of streamSmartChat(text, sessionId, language)) {
        if (chunk.type === "token") {
          fullReply += chunk.content as string;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsgId ? { ...m, content: fullReply } : m
            )
          );
        } else if (chunk.type === "sources") {
          sources = chunk.content as SmartChatSource[];
        } else if (chunk.type === "content") {
          fullReply = chunk.content as string;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsgId ? { ...m, content: fullReply } : m
            )
          );
        } else if (chunk.type === "done") {
          break;
        }
      }

      // Finalize message
      const smartData: SmartChatApiResponse = {
        reply: fullReply,
        sources,
        query_type: queryType,
        entities: {},
        session_id: sessionId,
        route,
      };

      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiMsgId ? { ...m, content: fullReply, smartData, streaming: false } : m
        )
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiMsgId
            ? { ...m, content: "Sorry, I encountered an error processing your request. Please try again.", streaming: false }
            : m
        )
      );
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  return (
    <section className="view active">
      <div className="assist-shell">
        <div className="assist-col">
          <div className="assist-col-pad">
            <div className="col-title">Recent Topics</div>
            {messages.length === 0 ? (
              <div className="topic-empty">No conversations yet</div>
            ) : (
              messages
                .filter((m) => m.role === "user")
                .slice(-8)
                .reverse()
                .map((m) => (
                  <div
                    className="topic-item"
                    key={m.id}
                    onClick={() => {
                      const aiResponse = messages.find(
                        (r) => r.role === "ai" && messages.indexOf(r) === messages.indexOf(m) + 1
                      );
                      if (aiResponse) {
                        const el = document.getElementById(aiResponse.id);
                        el?.scrollIntoView({ behavior: "smooth" });
                      }
                    }}
                  >
                    {m.content.length > 45 ? m.content.slice(0, 45) + "..." : m.content}
                    <span className="t-date">
                      {m.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                ))
            )}

            <div className="col-title" style={{ marginTop: 18 }}>
              Quick Actions
            </div>
            {quickActions.map((a) => (
              <div
                className="topic-item"
                key={a.label}
                onClick={(e) => handleSend(e, a.query)}
              >
                {a.label}
              </div>
            ))}
          </div>
        </div>

        <div className="assist-center">
          {/* Top Bar */}
          <div className="jaladhi-topbar">
            <div className="jaladhi-brand">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} width="18" height="18">
                <path d="M12 2a7 7 0 017 7c0 3-2 5.5-4 7.5L12 20l-3-3.5C7 14.5 5 12 5 9a7 7 0 017-7z" />
                <circle cx="12" cy="9" r="2.5" />
              </svg>
              <span className="jaladhi-name">Jaladhi</span>
              <span className="jaladhi-badge">AI</span>
            </div>
            <div className="jaladhi-controls">
              <div className="lang-toggle">
                <button
                  className={`lang-btn ${language === "english" ? "active" : ""}`}
                  onClick={() => setLanguage("english")}
                >
                  EN
                </button>
                <button
                  className={`lang-btn ${language === "hindi" ? "active" : ""}`}
                  onClick={() => setLanguage("hindi")}
                >
                  हिंदी
                </button>
              </div>
              <div className={`jaladhi-status ${isLLMAvailable ? "online" : "offline"}`}>
                <span className="status-dot" />
                {isLLMAvailable ? "Online" : "Offline"}
              </div>
            </div>
          </div>

          <div className="assist-thread" ref={threadRef}>
            {messages.length === 0 && (
              <div className="assist-welcome">
                <div className="assist-welcome-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2}>
                    <path d="M12 2C12 2 4 12 4 17.2C4 22 8 24.5 12 24.5C16 24.5 20 22 20 17.2C20 12 12 2 12 2Z" />
                    <path d="M8 17c1.5 2 3 2.8 4 2.8s2.5-.8 4-2.8" />
                  </svg>
                </div>
                <h2 className="assist-welcome-title">जल DRISTHI</h2>
                <p className="assist-welcome-sub">
                  Professional groundwater intelligence for all 36 Indian states and union territories.
                  Ask about extraction, recharge, trends, comparisons, quality, and management.
                </p>
                <div className="assist-welcome-chips">
                  {suggestedQueries.slice(0, 4).map((q) => (
                    <button
                      className="assist-welcome-chip"
                      key={q}
                      onClick={(e) => handleSend(e, q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div
                className={`msg msg-${msg.role}`}
                key={msg.id}
                id={msg.id}
              >
                {msg.role === "ai" && (
                  <div className="ai-tag">
                    <span className="dot-live" />
                    <span>Jaladhi</span>
                  </div>
                )}
                <div className={msg.role === "user" ? "bubble" : "ai-card"}>
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className="ai-card-inner">
                      <div className="ai-card-body">
                        {msg.streaming && !msg.content ? (
                          <div className="ai-typing">
                            <span className="dot" />
                            <span className="dot" />
                            <span className="dot" />
                            <span className="ai-typing-label">Analyzing groundwater data...</span>
                          </div>
                        ) : (
                          <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                        )}
                      </div>

                      {msg.smartData?.sources && msg.smartData.sources.length > 0 && (
                        <div className="ai-evidence">
                          {msg.smartData.sources.map((s: SmartChatSource, i: number) => (
                            <div className="ai-evidence-row" key={i}>
                              <span className="ai-evidence-label">{s.type === "database" ? "Data" : "Knowledge"}</span>
                              <span>{s.title}</span>
                            </div>
                          ))}
                          {msg.smartData.route && (
                            <div className="ai-evidence-row">
                              <span className="ai-evidence-label">Analysis</span>
                              <span className="mono">{msg.smartData.query_type}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {msg.smartData && !msg.streaming && (
                        <div className="ai-followups">
                          {["Tell me more about this.", "Compare with other states.", "Show the trend."].map((f) => (
                            <button
                              className="chip"
                              key={f}
                              onClick={(e) => handleSend(e, f)}
                            >
                              {f}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && messages[messages.length - 1]?.role === "user" && (
              <div className="msg msg-ai">
                <div className="ai-tag">
                  <span className="dot-live" />
                  <span>Jaladhi</span>
                </div>
                <div className="ai-card">
                  <div className="ai-typing">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                    <span className="ai-typing-label">Analyzing groundwater data...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form className="assist-inputbar" onSubmit={handleSend}>
            <div className="assist-input">
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask about Indian groundwater..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <button type="submit" aria-label="Send" disabled={loading || !input.trim()}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </button>
            </div>
          </form>
        </div>

        <div className="assist-col assist-right">
          <div className="assist-col-pad">
            <div className="col-title">Suggested Queries</div>
            {suggestedQueries.map((q) => (
              <div
                className="topic-item"
                key={q}
                onClick={(e) => handleSend(e, q)}
              >
                {q}
              </div>
            ))}
            <div className="col-title" style={{ marginTop: 18 }}>
              Capabilities
            </div>
            <div className="coverage-item">
              <span className="coverage-label">States/UTs</span>
              <span className="coverage-val mono">36</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Data Source</span>
              <span className="coverage-val">CGWB / IN-GRES</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Analysis</span>
              <span className="coverage-val">SQL + Knowledge</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Languages</span>
              <span className="coverage-val">English / हिंदी</span>
            </div>
            <div className="col-title" style={{ marginTop: 18 }}>
              Query Types
            </div>
            <div className="topic-item">State status & overview</div>
            <div className="topic-item">State comparisons</div>
            <div className="topic-item">Trend analysis</div>
            <div className="topic-item">Rankings & top areas</div>
            <div className="topic-item">Quality information</div>
            <div className="topic-item">Management advice</div>
          </div>
        </div>
      </div>
    </section>
  );
}
