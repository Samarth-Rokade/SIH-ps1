import { useEffect, useState } from "react";

/** Returns `value` after it has stopped changing for `delayMs` (for search-as-you-type inputs). */
export function useDebouncedValue(value, delayMs = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}
