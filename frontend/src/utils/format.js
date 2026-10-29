const LAKH_CRORE = 100000;

/** Compact rupee-crore label: 2,500,000 -> "25 L Cr" (lakh crore), 4,200 -> "4.2K Cr", 350 -> "350 Cr". */
export function formatCrore(value) {
  const abs = Math.abs(value);
  if (abs >= LAKH_CRORE) return `${+(value / LAKH_CRORE).toFixed(1)} L Cr`;
  if (abs >= 1000) return `${+(value / 1000).toFixed(1)}K Cr`;
  return `${+value.toFixed(0)} Cr`;
}

export const rupeesCrore = (value) => `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 1 })} Cr`;
