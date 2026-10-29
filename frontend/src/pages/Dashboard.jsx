import { useNavigate } from "react-router";
import { listAlerts } from "../api/alerts";
import { getOverview, getPriorityProjects, getRiskDistribution, getRiskMap, getRiskTrend } from "../api/dashboard";
import RiskBadge from "../components/common/RiskBadge";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import StatCard from "../components/common/StatCard";
import RiskDistributionDonut from "../components/charts/RiskDistributionDonut";
import RiskTrendChart from "../components/charts/RiskTrendChart";
import IndiaRiskMap from "../components/map/IndiaRiskMap";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

export default function Dashboard() {
  const navigate = useNavigate();

  const overview = useApiData(getOverview, []);
  const riskMap = useApiData(() => getRiskMap(), []);
  const distribution = useApiData(getRiskDistribution, []);
  const trend = useApiData(() => getRiskTrend(6), []);
  const priority = useApiData(() => getPriorityProjects(5), []);
  const recentAlerts = useApiData(() => listAlerts({ page: 1, page_size: 4 }), []);

  const anyError = overview.error || riskMap.error || distribution.error || trend.error || priority.error;
  if (anyError) return <ErrorState error={anyError} onRetry={() => window.location.reload()} />;

  return (
    <div>
      <Topbar
        title="Command Center"
        subtitle="Visualize and analyze project risks across Indian infrastructure"
      />

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-5">
        {overview.loading ? (
          <div className="col-span-5">
            <LoadingState />
          </div>
        ) : (
          <>
            <StatCard label="Total Projects" value={overview.data.total_projects} tone="accent" />
            <StatCard label="Critical Projects" value={overview.data.critical_projects} tone="critical" />
            <StatCard label="High Risk Projects" value={overview.data.high_risk_projects} tone="high" />
            <StatCard
              label="Cost Exposure"
              value={`₹${overview.data.cost_exposure_crore.toLocaleString("en-IN")} Cr`}
              tone="medium"
            />
            <StatCard label="Avg. Delay Risk" value={`${overview.data.average_delay_risk}%`} tone="accent" />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Project Risk Map (India)</h2>
            {riskMap.loading ? <LoadingState /> : <IndiaRiskMap points={riskMap.data} />}
          </div>
          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Risk Trend (Last 6 Months)</h2>
            {trend.loading ? <LoadingState /> : <RiskTrendChart points={trend.data} />}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Risk Distribution</h2>
            {distribution.loading ? (
              <LoadingState />
            ) : (
              <RiskDistributionDonut distribution={distribution.data.distribution} total={distribution.data.total} />
            )}
          </div>

          <div className="rounded-xl border border-border bg-surface p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold">Top Priority Projects</h2>
              <button onClick={() => navigate("/projects")} className="text-xs text-accent hover:underline">
                View All
              </button>
            </div>
            {priority.loading ? (
              <LoadingState />
            ) : (
              <ul className="divide-y divide-border">
                {priority.data.map((p) => (
                  <li
                    key={p.project_id}
                    onClick={() => navigate(`/projects/${p.project_id}`)}
                    className="cursor-pointer py-2 hover:bg-surface-hover"
                  >
                    <div className="flex items-center justify-between text-sm">
                      <span className="truncate pr-2">{p.project_name}</span>
                      <RiskBadge level={p.risk_level} />
                    </div>
                    <div className="text-xs text-text-muted">
                      {p.ministry} · Risk {p.risk_score} · {p.predicted_delay_months}mo delay
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-border bg-surface p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Recent Early Warnings</h2>
          <button onClick={() => navigate("/early-warnings")} className="text-xs text-accent hover:underline">
            View All
          </button>
        </div>
        {recentAlerts.loading ? (
          <LoadingState />
        ) : (
          <ul className="divide-y divide-border">
            {recentAlerts.data.map((a) => (
              <li
                key={a.alert_id}
                onClick={() => navigate(`/projects/${a.project_id}`)}
                className="flex cursor-pointer items-center justify-between py-2 text-sm hover:bg-surface-hover"
              >
                <span>{a.message}</span>
                <RiskBadge level={a.severity} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
