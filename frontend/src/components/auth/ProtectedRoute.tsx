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
    return null;
  }

  if (requireAuth && !session) {
    return <LoginPage />;
  }

  if (session && !profileComplete) {
    return <ProfileCompletePage />;
  }

  return <>{children}</>;
}
