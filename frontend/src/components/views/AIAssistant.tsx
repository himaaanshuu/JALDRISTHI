import { useState, useRef, useEffect, type FormEvent } from "react";
import { sendChatMessage, type ChatApiResponse } from "../../lib/api";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  data?: ChatApiResponse;
  timestamp: Date;
}

const suggestedQueries = [
  "What is the groundwater status of Punjab?",
  "Compare Haryana between 2020 and 2024.",
  "Which districts have the highest extraction?",
  "Show over-exploited areas in Rajasthan.",
  "What is the trend for Gujarat?",
  "Which states are in critical condition?",
  "Tell me about Delhi NCR groundwater.",
  "Compare extraction in Tamil Nadu and Karnataka.",
];

const quickActions = [
  { label: "Status", query: "What is the groundwater status of India?" },
  { label: "Critical", query: "Show critical and over-exploited areas." },
  { label: "Compare", query: "Compare extraction between 2020 and 2024." },
  { label: "Trend", query: "What is the extraction trend?" },
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

    try {
      const data = await sendChatMessage(text);
      const aiMsg: Message = {
        id: nextId(),
        role: "ai",
        content: data.reply,
        data,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      const errMsg: Message = {
        id: nextId(),
        role: "ai",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
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
          <div className="assist-thread" ref={threadRef}>
            {messages.length === 0 && (
              <div className="assist-welcome">
                <div className="assist-welcome-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2}>
                    <path d="M12 2C12 2 4 12 4 17.2C4 22 8 24.5 12 24.5C16 24.5 20 22 20 17.2C20 12 12 2 12 2Z" />
                    <path d="M8 17c1.5 2 3 2.8 4 2.8s2.5-.8 4-2.8" />
                  </svg>
                </div>
                <h2 className="assist-welcome-title">जलदृष्टि DRISTI</h2>
                <p className="assist-welcome-sub">
                  Ask me anything about India's groundwater data. I have access to official
                  CGWB/IN-GRES assessments covering all 36 states, 285 districts, and 4 years of data.
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
                    <span>जलदृष्टि DRISTI</span>
                  </div>
                )}
                <div className={msg.role === "user" ? "bubble" : "ai-card"}>
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className="ai-card-inner">
                      <div
                        className="ai-card-body"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                      />

                      {msg.data?.evidence && (
                        <div className="ai-evidence">
                          <div className="ai-evidence-row">
                            <span className="ai-evidence-label">Source</span>
                            <span>{msg.data.evidence.source}</span>
                          </div>
                          <div className="ai-evidence-row">
                            <span className="ai-evidence-label">Location</span>
                            <span>{msg.data.evidence.location}</span>
                          </div>
                          <div className="ai-evidence-row">
                            <span className="ai-evidence-label">Records</span>
                            <span className="mono">{msg.data.evidence.records_used}</span>
                          </div>
                          <div className="ai-evidence-row">
                            <span className="ai-evidence-label">Confidence</span>
                            <span
                              className={`confidence-${msg.data.evidence.confidence.toLowerCase()}`}
                            >
                              {msg.data.evidence.confidence}
                            </span>
                          </div>
                        </div>
                      )}

                      {msg.data?.suggested_followups &&
                        msg.data.suggested_followups.length > 0 && (
                          <div className="ai-followups">
                            {msg.data.suggested_followups.map((f) => (
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

            {loading && (
              <div className="msg msg-ai">
                <div className="ai-tag">
                  <span className="dot-live" />
                  <span>जलदृष्टि DRISTI</span>
                </div>
                <div className="ai-card">
                  <div className="ai-typing">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
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
                placeholder="Ask a follow-up about groundwater..."
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
              Data Coverage
            </div>
            <div className="coverage-item">
              <span className="coverage-label">States/UTs</span>
              <span className="coverage-val mono">36</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Districts</span>
              <span className="coverage-val mono">285</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Blocks</span>
              <span className="coverage-val mono">192</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Assessment Years</span>
              <span className="coverage-val mono">2020, 22, 24, 25</span>
            </div>
            <div className="coverage-item">
              <span className="coverage-label">Total Records</span>
              <span className="coverage-val mono">914</span>
            </div>
            <div className="col-title" style={{ marginTop: 18 }}>
              Source
            </div>
            <div className="coverage-source">
              Central Ground Water Board (CGWB)
              <br />
              Ministry of Jal Shakti
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
