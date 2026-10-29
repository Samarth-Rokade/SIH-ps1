import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router";
import Sidebar from "./components/layout/Sidebar";
import LoadingState from "./components/common/LoadingState";
const Dashboard = lazy(() => import("./pages/Dashboard"));
const RiskRadar = lazy(() => import("./pages/RiskRadar"));
const Projects = lazy(() => import("./pages/Projects"));
const ProjectDetail = lazy(() => import("./pages/ProjectDetail"));
const EarlyWarnings = lazy(() => import("./pages/EarlyWarnings"));
const Analytics = lazy(() => import("./pages/Analytics"));
const CostIntelligence = lazy(() => import("./pages/CostIntelligence"));
const Simulator = lazy(() => import("./pages/Simulator"));
const Assistant = lazy(() => import("./pages/Assistant"));
const Reports = lazy(() => import("./pages/Reports"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {
  return (
    <div className="flex h-screen bg-bg text-text">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <Suspense fallback={<LoadingState />}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/risk-radar" element={<RiskRadar />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
          <Route path="/early-warnings" element={<EarlyWarnings />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/cost-intelligence" element={<CostIntelligence />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        </Suspense>
      </main>
    </div>
  );
}

export default App;
