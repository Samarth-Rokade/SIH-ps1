import { cleanParams, request } from "./client";

export const getOverview = () => request({ url: "/dashboard/overview" });

export const getRiskMap = (riskLevel) =>
  request({ url: "/dashboard/risk-map", params: cleanParams({ risk_level: riskLevel }) });

export const getRiskDistribution = () => request({ url: "/dashboard/risk-distribution" });

export const getRiskTrend = (months = 6) =>
  request({ url: "/dashboard/risk-trend", params: { months } });

export const getPriorityProjects = (limit = 10) =>
  request({ url: "/dashboard/priority-projects", params: { limit } });
