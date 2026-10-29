export const RISK_COLORS = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

export const RISK_LEVELS = ["critical", "high", "medium", "low"];

/** Display-only categorization, mirrors backend/app/ml/risk_engine.py risk_level(). */
export function riskLevelFromScore(score) {
  if (score > 80) return "critical";
  if (score > 60) return "high";
  if (score > 30) return "medium";
  return "low";
}
