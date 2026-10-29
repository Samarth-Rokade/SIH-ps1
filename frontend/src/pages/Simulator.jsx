import { useState } from "react";
import { Link, useSearchParams } from "react-router";
import { getProject } from "../api/projects";
import { getSimulatorParameters, runSimulation } from "../api/simulator";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import ProjectPicker from "../components/common/ProjectPicker";
import RiskBadge from "../components/common/RiskBadge";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

const RECOVERY_OPTIONS = [
  { value: "none", label: "None", share: "0%" },
  { value: "low", label: "Low", share: "10%" },
  { value: "medium", label: "Medium", share: "25%" },
  { value: "high", label: "High", share: "40%" },
];

export default function Simulator() {
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = searchParams.get("project");

  const project = useApiData(() => (projectId ? getProject(projectId) : Promise.resolve({ data: null })), [projectId]);

  return (
    <div>
      <Topbar title="What-if Simulator" subtitle="Test interventions and see how the model re-scores the project" />

      <div className="mb-4 rounded-xl border border-border bg-surface p-4">
        <h2 className="mb-2 text-sm font-semibold">Project</h2>
        <ProjectPicker
          selected={project.data}
          onSelect={(p) => setSearchParams({ project: p.project_id })}
          placeholder="Search for a project to simulate..."
        />
        {project.data && (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-text-muted">
            <span className="text-sm font-medium text-text">{project.data.project_name}</span>
            <span>{project.data.project_id}</span>
            <span>· {project.data.sector}</span>
            <span>· {project.data.state}</span>
            <Link to={`/projects/${project.data.project_id}`} className="text-accent hover:underline">
              View project →
            </Link>
          </div>
        )}
        {project.error && <p className="mt-2 text-xs text-critical">{project.error.message}</p>}
      </div>

      {projectId ? (
        <SimulatorPanel key={projectId} projectId={projectId} />
      ) : (
        <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-border bg-surface text-sm text-text-muted">
          Select a project above to start a simulation.
        </div>
      )}
    </div>
  );
}

function SimulatorPanel({ projectId }) {
  const params = useApiData(() => getSimulatorParameters(projectId), [projectId]);
  // Only the user's edits are state; unedited fields fall back to the project's current values.
  const [edits, setEdits] = useState({});
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState(null);

  if (params.loading) return <LoadingState label="Loading simulator..." />;
  if (params.error) return <ErrorState error={params.error} onRetry={params.refetch} />;

  const p = params.data;

  const values = {
    physical_progress: p.physical_progress.current,
    expenditure_percentage: p.expenditure_percentage.current,
    milestone_recovery: p.milestone_recovery.current,
    ...edits,
  };
  const setValues = (update) => setEdits(update(values));

  function reset() {
    setEdits({});
    setResult(null);
    setRunError(null);
  }

  async function run() {
    setRunning(true);
    setRunError(null);
    try {
      const { data } = await runSimulation({ project_id: projectId, ...values });
      setResult(data);
    } catch (err) {
      setRunError(err);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="rounded-xl border border-border bg-surface p-5 lg:col-span-1">
        <h2 className="mb-4 text-sm font-semibold">Scenario Inputs</h2>

        <SliderField
          label="Physical progress (%)"
          param={p.physical_progress}
          value={values.physical_progress}
          onChange={(v) => setValues((s) => ({ ...s, physical_progress: v }))}
        />
        <SliderField
          label="Expenditure (% of revised cost)"
          param={p.expenditure_percentage}
          value={values.expenditure_percentage}
          onChange={(v) => setValues((s) => ({ ...s, expenditure_percentage: v }))}
        />

        <div className="mb-5">
          <div className="mb-1 text-xs text-text-muted">Milestone recovery</div>
          <div className="grid grid-cols-4 gap-1 rounded-lg border border-border bg-bg p-1">
            {RECOVERY_OPTIONS.filter((o) => p.milestone_recovery.options.includes(o.value)).map((o) => (
              <button
                key={o.value}
                type="button"
                onClick={() => setValues((s) => ({ ...s, milestone_recovery: o.value }))}
                className={`rounded-md px-2 py-1.5 text-xs transition-colors ${
                  values.milestone_recovery === o.value
                    ? "bg-accent text-white"
                    : "text-text-muted hover:bg-surface-hover"
                }`}
              >
                {o.label}
              </button>
            ))}
          </div>
          <p className="mt-2 text-xs text-text-muted">
            Share of accumulated schedule slippage recovered:{" "}
            {RECOVERY_OPTIONS.map((o) => `${o.label.toLowerCase()} ${o.share}`).join(" / ")}.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={run}
            disabled={running}
            className="flex-1 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {running ? "Running..." : "Run Simulation"}
          </button>
          <button
            onClick={reset}
            className="rounded-lg border border-border px-3 py-2 text-sm text-text-muted hover:bg-surface-hover"
          >
            Reset
          </button>
        </div>
        {runError && <p className="mt-3 text-xs text-critical">{runError.message}</p>}
      </div>

      <div className="lg:col-span-2">
        {result ? (
          <Results result={result} />
        ) : (
          <div className="flex h-full min-h-48 items-center justify-center rounded-xl border border-dashed border-border bg-surface p-6 text-center text-sm text-text-muted">
            Adjust the inputs and run the simulation to compare the current and simulated risk.
          </div>
        )}
      </div>
    </div>
  );
}

function SliderField({ label, param, value, onChange }) {
  function set(raw) {
    const n = Number(raw);
    if (Number.isNaN(n)) return;
    onChange(Math.min(param.max, Math.max(param.min, n)));
  }
  return (
    <div className="mb-5">
      <div className="mb-1 flex items-center justify-between text-xs text-text-muted">
        <span>{label}</span>
        <span>current {param.current}</span>
      </div>
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={param.min}
          max={param.max}
          step="0.5"
          value={value}
          onChange={(e) => set(e.target.value)}
          className="h-2 flex-1 cursor-pointer accent-[var(--color-accent)]"
        />
        <input
          type="number"
          min={param.min}
          max={param.max}
          step="0.5"
          value={value}
          onChange={(e) => set(e.target.value)}
          className="w-20 rounded-lg border border-border bg-bg px-2 py-1 text-right text-sm text-text"
        />
      </div>
    </div>
  );
}

function Results({ result }) {
  const { baseline, simulation, change } = result;
  const delta = simulation.risk_score - baseline.risk_score;
  const tone = delta < 0 ? "text-low" : delta > 0 ? "text-critical" : "text-text-muted";

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-border bg-surface p-5">
        <div className="text-xs uppercase tracking-wide text-text-muted">Simulation result</div>
        <div className={`mt-1 text-2xl font-bold ${tone}`}>
          Risk {baseline.risk_score} → {simulation.risk_score} ({delta > 0 ? "+" : ""}
          {delta.toFixed(1)})
        </div>
        <div className="mt-1 text-xs text-text-muted">
          {change.delay_reduction_months >= 0 ? "Delay reduced" : "Delay increased"} by{" "}
          {Math.abs(change.delay_reduction_months)} months · cost{" "}
          {change.cost_reduction_crore >= 0 ? "reduced" : "increased"} by ₹
          {Math.abs(change.cost_reduction_crore).toLocaleString("en-IN")} Cr
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <OutcomeCard title="Current" outcome={baseline} />
        <OutcomeCard title="Simulated" outcome={simulation} baseline={baseline} highlight />
      </div>

      <div className="rounded-xl border border-high/30 bg-high-soft p-4 text-xs text-high">
        <div className="mb-1 font-semibold">Model-based scenario simulation, not a guaranteed outcome</div>
        {result.disclaimer}
      </div>
    </div>
  );
}

function OutcomeCard({ title, outcome, baseline, highlight }) {
  return (
    <div className={`rounded-xl border bg-surface p-5 ${highlight ? "border-accent" : "border-border"}`}>
      <div className="mb-3 text-xs uppercase tracking-wide text-text-muted">{title}</div>
      <div className="mb-4 flex items-end gap-3">
        <span className="text-4xl font-bold">{outcome.risk_score}</span>
        <RiskBadge level={outcome.risk_level} />
        {baseline && <Delta now={outcome.risk_score} before={baseline.risk_score} unit="" />}
      </div>
      <div className="space-y-2 text-sm">
        <Line
          label="Delay probability"
          value={`${Math.round(outcome.delay_probability * 100)}%`}
          delta={baseline && <Delta now={outcome.delay_probability * 100} before={baseline.delay_probability * 100} unit="%" digits={0} />}
        />
        <Line
          label="Predicted delay"
          value={`${outcome.predicted_delay_months} months`}
          delta={baseline && <Delta now={outcome.predicted_delay_months} before={baseline.predicted_delay_months} unit=" mo" digits={0} />}
        />
        <Line
          label="Predicted cost"
          value={`₹${outcome.predicted_cost_crore.toLocaleString("en-IN")} Cr`}
          delta={baseline && <Delta now={outcome.predicted_cost_crore} before={baseline.predicted_cost_crore} unit=" Cr" digits={1} />}
        />
      </div>
    </div>
  );
}

function Line({ label, value, delta }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="flex items-center gap-2 font-medium">
        {value}
        {delta}
      </span>
    </div>
  );
}

/** Lower is better for every metric shown (risk, probability, months, cost). */
function Delta({ now, before, unit, digits = 1 }) {
  const diff = now - before;
  if (Math.abs(diff) < 10 ** -digits / 2) return <span className="text-xs text-text-muted">no change</span>;
  const good = diff < 0;
  return (
    <span className={`text-xs font-semibold ${good ? "text-low" : "text-critical"}`}>
      {diff > 0 ? "+" : ""}
      {diff.toFixed(digits)}
      {unit}
    </span>
  );
}
