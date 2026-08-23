import { useEffect, useState } from "react";
import { fetchJson } from "../lib/api";

interface TopbarProps {
  onMenuClick?: () => void;
}

interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [health, setHealth] = useState<HealthResponse | null>(null);

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

      <div className="search-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <circle cx="11" cy="11" r="7" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input type="text" placeholder="Search district, block, or dataset…" />
      </div>

      <div className="topbar-field">
        <span className="fk">Year</span>
        <span className="fv">2024</span>
      </div>
      <div className="topbar-field">
        <span className="fk">Location</span>
        <span className="fv">India</span>
      </div>

      <div className="topbar-spacer" />

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
