import { ReactNode } from "react";
import { useAuth } from "./AuthContext";
import LoginPage from "./LoginPage";

interface ProtectedRouteProps {
  children: ReactNode;
  requireAuth?: boolean;
}

export default function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
  const { session, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-loading">
            <div className="auth-spinner" />
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (requireAuth && !session) {
    return <LoginPage />;
  }

  return <>{children}</>;
}
