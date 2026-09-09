import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../lib/supabase";

function getRedirectPath(): string {
  const intent = localStorage.getItem("jd-auth-intent");
  const target = localStorage.getItem("jd-auth-target");
  if (intent) {
    localStorage.removeItem("jd-auth-intent");
    localStorage.removeItem("jd-auth-target");
    if (intent === "signup") return "/profile";
    if (target) return target;
    return "/dashboard";
  }
  if (target) {
    localStorage.removeItem("jd-auth-target");
    return target;
  }
  return "/";
}

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        navigate(getRedirectPath(), { replace: true });
      } else {
        const timer = setTimeout(() => {
          supabase.auth.getSession().then(() => {
            navigate(getRedirectPath(), { replace: true });
          });
        }, 1000);
        return () => clearTimeout(timer);
      }
    });
  }, [navigate]);

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-loading">
          <div className="auth-spinner" />
          <p style={{ color: "rgba(255,255,255,0.5)", fontFamily: "var(--font-ui)", fontSize: 13 }}>
            Completing sign-in...
          </p>
        </div>
      </div>
    </div>
  );
}
