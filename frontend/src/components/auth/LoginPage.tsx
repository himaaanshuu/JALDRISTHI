import { useState } from "react";
import { useAuth } from "./AuthContext";
import { supabase } from "../../lib/supabase";

type AuthView = "login" | "otp-sent" | "profile-complete";

export default function LoginPage() {
  const { signInWithGoogle, signInWithOtp, verifyOtp, user } = useAuth();
  const [view, setView] = useState<AuthView>("login");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // Profile completion fields
  const [fullName, setFullName] = useState(user?.user_metadata?.full_name || user?.user_metadata?.name || "");
  const [profileEmail, setProfileEmail] = useState(user?.email || "");
  const [profilePhone, setProfilePhone] = useState(user?.phone || "");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  const validateIndianPhone = (p: string): boolean => {
    const cleaned = p.replace(/\D/g, "");
    if (cleaned.length === 10 && /^[6-9]\d{9}$/.test(cleaned)) return true;
    if (cleaned.length === 12 && /^91[6-9]\d{9}$/.test(cleaned)) return true;
    return false;
  };

  const formatPhone = (p: string): string => {
    const cleaned = p.replace(/\D/g, "");
    if (cleaned.length === 10) return `+91${cleaned}`;
    if (cleaned.length === 12 && cleaned.startsWith("91")) return `+${cleaned}`;
    return `+91${cleaned}`;
  };

  const handleGoogleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Google sign-in failed");
      setLoading(false);
    }
  };

  const handleSendOtp = async () => {
    setError("");
    const formatted = formatPhone(phone);
    if (!validateIndianPhone(phone)) {
      setError("Please enter a valid 10-digit Indian mobile number");
      return;
    }
    setLoading(true);
    const result = await signInWithOtp(formatted);
    setLoading(false);
    if (result.error) {
      setError(result.error);
    } else {
      setView("otp-sent");
      startCountdown();
    }
  };

  const handleVerifyOtp = async () => {
    setError("");
    if (otp.length !== 6) {
      setError("Please enter a 6-digit OTP");
      return;
    }
    const formatted = formatPhone(phone);
    setLoading(true);
    const result = await verifyOtp(formatted, otp);
    setLoading(false);
    if (result.error) {
      setError(result.error);
    }
  };

  const handleResendOtp = async () => {
    setError("");
    const formatted = formatPhone(phone);
    setLoading(true);
    const result = await signInWithOtp(formatted);
    setLoading(false);
    if (result.error) {
      setError(result.error);
    } else {
      startCountdown();
    }
  };

  const startCountdown = () => {
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleSaveProfile = async () => {
    if (!user) return;
    if (!fullName.trim()) {
      setError("Please enter your name");
      return;
    }
    setProfileSaving(true);
    setError("");

    const { error: upsertError } = await supabase
      .from("profiles")
      .upsert(
        {
          auth_user_id: user.id,
          full_name: fullName.trim(),
          email: profileEmail.trim(),
          phone: profilePhone.trim(),
          avatar_url: user.user_metadata?.avatar_url || "",
          updated_at: new Date().toISOString(),
        },
        { onConflict: "auth_user_id" }
      );

    setProfileSaving(false);
    if (upsertError) {
      setError(upsertError.message);
    } else {
      setProfileSaved(true);
      setTimeout(() => window.location.reload(), 800);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            <svg viewBox="0 0 48 48" fill="none" width="56" height="56">
              <defs>
                <linearGradient id="authDropGrad" x1="24" y1="4" x2="24" y2="44">
                  <stop offset="0%" stopColor="#3498db" />
                  <stop offset="100%" stopColor="#1a5276" />
                </linearGradient>
              </defs>
              <path d="M24 4C24 4 8 18 8 26C8 34 15 42 24 42C33 42 40 34 40 26C40 18 24 4 24 4Z" fill="url(#authDropGrad)" />
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
          <div className="auth-tagline">जल संरक्षण • जल संवर्धन • जल समृद्धि</div>
          <div className="auth-sub-tagline">Groundwater Intelligence for a Sustainable India</div>
        </div>

        {view === "login" && (
          <div className="auth-form">
            <h2 className="auth-form-title">Welcome</h2>
            <p className="auth-form-sub">Sign in to access groundwater intelligence</p>

            <button
              className="auth-btn auth-btn-google"
              onClick={handleGoogleLogin}
              disabled={loading}
            >
              <svg viewBox="0 0 24 24" width="20" height="20">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
              Continue with Google
            </button>

            <div className="auth-divider">
              <span>OR</span>
            </div>

            <div className="auth-phone-group">
              <label className="auth-label">Mobile Number</label>
              <div className="auth-phone-input">
                <span className="auth-country-code">+91</span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => {
                    setPhone(e.target.value.replace(/\D/g, "").slice(0, 10));
                    setError("");
                  }}
                  placeholder="9876543210"
                  className="auth-input"
                  maxLength={10}
                />
              </div>
            </div>

            <button
              className="auth-btn auth-btn-primary"
              onClick={handleSendOtp}
              disabled={loading || phone.length < 10}
            >
              {loading ? "Sending..." : "Send OTP"}
            </button>

            {error && <div className="auth-error">{error}</div>}
          </div>
        )}

        {view === "otp-sent" && (
          <div className="auth-form">
            <div className="auth-step-indicator">
              <div className="auth-step-dot done" />
              <div className="auth-step-dot active" />
              <div className="auth-step-dot" />
            </div>
            <h2 className="auth-form-title">Enter OTP</h2>
            <p className="auth-form-sub">
              6-digit code sent to +91 {phone}
            </p>

            <div className="auth-otp-group">
              <input
                type="text"
                value={otp}
                onChange={(e) => {
                  setOtp(e.target.value.replace(/\D/g, "").slice(0, 6));
                  setError("");
                }}
                placeholder="_ _ _ _ _ _"
                className="auth-input auth-otp-input"
                maxLength={6}
                autoFocus
              />
            </div>

            <button
              className="auth-btn auth-btn-primary"
              onClick={handleVerifyOtp}
              disabled={loading || otp.length !== 6}
            >
              {loading ? "Verifying..." : "Verify OTP"}
            </button>

            <div className="auth-otp-actions">
              {countdown > 0 ? (
                <span className="auth-countdown">Resend OTP in {countdown}s</span>
              ) : (
                <button
                  className="auth-link-btn"
                  onClick={handleResendOtp}
                  disabled={loading}
                >
                  Resend OTP
                </button>
              )}
              <button
                className="auth-link-btn"
                onClick={() => {
                  setView("login");
                  setOtp("");
                  setError("");
                }}
              >
                Change Number
              </button>
            </div>

            {error && <div className="auth-error">{error}</div>}
          </div>
        )}

        {view === "profile-complete" && (
          <div className="auth-form">
            <div className="auth-step-indicator">
              <div className="auth-step-dot done" />
              <div className="auth-step-dot done" />
              <div className="auth-step-dot active" />
            </div>
            <h2 className="auth-form-title">Complete Your Profile</h2>
            <p className="auth-form-sub">Tell us a bit about yourself</p>

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
                value={profileEmail}
                onChange={(e) => setProfileEmail(e.target.value)}
                placeholder="your@email.com"
                className="auth-text-input"
              />
            </div>

            <div className="auth-field-group">
              <label className="auth-label">Mobile Number</label>
              <input
                type="tel"
                value={profilePhone}
                onChange={(e) => setProfilePhone(e.target.value)}
                placeholder="+91 9876543210"
                className="auth-text-input"
              />
            </div>

            <button
              className="auth-btn auth-btn-success"
              onClick={handleSaveProfile}
              disabled={profileSaving || !fullName.trim()}
            >
              {profileSaving ? "Saving..." : profileSaved ? "Redirecting..." : "Continue to Dashboard"}
            </button>

            {error && <div className="auth-error">{error}</div>}
          </div>
        )}

        <div className="auth-footer">
          <p>By signing in, you agree to our terms of service and privacy policy.</p>
        </div>
      </div>
    </div>
  );
}
