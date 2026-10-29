import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { getPriorityProjects } from "../api/dashboard";
import { getRadar, getSummary } from "../api/risk";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import RiskBadge from "../components/common/RiskBadge";
import RiskRadarScatter from "../components/charts/RiskRadarScatter";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";
import { RISK_LEVELS } from "../utils/riskColors";

const EMPTY_FILTERS = { sector: "", state: "", risk_level: "" };

export default function RiskRadar() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const radar = useApiData(() => getRadar(filters), [filters.sector, filters.state, filters.risk_level]);
  const summary = useApiData(getSummary, []);
  const priority = useApiData(() => getPriorityProjects(10), []);

  // Filter dropdown options derived once from the (currently unfiltered-by-these-fields) dataset.
  const allSectors = useApiData(() => getRadar({}), []);
  const sectorOptions = useMemo(
    () => [...new Set((allSectors.data ?? []).map((p) => p.sector))].sort(),
    [allSectors.data]
  );
  const stateOptions = useMemo(
    () => [...new Set((allSectors.data ?? []).map((p) => p.state))].sort(),
    [allSectors.data]
  );

  const clusters = useMemo(() => {
    const points = radar.data ?? [];
    const buckets = {
      "High Risk & High Cost": 0,
      "High Risk & Low Cost": 0,
      "Low Risk & High Cost": 0,
      "Low Risk & Low Cost": 0,
    };
    for (const p of points) {
      const highDelay = p.delay_probability * 100 >= 50;
      const highCost = p.cost_risk * 100 >= 50;
      if (highDelay && highCost) buckets["High Risk & High Cost"]++;
      else if (highDelay) buckets["High Risk & Low Cost"]++;
      else if (highCost) buckets["Low Risk & High Cost"]++;
      else buckets["Low Risk & Low Cost"]++;
    }
    return buckets;
  }, [radar.data]);

  return (
    <div>
      <Topbar title="Risk Radar" subtitle="Visualize and analyze project risks across India" />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="lg:col-span-3">
          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Project Risk Radar</h2>
            {radar.loading && <LoadingState />}
            {radar.error && <ErrorState error={radar.error} onRetry={radar.refetch} />}
            {radar.data && (
              <RiskRadarScatter points={radar.data} onSelect={(id) => navigate(`/projects/${id}`)} />
            )}
          </div>

          <div className="mt-4 rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Top Priority Projects</h2>
            {priority.loading ? (
              <LoadingState />
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase text-text-muted">
                    <th className="pb-2">Project</th>
                    <th className="pb-2">Ministry</th>
                    <th className="pb-2">Risk</th>
                    <th className="pb-2">Delay</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {priority.data.map((p) => (
                    <tr
                      key={p.project_id}
                      onClick={() => navigate(`/projects/${p.project_id}`)}
                      className="cursor-pointer hover:bg-surface-hover"
                    >
                      <td className="py-2 pr-2">{p.project_name}</td>
                      <td className="py-2 pr-2 text-text-muted">{p.ministry}</td>
                      <td className="py-2 pr-2">
                        <RiskBadge level={p.risk_level} />
                      </td>
                      <td className="py-2 text-text-muted">{p.predicted_delay_months} mo</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Filters</h2>
            <div className="space-y-3 text-sm">
              <FilterSelect
                label="Sector"
                value={filters.sector}
                options={sectorOptions}
                onChange={(v) => setFilters((f) => ({ ...f, sector: v }))}
              />
              <FilterSelect
                label="State"
                value={filters.state}
                options={stateOptions}
                onChange={(v) => setFilters((f) => ({ ...f, state: v }))}
              />
              <FilterSelect
                label="Risk Level"
                value={filters.risk_level}
                options={RISK_LEVELS}
                onChange={(v) => setFilters((f) => ({ ...f, risk_level: v }))}
              />
              <button
                onClick={() => setFilters(EMPTY_FILTERS)}
                className="text-xs text-accent hover:underline"
              >
                Reset filters
              </button>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Risk Summary</h2>
            {summary.loading ? (
              <LoadingState />
            ) : (
              <div className="space-y-2 text-sm">
                <SummaryRow label="Average Risk" value={summary.data.average_risk} />
                {RISK_LEVELS.map((level) => (
                  <SummaryRow key={level} label={<RiskBadge level={level} />} value={summary.data[level]} />
                ))}
              </div>
            )}
          </div>

          <div className="rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold">Project Clusters</h2>
            <div className="space-y-2 text-sm">
              {Object.entries(clusters).map(([label, count]) => (
                <SummaryRow key={label} label={label} value={count} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-text-muted">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-border bg-bg px-2 py-1.5 capitalize text-text"
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
