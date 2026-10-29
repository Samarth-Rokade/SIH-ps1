import Topbar from "../components/layout/Topbar";

export default function ComingSoon({ title }) {
  return (
    <div>
      <Topbar title={title} subtitle="This section is coming soon" />
      <div className="flex h-80 flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border bg-surface text-text-muted">
        <span className="text-4xl">🚧</span>
        <span className="text-sm">
          {title} will be available once its backend endpoints are built.
        </span>
      </div>
    </div>
  );
}
