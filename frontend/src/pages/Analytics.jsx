import { useMemo, useState } from "react";
import { getMinistryAnalytics, getSectorAnalytics, getStateAnalytics } from "../api/analytics";
import HorizontalRiskBars from "../components/charts/HorizontalRiskBars";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

const CHART_ROWS = 12;
const NOISY_BELOW = 5;

const TABS = {
  ministries: {
    label: "Ministries",
    singular: "Ministry",
    fetcher: getMinistryAnalytics,
    nameKey: "ministry",
    columns: [
      { key: "projects", label: "Projects" },
      { key: "average_risk", label: "Avg Risk" },
      { key: "high_risk_percentage", label: "High/Critical %" },
      { key: "average_delay_months", label: "Avg Delay (mo)" },
      { key: "cost_escalation_percentage", label: "Cost Escalation %" },
    ],
  },
  sectors: {
    label: "Sectors",
    singular: "Sector",
    fetcher: getSectorAnalytics,
    nameKey: "sector",
    columns: [
      { key: "projects", label: "Projects" },
      { key: "average_risk", label: "Avg Risk" },
      { key: "high_risk_percentage", label: "High/Critical %" },
    ],
  },
  states: {
    label: "States",
    singular: "State",
    fetcher: getStateAnalytics,
    nameKey: "state",
    columns: [
      { key: "projects", label: "Projects" },
      { key: "average_risk", label: "Avg Risk" },
      { key: "critical_projects", label: "Critical Projects" },
    ],
  },
};

export default function Analytics() {
  const [tab, setTab] = useState("ministries");

  return (
    <div>
      <Topbar title="Analytics" subtitle="Ministry, sector and state risk benchmarking" />

      <div className="mb-4 inline-flex rounded-lg border border-border bg-surface p-1 text-sm">
        {Object.entries(TABS).map(([key, { label }]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`rounded-md px-4 py-1.5 transition-colors ${
              tab === key ? "bg-accent-soft font-medium text-accent" : "text-text-muted hover:text-text"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <AnalyticsTab key={tab} config={TABS[tab]} />
    </div>
  );
}

function AnalyticsTab({ config }) {
  const { nameKey, columns, fetcher, label, singular } = config;
  const result = useApiData(fetcher, []);
  const [sort, setSort] = useState({ key: "average_risk", order: "desc" });
  const [filter, setFilter] = useState("");

  const chartRows = useMemo(
    () =>
      [...(result.data ?? [])]
        .filter((r) => r.projects >= NOISY_BELOW)
        .sort((a, b) => b.average_risk - a.average_risk)
        .slice(0, CHART_ROWS),
    [result.data]
  );

  const tableRows = useMemo(() => {
    const needle = filter.trim().toLowerCase();
    const rows = (result.data ?? []).filter((r) => !needle || r[nameKey].toLowerCase().includes(needle));
    return rows.sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      const cmp = typeof av === "string" ? av.localeCompare(bv) : av - bv;
      return sort.order === "asc" ? cmp : -cmp;
    });
  }, [result.data, filter, sort, nameKey]);

  function toggleSort(key) {
    setSort((s) => (s.key === key ? { key, order: s.order === "asc" ? "desc" : "asc" } : { key, order: "desc" }));
  }

  if (result.loading) return <LoadingState />;
  if (result.error) return <ErrorState error={result.error} onRetry={result.refetch} />;

  const sortHeaders = [{ key: nameKey, label: singular }, ...columns];

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-border bg-surface p-4">
        <h2 className="mb-1 text-sm font-semibold">Highest Average Risk — Top {chartRows.length}</h2>
        <p className="mb-3 text-xs text-text-muted">
          Only entries with at least {NOISY_BELOW} projects are charted; smaller samples are noisy.
        </p>
        <HorizontalRiskBars rows={chartRows} labelKey={nameKey} />
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4">
          <h2 className="text-sm font-semibold">
            All {label} ({tableRows.length})
          </h2>
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder={`Filter ${label.toLowerCase()}...`}
            className="rounded-lg border border-border bg-bg px-3 py-1.5 text-sm"
          />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-text-muted">
                {sortHeaders.map((c) => (
                  <th
                    key={c.key}
                    onClick={() => toggleSort(c.key)}
                    className="cursor-pointer select-none whitespace-nowrap px-4 py-2 hover:text-text"
                  >
                    {c.label}
                    {sort.key === c.key && (sort.order === "asc" ? " ▲" : " ▼")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {tableRows.map((r) => (
                <tr key={r[nameKey]} className="hover:bg-surface-hover">
                  <td className="px-4 py-2">
                    {r[nameKey]}
                    {r.projects < NOISY_BELOW && (
                      <span className="ml-2 rounded bg-surface-hover px-1.5 py-0.5 text-[10px] text-text-muted">
                        small sample
                      </span>
                    )}
                  </td>
                  {columns.map((c) => (
                    <td key={c.key} className="px-4 py-2 text-text-muted">
                      {r[c.key]}
                    </td>
                  ))}
                </tr>
              ))}
              {tableRows.length === 0 && (
                <tr>
                  <td colSpan={sortHeaders.length} className="px-4 py-8 text-center text-text-muted">
                    No matches.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="border-t border-border px-4 py-3 text-xs text-text-muted">
          Note: rows with fewer than {NOISY_BELOW} projects are noisy and should be read with caution.
        </p>
      </div>
    </div>
  );
}
