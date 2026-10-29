import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { listProjects } from "../api/projects";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import Pagination from "../components/common/Pagination";
import RiskBadge from "../components/common/RiskBadge";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";
import { RISK_LEVELS } from "../utils/riskColors";

const PAGE_SIZE = 20;
const EMPTY_FILTERS = { search: "", ministry: "", sector: "", state: "", risk_level: "", status: "" };

export default function Projects() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState({ sort_by: "risk_score", sort_order: "desc" });

  const params = { ...filters, page, page_size: PAGE_SIZE, ...sort };
  const list = useApiData(() => listProjects(params), [JSON.stringify(params)]);

  // Fetch the full dataset once (small enough - a few thousand rows) so
  // filter dropdowns reflect every ministry/sector/state, not a biased sample.
  const optionsSource = useApiData(() => listProjects({ page: 1, page_size: 4000 }), []);
  const options = useMemo(() => {
    const rows = optionsSource.data ?? [];
    return {
      ministry: [...new Set(rows.map((r) => r.ministry))].sort(),
      sector: [...new Set(rows.map((r) => r.sector))].sort(),
      state: [...new Set(rows.map((r) => r.state))].sort(),
    };
  }, [optionsSource.data]);

  function updateFilter(key, value) {
    setPage(1);
    setFilters((f) => ({ ...f, [key]: value }));
  }

  function toggleSort(column) {
    setSort((s) =>
      s.sort_by === column
        ? { sort_by: column, sort_order: s.sort_order === "asc" ? "desc" : "asc" }
        : { sort_by: column, sort_order: "desc" }
    );
  }

  const columns = [
    { key: "project_name", label: "Project Name", sortable: false },
    { key: "ministry", label: "Ministry", sortable: false },
    { key: "state", label: "State", sortable: false },
    { key: "current_cost_crore", label: "Cost (Cr)", sortable: true },
    { key: "physical_progress", label: "Progress", sortable: true },
    { key: "risk_score", label: "Risk", sortable: true },
    { key: "predicted_delay_months", label: "Delay", sortable: false },
  ];

  return (
    <div>
      <Topbar title="Projects" subtitle="Search and filter all monitored infrastructure projects" />

      <div className="mb-4 flex flex-wrap gap-3 rounded-xl border border-border bg-surface p-4">
        <input
          value={filters.search}
          onChange={(e) => updateFilter("search", e.target.value)}
          placeholder="Search project name..."
          className="min-w-[220px] flex-1 rounded-lg border border-border bg-bg px-3 py-2 text-sm"
        />
        <FilterSelect label="Ministry" value={filters.ministry} options={options.ministry} onChange={(v) => updateFilter("ministry", v)} />
        <FilterSelect label="Sector" value={filters.sector} options={options.sector} onChange={(v) => updateFilter("sector", v)} />
        <FilterSelect label="State" value={filters.state} options={options.state} onChange={(v) => updateFilter("state", v)} />
        <FilterSelect label="Risk Level" value={filters.risk_level} options={RISK_LEVELS} onChange={(v) => updateFilter("risk_level", v)} />
        <FilterSelect label="Status" value={filters.status} options={["Ongoing", "Completed"]} onChange={(v) => updateFilter("status", v)} />
        <button
          onClick={() => {
            setFilters(EMPTY_FILTERS);
            setPage(1);
          }}
          className="rounded-lg border border-border px-3 py-2 text-sm text-text-muted hover:bg-surface-hover"
        >
          Reset
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        {list.loading && <LoadingState />}
        {list.error && <ErrorState error={list.error} onRetry={list.refetch} />}
        {list.data && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs uppercase text-text-muted">
                    {columns.map((col) => (
                      <th
                        key={col.key}
                        onClick={() => col.sortable && toggleSort(col.key)}
                        className={`px-4 py-3 ${col.sortable ? "cursor-pointer select-none hover:text-text" : ""}`}
                      >
                        {col.label}
                        {sort.sort_by === col.key && (sort.sort_order === "asc" ? " ↑" : " ↓")}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {list.data.map((p) => (
                    <tr
                      key={p.project_id}
                      onClick={() => navigate(`/projects/${p.project_id}`)}
                      className="cursor-pointer hover:bg-surface-hover"
                    >
                      <td className="max-w-xs truncate px-4 py-3">{p.project_name}</td>
                      <td className="px-4 py-3 text-text-muted">{p.ministry}</td>
                      <td className="px-4 py-3 text-text-muted">{p.state}</td>
                      <td className="px-4 py-3">₹{p.current_cost_crore.toLocaleString("en-IN")}</td>
                      <td className="px-4 py-3">{p.physical_progress}%</td>
                      <td className="px-4 py-3">
                        <RiskBadge level={p.risk_level} />
                        <span className="ml-1 text-text-muted">{p.risk_score}</span>
                      </td>
                      <td className="px-4 py-3 text-text-muted">{p.predicted_delay_months} mo</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              page={page}
              totalPages={list.meta?.total_pages ?? 1}
              total={list.meta?.total}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-border bg-bg px-3 py-2 text-sm capitalize text-text"
    >
      <option value="">{label}: All</option>
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  );
}
