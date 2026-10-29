import { useState } from "react";
import { useNavigate } from "react-router";
import { getAlertSummary, listAlerts } from "../api/alerts";
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
  const [page, setPage] = useState(1);

  const summary = useApiData(getAlertSummary, []);
  const params = { page, page_size: PAGE_SIZE, severity, state, sector };
  const alerts = useApiData(() => listAlerts(params), [JSON.stringify(params)]);

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
            setPage(1);
          }}
          className="rounded-lg border border-border px-3 py-2 text-sm text-text-muted hover:bg-surface-hover"
        >
          Reset
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        {alerts.loading && <LoadingState />}
        {alerts.error && <ErrorState error={alerts.error} onRetry={alerts.refetch} />}
        {alerts.data && (
          <>
            <ul className="divide-y divide-border">
              {alerts.data.map((a) => (
                <li
                  key={a.alert_id}
                  onClick={() => navigate(`/projects/${a.project_id}`)}
                  className="flex cursor-pointer items-center justify-between gap-4 px-4 py-3 hover:bg-surface-hover"
                >
                  <div>
                    <div className="text-sm font-medium">{a.project_name}</div>
                    <div className="text-xs text-text-muted">{a.message}</div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-text-muted">
                    <span>Risk {a.risk_score}</span>
                    <span>{a.detected_at}</span>
                    <RiskBadge level={a.severity} />
                  </div>
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
