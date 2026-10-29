import { cleanParams, request } from "./client";

export const getMinistryAnalytics = () => request({ url: "/analytics/ministries" });

export const getSectorAnalytics = () => request({ url: "/analytics/sectors" });

export const getStateAnalytics = () => request({ url: "/analytics/states" });

export const getCostAnalytics = (params = {}) =>
  request({ url: "/analytics/cost", params: cleanParams(params) });
