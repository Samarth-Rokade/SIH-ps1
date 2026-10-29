import { cleanParams, request } from "./client";

export const listAlerts = (params) => request({ url: "/alerts", params: cleanParams(params) });

export const getAlertSummary = () => request({ url: "/alerts/summary" });

export const getAlert = (alertId) => request({ url: `/alerts/${alertId}` });

export const updateAlertStatus = (alertId, status) =>
  request({ url: `/alerts/${alertId}`, method: "PATCH", data: { status } });
