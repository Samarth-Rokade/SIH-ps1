const STYLES = {
  critical: "bg-critical-soft text-critical",
  high: "bg-high-soft text-high",
  medium: "bg-medium-soft text-medium",
  low: "bg-low-soft text-low",
};

export default function RiskBadge({ level }) {
  const style = STYLES[level] ?? "bg-surface-hover text-text-muted";
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold capitalize ${style}`}>
      {level}
    </span>
  );
}
