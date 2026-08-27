import { useEffect, useState } from "react";
import { fetchJson } from "../lib/api";
import type { ViewKey } from "../data/states";

interface TopbarProps {
  onMenuClick?: () => void;
  onNavigate?: (view: ViewKey) => void;
}

interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

export default function Topbar({ onMenuClick, onNavigate }: TopbarProps) {
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;

    fetchJson<HealthResponse>("/api/health")
      .then((data) => {
        if (active) {
          setHealth(data);
        }
      })
      .catch(() => {
        if (active) {
          setHealth(null);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const handleAsk = () => {
    if (query.trim()) {
      onNavigate?.("assistant");
    }
  };

  return (
    <header className="topbar">
      <button
        className="menu-btn"
        aria-label="Toggle navigation"
        onClick={onMenuClick}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      </button>

      <div className="topbar-ask">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} width="16" height="16">
          <path d="M12 2 3 7l9 5 9-5-9-5Z" />
          <path d="M3 12l9 5 9-5M3 17l9 5 9-5" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask INGRES AI about groundwater…"
        />
        <button className="topbar-ask-btn" onClick={handleAsk}>
          Ask
        </button>
      </div>

      <div className="topbar-field">
        <span className="fk">Year</span>
        <span className="fv">2026</span>
      </div>
      <div className="topbar-field">
        <span className="fk">Location</span>
        <span className="fv">India</span>
      </div>

      <div className="topbar-spacer" />

      <button
        className="topbar-ai-btn"
        onClick={() => onNavigate?.("assistant")}
        title="Open INGRES AI Chatbot"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} width="16" height="16">
          <path d="M12 2a7 7 0 017 7c0 3-2 5.5-4 7.5L12 20l-3-3.5C7 14.5 5 12 5 9a7 7 0 017-7z" />
          <circle cx="12" cy="9" r="2.5" />
        </svg>
        <span>INGRES AI</span>
      </button>

      <div className="lang-toggle">
        <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>
          EN
        </button>
        <button className={lang === "hi" ? "active" : ""} onClick={() => setLang("hi")}>
          हिन्दी
        </button>
      </div>

      <div className="topbar-status">
        <span className="dot-live" /> {health ? `${health.service} Live` : "Backend Offline"}
      </div>
    </header>
  );
}
