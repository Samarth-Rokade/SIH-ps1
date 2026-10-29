import { useSystemStatus } from "../../hooks/useSystemStatus";

export default function Topbar({ title, subtitle }) {
  const status = useSystemStatus();

  return (
    <div className="mb-6 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-semibold text-text">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-text-muted">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-text-muted">
        <span className={`h-2 w-2 rounded-full ${status.dot}`} />
        {status.pill}
      </div>
    </div>
  );
}
