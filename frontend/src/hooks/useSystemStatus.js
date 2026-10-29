import { getSystemStatus } from "../api/system";
import { useApiData } from "./useApiData";

/** Maps the live /system/status result to a dot colour class and the two label variants. */
export function useSystemStatus() {
  const { data, error, loading } = useApiData(getSystemStatus, []);
  if (error) return { dot: "bg-critical", pill: "Offline", footer: "Backend Unreachable" };
  if (loading) return { dot: "bg-text-muted", pill: "Checking...", footer: "Checking status..." };
  if (data.status === "online") return { dot: "bg-low", pill: "System Online", footer: "All Systems Online" };
  return { dot: "bg-medium", pill: "Degraded", footer: "Degraded" };
}
