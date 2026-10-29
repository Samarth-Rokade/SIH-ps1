// higherIsWorse: true -> a positive difference is bad; false -> a negative one is bad; null -> neutral.
const ROWS = [
  {
    key: "risk",
    label: "Risk score",
    own: (b) => b.project.risk,
    peer: (b) => b.similar_projects.average_risk,
    diff: (b) => b.comparison.risk_difference,
    higherIsWorse: true,
  },
  {
    key: "progress",
    label: "Physical progress (%)",
    own: (b) => b.project.progress,
    peer: (b) => b.similar_projects.average_progress,
    diff: (b) => b.comparison.progress_difference,
    higherIsWorse: false,
  },
  {
    key: "spend",
    label: "Expenditure (% of cost)",
    own: (b) => b.project.expenditure_percentage,
    peer: (b) => b.similar_projects.average_expenditure_percentage,
    diff: (b) => b.comparison.expenditure_difference,
    higherIsWorse: null,
  },
];

export default function BenchmarkCard({ benchmark }) {
  const peers = benchmark.similar_projects;
  return (
    <div>
      <p className="mb-3 text-xs text-text-muted">
        Compared with {peers.count} similar projects ({peers.basis}).
      </p>
      <div className="space-y-3">
        {ROWS.map((row) => {
          const own = row.own(benchmark);
          const peer = row.peer(benchmark);
          const diff = row.diff(benchmark);
          const neutral = row.higherIsWorse === null || diff === 0;
          const worse = row.higherIsWorse ? diff > 0 : diff < 0;
          const tone = neutral ? "text-text-muted" : worse ? "text-critical" : "text-low";
          const scale = Math.max(100, own, peer);
          return (
            <div key={row.key}>
              <div className="mb-1 flex justify-between text-sm">
                <span>{row.label}</span>
                <span className={tone}>
                  {own} vs {peer} ({diff > 0 ? "+" : ""}
                  {diff})
                </span>
              </div>
              <div className="h-2 rounded-full bg-surface-hover">
                <div className="h-2 rounded-full bg-accent" style={{ width: `${Math.min(100, (own / scale) * 100)}%` }} />
              </div>
              <div className="mt-0.5 h-1 rounded-full bg-surface-hover">
                <div className="h-1 rounded-full bg-text-muted" style={{ width: `${Math.min(100, (peer / scale) * 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <p className="mt-3 text-[11px] text-text-muted">Blue bar: this project · grey bar: peer average</p>
    </div>
  );
}
