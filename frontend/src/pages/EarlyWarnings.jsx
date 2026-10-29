import { useState } from "react";
import { useNavigate } from "react-router";
import { getAlert, getAlertSummary, listAlerts, updateAlertStatus } from "../api/alerts";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import Pagination from "../components/common/Pagination";
import RiskBadge from "../components/common/RiskBadge";
import StatCard from "../components/common/StatCard";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

const PAGE_SIZE = 15;

export default function EarlyWarnings() {
  const navigate = useNavigate();
  const [severity, setSeverity] = useState("");
  const [state, setState] = useState("");
  const [sector, setSector] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [expandedId, setExpandedId] = useState(null);
  const [actionError, setActionError] = useState(null);

  const summary = useApiData(getAlertSummary, []);
  const params = { page, page_size: PAGE_SIZE, severity, state, sector, status };
  const alerts = useApiData(() => listAlerts(params), [JSON.stringify(params)]);

  async function changeStatus(alertId, next) {
    setActionError(null);
    try {
      await updateAlertStatus(alertId, next);
      alerts.refetch();
      summary.refetch();
    } catch (err) {
      setActionError(err.message);
    }
  }

  function resetPage(setter) {
    return (value) => {
      setPage(1);
      setter(value);
    };
  }

  return (
    <div>
      <Topbar title="Early Warnings" subtitle="Alerts generated from project risk indicators" />

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-5">
        {summary.loading ? (
          <div className="col-span-5">
            <LoadingState />
          </div>
        ) : summary.error ? (
          <div className="col-span-5">
            <ErrorState error={summary.error} onRetry={summary.refetch} />
          </div>
        ) : (
          <>
            <StatCard label="Critical" value={summary.data.critical} tone="critical" />
            <StatCard label="High" value={summary.data.high} tone="high" />
            <StatCard label="Medium" value={summary.data.medium} tone="medium" />
            <StatCard label="New" value={summary.data.new} tone="accent" />
            <StatCard label="Resolved" value={summary.data.resolved} tone="low" />
          </>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-3 rounded-xl border border-border bg-surface p-4">
        <select
          value={severity}
          onChange={(e) => resetPage(setSeverity)(e.target.value)}
          className="rounded-lg border border-border bg-bg px-3 py-2 text-sm capitalize"
        >
          <option value="">Severity: All</option>
          {["critical", "high", "medium"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => resetPage(setStatus)(e.target.value)}
          className="rounded-lg border border-border bg-bg px-3 py-2 text-sm capitalize"
        >
          <option value="">Status: All</option>
          {["new", "acknowledged", "resolved"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <input
          value={state}
          onChange={(e) => resetPage(setState)(e.target.value)}
          placeholder="Filter by state..."
          className="rounded-lg border border-border bg-bg px-3 py-2 text-sm"
        />
        <input
          value={sector}
          onChange={(e) => resetPage(setSector)(e.target.value)}
          placeholder="Filter by sector..."
          className="rounded-lg border border-border bg-bg px-3 py-2 text-sm"
        />
        <button
          onClick={() => {
            setSeverity("");
            setState("");
            setSector("");
            setStatus("");
            setPage(1);
          }}
          className="rounded-lg border border-border px-3 py-2 text-sm text-text-muted hover:bg-surface-hover"
        >
          Reset
        </button>
      </div>

      {actionError && (
        <div className="mb-4 rounded-lg border border-critical/30 bg-critical-soft px-4 py-2 text-sm text-critical">
          Could not update the alert: {actionError}
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        {alerts.loading && <LoadingState />}
        {alerts.error && <ErrorState error={alerts.error} onRetry={alerts.refetch} />}
        {alerts.data && (
          <>
            <ul className="divide-y divide-border">
              {alerts.data.map((a) => (
                <li key={a.alert_id}>
                  <div
                    onClick={() => setExpandedId((id) => (id === a.alert_id ? null : a.alert_id))}
                    className="flex cursor-pointer items-center justify-between gap-4 px-4 py-3 hover:bg-surface-hover"
                  >
                    <div>
                      <div className="text-sm font-medium">{a.project_name}</div>
                      <div className="text-xs text-text-muted">{a.message}</div>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-text-muted">
                      <StatusPill status={a.status} />
                      <span>Risk {a.risk_score}</span>
                      <span>{a.detected_at}</span>
                      <RiskBadge level={a.severity} />
                    </div>
                  </div>
                  {expandedId === a.alert_id && (
                    <AlertDetailPanel
                      alert={a}
                      onOpenProject={() => navigate(`/projects/${a.project_id}`)}
                      onChangeStatus={(next) => changeStatus(a.alert_id, next)}
                    />
                  )}
                </li>
              ))}
              {alerts.data.length === 0 && (
                <li className="px-4 py-8 text-center text-sm text-text-muted">No alerts match these filters.</li>
              )}
            </ul>
            <Pagination
              page={page}
              totalPages={Math.max(1, Math.ceil((alerts.meta?.total ?? 0) / PAGE_SIZE))}
              total={alerts.meta?.total}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}

const STATUS_STYLES = {
  new: "bg-accent-soft text-accent",
  acknowledged: "bg-medium-soft text-medium",
  resolved: "bg-low-soft text-low",
};

function StatusPill({ status }) {
  return (
    <span className={`rounded px-2 py-0.5 text-[11px] font-semibold capitalize ${STATUS_STYLES[status] ?? ""}`}>
      {status}
    </span>
  );
}

function AlertDetailPanel({ alert, onOpenProject, onChangeStatus }) {
  const detail = useApiData(() => getAlert(alert.alert_id), [alert.alert_id, alert.status]);

  return (
    <div className="border-t border-border bg-bg/40 px-4 py-4 text-sm">
      {detail.loading && <div className="text-text-muted">Loading details...</div>}
      {detail.error && <ErrorState error={detail.error} onRetry={detail.refetch} />}
      {detail.data && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="md:col-span-2 space-y-2">
            <div>
              <div className="text-xs uppercase text-text-muted">Alert type</div>
              <div className="capitalize">{detail.data.type.replaceAll("_", " ")}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-text-muted">Description</div>
              <div>{detail.data.description}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-text-muted">Recommended review</div>
              <div>{detail.data.recommended_review}</div>
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-xs uppercase text-text-muted">Risk movement</div>
              <div className="text-lg font-semibold">
                {detail.data.risk_before} → {detail.data.risk_current}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={onOpenProject}
                className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:bg-surface-hover"
              >
                Open project
              </button>
              {detail.data.status === "new" && (
                <button
                  onClick={() => onChangeStatus("acknowledged")}
                  className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white hover:opacity-90"
                >
                  Acknowledge
                </button>
              )}
              {detail.data.status !== "resolved" ? (
                <button
                  onClick={() => onChangeStatus("resolved")}
                  className="rounded-lg border border-low/50 px-3 py-1.5 text-xs font-medium text-low hover:bg-low-soft"
                >
                  Mark resolved
                </button>
              ) : (
                <button
                  onClick={() => onChangeStatus("new")}
                  className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-text-muted hover:bg-surface-hover"
                >
                  Reopen
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
