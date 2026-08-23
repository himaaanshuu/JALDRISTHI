import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Overview from "./components/views/Overview";
import AIAssistant from "./components/views/AIAssistant";
import MapView from "./components/views/MapView";
import Analytics from "./components/views/Analytics";
import Compare from "./components/views/Compare";
import Reports from "./components/views/Reports";
import DataSources from "./components/views/DataSources";
import type { ViewKey } from "./data/states";
import "./App.css";

export default function App() {
  const [view, setView] = useState<ViewKey>("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNavigate = (next: ViewKey) => {
    setView(next);
    setSidebarOpen(false);
  };

  return (
    <div className="app">
      <Sidebar active={view} onNavigate={handleNavigate} open={sidebarOpen} />
      <Topbar onMenuClick={() => setSidebarOpen((o) => !o)} />

      <main className="content" id="content">
        {view === "overview" && <Overview />}
        {view === "assistant" && <AIAssistant />}
        {view === "map" && <MapView />}
        {view === "analytics" && <Analytics />}
        {view === "compare" && <Compare />}
        {view === "reports" && <Reports />}
        {view === "sources" && <DataSources />}
      </main>
    </div>
  );
}
