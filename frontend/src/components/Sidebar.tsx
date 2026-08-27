import type { ReactNode } from "react";
import type { ViewKey } from "../data/states";

interface NavEntry {
  key: ViewKey;
  label: string;
  hindi: string;
  icon: ReactNode;
  badge?: string;
}

const navEntries: NavEntry[] = [
  {
    key: "overview",
    label: "Overview",
    hindi: "अवलोकन",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <rect x="3" y="3" width="7" height="9" rx="1" />
        <rect x="14" y="3" width="7" height="5" rx="1" />
        <rect x="14" y="12" width="7" height="9" rx="1" />
        <rect x="3" y="16" width="7" height="5" rx="1" />
      </svg>
    ),
  },
  {
    key: "assistant",
    label: "Jaladhi",
    hindi: "जलाधि",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M12 2a7 7 0 017 7c0 3-2 5.5-4 7.5L12 20l-3-3.5C7 14.5 5 12 5 9a7 7 0 017-7z" />
        <circle cx="12" cy="9" r="2.5" />
      </svg>
    ),
  },
  {
    key: "map",
    label: "Groundwater Map",
    hindi: "भूजल मानचित्र",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M9 4 3 6.5v14L9 18l6 2.5 6-2.5v-14L15 6.5 9 4Z" />
        <path d="M9 4v14M15 6.5v14" />
      </svg>
    ),
  },
  {
    key: "learning",
    label: "Groundwater Learning",
    hindi: "जलज्ञान",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M12 2L2 7l10 5 10-5-10-5Z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
  {
    key: "analytics",
    label: "Analytics",
    hindi: "विश्लेषण",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M4 20V10M11 20V4M18 20v-7" />
      </svg>
    ),
  },
  {
    key: "compare",
    label: "Compare",
    hindi: "तुलना",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M8 3v18M16 3v18M3 8h5M16 8h5M3 16h5M16 16h5" />
      </svg>
    ),
  },
  {
    key: "reports",
    label: "Reports",
    hindi: "रिपोर्ट्स",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M6 3h9l5 5v13H6V3Z" />
        <path d="M15 3v5h5M9 12h6M9 16h6" />
      </svg>
    ),
  },
  {
    key: "sources",
    label: "Data Sources",
    hindi: "डेटा स्रोत",
    badge: "CGWB",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <ellipse cx="12" cy="6" rx="8" ry="3" />
        <path d="M4 6v12c0 1.66 3.58 3 8 3s8-1.34 8-3V6" />
        <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
      </svg>
    ),
  },
];

interface SidebarProps {
  active: ViewKey;
  onNavigate: (view: ViewKey) => void;
  open: boolean;
}

export default function Sidebar({ active, onNavigate, open }: SidebarProps) {
  return (
    <aside className={`sidebar${open ? " open" : ""}`} id="sidebar">
      <div className="brand" style={{ cursor: "pointer" }} onClick={() => onNavigate("overview")}>
        <div className="brand-mark">
          <span className="brand-glyph">
            <svg viewBox="0 0 26 26" fill="none">
              <path
                d="M13 2C13 2 4 12 4 17.2C4 22 8 24.5 13 24.5C18 24.5 22 22 22 17.2C22 12 13 2 13 2Z"
                stroke="#5796A5"
                strokeWidth={1.6}
              />
              <path
                d="M8 17c1.5 2 3 2.8 5 2.8s3.5-.8 5-2.8"
                stroke="#5796A5"
                strokeWidth={1.2}
                opacity={0.6}
              />
            </svg>
          </span>
          <div className="brand-name-block">
            <span className="brand-hindi">जलदृष्टि</span>
            <span className="brand-english">DRISTI</span>
          </div>
        </div>
        <div className="brand-sub">Groundwater Intelligence</div>
      </div>

      <nav className="nav">
        <div className="nav-section-label">Overview</div>
        {navEntries.slice(0, 3).map((entry) => (
          <a
            key={entry.key}
            className={`nav-item${active === entry.key ? " active" : ""}`}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onNavigate(entry.key);
            }}
          >
            {entry.icon}
            <div className="nav-item-text">
              <span className="nav-item-label">{entry.label}</span>
              <span className="nav-item-hindi">{entry.hindi}</span>
            </div>
            {entry.badge && <span className="badge">{entry.badge}</span>}
          </a>
        ))}

        <div className="nav-section-label" style={{ marginTop: 8 }}>Intelligence</div>
        {navEntries.slice(3).map((entry) => (
          <a
            key={entry.key}
            className={`nav-item${active === entry.key ? " active" : ""}`}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onNavigate(entry.key);
            }}
          >
            {entry.icon}
            <div className="nav-item-text">
              <span className="nav-item-label">{entry.label}</span>
              <span className="nav-item-hindi">{entry.hindi}</span>
            </div>
            {entry.badge && <span className="badge">{entry.badge}</span>}
          </a>
        ))}
      </nav>

      <div className="sidebar-foot">
        <div className="sys-status">
          <span className="dot-live" /> System Status · Operational
        </div>
        <div className="nav-item" style={{ color: "#A0B8BD" }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
            <circle cx="12" cy="12" r="9" />
            <path d="M12 16v-5M12 8h.01" />
          </svg>
          About
        </div>
      </div>
    </aside>
  );
}
