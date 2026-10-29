import { useState } from "react";
import { useNavigate } from "react-router";
import { getCostAnalytics } from "../api/analytics";
import { getFilterOptions } from "../api/risk";
import CostBySectorChart from "../components/charts/CostBySectorChart";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import StatCard from "../components/common/StatCard";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";
import { rupeesCrore } from "../utils/format";

const FIRST_YEAR = 2005;
const LAST_YEAR = 2026;
const CHART_SECTORS = 8;
const YEARS = Array.from({ length: LAST_YEAR - FIRST_YEAR + 1 }, (_, i) => LAST_YEAR - i);
const EMPTY_FILTERS = { sector: "", ministry: "", year: "" };

export default function CostIntelligence() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const options = useApiData(getFilterOptions, []);
  const cost = useApiData(() => getCostAnalytics(filters), [filters.sector, filters.ministry, filters.year]);

  const set = (key) => (e) => setFilters((f) => ({ ...f, [key]: e.target.value }));
  const d = cost.data;

  return (
    <div>
      <Topbar title="Cost Intelligence" subtitle="Cost escalation and forecast exposure across the portfolio" />

      <div className="mb-4 flex flex-wrap items-end gap-3 rounded-xl border border-border bg-surface p-4 text-sm">
        <FilterSelect label="Sector" value={filters.sector} onChange={set("sector")} options={options.data?.sectors ?? []} />
        <FilterSelect
          label="Ministry"
          value={filters.ministry}
          onChange={set("ministry")}
          options={options.data?.ministries ?? []}
        />
        <FilterSelect label="Start Year" value={filters.year} onChange={set("year")} options={YEARS} />
        <button
          onClick={() => setFilters(EMPTY_FILTERS)}
          className="rounded-lg border border-border px-3 py-2 text-xs text-text-muted hover:bg-surface-hover"
        >
          Reset
        </button>
      </div>

      {cost.loading && <LoadingState />}
      {cost.error && <ErrorState error={cost.error} onRetry={cost.refetch} />}
      {d && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            <StatCard label="Original Cost" value={rupeesCrore(d.total_original_cost_crore)} tone="accent" />
            <StatCard label="Current Cost" value={rupeesCrore(d.total_current_cost_crore)} tone="medium" />
            <StatCard label="Predicted Final" value={rupeesCrore(d.total_predicted_final_cost_crore)} tone="high" />
            <StatCard label="Expenditure" value={rupeesCrore(d.total_expenditure_crore)} tone="low" />
            <StatCard label="Avg Escalation" value={`${d.average_escalation_percentage}%`} tone="critical" sublabel="realized" />
            <StatCard label="Projects Escalated" value={d.projects_with_escalation.toLocaleString("en-IN")} tone="high" />
          </div>

          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Cost by Sector (top {CHART_SECTORS} by predicted final cost)</h2>
            {d.by_sector.length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">No projects match these filters.</p>
            ) : (
              <CostBySectorChart rows={d.by_sector.slice(0, CHART_SECTORS)} />
            )}
          </div>

          <div className="overflow-hidden rounded-xl border border-border bg-surface">
            <h2 className="border-b border-border p-4 text-sm font-semibold">Highest Forecast Cost Exposure</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase text-text-muted">
                    <th className="px-4 py-2">Project</th>
                    <th className="px-4 py-2">Sector</th>
                    <th className="px-4 py-2 text-right">Current</th>
                    <th className="px-4 py-2 text-right">Predicted Final</th>
                    <th className="px-4 py-2 text-right">Additional Exposure</th>
                    <th className="px-4 py-2 text-right">Escalation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {d.top_exposure_projects.map((p) => (
                    <tr
                      key={p.project_id}
                      onClick={() => navigate(`/projects/${p.project_id}`)}
                      className="cursor-pointer hover:bg-surface-hover"
                    >
                      <td className="max-w-xs truncate px-4 py-2">{p.project_name}</td>
                      <td className="px-4 py-2 text-text-muted">{p.sector}</td>
                      <td className="whitespace-nowrap px-4 py-2 text-right text-text-muted">
                        {rupeesCrore(p.current_cost_crore)}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-right text-text-muted">
                        {rupeesCrore(p.predicted_final_cost_crore)}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-right font-medium text-high">
                        {rupeesCrore(p.additional_exposure_crore)}
                      </td>
                      <td className="px-4 py-2 text-right text-text-muted">{p.expected_escalation_percentage}%</td>
                    </tr>
                  ))}
                  {d.top_exposure_projects.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                        No projects match these filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <p className="border-t border-border px-4 py-3 text-xs text-text-muted">
              Forecasts are model-based estimates, not guaranteed outcomes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function FilterSelect({ label, value, onChange, options }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-text-muted">{label}</span>
      <select value={value} onChange={onChange} className="min-w-44 rounded-lg border border-border bg-bg px-3 py-2 text-text">
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}
