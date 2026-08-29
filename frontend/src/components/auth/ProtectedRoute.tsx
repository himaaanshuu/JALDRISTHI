import { ReactNode } from "react";
import { useAuth } from "./AuthContext";
import LoginPage from "./LoginPage";
import ProfileCompletePage from "./ProfileCompletePage";

interface ProtectedRouteProps {
  children: ReactNode;
  requireAuth?: boolean;
}

export default function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
  const { session, loading, profileComplete } = useAuth();

  if (loading) {
    return (
      <div className="auth-page" style={{ background: "#0a1628" }}>
        <div className="auth-card">
          <div className="auth-loading">
            <div className="auth-spinner" />
            <p style={{ color: "rgba(255,255,255,0.5)", fontFamily: "var(--font-ui)", fontSize: 13 }}>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (requireAuth && !session) {
    return <LoginPage />;
  }

  if (session && !profileComplete) {
    return <ProfileCompletePage />;
  }

  return <>{children}</>;
}
