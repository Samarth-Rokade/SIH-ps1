import { cleanParams, request } from "./client";

export const listAlerts = (params) => request({ url: "/alerts", params: cleanParams(params) });

export const getAlertSummary = () => request({ url: "/alerts/summary" });
