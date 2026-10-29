export default function ErrorState({ error, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-critical/30 bg-critical-soft p-10 text-sm text-critical">
      <span>{error?.message || "Something went wrong."}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded border border-critical/40 px-3 py-1 text-xs font-semibold hover:bg-critical/10"
        >
          Retry
        </button>
      )}
    </div>
  );
}
