export default function StatCard({ label, value, sublabel, tone = "accent" }) {
  const toneClass = {
    accent: "bg-accent-soft text-accent",
    critical: "bg-critical-soft text-critical",
    high: "bg-high-soft text-high",
    medium: "bg-medium-soft text-medium",
    low: "bg-low-soft text-low",
  }[tone];

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wide text-text-muted">{label}</span>
        <span className={`h-2 w-2 rounded-full ${toneClass}`} />
      </div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {sublabel && <div className="mt-1 text-xs text-text-muted">{sublabel}</div>}
    </div>
  );
}
