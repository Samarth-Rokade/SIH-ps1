import { Navigate, Route, Routes } from "react-router";
import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard";
import RiskRadar from "./pages/RiskRadar";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import EarlyWarnings from "./pages/EarlyWarnings";
import ComingSoon from "./pages/ComingSoon";

const COMING_SOON_ROUTES = [
  { path: "/analytics", title: "Analytics" },
  { path: "/cost-intelligence", title: "Cost Intelligence" },
  { path: "/simulator", title: "What-if Simulator" },
  { path: "/assistant", title: "AI Assistant" },
  { path: "/reports", title: "Reports" },
  { path: "/settings", title: "Settings" },
];

function App() {
  return (
    <div className="flex h-screen bg-bg text-text">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/risk-radar" element={<RiskRadar />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
          <Route path="/early-warnings" element={<EarlyWarnings />} />
          {COMING_SOON_ROUTES.map(({ path, title }) => (
            <Route key={path} path={path} element={<ComingSoon title={title} />} />
          ))}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
