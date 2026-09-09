import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./components/auth/AuthContext";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import AuthCallback from "./components/auth/AuthCallback";
import ProfilePage from "./components/auth/ProfilePage";
import LandingPage from "./components/Landing/LandingPage";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Overview from "./components/views/Overview";
import AIAssistant from "./components/views/AIAssistant";
import MapView from "./components/views/MapView";
import Analytics from "./components/views/Analytics";
import Compare from "./components/views/Compare";
import Reports from "./components/views/Reports";
import DataSources from "./components/views/DataSources";
import Learning from "./components/views/Learning";
import WaterQuality from "./components/views/WaterQuality";
import type { ViewKey } from "./data/states";
import "./App.css";
import "./Auth.css";

function PostLoginRedirect() {
  const { consumeRedirect } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const path = consumeRedirect();
    if (path) {
      navigate(path, { replace: true });
    }
  }, [consumeRedirect, navigate]);

  return null;
}

function MainApp() {
  const [view, setView] = useState<ViewKey>("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNavigate = (next: ViewKey) => {
    setView(next);
    setSidebarOpen(false);
  };

  return (
    <div className="app">
      <Sidebar active={view} onNavigate={handleNavigate} open={sidebarOpen} />
      <Topbar onMenuClick={() => setSidebarOpen((o) => !o)} onNavigate={handleNavigate} />

      <main className="content" id="content">
        {view === "overview" && <Overview />}
        {view === "assistant" && <AIAssistant />}
        {view === "map" && <MapView />}
        {view === "analytics" && <Analytics />}
        {view === "compare" && <Compare />}
        {view === "reports" && <Reports />}
        {view === "sources" && <DataSources />}
        {view === "learning" && <Learning />}
        {view === "quality" && <WaterQuality />}
        {view === "profile" && <ProfilePage />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PostLoginRedirect />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/*"
            element={
              <ProtectedRoute requireAuth={true}>
                <MainApp />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
