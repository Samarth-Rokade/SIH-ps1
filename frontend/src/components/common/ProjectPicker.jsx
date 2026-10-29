import { useState } from "react";
import { listProjects } from "../../api/projects";
import { useApiData } from "../../hooks/useApiData";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import RiskBadge from "./RiskBadge";

/**
 * Search-as-you-type project selector. Calls onSelect(project) with a
 * ProjectListItem; `selected` (optional) shows the current choice.
 */
export default function ProjectPicker({ selected, onSelect, placeholder = "Search projects by name..." }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const search = useDebouncedValue(query.trim(), 300);
  const results = useApiData(
    () => listProjects({ search, page: 1, page_size: 8, sort_by: "risk_score", sort_order: "desc" }),
    [search]
  );

  return (
    <div className="relative">
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={selected ? selected.project_name : placeholder}
        className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-text-muted"
      />
      {open && (
        <div className="absolute z-20 mt-1 max-h-72 w-full overflow-y-auto rounded-lg border border-border bg-surface shadow-lg">
          {results.loading && <div className="px-3 py-2 text-xs text-text-muted">Searching...</div>}
          {results.error && <div className="px-3 py-2 text-xs text-critical">{results.error.message}</div>}
          {results.data?.length === 0 && <div className="px-3 py-2 text-xs text-text-muted">No projects found.</div>}
          {results.data?.map((p) => (
            <button
              key={p.project_id}
              type="button"
              onClick={() => {
                onSelect(p);
                setQuery("");
                setOpen(false);
              }}
              className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm hover:bg-surface-hover"
            >
              <span className="min-w-0">
                <span className="block truncate">{p.project_name}</span>
                <span className="block truncate text-xs text-text-muted">
                  {p.project_id} · {p.sector} · {p.state}
                </span>
              </span>
              <RiskBadge level={p.risk_level} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
