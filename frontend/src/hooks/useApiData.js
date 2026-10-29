import { useEffect, useState } from "react";

/**
 * Runs `fetcher()` (expected to return `request(...)`'s {data, meta}) whenever
 * `deps` changes, exposing {data, meta, loading, error, refetch}.
 */
export function useApiData(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, meta: null, loading: true, error: null });
  const [reloadIndex, setReloadIndex] = useState(0);
  const depsKey = JSON.stringify(deps);

  useEffect(() => {
    let cancelled = false;
    Promise.resolve()
      .then(() => {
        if (!cancelled) setState((s) => ({ ...s, loading: true, error: null }));
        return fetcher();
      })
      .then(({ data, meta }) => {
        if (!cancelled) setState({ data, meta, loading: false, error: null });
      })
      .catch((error) => {
        if (!cancelled) setState({ data: null, meta: null, loading: false, error });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [depsKey, reloadIndex]);

  return { ...state, refetch: () => setReloadIndex((i) => i + 1) };
}
