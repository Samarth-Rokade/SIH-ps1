import { getDataInfo, getModelInfo, getSystemStatus } from "../api/system";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";
import { useTheme } from "../theme/themeContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
const APP_VERSION = "1.0";

const SERVICE_DOT = {
  online: "bg-low",
  healthy: "bg-low",
  fallback: "bg-medium",
  degraded: "bg-medium",
  unavailable: "bg-critical",
};

export default function Settings() {
  const { theme, toggleTheme } = useTheme();
  const status = useApiData(getSystemStatus, []);
  const dataInfo = useApiData(getDataInfo, []);
  const models = useApiData(getModelInfo, []);

  return (
    <div>
      <Topbar title="Settings" subtitle="System health, data, models and appearance" />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Section title="System Status">
          <Async state={status}>
            {(s) => (
              <div className="space-y-2 text-sm">
                <StatusRow label="Overall" value={s.status} />
                <StatusRow label="Database" value={s.database} />
                <StatusRow label="ML Service" value={s.ml_service} />
                <StatusRow label={`LLM Service (${s.llm_model})`} value={s.llm_service} />
                <Row label="Last Data Update" value={s.last_data_update} />
                {s.llm_note && (
                  <div className="mt-3 rounded-lg border border-border bg-bg p-3 text-xs text-text-muted">
                    <p className="mb-2 text-text">{s.llm_note}</p>
                    <p className="mb-1">To enable the local LLM assistant:</p>
                    <ol className="list-decimal space-y-1 pl-4">
                      <li>Install Ollama from ollama.com.</li>
                      <li>
                        Run <code className="rounded bg-surface-hover px-1">ollama pull llama3.2</code>
                      </li>
                      <li>
                        Optionally set <code className="rounded bg-surface-hover px-1">OLLAMA_URL</code> and{" "}
                        <code className="rounded bg-surface-hover px-1">OLLAMA_MODEL</code> environment variables on the
                        backend, then restart it.
                      </li>
                    </ol>
                  </div>
                )}
              </div>
            )}
          </Async>
        </Section>

        <Section title="Data Information">
          <Async state={dataInfo}>
            {(d) => (
              <div className="space-y-2 text-sm">
                <Row label="Data As Of" value={d.data_as_of} />
                <Row label="Total Projects" value={d.total_projects.toLocaleString("en-IN")} />
                <Row label="Records Processed" value={d.records_processed.toLocaleString("en-IN")} />
                <Row label="Last Processed" value={new Date(d.last_processed).toLocaleString()} />
                <Row label="Source" value={d.source} />
              </div>
            )}
          </Async>
        </Section>

        <Section title="Model Information" className="lg:col-span-2">
          <Async state={models}>
            {(m) => (
              <>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <ModelCard title="Delay Model" model={m.delay_model} />
                  <ModelCard title="Cost Model" model={m.cost_model} />
                </div>
                <p className="mt-3 text-xs text-text-muted">Explainability: {m.explainability}</p>
              </>
            )}
          </Async>
        </Section>

        <Section title="Appearance">
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-muted">Theme: {theme === "dark" ? "Dark" : "Light"}</span>
            <button
              onClick={toggleTheme}
              className="rounded-lg border border-border px-3 py-1.5 text-xs hover:bg-surface-hover"
            >
              Switch to {theme === "dark" ? "Light" : "Dark"}
            </button>
          </div>
        </Section>

        <Section title="About">
          <div className="space-y-2 text-sm">
            <Row label="Application" value="PAIMANA Sentinel AI" />
            <Row label="Version" value={APP_VERSION} />
            <Row label="API Base URL" value={API_BASE_URL} />
            <p className="pt-2 text-xs text-text-muted">
              Decision-support prototype. Risk scores and predictions are model estimates built on a monthly data
              snapshot and are not official figures or guaranteed outcomes.
            </p>
          </div>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children, className = "" }) {
  return (
    <div className={`rounded-xl border border-border bg-surface p-5 ${className}`}>
      <h2 className="mb-3 text-sm font-semibold">{title}</h2>
      {children}
    </div>
  );
}

function Async({ state, children }) {
  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState error={state.error} onRetry={state.refetch} />;
  return children(state.data);
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-text-muted">{label}</span>
      <span className="break-all text-right font-medium">{value}</span>
    </div>
  );
}

function StatusRow({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="flex items-center gap-2 font-medium capitalize">
        <span className={`h-2 w-2 rounded-full ${SERVICE_DOT[value] ?? "bg-text-muted"}`} />
        {value}
      </span>
    </div>
  );
}

function ModelCard({ title, model }) {
  return (
    <div className="rounded-lg border border-border bg-bg p-4">
      <div className="mb-2 text-xs uppercase tracking-wide text-text-muted">{title}</div>
      <div className="space-y-2 text-sm">
        <Row label="Algorithm" value={model.name} />
        <Row label="Version" value={model.version} />
        <Row label="Last Trained" value={model.last_trained} />
        <Row label="Validation AUC" value={model.validation_auc} />
        <Row label="Validation MAE" value={model.validation_mae} />
      </div>
    </div>
  );
}
