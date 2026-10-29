import { useNavigate, useParams } from "react-router";
import { getCostPrediction, getDelayPrediction, getProject, getProjectRisk, getRiskDrivers } from "../api/projects";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import RiskBadge from "../components/common/RiskBadge";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const project = useApiData(() => getProject(projectId), [projectId]);
  const risk = useApiData(() => getProjectRisk(projectId), [projectId]);
  const delay = useApiData(() => getDelayPrediction(projectId), [projectId]);
  const cost = useApiData(() => getCostPrediction(projectId), [projectId]);
  const drivers = useApiData(() => getRiskDrivers(projectId), [projectId]);

  if (project.loading) return <LoadingState label="Loading project..." />;
  if (project.error) return <ErrorState error={project.error} onRetry={project.refetch} />;

  const p = project.data;

  return (
    <div>
      <Topbar title="Project Intelligence" subtitle="Detailed AI-driven insights for this project" />
      <button onClick={() => navigate(-1)} className="mb-3 text-sm text-accent hover:underline">
        ← Back
      </button>

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4 rounded-xl border border-border bg-surface p-5">
        <div>
          <h1 className="text-lg font-semibold">{p.project_name}</h1>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            <Tag>{p.ministry}</Tag>
            <Tag>{p.sector}</Tag>
            <Tag>{p.state}</Tag>
            <Tag>{p.project_id}</Tag>
            <Tag>{p.status}</Tag>
          </div>
        </div>
        {risk.data && (
          <div className="text-right">
            <div className="text-xs uppercase text-text-muted">Overall Risk Score</div>
            <div className="text-3xl font-bold">{risk.data.risk_score}</div>
            <RiskBadge level={risk.data.risk_level} />
          </div>
        )}
      </div>

      {risk.loading && <LoadingState />}
      {risk.error && <ErrorState error={risk.error} onRetry={risk.refetch} />}
      {risk.data && (
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Metric label="Delay Probability" value={`${Math.round(risk.data.delay_probability * 100)}%`} />
          <Metric label="Cost Overrun Probability" value={`${Math.round(risk.data.cost_overrun_probability * 100)}%`} />
          <Metric label="Progress Risk" value={Math.round(risk.data.progress_risk)} />
          <Metric label="Financial Risk" value={Math.round(risk.data.financial_risk)} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface p-5">
          <h2 className="mb-3 text-sm font-semibold">Delay Prediction</h2>
          {delay.loading && <LoadingState />}
          {delay.error && <ErrorState error={delay.error} onRetry={delay.refetch} />}
          {delay.data && (
            <div className="space-y-2 text-sm">
              <Row label="Predicted Probability" value={`${Math.round(delay.data.delay_probability * 100)}%`} />
              <Row label="Estimated Delay" value={`${delay.data.predicted_delay_months} months`} />
              <Row
                label="Likely Range"
                value={`${delay.data.prediction_range.lower}–${delay.data.prediction_range.upper} months`}
              />
              <Row label="Model" value={delay.data.model} />
              <p className="pt-2 text-xs text-text-muted">
                This is a model estimate, not a guaranteed outcome.
              </p>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-border bg-surface p-5">
          <h2 className="mb-3 text-sm font-semibold">Cost Prediction</h2>
          {cost.loading && <LoadingState />}
          {cost.error && <ErrorState error={cost.error} onRetry={cost.refetch} />}
          {cost.data && (
            <div className="space-y-2 text-sm">
              <Row label="Original Cost" value={`₹${cost.data.original_cost_crore.toLocaleString("en-IN")} Cr`} />
              <Row label="Current Cost" value={`₹${cost.data.current_cost_crore.toLocaleString("en-IN")} Cr`} />
              <Row
                label="Predicted Final Cost"
                value={`₹${cost.data.predicted_final_cost_crore.toLocaleString("en-IN")} Cr`}
              />
              <Row label="Expected Escalation" value={`${cost.data.expected_escalation_percentage}%`} />
              <Row
                label="Additional Exposure"
                value={`₹${cost.data.additional_exposure_crore.toLocaleString("en-IN")} Cr`}
              />
              <p className="pt-2 text-xs text-text-muted">
                Model-based scenario estimate, not a guaranteed outcome.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-border bg-surface p-5 lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold">Risk Drivers (Top {drivers.data?.drivers.length ?? 5})</h2>
          {drivers.loading && <LoadingState />}
          {drivers.error && <ErrorState error={drivers.error} onRetry={drivers.refetch} />}
          {drivers.data && (
            <div className="space-y-3">
              {drivers.data.drivers.map((d) => (
                <div key={d.feature}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>{d.feature}</span>
                    <span className={d.direction === "increases" ? "text-critical" : "text-low"}>
                      {d.direction === "increases" ? "+" : "-"}
                      {d.impact}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-surface-hover">
                    <div
                      className={`h-2 rounded-full ${d.direction === "increases" ? "bg-critical" : "bg-low"}`}
                      style={{ width: `${Math.min(100, d.impact)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-border bg-surface p-5">
          <h2 className="mb-3 text-sm font-semibold">Project Information</h2>
          <div className="space-y-2 text-sm">
            <Row label="Start Date" value={p.start_date} />
            <Row label="Original Completion" value={p.original_completion_date} />
            <Row label="Current Completion" value={p.current_completion_date ?? "—"} />
            <Row label="Physical Progress" value={`${p.physical_progress}%`} />
            <Row label="Expenditure" value={`₹${p.expenditure_crore.toLocaleString("en-IN")} Cr`} />
          </div>
        </div>
      </div>
    </div>
  );
}

function Tag({ children }) {
  return <span className="rounded bg-surface-hover px-2 py-1 text-text-muted">{children}</span>;
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <div className="text-xs uppercase text-text-muted">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
