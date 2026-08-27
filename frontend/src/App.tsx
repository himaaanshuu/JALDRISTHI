import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./components/auth/AuthContext";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import AuthCallback from "./components/auth/AuthCallback";
import ProfilePage from "./components/auth/ProfilePage";
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
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
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
