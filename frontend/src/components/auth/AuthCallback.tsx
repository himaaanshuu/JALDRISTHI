import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../lib/supabase";

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        navigate("/", { replace: true });
      } else {
        // Wait a moment for the session to be set
        const timer = setTimeout(() => {
          supabase.auth.getSession().then(({ data: { session: s } }) => {
            if (s) {
              navigate("/", { replace: true });
            } else {
              navigate("/", { replace: true });
            }
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
