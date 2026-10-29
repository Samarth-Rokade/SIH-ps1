export default function Pagination({ page, totalPages, total, onPageChange }) {
  return (
    <div className="flex items-center justify-between border-t border-border px-4 py-3 text-sm text-text-muted">
      <span>
        Page {page} of {totalPages} {total !== undefined && `(${total} total)`}
      </span>
      <div className="flex gap-2">
        <button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="rounded border border-border px-3 py-1 disabled:opacity-40 hover:enabled:bg-surface-hover"
        >
          Prev
        </button>
        <button
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="rounded border border-border px-3 py-1 disabled:opacity-40 hover:enabled:bg-surface-hover"
        >
          Next
        </button>
      </div>
    </div>
  );
}
