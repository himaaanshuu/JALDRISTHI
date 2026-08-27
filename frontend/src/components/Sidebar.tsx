import type { ReactNode } from "react";
import type { ViewKey } from "../data/states";
import { useAuth } from "./auth/AuthContext";

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
    label: "INGRES AI",
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
  {
    key: "quality",
    label: "Water Quality",
    hindi: "जल गुणवत्ता",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
        <path d="M12 2a7 7 0 017 7c0 3-2 5.5-4 7.5L12 20l-3-3.5C7 14.5 5 12 5 9a7 7 0 017-7z" />
        <path d="M8 16l4 4 4-4" />
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
  const { user, signOut } = useAuth();
  const displayName = user?.user_metadata?.full_name
    || user?.user_metadata?.name
    || user?.email
    || user?.phone
    || "User";
  const avatarUrl = user?.user_metadata?.avatar_url;
  const initial = displayName[0]?.toUpperCase() || "U";

  return (
    <aside className={`sidebar${open ? " open" : ""}`} id="sidebar">
      <div className="brand" style={{ cursor: "pointer" }} onClick={() => onNavigate("overview")}>
        <div className="brand-mark">
          <span className="brand-glyph">
            <svg viewBox="0 0 48 48" fill="none">
              <defs>
                <linearGradient id="dropGrad" x1="24" y1="4" x2="24" y2="44">
                  <stop offset="0%" stopColor="#3498db" />
                  <stop offset="50%" stopColor="#1a5276" />
                  <stop offset="100%" stopColor="#154360" />
                </linearGradient>
                <linearGradient id="leafGrad" x1="36" y1="12" x2="42" y2="24">
                  <stop offset="0%" stopColor="#27ae60" />
                  <stop offset="100%" stopColor="#2ecc71" />
                </linearGradient>
              </defs>
              <path d="M24 4C24 4 8 18 8 26C8 34 15 42 24 42C33 42 40 34 40 26C40 18 24 4 24 4Z" fill="url(#dropGrad)" />
              <path d="M12 32C16 28 18 26 24 26C30 26 32 28 36 32" stroke="#fff" strokeWidth="1.5" fill="none" opacity="0.4" />
              <path d="M36 14C38 12 40 14 38 16C36 18 34 16 36 14Z" fill="url(#leafGrad)" />
              <path d="M38 18C40 16 42 18 40 20C38 22 36 20 38 18Z" fill="#2ecc71" />
              <circle cx="24" cy="20" r="4" fill="#fff" opacity="0.2" />
              <circle cx="24" cy="20" r="2" fill="#fff" opacity="0.3" />
            </svg>
          </span>
          <div className="brand-name-block">
            <span className="brand-hindi">जल</span>
            <span className="brand-english">DRISTHI</span>
          </div>
        </div>
        <div className="brand-tagline">जल संरक्षण • जल संवर्धन • जल समृद्धि</div>
        <div className="brand-sub">Groundwater Intelligence for a Sustainable India</div>
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
        {user && (
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              {avatarUrl ? (
                <img src={avatarUrl} alt="" />
              ) : (
                <span>{initial}</span>
              )}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{displayName}</span>
              <span className="sidebar-user-role">{user.app_metadata?.role || "user"}</span>
            </div>
            <button
              className="sidebar-user-btn"
              onClick={signOut}
              title="Sign out"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                <polyline points="16,17 21,12 16,7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          </div>
        )}
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
