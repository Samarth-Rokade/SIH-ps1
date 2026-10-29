export default function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center rounded-xl border border-border bg-surface p-10 text-sm text-text-muted">
      {label}
    </div>
  );
}
