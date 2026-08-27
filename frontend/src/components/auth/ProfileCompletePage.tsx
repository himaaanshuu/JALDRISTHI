import { useState } from "react";
import { useAuth } from "./AuthContext";
import { supabase } from "../../lib/supabase";

export default function ProfileCompletePage() {
  const { user, refreshProfile } = useAuth();
  const [fullName, setFullName] = useState(user?.user_metadata?.full_name || user?.user_metadata?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!user) return;
    if (!fullName.trim()) {
      setError("Please enter your name");
      return;
    }
    setSaving(true);
    setError("");

    const { error: upsertError } = await supabase
      .from("profiles")
      .upsert(
        {
          auth_user_id: user.id,
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim(),
          avatar_url: user.user_metadata?.avatar_url || "",
          updated_at: new Date().toISOString(),
        },
        { onConflict: "auth_user_id" }
      );

    setSaving(false);
    if (upsertError) {
      setError(upsertError.message);
    } else {
      setSaved(true);
      await refreshProfile();
      setTimeout(() => window.location.reload(), 600);
    }
  };

  const handleSkip = async () => {
    if (!user) return;
    await supabase
      .from("profiles")
      .upsert(
        {
          auth_user_id: user.id,
          full_name: user.user_metadata?.full_name || user.user_metadata?.name || "User",
          email: user.email || "",
          phone: user.phone || "",
          avatar_url: user.user_metadata?.avatar_url || "",
          updated_at: new Date().toISOString(),
        },
        { onConflict: "auth_user_id" }
      );
    await refreshProfile();
    window.location.reload();
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            <svg viewBox="0 0 48 48" fill="none" width="56" height="56">
              <defs>
                <linearGradient id="pcDropGrad" x1="24" y1="4" x2="24" y2="44">
                  <stop offset="0%" stopColor="#3498db" />
                  <stop offset="100%" stopColor="#1a5276" />
                </linearGradient>
              </defs>
              <path d="M24 4C24 4 8 18 8 26C8 34 15 42 24 42C33 42 40 34 40 26C40 18 24 4 24 4Z" fill="url(#pcDropGrad)" />
              <path d="M12 32C16 28 18 26 24 26C30 26 32 28 36 32" stroke="#fff" strokeWidth="1.5" fill="none" opacity="0.4" />
              <path d="M36 14C38 12 40 14 38 16C36 18 34 16 36 14Z" fill="#27ae60" />
              <path d="M38 18C40 16 42 18 40 20C38 22 36 20 38 18Z" fill="#2ecc71" />
              <circle cx="24" cy="20" r="4" fill="#fff" opacity="0.2" />
              <circle cx="24" cy="20" r="2" fill="#fff" opacity="0.3" />
            </svg>
          </div>
          <h1 className="auth-title">
            <span className="auth-title-hi">जल</span>
            <span className="auth-title-en">DRISTHI</span>
          </h1>
        </div>

        <div className="auth-form">
          <div className="auth-step-indicator">
            <div className="auth-step-dot done" />
            <div className="auth-step-dot done" />
            <div className="auth-step-dot active" />
          </div>
          <h2 className="auth-form-title">Complete Your Profile</h2>
          <p className="auth-form-sub">Tell us about yourself to personalize your experience</p>

          {user?.user_metadata?.avatar_url && (
            <div style={{ textAlign: "center", marginBottom: "var(--sp-4)" }}>
              <img
                src={user.user_metadata.avatar_url}
                alt="Avatar"
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: "50%",
                  border: "2px solid rgba(93,173,226,0.3)",
                }}
              />
            </div>
          )}

          <div className="auth-field-group">
            <label className="auth-label">Full Name *</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Enter your full name"
              className="auth-text-input"
              autoFocus
            />
          </div>

          <div className="auth-field-group">
            <label className="auth-label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="auth-text-input"
            />
          </div>

          <div className="auth-field-group">
            <label className="auth-label">Mobile Number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 9876543210"
              className="auth-text-input"
            />
          </div>

          <button
            className="auth-btn auth-btn-success"
            onClick={handleSave}
            disabled={saving || !fullName.trim() || saved}
          >
            {saving ? "Saving..." : saved ? "Welcome!" : "Continue to Dashboard"}
          </button>

          <div style={{ textAlign: "center", marginTop: "var(--sp-3)" }}>
            <button className="auth-link-btn" onClick={handleSkip}>
              Skip for now
            </button>
          </div>

          {error && <div className="auth-error">{error}</div>}
        </div>

        <div className="auth-footer">
          <p>By continuing, you agree to our terms of service and privacy policy.</p>
        </div>
      </div>
    </div>
  );
}
